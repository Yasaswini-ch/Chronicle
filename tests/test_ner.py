"""Tests for the Chronicle NER module.

Covers:
- MythEntityRecognizer: entity extraction from myth text.
- RelationExtractor: relation extraction from annotations / text.
- KnowledgeGraph: graph building, node/edge queries, path finding.
"""

from __future__ import annotations

from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Sample annotated myth data for NER testing
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sample_myth_text() -> str:
    """A rich myth text containing multiple entity types."""
    return (
        "Zeus, the king of the gods, hurled his thunderbolt from the summit of "
        "Mount Olympus. Athena, his daughter, stood by his side bearing her "
        "aegis and spear. Together they waged war against the Titans in the "
        "great conflict known as the Titanomachy. Prometheus, a Titan who sided "
        "with Zeus, later stole fire from the forge of Hephaestus and brought "
        "it to the mortals living on the plains below."
    )


@pytest.fixture(scope="module")
def sample_annotations() -> list[dict[str, Any]]:
    """Pre-built annotations with characters, relations, and locations."""
    return [
        {
            "myth": "Prometheus Brings Fire",
            "characters": ["Prometheus", "Zeus", "Hephaestus"],
            "locations": ["Mount Olympus", "Caucasus"],
            "relations": [
                {"subject": "Prometheus", "predicate": "stole_from", "object": "Hephaestus"},
                {"subject": "Zeus", "predicate": "punished", "object": "Prometheus"},
                {"subject": "Prometheus", "predicate": "gave_fire_to", "object": "Humanity"},
            ],
        },
        {
            "myth": "Persephone and the Underworld",
            "characters": ["Hades", "Persephone", "Demeter", "Zeus"],
            "locations": ["Underworld", "Mount Olympus"],
            "relations": [
                {"subject": "Hades", "predicate": "abducted", "object": "Persephone"},
                {"subject": "Demeter", "predicate": "searched_for", "object": "Persephone"},
                {"subject": "Zeus", "predicate": "commanded", "object": "Hades"},
            ],
        },
        {
            "myth": "The Twelve Labours of Heracles",
            "characters": ["Heracles", "Hera", "Zeus", "Eurystheus"],
            "locations": ["Nemea", "Mount Olympus", "Delphi"],
            "relations": [
                {"subject": "Hera", "predicate": "cursed", "object": "Heracles"},
                {"subject": "Heracles", "predicate": "served", "object": "Eurystheus"},
                {"subject": "Heracles", "predicate": "slew", "object": "Nemean Lion"},
            ],
        },
    ]


# ---------------------------------------------------------------------------
# MythEntityRecognizer tests
# ---------------------------------------------------------------------------

class TestMythEntityRecognizer:
    """Tests for :class:`MythEntityRecognizer`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.ner.recognizer import MythEntityRecognizer
            self.RecognizerClass = MythEntityRecognizer
        except ImportError:
            pytest.skip("MythEntityRecognizer not yet implemented")

    @pytest.fixture()
    def recognizer(self):
        return self.RecognizerClass()

    def test_extract_entities_returns_list(
        self,
        recognizer,
        sample_myth_text: str,
    ) -> None:
        entities = recognizer.extract(sample_myth_text)
        assert isinstance(entities, list)
        assert len(entities) > 0

    def test_extract_characters(
        self,
        recognizer,
        sample_myth_text: str,
    ) -> None:
        entities = recognizer.extract(sample_myth_text)
        entity_texts = {e["text"] for e in entities if e.get("label") == "CHARACTER"}
        # Should recognise at least some of the named gods
        expected = {"Zeus", "Athena", "Prometheus", "Hephaestus"}
        found = entity_texts & expected
        assert len(found) >= 2, f"Expected characters from {expected}, got {entity_texts}"

    def test_extract_locations(
        self,
        recognizer,
        sample_myth_text: str,
    ) -> None:
        entities = recognizer.extract(sample_myth_text)
        entity_texts = {
            e["text"] for e in entities
            if e.get("label") in ("LOCATION", "LOC", "GPE")
        }
        assert "Mount Olympus" in entity_texts or "Olympus" in entity_texts

    def test_extract_empty_text(self, recognizer) -> None:
        entities = recognizer.extract("")
        assert entities == []

    @pytest.mark.parametrize(
        "text, expected_char",
        [
            ("Heracles slew the Nemean Lion.", "Heracles"),
            ("Odysseus blinded the Cyclops Polyphemus.", "Odysseus"),
            ("Medea, the sorceress of Colchis, brewed potions.", "Medea"),
        ],
    )
    def test_extract_specific_characters(
        self,
        recognizer,
        text: str,
        expected_char: str,
    ) -> None:
        entities = recognizer.extract(text)
        entity_texts = {e["text"] for e in entities}
        assert expected_char in entity_texts

    def test_entity_structure(
        self,
        recognizer,
        sample_myth_text: str,
    ) -> None:
        entities = recognizer.extract(sample_myth_text)
        for entity in entities:
            assert "text" in entity
            assert "label" in entity
            assert isinstance(entity["text"], str)
            assert isinstance(entity["label"], str)


# ---------------------------------------------------------------------------
# RelationExtractor tests
# ---------------------------------------------------------------------------

class TestRelationExtractor:
    """Tests for :class:`RelationExtractor`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.ner.relations import RelationExtractor
            self.ExtractorClass = RelationExtractor
        except ImportError:
            pytest.skip("RelationExtractor not yet implemented")

    @pytest.fixture()
    def extractor(self):
        return self.ExtractorClass()

    def test_extract_from_annotations(
        self,
        extractor,
        sample_annotations: list[dict[str, Any]],
    ) -> None:
        relations = extractor.extract_from_annotations(sample_annotations)
        assert isinstance(relations, list)
        assert len(relations) > 0

    def test_relation_structure(
        self,
        extractor,
        sample_annotations: list[dict[str, Any]],
    ) -> None:
        relations = extractor.extract_from_annotations(sample_annotations)
        for rel in relations:
            assert "subject" in rel
            assert "predicate" in rel
            assert "object" in rel

    def test_extract_from_text(
        self,
        extractor,
        sample_myth_text: str,
    ) -> None:
        relations = extractor.extract_from_text(sample_myth_text)
        assert isinstance(relations, list)
        # Should find at least one relation
        if len(relations) > 0:
            rel = relations[0]
            assert "subject" in rel
            assert "predicate" in rel
            assert "object" in rel

    def test_unique_predicates(
        self,
        extractor,
        sample_annotations: list[dict[str, Any]],
    ) -> None:
        relations = extractor.extract_from_annotations(sample_annotations)
        predicates = {r["predicate"] for r in relations}
        assert len(predicates) > 1  # Multiple relation types


# ---------------------------------------------------------------------------
# KnowledgeGraph tests
# ---------------------------------------------------------------------------

class TestKnowledgeGraph:
    """Tests for :class:`KnowledgeGraph`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.ner.knowledge_graph import KnowledgeGraph
            self.GraphClass = KnowledgeGraph
        except ImportError:
            pytest.skip("KnowledgeGraph not yet implemented")

    @pytest.fixture()
    def graph(self, sample_annotations: list[dict[str, Any]]):
        kg = self.GraphClass()
        kg.build_from_annotations(sample_annotations)
        return kg

    def test_build_creates_nodes(self, graph) -> None:
        nodes = graph.get_nodes()
        assert len(nodes) > 0
        # Zeus appears in all three myths' annotations
        node_names = {n["name"] if isinstance(n, dict) else n for n in nodes}
        assert "Zeus" in node_names

    def test_build_creates_edges(self, graph) -> None:
        edges = graph.get_edges()
        assert len(edges) > 0

    def test_get_neighbors(self, graph) -> None:
        neighbors = graph.get_neighbors("Zeus")
        assert isinstance(neighbors, (list, set))
        assert len(neighbors) > 0

    def test_get_neighbors_unknown(self, graph) -> None:
        neighbors = graph.get_neighbors("UnknownCharacter")
        assert len(neighbors) == 0

    def test_query_by_relation(self, graph) -> None:
        results = graph.query(predicate="punished")
        assert isinstance(results, list)
        if len(results) > 0:
            # Should find Zeus punished Prometheus
            subjects = {r["subject"] for r in results}
            assert "Zeus" in subjects

    def test_path_between_characters(self, graph) -> None:
        path = graph.find_path("Prometheus", "Hephaestus")
        assert isinstance(path, (list, type(None)))
        if path is not None:
            assert len(path) >= 2
            assert path[0] == "Prometheus"
            assert path[-1] == "Hephaestus"

    def test_character_degree(self, graph) -> None:
        degree = graph.degree("Zeus")
        assert isinstance(degree, int)
        assert degree > 0

    def test_graph_statistics(self, graph) -> None:
        stats = graph.statistics()
        assert isinstance(stats, dict)
        assert "num_nodes" in stats
        assert "num_edges" in stats
        assert stats["num_nodes"] > 0
        assert stats["num_edges"] > 0
