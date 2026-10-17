"""Response generator for the Chronicle mythology chatbot.

Generates structured and conversational replies from intent context and retrieved data.
"""

from __future__ import annotations

import re
from typing import Any


def _first_sentences(text: str, limit: int = 220) -> str:
    """First one or two sentences of *text*, at most *limit* characters."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    out = ""
    for s in sentences:
        if out and len(out) + len(s) > limit:
            break
        out = f"{out} {s}".strip()
        if len(out) >= limit * 0.6:
            break
    return out if len(out) <= limit else out[: limit - 1].rsplit(" ", 1)[0] + "…"


def _join(items: list[str]) -> str:
    items = [i for i in items if i]
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + f", and {items[-1]}"


class ResponseGenerator:
    """Generates natural language responses for dialog turns and myth narrations."""

    def generate(self, context: dict[str, Any]) -> str:
        """Generate response string from dialog context."""
        intent = context.get("intent", "unknown")

        if intent == "character_info":
            return self._format_character_response(context)
        elif intent == "myth_summary":
            return self._format_myth_summary_response(context)
        elif intent == "family":
            return self._format_family_response(context)
        elif intent == "relationship":
            return self._format_relationship_response(context)
        elif intent == "comparison":
            return self._format_comparison_response(context)
        elif intent == "theme":
            return self._format_theme_response(context)
        elif intent == "motif":
            return self._format_motif_response(context)
        elif intent == "similar_myths":
            return self._format_similar_myths_response(context)
        elif intent == "search":
            return self._format_search_response(context)
        else:
            return self.format_unknown()

    # ------------------------------------------------------------ characters
    def _format_character_response(self, context: dict[str, Any]) -> str:
        profile = context.get("profile")
        if not profile:
            char = context.get("character", "that figure")
            return f"I could not find **{char}** in the corpus. Try a name such as Athena, Odysseus or Medusa."

        name = profile["name"]
        kind = {"god": "a god", "titan": "a Titan", "creature": "a creature", "mortal": "a mortal"}.get(profile["type"], "a figure")
        lines = [f"**{name}** is {kind} of Greek mythology."]
        names = []
        if profile.get("roman_name") and profile["roman_name"] != name:
            names.append(f"known to the Romans as {profile['roman_name']}")
        other = [
            a for a in profile.get("aliases", [])
            if a not in (profile.get("roman_name"), name) and name not in a and a.lower() not in ("pallas",)
        ][:3]
        if other:
            names.append(f"also called {_join(other)}")
        if names:
            joined = ", ".join(names)
            lines[0] += " " + joined[0].upper() + joined[1:] + "."

        fam = profile.get("family", {})
        family_bits = []
        if fam.get("parents"):
            family_bits.append(f"child of {_join(fam['parents'])}")
        if fam.get("spouses"):
            family_bits.append(f"married to {_join(fam['spouses'])}")
        if fam.get("siblings"):
            family_bits.append(f"sibling of {_join(fam['siblings'][:4])}")
        if fam.get("half_siblings"):
            half = fam["half_siblings"]
            family_bits.append(f"half-sibling of {_join(half[:3])}" + (f" and {len(half) - 3} more" if len(half) > 3 else ""))
        if fam.get("children"):
            kids = fam["children"]
            family_bits.append(f"parent of {_join(kids[:4])}" + (f" and {len(kids) - 4} more" if len(kids) > 4 else ""))
        if family_bits:
            lines.append("**Family:** " + "; ".join(family_bits) + ".")

        if profile.get("themes"):
            lines.append("**Recurring themes:** " + ", ".join(f"{t['theme']} ({t['count']})" for t in profile["themes"][:4]) + ".")
        myths = [m["title"] for m in profile.get("myths", [])]
        if myths:
            extra = f", and {len(myths) - 5} more" if len(myths) > 5 else ""
            lines.append(f"**Appears in {len(myths)} myth{'s' if len(myths) != 1 else ''}:** {', '.join(myths[:5])}{extra}.")
        if profile.get("companions"):
            lines.append("**Often alongside:** " + _join([c["name"] for c in profile["companions"][:5]]) + ".")
        return "\n\n".join(lines)

    def _format_myth_summary_response(self, context: dict[str, Any]) -> str:
        title = context.get("myth_name", context.get("title", "Myth"))
        summary = context.get("summary", context.get("text", ""))
        moral = context.get("moral", "")

        lines = [f"### {title}"]
        if summary:
            lines.append(summary)
        if moral:
            lines.append(f"*Moral / Insight: {moral}*")
        return "\n\n".join(lines)

    # --------------------------------------------------------- relationships
    def _format_family_response(self, context: dict[str, Any]) -> str:
        name, rel, members = context.get("character"), context.get("relation"), context.get("members")
        if not name:
            return "Whose family? Try *Who are Zeus's children?* or *Who is the mother of Perseus?*"
        half = context.get("half_members") or []
        if members is None:
            return f"I have no family records for **{name}**."
        label = {"wives": "wife", "children": "children"}.get(rel, rel)
        if not members and not half:
            return f"No {label} of **{name}** is recorded."
        plural = len(members) > 1 and not label.endswith("children")
        word = label + ("s" if plural and not label.endswith("s") else "")
        if label == "child":
            word = "children" if len(members) > 1 else "child"
        parts = []
        if members:
            parts.append(f"**{name}'s {word}:** {_join(members)}.")
        if half:
            parts.append(f"**Half-{label.rstrip('s')}s:** {_join(half)}." if members else f"**{name}'s half-{label.rstrip('s')}s:** {_join(half)}.")
        return "\n\n".join(parts)

    def _format_relationship_response(self, context: dict[str, Any]) -> str:
        char1 = context.get("character_1")
        char2 = context.get("character_2")
        if not (char1 and char2):
            return "Tell me two characters, for example *How are Zeus and Hera related?*"
        rel = context.get("relationship", "")
        return f"**{char1} and {char2}**\n\n{rel}"

    def _format_comparison_response(self, context: dict[str, Any]) -> str:
        data = context.get("comparison_data")
        c1, c2 = context.get("character_1"), context.get("character_2")
        if not data:
            if not (c1 and c2):
                return "Name two characters to compare, for example *Compare Athena and Ares*."
            return f"I do not have enough on **{c1}** and **{c2}** to compare them."

        a, b = data["a"], data["b"]
        lines = [f"### {a['name']} vs {b['name']}"]
        if data.get("relationship"):
            lines.append(data["relationship"])
        for p in (a, b):
            themes = ", ".join(t["theme"] for t in p["themes"][:3]) or "no recorded themes"
            lines.append(f"- **{p['name']}** ({p['type']}): {len(p['myths'])} myths; themes: {themes}.")
        if data["shared_myths"]:
            lines.append("**Together in:** " + _join(data["shared_myths"][:4]) + ".")
        else:
            lines.append("They share no myth in this corpus.")
        if data["shared_themes"]:
            lines.append("**Both explore:** " + _join(data["shared_themes"]) + ".")
        if data["only_a_themes"]:
            lines.append(f"**Only {a['name']}:** " + _join(data["only_a_themes"][:3]) + ".")
        if data["only_b_themes"]:
            lines.append(f"**Only {b['name']}:** " + _join(data["only_b_themes"][:3]) + ".")
        return "\n\n".join(lines)

    # ---------------------------------------------------------------- themes
    def _format_theme_response(self, context: dict[str, Any]) -> str:
        theme = context.get("theme", "mythology")
        myths = context.get("theme_myths") or []
        if not myths:
            return f"I found no myths tagged **{theme}**. Try hubris, love, betrayal, revenge, wisdom, jealousy, transformation, quest or loss."
        lines = [f"### Myths of {theme}"]
        for i, m in enumerate(myths[:5], 1):
            lines.append(f"{i}. **{m.get('title', 'Untitled')}**: {_first_sentences(m.get('text', ''), 150)}")
        return "\n\n".join(lines)

    def _format_motif_response(self, context: dict[str, Any]) -> str:
        motif = context.get("motif") or {}
        rows = context.get("motif_rows") or []
        if not rows:
            return "I could not find myths with that pattern."
        lines = [f"### Pattern: {motif.get('label', 'Motif')}", motif.get("description", "")]
        for i, r in enumerate(rows, 1):
            snippet = f"\n   > {r['snippet']}" if r.get("snippet") else ""
            lines.append(f"{i}. **{r['title']}**{snippet}")
        return "\n\n".join(x for x in lines if x)

    def _format_search_response(self, context: dict[str, Any]) -> str:
        hits = context.get("search_hits") or []
        lines = ["I am not sure what you are asking, but these myths match your words best:"]
        for i, m in enumerate(hits, 1):
            lines.append(f"{i}. **{m.get('title', 'Untitled')}**: {_first_sentences(m.get('text', ''), 140)}")
        return "\n\n".join(lines)

    def _format_similar_myths_response(self, context: dict[str, Any]) -> str:
        myth_name = context.get("myth_name", "the requested myth")
        similar = context.get("similar_myths", [])
        if not similar:
            return f"I could not locate myths closely matching '{myth_name}'."
        lines = [
            f"### Myths Similar to '{myth_name}'",
            "These share the most vocabulary, characters and plot with it:",
        ]
        for i, m in enumerate(similar, 1):
            title = m.get("title", f"Myth {i}")
            theme = m.get("theme", "mythology")
            lines.append(f"{i}. **{title}** *[{theme.capitalize()}]*\n   {_first_sentences(m.get('text', ''), 140)}")
        return "\n\n".join(lines)

    # ---------------------------------------------------------------- shared
    def format_myth_narration(self, myth: dict[str, Any]) -> str:
        """Format a full myth narration."""
        title = myth.get("title", "Myth Retelling")
        theme = myth.get("theme", "myth")
        text = myth.get("text", "")
        out = f"## {title} [{theme.upper()}]\n\n{text}"
        if myth.get("moral") and myth.get("moral_source") != "theme_template":
            out += f"\n\n*Moral:* {myth['moral']}"
        return out

    def format_story_card(self, myth: dict[str, Any]) -> dict[str, Any]:
        """Generate structured story card data."""
        rels = myth.get("relationships", [])
        rel_snippets = []
        for r in rels[:3]:
            src = r.get("source", "?")
            tgt = r.get("target", "?")
            rel = r.get("relation", "related to").replace("_", " ")
            rel_snippets.append(f"{src} ({rel}) {tgt}")
        rel_text = "; ".join(rel_snippets) if rel_snippets else "No primary relationships cataloged"

        # Hand-written morals are shown as-is; generated ones are only a theme gloss,
        # so for those the summary is the opening of the story itself.
        authored = myth.get("moral") and myth.get("moral_source") != "theme_template"
        summary = myth["moral"] if authored else _first_sentences(myth.get("text", ""), 200)

        return {
            "id": myth.get("id"),
            "title": myth.get("title", "Untitled"),
            "theme": myth.get("theme", "Unknown"),
            "themes": myth.get("themes", [myth.get("theme", "Unknown")]),
            "summary": summary,
            "source": myth.get("source", ""),
            "characters": [c.get("name") if isinstance(c, dict) else str(c) for c in myth.get("characters", [])],
            "relationships": rels,
            "relationship_snippet": rel_text,
        }

    def format_greeting(self) -> str:
        return (
            "Greetings, seeker of ancient lore! I am the Chronicle Mythology Guide. "
            "Ask me to narrate a myth, compare gods, trace genealogies, or explore themes."
        )

    def format_help(self) -> str:
        return (
            "You can ask me questions like:\n"
            "- 'Tell me about Zeus'\n"
            "- 'Summarize the myth of Prometheus'\n"
            "- 'What is the relationship between Zeus and Hera?'\n"
            "- 'Compare Athena and Ares'\n"
            "- 'Find myths about hubris or jealousy'\n"
            "- 'Which myths have someone turned into a tree?'"
        )

    def format_unknown(self) -> str:
        return (
            "I could not quite understand that inquiry. You can ask me to summarize "
            "a myth (e.g. *The Fall of Icarus*), explain character backgrounds, or explore relationships!"
        )
