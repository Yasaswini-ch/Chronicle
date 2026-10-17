"""Slot extraction for mythology chatbot queries.

Identifies character names, myth titles, themes, and entity pairs from queries.
"""

from __future__ import annotations

import re
from typing import Any

_KNOWN_CHARACTERS = [
    "Zeus", "Hera", "Poseidon", "Hades", "Athena", "Apollo", "Artemis",
    "Aphrodite", "Ares", "Hephaestus", "Hermes", "Dionysus", "Demeter",
    "Persephone", "Heracles", "Hercules", "Prometheus", "Pandora", "Theseus",
    "Perseus", "Jason", "Medea", "Achilles", "Hector", "Odysseus", "Icarus",
    "Daedalus", "Arachne", "Niobe", "Bellerophon", "Phaethon", "Orpheus",
    "Eurydice", "Pygmalion", "Cupid", "Psyche", "Echo", "Narcissus",
    "Ceyx", "Alcyone", "Ariadne", "Clytemnestra", "Agamemnon", "Paris",
    "Cronus", "Kronos", "Uranus", "Gaia", "Rhea", "Atlas", "Minos",
    "Polyphemus", "Medusa", "Minotaur", "Nemean Lion", "Cerberus"
]


# Words users type for each corpus theme (canonical theme -> surface forms).
THEME_ALIASES: dict[str, tuple[str, ...]] = {
    "hubris": ("hubris", "pride", "arrogance", "overconfidence"),
    "love": ("love", "romance", "devotion"),
    "betrayal": ("betrayal", "treachery", "deceit"),
    "revenge": ("revenge", "vengeance", "retribution"),
    "wisdom": ("wisdom", "cunning", "prudence"),
    "jealousy": ("jealousy", "envy", "rivalry"),
    "transformation": ("transformation", "transformations", "metamorphosis", "metamorphoses", "shapeshifting"),
    "quest": ("quest", "quests", "journey", "journeys", "adventure", "adventures", "voyage"),
    "loss": ("loss", "grief", "mourning", "death", "sorrow"),
}

_THEME_LOOKUP = {w: t for t, words in THEME_ALIASES.items() for w in words}
THEME_WORD_RE = re.compile(
    r"\b(" + "|".join(sorted(_THEME_LOOKUP, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


_KIN_RE = re.compile(
    r"\b(fathers?|mothers?|parents?|sons?|daughters?|children|wives|wife|husbands?|spouses?"
    r"|brothers?|sisters?|siblings?)\b",
    re.IGNORECASE,
)


def find_theme(text: str) -> str | None:
    """Return the canonical corpus theme mentioned in *text*, if any."""
    m = THEME_WORD_RE.search(text or "")
    return _THEME_LOOKUP[m.group(1).lower()] if m else None


class SlotFiller:
    """Extracts slot entities from user queries based on classified intent."""

    def __init__(self, alias_resolver: Any | None = None, knowledge: Any | None = None) -> None:
        self.alias_resolver = alias_resolver
        self.knowledge = knowledge  # MythKnowledge: resolves Roman names and epithets

    def _extract_characters(self, text: str) -> list[str]:
        """Find known character names in query text in order of appearance."""
        if self.knowledge is not None:
            return self.knowledge.find_characters(text)
        found: list[tuple[int, str]] = []
        for name in _KNOWN_CHARACTERS:
            # Case-insensitive whole-word search
            pattern = rf"\b{re.escape(name)}\b"
            for match in re.finditer(pattern, text, re.IGNORECASE):
                found.append((match.start(), name))

        # Sort by appearance in query
        found.sort(key=lambda x: x[0])
        seen = set()
        ordered = []
        for _, name in found:
            norm = name.lower()
            if norm not in seen:
                seen.add(norm)
                ordered.append(name)
        return ordered

    def fill(self, query: str, intent: str) -> dict[str, str]:
        """Extract slots from *query* given *intent*.

        Parameters
        ----------
        query : str
            User query.
        intent : str
            Classified intent name.

        Returns
        -------
        dict[str, str]
            Dictionary of extracted slot names and values.
        """
        slots: dict[str, str] = {}
        if not query or not query.strip():
            return slots

        chars = self._extract_characters(query)

        if intent in ("relationship", "comparison"):
            if len(chars) >= 2:
                slots["character_1"] = chars[0]
                slots["character_2"] = chars[1]
            elif len(chars) == 1:
                slots["character_1"] = chars[0]
                slots["character"] = chars[0]

        elif intent == "character_info":
            if chars:
                slots["character"] = chars[0]

        elif intent == "family":
            if chars:
                slots["character"] = chars[0]
            m = _KIN_RE.search(query)
            if m:
                slots["relation"] = m.group(1).lower()
            elif re.search(r"\bmarry\b", query, re.IGNORECASE):
                slots["relation"] = "spouse"

        elif intent == "myth_summary":
            if chars:
                slots["myth_name"] = chars[0]
                slots["character"] = chars[0]
            else:
                # Try finding words following "myth of", "story of", "tale of"
                m = re.search(
                    r"(?:story|tale|myth)\s+of\s+([A-Za-z0-9'\s]+?)(?:\s+stealing|\s+and|\?|$|\.)",
                    query,
                    re.IGNORECASE,
                )
                if m:
                    slots["myth_name"] = m.group(1).strip()

        elif intent == "similar_myths":
            if chars:
                slots["myth_name"] = chars[0]
                slots["character"] = chars[0]
            else:
                m = re.search(
                    r"(?:similar\s+to|like|stories\s+like|myths\s+like)\s+(?:the\s+story\s+of\s+|the\s+myth\s+of\s+)?([A-Za-z0-9'\s]+?)(?:\?|$|\.)",
                    query,
                    re.IGNORECASE,
                )
                if m:
                    slots["myth_name"] = m.group(1).strip()

        elif intent == "theme":
            theme = find_theme(query)
            if theme:
                slots["theme"] = theme
            elif chars:
                slots["character"] = chars[0]
                slots["myth_name"] = chars[0]

        return slots
