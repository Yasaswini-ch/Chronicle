"""Tests for the Chronicle representation module.

Covers:
- TfidfRepresentation: fit, transform, fit_transform, top terms, persistence.
- Word2VecRepresentation: training, vector retrieval, similarity.
- SBERTRepresentation: encoding, cosine similarity, batch encoding.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# TfidfRepresentation tests — this module exists
# ---------------------------------------------------------------------------
from chronicle.representation.tfidf import TfidfRepresentation


class TestTfidfRepresentation:
    """Tests for :class:`TfidfRepresentation`."""

    @pytest.fixture()
    def corpus(self) -> list[str]:
        """A small corpus to fit on (min_df=1 to keep all terms)."""
        return [
            "Zeus hurled thunderbolts from Mount Olympus at the Titans",
            "Hera the queen of the gods watched from Mount Olympus above",
            "Poseidon shook the earth and summoned great waves across the sea",
            "Athena wielded her spear and shield in battle against the Titans",
            "Heracles fought the Nemean Lion and strangled it with bare hands",
            "Odysseus devised a cunning plan and blinded the Cyclops Polyphemus",
            "Prometheus stole fire from the gods and gave it to humanity below",
            "Aphrodite emerged from the sea foam born of the waves themselves",
        ]

    @pytest.fixture()
    def fitted_tfidf(self, corpus: list[str]) -> TfidfRepresentation:
        tfidf = TfidfRepresentation(
            ngram_range=(1, 1), max_features=500, min_df=1, max_df=1.0,
        )
        tfidf.fit(corpus)
        return tfidf

    def test_fit_sets_vocabulary(self, fitted_tfidf: TfidfRepresentation) -> None:
        names = fitted_tfidf.get_feature_names()
        assert len(names) > 0
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)

    def test_transform_shape(
        self,
        fitted_tfidf: TfidfRepresentation,
        corpus: list[str],
    ) -> None:
        matrix = fitted_tfidf.transform(corpus)
        assert matrix.shape[0] == len(corpus)
        assert matrix.shape[1] == len(fitted_tfidf.get_feature_names())

    def test_transform_before_fit_raises(self) -> None:
        tfidf = TfidfRepresentation()
        with pytest.raises(RuntimeError, match="not been fitted"):
            tfidf.transform(["some text"])

    def test_fit_transform(self, corpus: list[str]) -> None:
        tfidf = TfidfRepresentation(
            ngram_range=(1, 1), max_features=500, min_df=1, max_df=1.0,
        )
        matrix = tfidf.fit_transform(corpus)
        assert matrix.shape[0] == len(corpus)
        assert matrix.shape[1] > 0

    def test_fit_on_empty_raises(self) -> None:
        tfidf = TfidfRepresentation()
        with pytest.raises(ValueError, match="empty corpus"):
            tfidf.fit([])

    def test_fit_transform_on_empty_raises(self) -> None:
        tfidf = TfidfRepresentation()
        with pytest.raises(ValueError, match="empty corpus"):
            tfidf.fit_transform([])

    def test_get_top_terms(
        self,
        fitted_tfidf: TfidfRepresentation,
    ) -> None:
        top = fitted_tfidf.get_top_terms(
            "Zeus hurled thunderbolts from Mount Olympus", n=5,
        )
        assert isinstance(top, list)
        assert len(top) <= 5
        for term, score in top:
            assert isinstance(term, str)
            assert isinstance(score, float)
            assert score > 0.0

    def test_get_top_terms_ordering(
        self,
        fitted_tfidf: TfidfRepresentation,
    ) -> None:
        top = fitted_tfidf.get_top_terms(
            "Zeus hurled thunderbolts at the Titans on Olympus", n=10,
        )
        scores = [score for _, score in top]
        assert scores == sorted(scores, reverse=True)

    def test_save_and_load(
        self,
        fitted_tfidf: TfidfRepresentation,
        corpus: list[str],
        tmp_path: Path,
    ) -> None:
        save_path = tmp_path / "tfidf_model.pkl"
        fitted_tfidf.save(save_path)
        assert save_path.exists()

        loaded = TfidfRepresentation()
        loaded.load(save_path)
        matrix_orig = fitted_tfidf.transform(corpus)
        matrix_loaded = loaded.transform(corpus)
        np.testing.assert_array_almost_equal(
            matrix_orig.toarray(), matrix_loaded.toarray(),
        )

    def test_load_nonexistent_raises(self, tmp_path: Path) -> None:
        tfidf = TfidfRepresentation()
        with pytest.raises(FileNotFoundError):
            tfidf.load(tmp_path / "nonexistent.pkl")

    def test_repr(self, fitted_tfidf: TfidfRepresentation) -> None:
        r = repr(fitted_tfidf)
        assert "TfidfRepresentation" in r
        assert "fitted=True" in r

    def test_ngram_range(self, corpus: list[str]) -> None:
        tfidf_bi = TfidfRepresentation(
            ngram_range=(1, 2), max_features=1000, min_df=1, max_df=1.0,
        )
        tfidf_bi.fit(corpus)
        names = tfidf_bi.get_feature_names()
        # Should have bigrams (terms containing spaces)
        assert any(" " in name for name in names)


# ---------------------------------------------------------------------------
# Word2VecRepresentation tests — skip if not implemented
# ---------------------------------------------------------------------------

class TestWord2VecRepresentation:
    """Tests for :class:`Word2VecRepresentation`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.representation.word2vec import Word2VecRepresentation
            self.W2VClass = Word2VecRepresentation
        except ImportError:
            pytest.skip("Word2VecRepresentation not yet implemented")

    @pytest.fixture()
    def tokenised_corpus(self) -> list[list[str]]:
        return [
            ["zeus", "hurled", "thunderbolts", "olympus", "titans"],
            ["hera", "queen", "gods", "watched", "olympus"],
            ["poseidon", "shook", "earth", "waves", "sea"],
            ["athena", "spear", "shield", "battle", "titans"],
            ["heracles", "fought", "nemean", "lion", "hands"],
            ["odysseus", "cunning", "plan", "blinded", "cyclops"],
            ["prometheus", "stole", "fire", "gods", "humanity"],
            ["aphrodite", "emerged", "sea", "foam", "waves"],
        ]

    @pytest.fixture()
    def w2v(self, tokenised_corpus: list[list[str]]):
        model = self.W2VClass(vector_size=50, min_count=1, epochs=20)
        model.train(tokenised_corpus)
        return model

    def test_train_creates_model(self, w2v) -> None:
        assert w2v.is_trained

    def test_get_vector(self, w2v) -> None:
        vec = w2v.get_vector("zeus")
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (50,)

    def test_get_vector_unknown(self, w2v) -> None:
        vec = w2v.get_vector("unknownword123")
        assert vec is None or (isinstance(vec, np.ndarray) and vec.shape == (50,))

    def test_similarity(self, w2v) -> None:
        sim = w2v.similarity("sea", "waves")
        assert isinstance(sim, float)
        assert -1.0 <= sim <= 1.0

    def test_document_vector(self, w2v) -> None:
        doc_vec = w2v.get_document_vector(["zeus", "thunderbolts", "olympus"])
        assert isinstance(doc_vec, np.ndarray)
        assert doc_vec.shape == (50,)

    def test_vocabulary_size(self, w2v) -> None:
        vocab = w2v.vocabulary
        assert len(vocab) > 0
        assert "zeus" in vocab


# ---------------------------------------------------------------------------
# SBERTRepresentation tests — skip if not implemented
# ---------------------------------------------------------------------------

class TestSBERTRepresentation:
    """Tests for :class:`SBERTRepresentation`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.representation.sbert import SBERTRepresentation
            self.SBERTClass = SBERTRepresentation
        except ImportError:
            pytest.skip("SBERTRepresentation not yet implemented")

    @pytest.fixture(scope="class")
    def sbert(self):
        """Load a small SBERT model once for the class."""
        from chronicle.representation.sbert import SBERTRepresentation
        return SBERTRepresentation(model_name="all-MiniLM-L6-v2")

    def test_encode_single(self, sbert) -> None:
        vec = sbert.encode("Zeus is the king of the gods.")
        assert isinstance(vec, np.ndarray)
        assert len(vec.shape) == 1
        assert vec.shape[0] > 0

    def test_encode_batch(self, sbert) -> None:
        texts = [
            "Zeus rules Olympus.",
            "Poseidon rules the sea.",
            "Hades rules the underworld.",
        ]
        vecs = sbert.encode_batch(texts)
        assert isinstance(vecs, np.ndarray)
        assert vecs.shape[0] == 3

    def test_similarity_related(self, sbert) -> None:
        sim = sbert.similarity(
            "Zeus is the king of the gods",
            "Jupiter is the ruler of the deities",
        )
        assert isinstance(sim, float)
        assert sim > 0.5  # Should be semantically similar

    def test_similarity_unrelated(self, sbert) -> None:
        sim = sbert.similarity(
            "Zeus hurled thunderbolts",
            "The stock market crashed today",
        )
        # Should be less similar
        assert isinstance(sim, float)
        assert sim < 0.5

    def test_encode_empty_string(self, sbert) -> None:
        vec = sbert.encode("")
        assert isinstance(vec, np.ndarray)
