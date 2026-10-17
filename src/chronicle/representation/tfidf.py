"""TF-IDF text representation for Greek mythology corpus.

Wraps scikit-learn's TfidfVectorizer with persistence, top-term
extraction, and configuration helpers tailored for Chronicle.
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class TfidfRepresentation:
    """Build and query TF-IDF representations of myth texts.

    Parameters
    ----------
    ngram_range : tuple[int, int]
        The lower and upper boundary of the range of n-values for
        different word n-grams to be extracted.
    max_features : int | None
        Maximum vocabulary size.  ``None`` means unlimited.
    min_df : int | float
        Minimum document frequency for a term to be included.
    max_df : float
        Maximum document frequency for a term to be included.
    sublinear_tf : bool
        Apply sublinear TF scaling (1 + log(tf)).
    kwargs
        Extra keyword arguments forwarded to
        :class:`sklearn.feature_extraction.text.TfidfVectorizer`.
    """

    def __init__(
        self,
        ngram_range: tuple[int, int] = (1, 2),
        max_features: int | None = 10_000,
        min_df: int | float = 2,
        max_df: float = 0.95,
        sublinear_tf: bool = True,
        **kwargs: Any,
    ) -> None:
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            sublinear_tf=sublinear_tf,
            **kwargs,
        )
        self._is_fitted: bool = False
        logger.info(
            "TfidfRepresentation initialised (ngram_range=%s, max_features=%s)",
            ngram_range,
            max_features,
        )

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def fit(self, texts: list[str]) -> None:
        """Fit the TF-IDF vectorizer on *texts*.

        Parameters
        ----------
        texts : list[str]
            Raw or pre-processed documents.
        """
        if not texts:
            raise ValueError("Cannot fit on an empty corpus.")
        self.vectorizer.fit(texts)
        self._is_fitted = True
        logger.info(
            "Fitted TF-IDF vectorizer on %d documents (%d features)",
            len(texts),
            len(self.vectorizer.vocabulary_),
        )

    def transform(self, texts: list[str]) -> scipy.sparse.csr_matrix:
        """Transform *texts* to a TF-IDF sparse matrix.

        Parameters
        ----------
        texts : list[str]
            Documents to transform.

        Returns
        -------
        scipy.sparse.csr_matrix
            Sparse document-term matrix of shape ``(n_docs, n_features)``.
        """
        self._check_fitted()
        matrix = self.vectorizer.transform(texts)
        logger.debug("Transformed %d documents -> %s sparse matrix", len(texts), matrix.shape)
        return matrix

    def fit_transform(self, texts: list[str]) -> scipy.sparse.csr_matrix:
        """Fit the vectorizer and transform *texts* in one step.

        Parameters
        ----------
        texts : list[str]
            Documents to fit on and transform.

        Returns
        -------
        scipy.sparse.csr_matrix
            Sparse document-term matrix.
        """
        if not texts:
            raise ValueError("Cannot fit_transform on an empty corpus.")
        matrix = self.vectorizer.fit_transform(texts)
        self._is_fitted = True
        logger.info(
            "fit_transform on %d documents (%d features)",
            len(texts),
            len(self.vectorizer.vocabulary_),
        )
        return matrix

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_top_terms(self, text: str, n: int = 10) -> list[tuple[str, float]]:
        """Return the top *n* TF-IDF terms for a single document.

        Parameters
        ----------
        text : str
            The input document.
        n : int
            Number of top terms to return.

        Returns
        -------
        list[tuple[str, float]]
            ``(term, tfidf_score)`` pairs sorted descending by score.
        """
        self._check_fitted()
        vector = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        scores: np.ndarray = vector.toarray().flatten()

        # Get indices of the top-n scores
        top_indices = scores.argsort()[::-1][:n]
        return [
            (feature_names[idx], float(scores[idx]))
            for idx in top_indices
            if scores[idx] > 0.0
        ]

    def get_feature_names(self) -> list[str]:
        """Return the vocabulary learned during fitting.

        Returns
        -------
        list[str]
            Ordered list of feature (term) names.
        """
        self._check_fitted()
        return list(self.vectorizer.get_feature_names_out())

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Persist the fitted vectorizer to *path*.

        Parameters
        ----------
        path : str | Path
            Destination file path (pickle format).
        """
        self._check_fitted()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as fh:
            pickle.dump(self.vectorizer, fh)
        logger.info("Saved TF-IDF model to %s", path)

    def load(self, path: str | Path) -> None:
        """Load a previously saved vectorizer from *path*.

        Parameters
        ----------
        path : str | Path
            Source file path (pickle format).
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"TF-IDF model not found at {path}")
        with open(path, "rb") as fh:
            self.vectorizer = pickle.load(fh)  # noqa: S301
        self._is_fitted = True
        logger.info("Loaded TF-IDF model from %s", path)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _check_fitted(self) -> None:
        """Raise if the vectorizer has not been fitted yet."""
        if not self._is_fitted:
            raise RuntimeError(
                "TfidfRepresentation has not been fitted. "
                "Call fit() or fit_transform() first."
            )

    def __repr__(self) -> str:
        params = self.vectorizer.get_params()
        return (
            f"TfidfRepresentation(ngram_range={params['ngram_range']}, "
            f"max_features={params['max_features']}, fitted={self._is_fitted})"
        )
