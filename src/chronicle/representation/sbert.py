"""Sentence-BERT text representation for Greek mythology corpus.

Uses the ``sentence-transformers`` library to produce dense
semantic embeddings, compute similarity, and retrieve the most
relevant passages from a pre-encoded corpus.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SBERTRepresentation:
    """Encode myth texts with Sentence-BERT and run semantic queries.

    Parameters
    ----------
    model_name : str
        Name or path of a ``sentence-transformers`` model.
    device : str | None
        PyTorch device string (``"cpu"``, ``"cuda"``, …).
        ``None`` lets the library pick automatically.
    batch_size : int
        Default batch size used when encoding texts.
    show_progress : bool
        Whether to display a progress bar during encoding.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self.show_progress = show_progress

        logger.info("Loading SBERT model '%s' …", model_name)
        self.model = SentenceTransformer(model_name, device=device)
        self._embedding_dim: int = self.model.get_sentence_embedding_dimension()  # type: ignore[assignment]
        logger.info(
            "SBERT model ready (dim=%d, device=%s)",
            self._embedding_dim,
            self.model.device,
        )

    # ------------------------------------------------------------------
    # Encoding
    # ------------------------------------------------------------------

    def encode(
        self,
        texts: str | list[str],
        batch_size: int | None = None,
        normalize: bool = True,
    ) -> NDArray[np.float32]:
        """Encode *texts* into dense embeddings.

        Parameters
        ----------
        texts : str | list[str]
            Raw or pre-processed documents / sentences. If a single string
            is passed, returns a 1-D vector of shape ``(embedding_dim,)``.
        batch_size : int | None
            Override the default batch size.
        normalize : bool
            If ``True`` the embeddings are L2-normalised so that
            dot-product equals cosine similarity.

        Returns
        -------
        np.ndarray
            Matrix of shape ``(len(texts), embedding_dim)``, or 1-D vector
            of shape ``(embedding_dim,)`` if a single string was passed.
        """
        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else list(texts)

        if not text_list:
            return np.empty((0, self._embedding_dim), dtype=np.float32)

        embeddings: np.ndarray = self.model.encode(
            text_list,
            batch_size=batch_size or self.batch_size,
            show_progress_bar=self.show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
        )
        embeddings = embeddings.astype(np.float32)
        if is_single:
            return embeddings[0]
        return embeddings

    def encode_batch(
        self,
        texts: list[str],
        batch_size: int | None = None,
        normalize: bool = True,
    ) -> NDArray[np.float32]:
        """Encode a batch of texts into dense embeddings."""
        return self.encode(texts, batch_size=batch_size, normalize=normalize)

    # ------------------------------------------------------------------
    # Similarity helpers
    # ------------------------------------------------------------------

    def similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts.

        Parameters
        ----------
        text1, text2 : str
            Input texts.

        Returns
        -------
        float
            Cosine similarity in ``[-1, 1]``.
        """
        embeddings = self.encode([text1, text2], normalize=True)
        score = float(cosine_similarity(embeddings[:1], embeddings[1:])[0, 0])
        logger.debug("similarity(%.40s…, %.40s…) = %.4f", text1, text2, score)
        return score

    def find_similar(
        self,
        query: str,
        corpus_embeddings: NDArray[np.float32],
        corpus_texts: list[str],
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """Find the most similar texts in a pre-encoded corpus.

        Parameters
        ----------
        query : str
            The query document.
        corpus_embeddings : np.ndarray
            Pre-computed embeddings of shape ``(n_corpus, dim)``.
        corpus_texts : list[str]
            The original texts corresponding to *corpus_embeddings*.
        top_k : int
            Number of results to return.

        Returns
        -------
        list[tuple[str, float]]
            ``(text, cosine_similarity)`` pairs sorted descending.
        """
        if len(corpus_texts) != corpus_embeddings.shape[0]:
            raise ValueError(
                f"corpus_texts length ({len(corpus_texts)}) does not match "
                f"corpus_embeddings rows ({corpus_embeddings.shape[0]})"
            )

        query_emb = self.encode([query], normalize=True)
        scores = cosine_similarity(query_emb, corpus_embeddings).flatten()

        # Clamp top_k to available corpus size
        top_k = min(top_k, len(corpus_texts))
        top_indices = scores.argsort()[::-1][:top_k]

        results = [(corpus_texts[idx], float(scores[idx])) for idx in top_indices]
        logger.debug("find_similar returned %d results for query '%.50s…'", len(results), query)
        return results

    def pairwise_similarity(
        self,
        embeddings: NDArray[np.float32],
    ) -> NDArray[np.float32]:
        """Compute a full pairwise cosine-similarity matrix.

        Parameters
        ----------
        embeddings : np.ndarray
            Embedding matrix of shape ``(n, dim)``.

        Returns
        -------
        np.ndarray
            Symmetric similarity matrix of shape ``(n, n)``.
        """
        return cosine_similarity(embeddings).astype(np.float32)

    # ------------------------------------------------------------------
    # Persistence for pre-computed embeddings
    # ------------------------------------------------------------------

    @staticmethod
    def save_embeddings(
        embeddings: NDArray[np.float32],
        path: str | Path,
    ) -> None:
        """Save pre-computed embeddings to a ``.npy`` file.

        Parameters
        ----------
        embeddings : np.ndarray
            The embedding matrix to persist.
        path : str | Path
            Destination file path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, embeddings)
        logger.info("Saved embeddings (%s) to %s", embeddings.shape, path)

    @staticmethod
    def load_embeddings(path: str | Path) -> NDArray[np.float32]:
        """Load pre-computed embeddings from a ``.npy`` file.

        Parameters
        ----------
        path : str | Path
            Source file path.

        Returns
        -------
        np.ndarray
            The loaded embedding matrix.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Embeddings file not found at {path}")
        embeddings = np.load(path).astype(np.float32)
        logger.info("Loaded embeddings (%s) from %s", embeddings.shape, path)
        return embeddings

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def embedding_dim(self) -> int:
        """Dimensionality of the SBERT embeddings."""
        return self._embedding_dim

    def __repr__(self) -> str:
        return (
            f"SBERTRepresentation(model='{self.model_name}', "
            f"dim={self._embedding_dim})"
        )
