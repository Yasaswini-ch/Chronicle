"""Tests for the Chronicle chatbot module.

Covers:
- IntentDetector: intent classification for mythology queries.
- SlotFiller: slot/entity extraction from user queries.
- ResponseGenerator: response formatting and template rendering.
"""

from __future__ import annotations

from typing import Any

import pytest


# ---------------------------------------------------------------------------
# IntentDetector tests
# ---------------------------------------------------------------------------

class TestIntentDetector:
    """Tests for :class:`IntentDetector`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.chatbot.intent import IntentDetector
            self.DetectorClass = IntentDetector
        except ImportError:
            pytest.skip("IntentDetector not yet implemented")

    @pytest.fixture()
    def detector(self):
        return self.DetectorClass()

    # -- Core intent types --------------------------------------------------

    @pytest.mark.parametrize(
        "query, expected_intent",
        [
            # character_info intent
            ("Tell me about Zeus", "character_info"),
            ("Who is Athena?", "character_info"),
            ("What do you know about Heracles?", "character_info"),
            # myth_summary intent
            ("Summarize the myth of Prometheus", "myth_summary"),
            ("What is the story of Pandora's Box?", "myth_summary"),
            ("Tell me the tale of Persephone", "myth_summary"),
            # relationship intent
            ("What is the relationship between Zeus and Hera?", "relationship"),
            ("How are Heracles and Zeus related?", "relationship"),
            ("Who is the father of Athena?", "family"),
            # theme intent
            ("What are the themes in Greek creation myths?", "theme"),
            ("What lessons does the myth of Icarus teach?", "theme"),
            # comparison intent
            ("Compare Zeus and Poseidon", "comparison"),
            ("What are the differences between Athena and Ares?", "comparison"),
        ],
        ids=[
            "char-zeus",
            "char-athena",
            "char-heracles",
            "summary-prometheus",
            "summary-pandora",
            "summary-persephone",
            "rel-zeus-hera",
            "rel-heracles-zeus",
            "rel-father-athena",
            "theme-creation",
            "theme-icarus",
            "compare-zeus-poseidon",
            "compare-athena-ares",
        ],
    )
    def test_detect_intent(
        self,
        detector,
        query: str,
        expected_intent: str,
    ) -> None:
        result = detector.detect(query)
        assert isinstance(result, (str, dict))
        intent = result if isinstance(result, str) else result.get("intent")
        assert intent == expected_intent

    def test_detect_returns_confidence(self, detector) -> None:
        result = detector.detect("Tell me about Zeus")
        if isinstance(result, dict):
            assert "confidence" in result
            assert 0.0 <= result["confidence"] <= 1.0

    def test_detect_unknown_intent(self, detector) -> None:
        result = detector.detect("What is the weather like today?")
        intent = result if isinstance(result, str) else result.get("intent")
        assert intent in ("unknown", "fallback", "out_of_scope")

    def test_detect_empty_query(self, detector) -> None:
        result = detector.detect("")
        intent = result if isinstance(result, str) else result.get("intent")
        assert intent in ("unknown", "fallback", "empty")


# ---------------------------------------------------------------------------
# SlotFiller tests
# ---------------------------------------------------------------------------

class TestSlotFiller:
    """Tests for :class:`SlotFiller`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.chatbot.slots import SlotFiller
            self.FillerClass = SlotFiller
        except ImportError:
            pytest.skip("SlotFiller not yet implemented")

    @pytest.fixture()
    def filler(self):
        return self.FillerClass()

    @pytest.mark.parametrize(
        "query, intent, expected_slots",
        [
            (
                "Tell me about Zeus",
                "character_info",
                {"character": "Zeus"},
            ),
            (
                "Summarize the myth of Prometheus stealing fire",
                "myth_summary",
                {"myth_name": "Prometheus"},
            ),
            (
                "What is the relationship between Zeus and Hera?",
                "relationship",
                {"character_1": "Zeus", "character_2": "Hera"},
            ),
            (
                "Compare Athena and Ares",
                "comparison",
                {"character_1": "Athena", "character_2": "Ares"},
            ),
        ],
        ids=[
            "character-info-slot",
            "myth-summary-slot",
            "relationship-slots",
            "comparison-slots",
        ],
    )
    def test_fill_slots(
        self,
        filler,
        query: str,
        intent: str,
        expected_slots: dict[str, str],
    ) -> None:
        slots = filler.fill(query, intent)
        assert isinstance(slots, dict)
        # Each expected slot should be present with the right value
        for key, value in expected_slots.items():
            assert key in slots, f"Missing slot '{key}' in {slots}"
            assert value.lower() in slots[key].lower()

    def test_fill_empty_query(self, filler) -> None:
        slots = filler.fill("", "character_info")
        assert isinstance(slots, dict)

    def test_fill_no_entities(self, filler) -> None:
        slots = filler.fill("Tell me something interesting", "unknown")
        assert isinstance(slots, dict)


# ---------------------------------------------------------------------------
# ResponseGenerator tests
# ---------------------------------------------------------------------------

class TestResponseGenerator:
    """Tests for :class:`ResponseGenerator`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.chatbot.response import ResponseGenerator
            self.GeneratorClass = ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator not yet implemented")

    @pytest.fixture()
    def generator(self):
        return self.GeneratorClass()

    def test_generate_character_response(self, generator) -> None:
        context = {
            "intent": "character_info",
            "character": "Zeus",
            "info": {
                "name": "Zeus",
                "domain": "Sky, Thunder, Lightning",
                "roman_name": "Jupiter",
                "myths": ["Titanomachy", "Prometheus"],
            },
        }
        response = generator.generate(context)
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Zeus" in response

    def test_generate_myth_summary_response(self, generator) -> None:
        context = {
            "intent": "myth_summary",
            "myth_name": "Prometheus Brings Fire",
            "summary": "Prometheus stole fire from the gods and gave it to humanity.",
        }
        response = generator.generate(context)
        assert isinstance(response, str)
        assert "Prometheus" in response

    def test_generate_relationship_response(self, generator) -> None:
        context = {
            "intent": "relationship",
            "character_1": "Zeus",
            "character_2": "Hera",
            "relationship": "married",
        }
        response = generator.generate(context)
        assert isinstance(response, str)
        assert "Zeus" in response
        assert "Hera" in response

    def test_generate_fallback_response(self, generator) -> None:
        context = {"intent": "unknown"}
        response = generator.generate(context)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_response_is_not_empty(self, generator) -> None:
        context = {
            "intent": "character_info",
            "character": "Athena",
            "info": {"name": "Athena"},
        }
        response = generator.generate(context)
        assert response.strip() != ""

    def test_generate_comparison_response(self, generator) -> None:
        context = {
            "intent": "comparison",
            "character_1": "Athena",
            "character_2": "Ares",
            "comparison": {
                "Athena": {"domain": "Wisdom, War Strategy"},
                "Ares": {"domain": "War, Bloodlust"},
            },
        }
        response = generator.generate(context)
        assert isinstance(response, str)
        assert "Athena" in response
        assert "Ares" in response

    def test_generate_similar_myths_response(self, generator) -> None:
        context = {
            "intent": "similar_myths",
            "myth_name": "The Fall of Icarus",
            "similar_myths": [
                {"title": "Phaethon's Ride", "theme": "hubris", "moral": "Know your limits."},
                {"title": "Athena and Arachne", "theme": "hubris", "moral": "Do not challenge the divine."},
            ],
        }
        response = generator.generate(context)
        assert isinstance(response, str)
        assert "Similar" in response
        assert "Phaethon's Ride" in response
        assert "Athena and Arachne" in response

    def test_format_story_card_output_10(self, generator) -> None:
        sample_myth = {
            "title": "The Fall of Icarus",
            "theme": "hubris",
            "text": "Daedalus crafted wings of wax and feathers...",
            "moral": "Do not let hubris cloud reason.",
            "characters": [{"name": "Icarus", "type": "mortal"}, {"name": "Daedalus", "type": "mortal"}],
            "relationships": [{"source": "Daedalus", "target": "Icarus", "relation": "parent_of"}],
        }
        card = generator.format_story_card(sample_myth)
        assert card["title"] == "The Fall of Icarus"
        assert card["theme"] == "hubris"
        assert "Icarus" in card["characters"]
        assert "Daedalus" in card["characters"]
        assert "relationship_snippet" in card
        assert "parent of" in card["relationship_snippet"]

    def test_insights_leaderboard_stats_output_9(self) -> None:
        from chronicle.insights.dashboard import InsightsDashboard
        dash = InsightsDashboard()
        sample_myths = [
            {
                "title": "Myth 1",
                "theme": "hubris",
                "characters": [{"name": "Zeus"}, {"name": "Icarus"}],
                "relationships": [{"source": "Zeus", "target": "Icarus", "relation": "punishes"}],
            },
            {
                "title": "Myth 2",
                "theme": "fate",
                "characters": [{"name": "Zeus"}, {"name": "Oedipus"}],
                "relationships": [{"source": "Zeus", "target": "Oedipus", "relation": "decrees"}],
            },
        ]
        stats = dash.get_leaderboard_stats(sample_myths)
        assert stats["most_mentioned"]["character"] == "Zeus"
        assert stats["most_mentioned"]["count"] == 2
        assert stats["most_connected"]["character"] == "Zeus"
        assert stats["most_thematic_diversity"]["character"] == "Zeus"
        assert stats["most_thematic_diversity"]["num_themes"] == 2
        assert len(stats["leaderboard"]) > 0
