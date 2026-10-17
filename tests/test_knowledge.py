"""Tests for the knowledge layer: kinship, BM25, profiles, motifs, quiz, and corpus integrity."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from chronicle.chatbot.engine import ChatEngine
from chronicle.insights.knowledge import MOTIFS, MythKnowledge
from chronicle.ner.kinship import FamilyTree
from chronicle.text.bm25 import BM25, tokenize

ROOT = Path(__file__).resolve().parent.parent
MYTHS = json.loads((ROOT / "data" / "processed" / "myths.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tree() -> FamilyTree:
    return FamilyTree.from_file(ROOT / "data" / "annotations" / "genealogy.json")


@pytest.fixture(scope="module")
def knowledge() -> MythKnowledge:
    return MythKnowledge(MYTHS)


@pytest.fixture(scope="module")
def engine(knowledge) -> ChatEngine:
    return ChatEngine(myths=MYTHS, knowledge=knowledge)


# ---------------------------------------------------------------- kinship
@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("Hera", "Zeus", "Hera is Zeus's wife and sister."),
        ("Zeus", "Athena", "Zeus is Athena's father."),
        ("Athena", "Zeus", "Athena is Zeus's daughter."),
        ("Apollo", "Artemis", "Apollo is Artemis's brother."),
        ("Apollo", "Athena", "Apollo is Athena's half-brother."),
        ("Athena", "Hades", "Athena is Hades's niece."),
        ("Poseidon", "Athena", "Poseidon is Athena's uncle."),
        ("Perseus", "Heracles", "Perseus is Heracles's ancestor."),
        ("Hades", "Persephone", "Hades is Persephone's husband."),
    ],
)
def test_kinship_descriptions(tree, a, b, expected):
    assert tree.describe(a, b) == expected


def test_full_sibling_needs_two_known_parents(tree):
    # Athena and Epaphus each have Zeus recorded plus a different mother
    assert "half" in tree.describe("Athena", "Epaphus")


def test_unrelated_people_have_no_relation(tree):
    assert tree.describe("Heracles", "Achilles") is None


def test_family_of_splits_half_siblings(tree):
    fam = tree.family_of("Apollo")
    assert fam["siblings"] == ["Artemis"]
    assert "Athena" in fam["half_siblings"]


# ------------------------------------------------------------------ BM25
def test_bm25_ranks_rare_terms_first():
    docs = ["the sun and the sea", "a minotaur in the labyrinth of crete", "the sea and the sky"]
    top = BM25(docs).top("labyrinth", 2)
    assert top[0][0] == 1 and len(top) == 1  # only the matching document is returned


def test_tokenize_drops_stopwords_and_plurals():
    assert tokenize("The myths of Gods") == ["god"]


# ------------------------------------------------------- names and profile
@pytest.mark.parametrize("text,expected", [("Who is Minerva?", ["Athena"]), ("juno and jupiter", ["Hera", "Zeus"]),
                                           ("Ulysses and Hercules", ["Odysseus", "Heracles"])])
def test_roman_names_resolve(knowledge, text, expected):
    assert knowledge.find_characters(text) == expected


def test_ambiguous_words_need_capitals(knowledge):
    assert knowledge.find_characters("the echo in the cave") == []
    assert knowledge.find_characters("Echo loved Narcissus") == ["Echo", "Narcissus"]


def test_profile_contents(knowledge):
    p = knowledge.profile("Minerva")
    assert p["name"] == "Athena" and p["roman_name"] == "Minerva"
    assert p["family"]["parents"] == ["Metis", "Zeus"]
    assert p["myths"] and p["themes"] and p["companions"]
    assert knowledge.profile("Nobody Atall") is None


def test_gods_without_myths_still_have_types(knowledge):
    assert knowledge.profile("Ares")["type"] == "god"


def test_compare(knowledge):
    c = knowledge.compare("Athena", "Arachne")
    assert c["shared_myths"], "Athena and Arachne share a myth"
    assert "hubris" in c["shared_themes"]
    assert c["relationship"] is None  # no family tie between them
    kin = knowledge.compare("Athena", "Apollo")
    assert kin["relationship"] == "Athena is Apollo's half-sister."
    assert knowledge.compare("Athena", "Nobody Atall") is None


# ---------------------------------------------------------------- motifs
def test_every_motif_matches_something(knowledge):
    for m in knowledge.motifs():
        assert m["count"] > 0, f"motif {m['id']} matches no myth"
    assert {m["id"] for m in knowledge.motifs()} == set(MOTIFS)


def test_transformation_motif_finds_niobe(knowledge):
    titles = [r["title"] for r in knowledge.motif_myths("transformation")]
    assert any("Niobe" in t for t in titles)
    assert all(r["snippet"] for r in knowledge.motif_myths("transformation"))


# ------------------------------------------------------------------ quiz
def test_quiz_is_wellformed_and_deterministic(knowledge):
    q1, q2 = knowledge.quiz(10, seed=7), knowledge.quiz(10, seed=7)
    assert q1 == q2 and len(q1) == 10
    for q in q1:
        assert len(q["options"]) == 4 and len(set(q["options"])) == 4
        assert 0 <= q["answer"] < 4


def test_quiz_answers_are_true_family_facts(knowledge, tree):
    for q in knowledge.quiz(20, seed=1):
        if q["kind"] != "family":
            continue
        answer = q["options"][q["answer"]]
        subject = q["question"].rsplit(" of ", 1)[1].rstrip("?")
        assert tree.describe(answer, subject), q["question"]


# ------------------------------------------------------------ chat intents
@pytest.mark.parametrize(
    "query,intent,must_contain",
    [
        ("Who are Zeus's children?", "family", "Athena"),
        ("Who is the mother of Perseus?", "family", "Danae"),
        ("Who was the wife of Odysseus?", "family", "Penelope"),
        ("Who is Juno's son?", "family", "Hephaestus"),
        ("How are Zeus and Hera related?", "relationship", "husband and brother"),
        ("Compare Athena and Arachne", "comparison", "Athena vs Arachne"),
        ("Which myths have someone turned into a tree?", "motif", "Transformation"),
        ("Which myths are about hubris?", "theme", "hubris"),
        ("Who is Minerva?", "character_info", "Athena"),
    ],
)
def test_chat_answers(engine, query, intent, must_contain):
    out = engine.chat(query, history=[])
    assert out["intent"] == intent
    assert must_contain in out["response"]


def test_unknown_question_falls_back_to_search(engine):
    out = engine.chat("which myths mention a golden apple", history=[])
    assert out["intent"] == "search"
    assert "Golden Apple" in out["response"]


def test_nonsense_gets_suggestions_not_a_crash(engine):
    out = engine.chat("qwertyuiop zxcvb", history=[])
    assert out["intent"] == "unknown" and out["suggestions"]


# ------------------------------------------------------ corpus integrity
def test_corpus_size_and_unique_ids():
    assert len(MYTHS) >= 100
    ids = [m["id"] for m in MYTHS]
    assert len(ids) == len(set(ids))


def test_every_myth_is_complete():
    for m in MYTHS:
        assert m["title"] and len(m["text"]) > 200
        assert len(m["characters"]) >= 2, m["title"]
        assert m["theme"] in m["themes"], m["title"]
        assert m["source"]


def test_characters_are_canonical(knowledge):
    """No Roman or variant names leak into the character lists."""
    roman = {"Jupiter", "Juno", "Minerva", "Venus", "Mars", "Mercury", "Bacchus", "Cupid", "Ulysses", "Hercules", "Diana"}
    seen = {c["name"] for m in MYTHS for c in m["characters"]}
    assert not (seen & roman), seen & roman


def test_genealogy_is_consistent(tree):
    for child, parents in tree.parents.items():
        assert child not in tree.ancestors(child), f"{child} is their own ancestor"
        assert len(parents) <= 3
    for a, others in tree.spouses.items():
        assert all(a in tree.spouses[b] for b in others)  # symmetric
    counts = Counter(tuple(r) for r in json.loads((ROOT / "data/annotations/genealogy.json").read_text("utf-8"))["relations"])
    assert max(counts.values()) == 1, "duplicate relation rows"


# ------------------------------------------------- semantic search attaches late
def test_sbert_can_be_attached_after_start(engine):
    """The API starts on BM25 and enables Sentence-BERT in the background; search must work both ways."""
    import numpy as np

    from chronicle.chatbot.retriever import MythRetriever

    class FakeSBERT:
        def encode(self, x):
            n = len(x) if isinstance(x, list) else 1
            rng = np.random.default_rng(0)
            v = rng.normal(size=(n, 8))
            return v if isinstance(x, list) else v[0]

    r = MythRetriever(myths=MYTHS)
    before = [m["title"] for m in r.retrieve_by_query("a sculptor falls in love with a statue", top_k=3)]
    assert any("Pygmalion" in t for t in before)  # BM25 only

    r.attach_sbert(FakeSBERT())
    assert r.sbert is not None and r._embeddings.shape[0] == len(MYTHS)
    after = r.retrieve_by_query("a sculptor falls in love with a statue", top_k=3)
    assert len(after) == 3  # hybrid path runs without error
