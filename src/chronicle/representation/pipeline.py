"""Representation pipeline — orchestrates TF-IDF, Word2Vec, and SBERT.

Provides a single entry-point to build every representation from a
list of myth dictionaries and answer similarity queries across methods.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from sklearn.metrics.pairwise import cosine_similarity

from .sbert import SBERTRepresentation
from .tfidf import TfidfRepresentation
from .word2vec import Word2VecRepresentation

logger = logging.getLogger(__name__)


class RepresentationPipeline:
    """Build and query all text representations for a mythology corpus.

    The pipeline expects myths as dictionaries with **at least** the
    following keys:

    * ``"id"``   — unique myth identifier (e.g. ``"myth_001"``).
    * ``"text"`` — the full myth narrative as a plain string.
    * ``"title"``— human-readable title (used for display).

    Optional keys consumed by the pipeline:

    * ``"tokens"`` — pre-tokenised form ``list[str]`` used for
      Word2Vec.  If absent, simple whitespace splitting is applied.
    * ``"theme"``  — thematic category string (used for visualisation).

    Parameters
    ----------
    tfidf_kwargs
        Extra keyword arguments forwarded to
        :class:`TfidfRepresentation`.
    w2v_kwargs
        Extra keyword arguments forwarded to
        :class:`Word2VecRepresentation`.
    sbert_model : str
        Sentence-BERT model name.
    sbert_device : str | None
        Device for Sentence-BERT (``None`` = auto).
    """

    def __init__(
        self,
        tfidf_kwargs: dict[str, Any] | None = None,
        w2v_kwargs: dict[str, Any] | None = None,
        sbert_model: str = "all-MiniLM-L6-v2",
        sbert_device: str | None = None,
    ) -> None:
        self.tfidf = TfidfRepresentation(**(tfidf_kwargs or {}))
        self.word2vec = Word2VecRepresentation(**(w2v_kwargs or {}))
        self.sbert = SBERTRepresentation(model_name=sbert_model, device=sbert_device)

        # Populated by build_all_representations
        self._myths: list[dict[str, Any]] = []
        self._texts: list[str] = []
        self._ids: list[str] = []
        self._titles: list[str] = []
        self._tokenized: list[list[str]] = []

        # Cached representation matrices
        self._tfidf_matrix: Any | None = None  # scipy sparse
        self._w2v_matrix: NDArray[np.float32] | None = None
        self._sbert_matrix: NDArray[np.float32] | None = None

        logger.info("RepresentationPipeline initialised")

    # ------------------------------------------------------------------
    # Main entry-point
    # ------------------------------------------------------------------

    def build_all_representations(
        self,
        myths: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build TF-IDF, Word2Vec, and SBERT representations.

        Parameters
        ----------
        myths : list[dict]
            Each dict must contain ``"id"``, ``"text"``, and
            ``"title"`` keys.  ``"tokens"`` and ``"theme"`` are
            optional.

        Returns
        -------
        dict[str, Any]
            Dictionary with keys:

            * ``"tfidf"``  — sparse TF-IDF matrix
            * ``"word2vec"`` — dense document vectors ``(n, w2v_dim)``
            * ``"sbert"`` — dense SBERT embeddings ``(n, sbert_dim)``
            * ``"ids"`` — list of myth IDs
            * ``"titles"`` — list of myth titles
        """
        self._validate_myths(myths)
        self._myths = myths
        self._ids = [m["id"] for m in myths]
        self._titles = [m["title"] for m in myths]
        self._texts = [m["text"] for m in myths]
        self._tokenized = [
            m.get("tokens") or m["text"].split() for m in myths
        ]

        logger.info("Building representations for %d myths …", len(myths))

        # --- TF-IDF ---
        self._tfidf_matrix = self.tfidf.fit_transform(self._texts)
        logger.info("  TF-IDF matrix: %s", self._tfidf_matrix.shape)

        # --- Word2Vec ---
        self.word2vec.train(self._tokenized)
        self._w2v_matrix = self.word2vec.get_document_vectors(self._tokenized)
        logger.info("  Word2Vec matrix: %s", self._w2v_matrix.shape)

        # --- SBERT ---
        self._sbert_matrix = self.sbert.encode(self._texts)
        logger.info("  SBERT matrix: %s", self._sbert_matrix.shape)

        return {
            "tfidf": self._tfidf_matrix,
            "word2vec": self._w2v_matrix,
            "sbert": self._sbert_matrix,
            "ids": list(self._ids),
            "titles": list(self._titles),
        }

    # ------------------------------------------------------------------
    # Similarity queries
    # ------------------------------------------------------------------

    def get_similarity_matrix(
        self,
        method: Literal["tfidf", "word2vec", "sbert"] = "sbert",
    ) -> NDArray[np.float32]:
        """Compute a pairwise cosine-similarity matrix.

        Parameters
        ----------
        method : ``"tfidf"`` | ``"word2vec"`` | ``"sbert"``
            Which representation to use.

        Returns
        -------
        np.ndarray
            Symmetric matrix of shape ``(n_myths, n_myths)``.
        """
        matrix = self._get_matrix(method)
        return cosine_similarity(matrix).astype(np.float32)

    def find_similar_myths(
        self,
        myth_id: str,
        top_k: int = 3,
        method: Literal["tfidf", "word2vec", "sbert"] = "sbert",
    ) -> list[dict[str, Any]]:
        """Find the most similar myths to the one identified by *myth_id*.

        Parameters
        ----------
        myth_id : str
            Unique myth identifier.
        top_k : int
            Number of similar myths to return.
        method : ``"tfidf"`` | ``"word2vec"`` | ``"sbert"``
            Representation to use for similarity.

        Returns
        -------
        list[dict]
            Each dict has keys ``"id"``, ``"title"``, ``"score"``.
        """
        if myth_id not in self._ids:
            raise KeyError(f"Myth ID '{myth_id}' not found in corpus.")

        idx = self._ids.index(myth_id)
        sim_matrix = self.get_similarity_matrix(method)
        scores = sim_matrix[idx]

        # Exclude self and sort descending
        ranked_indices = scores.argsort()[::-1]
        results: list[dict[str, Any]] = []
        for i in ranked_indices:
            if i == idx:
                continue
            results.append(
                {
                    "id": self._ids[i],
                    "title": self._titles[i],
                    "score": float(scores[i]),
                }
            )
            if len(results) >= top_k:
                break

        logger.info(
            "find_similar_myths(%s, top_k=%d, method=%s) -> %s",
            myth_id,
            top_k,
            method,
            [r["id"] for r in results],
        )
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_matrix(
        self,
        method: Literal["tfidf", "word2vec", "sbert"],
    ) -> Any:
        """Return the cached representation matrix for *method*."""
        matrices = {
            "tfidf": self._tfidf_matrix,
            "word2vec": self._w2v_matrix,
            "sbert": self._sbert_matrix,
        }
        if method not in matrices:
            raise ValueError(
                f"Unknown method '{method}'. Choose from {list(matrices.keys())}."
            )
        matrix = matrices[method]
        if matrix is None:
            raise RuntimeError(
                f"'{method}' representations have not been built yet.  "
                "Call build_all_representations() first."
            )
        return matrix

    @staticmethod
    def _validate_myths(myths: list[dict[str, Any]]) -> None:
        """Ensure every myth dict has the required keys."""
        required = {"id", "text", "title"}
        for i, myth in enumerate(myths):
            missing = required - set(myth.keys())
            if missing:
                raise ValueError(
                    f"Myth at index {i} is missing required keys: {missing}"
                )

    def __repr__(self) -> str:
        n = len(self._myths)
        return f"RepresentationPipeline(myths={n})"
