"""Word2Vec text representation for Greek mythology corpus.

Wraps gensim's Word2Vec with document-level aggregation, similarity
queries, and persistence helpers for Chronicle.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from gensim.models import Word2Vec

logger = logging.getLogger(__name__)


class Word2VecRepresentation:
    """Train, query, and persist Word2Vec embeddings.

    The model is exposed via :pyattr:`model` after calling
    :pymeth:`train` or :pymeth:`load`.

    Parameters
    ----------
    vector_size : int
        Dimensionality of the word vectors.
    window : int
        Maximum distance between the current and predicted word
        within a sentence.
    min_count : int
        Ignores all words with total frequency lower than this.
    workers : int
        Number of worker threads for training.
    sg : int
        Training algorithm: 1 for skip-gram, 0 for CBOW.
    epochs : int
        Number of iterations over the corpus.
    seed : int
        Random seed for reproducibility.
    """

    def __init__(
        self,
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 2,
        workers: int = 4,
        sg: int = 1,
        epochs: int = 50,
        seed: int = 42,
    ) -> None:
        self._default_params = {
            "vector_size": vector_size,
            "window": window,
            "min_count": min_count,
            "workers": workers,
            "sg": sg,
            "epochs": epochs,
            "seed": seed,
        }
        self.model: Word2Vec | None = None
        logger.info("Word2VecRepresentation initialised with defaults %s", self._default_params)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(
        self,
        tokenized_texts: list[list[str]],
        vector_size: int | None = None,
        window: int | None = None,
        min_count: int | None = None,
        **kwargs,
    ) -> None:
        """Train a Word2Vec model on tokenized documents.

        Parameters
        ----------
        tokenized_texts : list[list[str]]
            Each inner list is a sequence of tokens (one document /
            sentence).
        vector_size, window, min_count
            Override the defaults supplied at construction time.  Any
            extra *kwargs* are forwarded to :class:`gensim.models.Word2Vec`.
        """
        if not tokenized_texts:
            raise ValueError("Cannot train on an empty corpus.")

        params = {**self._default_params, **kwargs}
        if vector_size is not None:
            params["vector_size"] = vector_size
        if window is not None:
            params["window"] = window
        if min_count is not None:
            params["min_count"] = min_count

        epochs = params.pop("epochs")
        self.model = Word2Vec(sentences=tokenized_texts, epochs=epochs, **params)

        logger.info(
            "Trained Word2Vec: vocab=%d, vector_size=%d, corpus_count=%d",
            len(self.model.wv),
            self.model.wv.vector_size,
            self.model.corpus_count,
        )

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    @property
    def is_trained(self) -> bool:
        """Return True if model is trained or loaded."""
        return self.model is not None

    @property
    def vocabulary(self) -> list[str]:
        """Return list of vocabulary words."""
        if self.model is None or not hasattr(self.model, "wv"):
            return []
        return list(self.model.wv.key_to_index.keys())

    def get_vector(self, word: str) -> np.ndarray | None:
        """Return word vector or None if word not in vocabulary."""
        if self.model is None or word not in self.model.wv:
            return None
        return self.model.wv[word]

    def similarity(self, word1: str, word2: str) -> float:
        """Compute cosine similarity between two words in the vocabulary."""
        self._check_model()
        assert self.model is not None
        return float(self.model.wv.similarity(word1, word2))

    def document_vector(self, tokens: list[str]) -> np.ndarray:
        """Alias for get_document_vector."""
        return self.get_document_vector(tokens)

    def get_word_vector(self, word: str) -> np.ndarray:
        """Return the embedding vector for *word*.

        Parameters
        ----------
        word : str
            A word present in the trained vocabulary.

        Returns
        -------
        np.ndarray
            1-D vector of shape ``(vector_size,)``.

        Raises
        ------
        KeyError
            If *word* is not in the vocabulary.
        """
        self._check_model()
        assert self.model is not None  # mypy guard
        if word not in self.model.wv:
            raise KeyError(f"Word '{word}' not found in vocabulary.")
        return self.model.wv[word]

    def get_document_vector(self, tokens: list[str]) -> np.ndarray:
        """Compute a document vector by averaging its word vectors.

        Tokens not in the vocabulary are silently skipped.  If no
        tokens are in-vocabulary the zero vector is returned.

        Parameters
        ----------
        tokens : list[str]
            Token sequence for the document.

        Returns
        -------
        np.ndarray
            1-D vector of shape ``(vector_size,)``.
        """
        self._check_model()
        assert self.model is not None

        vectors = [
            self.model.wv[tok]
            for tok in tokens
            if tok in self.model.wv
        ]
        if not vectors:
            logger.warning("No in-vocabulary tokens found; returning zero vector.")
            return np.zeros(self.model.wv.vector_size, dtype=np.float32)
        return np.mean(vectors, axis=0).astype(np.float32)

    def get_document_vectors(self, tokenized_texts: list[list[str]]) -> np.ndarray:
        """Compute document vectors for every document in *tokenized_texts*.

        Parameters
        ----------
        tokenized_texts : list[list[str]]
            Each inner list is a tokenized document.

        Returns
        -------
        np.ndarray
            Matrix of shape ``(n_docs, vector_size)``.
        """
        return np.vstack([self.get_document_vector(tokens) for tokens in tokenized_texts])

    def most_similar(self, word: str, topn: int = 10) -> list[tuple[str, float]]:
        """Find the most similar words to *word* in the embedding space.

        Parameters
        ----------
        word : str
            Query word.
        topn : int
            Number of nearest neighbours to return.

        Returns
        -------
        list[tuple[str, float]]
            ``(word, cosine_similarity)`` pairs sorted descending.

        Raises
        ------
        KeyError
            If *word* is not in the vocabulary.
        """
        self._check_model()
        assert self.model is not None
        if word not in self.model.wv:
            raise KeyError(f"Word '{word}' not found in vocabulary.")
        return self.model.wv.most_similar(word, topn=topn)

    @property
    def vocabulary(self) -> list[str]:
        """Return the full vocabulary as a sorted list."""
        self._check_model()
        assert self.model is not None
        return sorted(self.model.wv.index_to_key)

    @property
    def vector_size(self) -> int:
        """Return the dimensionality of the word vectors."""
        self._check_model()
        assert self.model is not None
        return self.model.wv.vector_size

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Persist the trained Word2Vec model to *path*.

        Parameters
        ----------
        path : str | Path
            Destination file path.
        """
        self._check_model()
        assert self.model is not None
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.model.save(str(path))
        logger.info("Saved Word2Vec model to %s", path)

    def load(self, path: str | Path) -> None:
        """Load a Word2Vec model from *path*.

        Parameters
        ----------
        path : str | Path
            Source file path.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Word2Vec model not found at {path}")
        self.model = Word2Vec.load(str(path))
        logger.info(
            "Loaded Word2Vec model from %s (vocab=%d, vector_size=%d)",
            path,
            len(self.model.wv),
            self.model.wv.vector_size,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _check_model(self) -> None:
        """Raise if no model has been trained or loaded."""
        if self.model is None:
            raise RuntimeError(
                "No Word2Vec model available. Call train() or load() first."
            )

    def __repr__(self) -> str:
        if self.model is not None:
            return (
                f"Word2VecRepresentation(vocab={len(self.model.wv)}, "
                f"vector_size={self.model.wv.vector_size})"
            )
        return "Word2VecRepresentation(not trained)"
