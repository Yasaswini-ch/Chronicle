"""Chat engine orchestrating intents, slot filling, retrieval, and generation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from chronicle.chatbot.intent import IntentDetector
from chronicle.chatbot.response import ResponseGenerator
from chronicle.chatbot.retriever import MythRetriever
from chronicle.chatbot.slots import SlotFiller
from chronicle.insights.knowledge import MythKnowledge
from chronicle.ner.knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)


class ChatEngine:
    """Conversational dialogue manager for Greek mythology analysis and storytelling."""

    def __init__(
        self,
        myths: list[dict[str, Any]] | None = None,
        myths_path: str | Path | None = None,
        sbert_model: Any | None = None,
        knowledge_graph: KnowledgeGraph | None = None,
        knowledge: MythKnowledge | None = None,
    ) -> None:
        self.retriever = MythRetriever(myths=myths, myths_path=myths_path, sbert_model=sbert_model)
        self.knowledge = knowledge or MythKnowledge(self.retriever.myths)
        self.intent_detector = IntentDetector(knowledge=self.knowledge)
        self.slot_filler = SlotFiller(knowledge=self.knowledge)
        self.generator = ResponseGenerator()
        self.history: list[dict[str, Any]] = []

        if knowledge_graph is not None:
            self.kg = knowledge_graph
        else:
            self.kg = KnowledgeGraph()
            if self.retriever.myths:
                self.kg.build_from_annotations(self.retriever.myths)

    # ------------------------------------------------------------------ chat
    def chat(
        self, query: str, history: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Process a user query through the end-to-end dialog pipeline.

        ``history`` is the conversation memory used to resolve follow-ups and
        to record the new turn. When omitted, the engine's own shared history
        is used (fine for a single local user; servers should pass one
        history list per session).
        """
        if history is None:
            history = self.history

        if not query or not query.strip():
            return self._turn(query, self.generator.format_greeting(), "greeting", {}, None, None, history,
                              record=False, suggestions=self._starter_suggestions())

        detection = self.intent_detector.detect(query)
        intent = detection.get("intent", "unknown")

        was_follow_up = intent == "follow_up"
        # Resolve vague follow-ups ("explain it", "tell me more") against the previous turn.
        if intent == "follow_up":
            last_myth = next((t.get("myth") for t in reversed(history) if t.get("myth")), None)
            if last_myth:
                return self._turn(
                    query, self.generator.format_myth_narration(last_myth), "myth_summary",
                    {"myth_name": last_myth.get("title", "")}, last_myth, self.generator.format_story_card(last_myth), history,
                )
            intent = "unknown"

        slots = self.slot_filler.fill(query, intent)
        context: dict[str, Any] = {"intent": intent, **slots}
        retrieved_myth: dict[str, Any] | None = None
        story_card: dict[str, Any] | None = None
        suggestions: list[str] = []

        if intent == "character_info":
            name = slots.get("character", "")
            profile = self.knowledge.profile(name) if name else None
            if profile:
                context.update(character=profile["name"], profile=profile)
                if profile["myths"]:
                    retrieved_myth = self.knowledge.by_id[profile["myths"][0]["id"]]
                    story_card = self.generator.format_story_card(retrieved_myth)
                suggestions = self._character_suggestions(profile)
            elif name:
                context["character"] = name

        elif intent == "myth_summary":
            myth_name = slots.get("myth_name", slots.get("character", ""))
            myth = None
            if myth_name:
                myth = self.retriever.retrieve_by_title(myth_name)
                if not myth:
                    matches = self.retriever.retrieve_by_character(myth_name, limit=1)
                    myth = matches[0] if matches else None
            else:
                sem = self.retriever.retrieve_by_query(query, top_k=1)
                myth = sem[0] if sem else None
            if myth:
                retrieved_myth = myth
                context.update(myth_name=myth.get("title", myth_name), summary=myth.get("text", ""), moral=myth.get("moral", ""))
                story_card = self.generator.format_story_card(myth)
                suggestions = [f"Which myths are similar to {myth.get('title')}?"] + [
                    f"Who is {c['name']}?" for c in myth.get("characters", [])[:2]
                ]
            elif myth_name:
                context["summary"] = f"I could not locate an exact retelling for '{myth_name}'."

        elif intent == "family":
            name, rel = slots.get("character", ""), slots.get("relation", "")
            members = self.knowledge.family_members(name, rel) if name and rel else None
            half = self.knowledge.half_siblings(name, rel) if name and rel else []
            context.update(character=name, relation=rel, members=members, half_members=half)
            if name:
                suggestions = [f"Who is {name}?"] + [f"Who is {m}?" for m in (members or [])[:2]]

        elif intent == "relationship":
            c1, c2 = slots.get("character_1", ""), slots.get("character_2", "")
            if c1 and c2:
                context["relationship"], context["relationship_kind"] = self._relationship(c1, c2)
                suggestions = [f"Compare {c1} and {c2}", f"Who is {c1}?"]

        elif intent == "comparison":
            c1, c2 = slots.get("character_1", ""), slots.get("character_2", "")
            comparison = self.knowledge.compare(c1, c2) if c1 and c2 else None
            context["comparison_data"] = comparison
            if comparison and comparison["shared_myths"]:
                retrieved_myth = self.retriever.retrieve_by_title(comparison["shared_myths"][0])
                story_card = self.generator.format_story_card(retrieved_myth) if retrieved_myth else None
            if c1 and c2:
                suggestions = [f"How are {c1} and {c2} related?"]

        elif intent == "theme":
            theme = slots.get("theme", slots.get("character", "mythology"))
            matches = self.retriever.retrieve_by_theme(theme, limit=5)
            context.update(theme=theme, myths=[m.get("title", "") for m in matches], theme_myths=matches)
            if matches:
                retrieved_myth = matches[0]
                story_card = self.generator.format_story_card(retrieved_myth)

        elif intent == "motif":
            motif_id = self.knowledge.match_motif(query)
            rows = (self.knowledge.motif_myths(motif_id) or [])[:5] if motif_id else []
            from chronicle.insights.knowledge import MOTIFS

            context.update(motif=MOTIFS[motif_id] if motif_id else {}, motif_rows=rows)
            if rows:
                retrieved_myth = self.knowledge.by_id[rows[0]["id"]]
                story_card = self.generator.format_story_card(retrieved_myth)

        elif intent == "similar_myths":
            myth_name = slots.get("myth_name", slots.get("character", query))
            similar = self.retriever.retrieve_similar(myth_name, top_k=3)
            context.update(myth_name=myth_name, similar_myths=similar)
            if similar:
                retrieved_myth = similar[0]
                story_card = self.generator.format_story_card(retrieved_myth)

        else:
            # Nothing matched a pattern: fall back to search rather than a dead end.
            hits = [] if was_follow_up else self.knowledge.search(query, top_k=3)
            if hits:
                intent = "search"
                context.update(intent="search", search_hits=hits)
                retrieved_myth = hits[0]
                story_card = self.generator.format_story_card(retrieved_myth)
            else:
                suggestions = self._starter_suggestions()

        response_text = self.generator.generate(context)
        return self._turn(query, response_text, intent, slots, retrieved_myth, story_card, history,
                          suggestions=suggestions)

    # --------------------------------------------------------------- helpers
    def _relationship(self, c1: str, c2: str) -> tuple[str, str]:
        """Best available statement of how two characters are connected."""
        fam = self.knowledge.family
        direct = fam.describe(c1, c2)
        if direct:
            return direct, "family"
        chain = fam.path_description(c1, c2)
        if chain:
            return f"They are linked through family: {chain}", "family_chain"
        rels = self.kg.query(subject=c1, object=c2) or self.kg.query(subject=c2, object=c1)
        if rels:
            rel = rels[0]
            return f"{rel['subject']} is {rel.get('predicate', 'linked').replace('_', ' ')} {rel['object']}.", "story"
        shared = [m["title"] for m in self.retriever.myths
                  if {c1, c2} <= {c["name"] for c in m.get("characters", []) if isinstance(c, dict)}]
        if shared:
            return f"No family tie is recorded, but they appear together in {', '.join(shared[:3])}.", "shared_myth"
        path = self.kg.find_path(c1, c2)
        if path:
            return f"They are connected through {' -> '.join(path)}.", "path"
        return "No direct connection between them is recorded in the corpus.", "none"

    def _character_suggestions(self, profile: dict[str, Any]) -> list[str]:
        out = []
        for comp in profile["companions"][:2]:
            out.append(f"How are {profile['name']} and {comp['name']} related?")
        if profile["companions"]:
            out.append(f"Compare {profile['name']} and {profile['companions'][0]['name']}")
        return out[:3]

    @staticmethod
    def _starter_suggestions() -> list[str]:
        return ["Tell me the story of Icarus", "Who is Athena?", "How are Zeus and Hera related?",
                "Which myths are about hubris?", "Compare Athena and Ares"]

    def _turn(self, query, response, intent, slots, myth, story_card, history, record: bool = True,
              suggestions: list[str] | None = None) -> dict[str, Any]:
        turn = {
            "query": query,
            "response": response,
            "intent": intent,
            "slots": slots,
            "story_card": story_card,
            "myth": myth,
            "suggestions": suggestions or [],
        }
        if record:
            history.append(turn)
        return turn

    def get_history(self) -> list[dict[str, Any]]:
        """Return the conversation message history."""
        return self.history

    def reset(self) -> None:
        """Reset conversation memory."""
        self.history.clear()
