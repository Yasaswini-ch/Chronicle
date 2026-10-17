"""Relationship extraction for Greek mythology texts.

Extracts typed relationships between mythology entities from both structured
annotations (the ``relationships`` field in myth data) and from raw text using
co-occurrence heuristics and spaCy dependency parsing.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Any

import spacy
from spacy.tokens import Doc

logger = logging.getLogger(__name__)

# Canonical relation types used across the Chronicle system.
RELATION_TYPES: list[str] = [
    "parent_of",
    "child_of",
    "lover_of",
    "enemy_of",
    "sibling_of",
    "mentor_of",
    "killed_by",
    "married_to",
]

# Inverse relation mapping for bidirectional inference.
_INVERSE_RELATIONS: dict[str, str] = {
    "parent_of": "child_of",
    "child_of": "parent_of",
    "lover_of": "lover_of",
    "enemy_of": "enemy_of",
    "sibling_of": "sibling_of",
    "mentor_of": "student_of",
    "killed_by": "killed",
    "married_to": "married_to",
}

# Lexical patterns that suggest a specific relationship type.
# Each entry maps a relation type to a list of (pattern, direction) tuples
# where direction is 'forward' (subject -> object) or 'backward' (object -> subject).
_RELATION_PATTERNS: dict[str, list[tuple[re.Pattern[str], str]]] = {
    "parent_of": [
        (re.compile(r"\bfather\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bmother\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bson\s+of\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bdaughter\s+of\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bchild\s+of\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bborn\s+(?:to|of)\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bsired\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bbore\b", re.IGNORECASE), "forward"),
    ],
    "sibling_of": [
        (re.compile(r"\bbrother\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bsister\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\btwin\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bsiblings?\b", re.IGNORECASE), "forward"),
    ],
    "married_to": [
        (re.compile(r"\bmarried\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bwife\s+of\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bhusband\s+of\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bwedded\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bconsort\s+of\b", re.IGNORECASE), "backward"),
    ],
    "lover_of": [
        (re.compile(r"\blover\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bbeloved\s+of\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bseduced\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bloved\b", re.IGNORECASE), "forward"),
    ],
    "killed_by": [
        (re.compile(r"\bkilled\s+by\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bslew\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bslain\s+by\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bmurdered\s+by\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bkilled\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bdefeated\b", re.IGNORECASE), "backward"),
    ],
    "enemy_of": [
        (re.compile(r"\benemy\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bfought\s+against\b", re.IGNORECASE), "forward"),
        (re.compile(r"\brivaled\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bopposed\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bbattled\b", re.IGNORECASE), "forward"),
    ],
    "mentor_of": [
        (re.compile(r"\bmentored\b", re.IGNORECASE), "forward"),
        (re.compile(r"\btaught\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bguided\b", re.IGNORECASE), "forward"),
        (re.compile(r"\btrained\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bmentor\s+of\b", re.IGNORECASE), "forward"),
        (re.compile(r"\bstudent\s+of\b", re.IGNORECASE), "backward"),
        (re.compile(r"\bpupil\s+of\b", re.IGNORECASE), "backward"),
    ],
}


class RelationExtractor:
    """Extract typed relationships between mythology entities.

    Supports two extraction modes:

    1. **Annotation-based** — reads the structured ``relationships`` field
       present in the Chronicle myth dataset.
    2. **Text-based** — uses co-occurrence within sentences plus
       lexical/dependency patterns to *infer* likely relationships.

    Parameters
    ----------
    spacy_model : str
        spaCy model name for dependency parsing (used in text-based
        extraction).  Defaults to ``"en_core_web_sm"``.

    Example::

        extractor = RelationExtractor()
        myths = json.load(open("data/processed/myths.json"))
        relations = extractor.extract_from_annotations(myths)
    """

    def __init__(self, spacy_model: str = "en_core_web_sm") -> None:
        self._relations: list[dict[str, str]] = []
        self._spacy_model_name = spacy_model
        self._nlp: spacy.language.Language | None = None

    # ------------------------------------------------------------------
    # Lazy spaCy model loading
    # ------------------------------------------------------------------

    def _get_nlp(self) -> spacy.language.Language:
        """Lazily load the spaCy model for dependency parsing."""
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self._spacy_model_name)
            except OSError:
                logger.warning(
                    "spaCy model '%s' not found — falling back to blank English model. "
                    "Dependency-based extraction quality will be reduced.",
                    self._spacy_model_name,
                )
                self._nlp = spacy.blank("en")
                if "sentencizer" not in self._nlp.pipe_names:
                    self._nlp.add_pipe("sentencizer")
        return self._nlp

    # ------------------------------------------------------------------
    # Annotation-based extraction
    # ------------------------------------------------------------------

    def extract_from_annotations(
        self,
        myths: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        """Extract relationships from the structured ``relationships`` field.

        Each myth document may contain a ``relationships`` list with entries
        of the form::

            {"source": "Zeus", "target": "Athena", "relation": "parent_of"}

        Parameters
        ----------
        myths :
            List of myth documents (dicts) from the Chronicle dataset.

        Returns
        -------
        list[dict]
            Extracted relations, each having keys ``source``, ``target``,
            ``relation``, and ``myth_id``.
        """
        extracted: list[dict[str, str]] = []

        for myth in myths:
            myth_id = myth.get("id", myth.get("title", myth.get("myth", "unknown")))
            relationships = myth.get("relationships") or myth.get("relations") or []

            for rel in relationships:
                source = rel.get("source") or rel.get("subject", "")
                target = rel.get("target") or rel.get("object", "")
                relation = rel.get("relation") or rel.get("predicate") or rel.get("type", "")

                if not source or not target or not relation:
                    logger.debug(
                        "Skipping incomplete relationship in myth '%s': %s",
                        myth_id,
                        rel,
                    )
                    continue

                # Normalise relation type
                relation = relation.lower().replace(" ", "_")

                entry = {
                    "source": source,
                    "target": target,
                    "relation": relation,
                    "subject": source,
                    "object": target,
                    "predicate": relation,
                    "myth_id": str(myth_id),
                }
                extracted.append(entry)
                self._relations.append(entry)

        logger.info(
            "Extracted %d relations from %d myth annotations",
            len(extracted),
            len(myths),
        )
        return extracted

    # ------------------------------------------------------------------
    # Text-based extraction
    # ------------------------------------------------------------------

    def extract_from_text(
        self,
        text: str,
        entities: list[dict[str, Any]] | None = None,
        myth_id: str = "unknown",
        window_size: int = 1,
    ) -> list[dict[str, str]]:
        """Infer relationships between entities using co-occurrence and patterns.

        Operates in two phases:

        1. **Lexical pattern matching** — searches for relationship-indicating
           phrases between entity pairs that co-occur in the same sentence.
        2. **Co-occurrence fallback** — entity pairs in the same sentence that
           are not captured by patterns are recorded with an ``"associated_with"``
           relation type (lower confidence).

        Parameters
        ----------
        text :
            The full text to analyse.
        entities :
            Pre-extracted entities (as returned by
            :class:`~chronicle.ner.entity_recognizer.MythEntityRecognizer`).
        myth_id :
            Identifier for provenance tracking.
        window_size :
            Sentence window for co-occurrence (1 = same sentence,
            2 = adjacent sentences, etc.).

        Returns
        -------
        list[dict]
            Inferred relations with ``source``, ``target``, ``relation``,
            and ``myth_id``.
        """
        if not text:
            return []

        if entities is None:
            from chronicle.ner.entity_recognizer import MythEntityRecognizer
            rec = MythEntityRecognizer()
            entities = rec.predict(text)

        if not entities:
            return []

        nlp = self._get_nlp()
        doc = nlp(text)

        # Build a mapping from sentence index to entities in that sentence
        sentences = list(doc.sents)
        sent_entity_map: dict[int, list[dict[str, Any]]] = defaultdict(list)

        for ent in entities:
            for sent_idx, sent in enumerate(sentences):
                if ent["start"] >= sent.start_char and ent["end"] <= sent.end_char:
                    sent_entity_map[sent_idx].append(ent)
                    break

        extracted: list[dict[str, str]] = []
        seen_pairs: set[tuple[str, str, str]] = set()

        # For each sentence window, look at entity pairs
        for sent_idx in range(len(sentences)):
            # Gather entities in the sentence window
            window_entities: list[dict[str, Any]] = []
            for offset in range(window_size):
                idx = sent_idx + offset
                if idx in sent_entity_map:
                    window_entities.extend(sent_entity_map[idx])

            if len(window_entities) < 2:
                continue

            # Get the text span for this window
            window_start_idx = sent_idx
            window_end_idx = min(sent_idx + window_size, len(sentences))
            window_text = text[
                sentences[window_start_idx].start_char:
                sentences[window_end_idx - 1].end_char
            ]

            # Check all entity pairs
            for i, ent_a in enumerate(window_entities):
                for ent_b in window_entities[i + 1:]:
                    if ent_a["text"] == ent_b["text"]:
                        continue

                    # Try pattern-based extraction
                    relation = self._match_pattern(
                        window_text, ent_a, ent_b
                    )

                    if relation is None:
                        # Co-occurrence fallback
                        relation = ("associated_with", ent_a["text"], ent_b["text"])

                    rel_type, source, target = relation
                    pair_key = (source, target, rel_type)
                    reverse_key = (target, source, rel_type)

                    if pair_key in seen_pairs or reverse_key in seen_pairs:
                        continue

                    entry = {
                        "source": source,
                        "target": target,
                        "relation": rel_type,
                        "subject": source,
                        "object": target,
                        "predicate": rel_type,
                        "myth_id": myth_id,
                    }
                    extracted.append(entry)
                    self._relations.append(entry)
                    seen_pairs.add(pair_key)

        logger.info(
            "Extracted %d relations from text (myth_id=%s)",
            len(extracted),
            myth_id,
        )
        return extracted

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def get_all_relations(self) -> list[dict[str, str]]:
        """Return all accumulated relations.

        Returns
        -------
        list[dict]
            Every relation extracted so far, with keys ``source``,
            ``target``, ``relation``, and ``myth_id``.
        """
        return list(self._relations)

    def get_character_relations(self, character: str) -> list[dict[str, str]]:
        """Return all relations involving *character* (as source or target).

        Parameters
        ----------
        character :
            Character name to look up (case-insensitive).

        Returns
        -------
        list[dict]
            Filtered list of relations.
        """
        char_lower = character.lower()
        return [
            rel
            for rel in self._relations
            if rel["source"].lower() == char_lower
            or rel["target"].lower() == char_lower
        ]

    def get_relations_by_type(self, relation_type: str) -> list[dict[str, str]]:
        """Return all relations of a given type.

        Parameters
        ----------
        relation_type :
            One of :data:`RELATION_TYPES` or any custom type.

        Returns
        -------
        list[dict]
            Filtered list of relations.
        """
        return [
            rel for rel in self._relations if rel["relation"] == relation_type
        ]

    def get_relation_summary(self) -> dict[str, int]:
        """Summarise the number of relations by type.

        Returns
        -------
        dict[str, int]
            Mapping from relation type to count.
        """
        counts: dict[str, int] = defaultdict(int)
        for rel in self._relations:
            counts[rel["relation"]] += 1
        return dict(counts)

    def clear(self) -> None:
        """Clear all accumulated relations."""
        self._relations.clear()

    # ------------------------------------------------------------------
    # Pattern matching helpers
    # ------------------------------------------------------------------

    def _match_pattern(
        self,
        text: str,
        ent_a: dict[str, Any],
        ent_b: dict[str, Any],
    ) -> tuple[str, str, str] | None:
        """Try to match a lexical pattern between two entities.

        Examines the text *between* (and slightly around) the two entities
        for relationship-indicating phrases.

        Returns
        -------
        tuple[str, str, str] | None
            ``(relation_type, source, target)`` if a pattern matches, else
            ``None``.
        """
        # Determine entity order in the text
        if ent_a["start"] <= ent_b["start"]:
            first, second = ent_a, ent_b
        else:
            first, second = ent_b, ent_a

        # Get the text between (and slightly before/after) the two entities
        between_start = max(0, first["start"] - 20)
        between_end = min(len(text), second["end"] + 20)
        context = text[between_start:between_end]

        for rel_type, patterns in _RELATION_PATTERNS.items():
            for pattern, direction in patterns:
                if pattern.search(context):
                    if direction == "forward":
                        return (rel_type, first["text"], second["text"])
                    else:
                        return (rel_type, second["text"], first["text"])

        return None

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"RelationExtractor(relations={len(self._relations)}, "
            f"model={self._spacy_model_name!r})"
        )

    def __len__(self) -> int:
        return len(self._relations)
