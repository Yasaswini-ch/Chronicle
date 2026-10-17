"""Intent detector for mythology chatbot queries.

Identifies user intent using keyword patterns, phrase matching, and rule-based
intent routing with confidence estimation.
"""

from __future__ import annotations

import re
from typing import Any

from chronicle.chatbot.slots import find_theme

_KIN = (
    r"(?:fathers?|mothers?|parents?|sons?|daughters?|children|wife|wives|husbands?|spouses?"
    r"|brothers?|sisters?|siblings?)"
)


class IntentDetector:
    """Classifies user queries into distinct mythology conversational intents."""

    def __init__(self, knowledge: Any | None = None) -> None:
        self.knowledge = knowledge  # MythKnowledge: motif phrases and full character list

    # Intent regex patterns ordered by specificity
    _INTENT_PATTERNS = [
        (
            "follow_up",
            [
                r"\bexplain\s+(?:it|that|this|more)\b",
                r"\btell\s+me\s+more\b",
                r"\bmore\s+(?:details?|info(?:rmation)?)\b",
                r"^\s*more\s*\??\s*$",
                r"\bgo\s+on\b",
                r"^\s*continue\s*$",
                r"\belaborate\b",
                r"\bwhat\s+(?:else|happens?\s+next)\b",
                r"\bkeep\s+(?:going|reading|telling)\b",
                r"\bcan\s+you\s+expand\b",
            ],
        ),
        (
            "comparison",
            [
                r"\bcompare\b",
                r"\bdifferences?\s+between\b",
                r"\bhow\s+do\s+\w+\s+and\s+\w+\s+differ\b",
                r"\bversus\b|\bvs\.?\b",
            ],
        ),
        (
            "family",
            [
                rf"\b(?:who|what)\s+(?:is|was|are|were)\s+(?:the\s+)?{_KIN}\s+(?:of|to)\b",
                rf"\b(?:who|what)\s+(?:is|was|are|were)\s+[A-Za-z' -]+?'s\s+{_KIN}\b",
                r"\b(?:who|whom)\s+(?:did|does)\s+\w+\s+marry\b",
            ],
        ),
        (
            "relationship",
            [
                r"\brelationship\s+between\b",
                r"\bhow\s+are\s+.*\s+related\b",
                r"\bis\s+.*\s+related\s+to\b",
            ],
        ),
        (
            "similar_myths",
            [
                r"\bsimilar\s+(?:to|myths?|stories)\b",
                r"\bmyths?\s+similar\s+to\b",
                r"\bstories\s+similar\s+to\b",
                r"\bfind\s+(?:myths?|stories)\s+like\b",
                r"\bmyths?\s+like\b",
                r"\bstories\s+like\b",
                r"\blike\s+the\s+(?:story|myth|tale)\s+of\b",
                r"\bmore\s+like\b",
            ],
        ),
        (
            "theme",
            [
                r"\bthemes?\b",
                r"\blessons?\b",
                r"\bmorals?\b",
                r"\bwhat\s+does\s+.*\s+teach\b",
                r"\bmyths?\s+(?:that\s+are\s+|which\s+are\s+)?(?:about|involving|featuring|dealing\s+with)\b",
                r"\bstories\s+(?:that\s+are\s+)?(?:about|involving|featuring)\b",
            ],
        ),
        (
            "myth_summary",
            [
                r"\bsummarize\b",
                r"\bsummary\s+of\b",
                r"\btell\s+me\s+the\s+(?:story|tale|myth)\s+of\b",
                r"\bwhat\s+is\s+the\s+story\s+of\b",
                r"\bstory\s+of\b",
                r"\btale\s+of\b",
                r"\bmyth\s+of\b",
            ],
        ),
        (
            "character_info",
            [
                r"\btell\s+me\s+about\b",
                r"\bwho\s+is\b",
                r"\bwho\s+was\b",
                r"\bwhat\s+do\s+you\s+know\s+about\b",
                r"\binfo(?:rmation)?\s+(?:about|on)\b",
            ],
        ),
    ]

    def detect(self, query: str) -> dict[str, Any]:
        """Detect the intent and confidence for a user query.

        Parameters
        ----------
        query : str
            Raw text query from user.

        Returns
        -------
        dict[str, Any]
            Dict with 'intent', 'confidence', and 'slots'.
        """
        if not query or not query.strip():
            return {"intent": "unknown", "confidence": 0.0, "slots": {}}

        clean_query = query.strip()
        lower_query = clean_query.lower()

        # A question about a recurring story pattern ("myths where someone is turned into a tree")
        if self.knowledge is not None and re.search(r"\b(myths?|stories|tales?|legends?)\b", lower_query):
            if self.knowledge.match_motif(lower_query):
                return {"intent": "motif", "confidence": 0.85, "slots": {}}

        # Check matched intent patterns
        for intent, patterns in self._INTENT_PATTERNS:
            for pattern in patterns:
                if re.search(pattern, lower_query):
                    return {
                        "intent": intent,
                        "confidence": 0.95,
                        "slots": {},
                    }

        # A bare theme word ("hubris", "stories of revenge") is a theme query
        if find_theme(lower_query):
            return {"intent": "theme", "confidence": 0.75, "slots": {}}

        # Check if query directly mentions a known character or myth
        if self.knowledge is not None and self.knowledge.find_characters(clean_query):
            return {"intent": "character_info", "confidence": 0.70, "slots": {}}

        known_keywords = [
            "zeus", "hera", "poseidon", "hades", "athena", "apollo",
            "artemis", "aphrodite", "ares", "hephaestus", "hermes",
            "dionysus", "demeter", "prometheus", "pandora", "persephone",
            "heracles", "hercules", "odysseus", "achilles", "theseus",
            "perseus", "jason", "medea", "icarus", "daedalus", "arachne"
        ]
        if any(re.search(rf"\b{kw}\b", lower_query) for kw in known_keywords):
            return {
                "intent": "character_info",
                "confidence": 0.70,
                "slots": {},
            }

        return {"intent": "unknown", "confidence": 0.0, "slots": {}}
