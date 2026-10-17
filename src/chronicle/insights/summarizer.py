"""Myth summarization using extractive (TF-IDF) and abstractive (HuggingFace) methods.

This module provides ``MythSummarizer``, which can produce concise summaries of
Greek mythology texts via two complementary strategies:

* **Extractive** — ranks sentences by TF-IDF cosine similarity to the full
  document and returns the top-*k* most informative sentences in their original
  order.
* **Abstractive** — delegates to a HuggingFace ``summarization`` pipeline
  (defaults to *sshleifer/distilbart-cnn-12-6* for speed, with an option for
  *facebook/bart-large-cnn* for quality).
"""

from __future__ import annotations

import logging
import re
from copy import deepcopy
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sentence tokenisation helpers
# ---------------------------------------------------------------------------

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    """Split *text* into sentences using a regex heuristic.

    Falls back to NLTK's ``sent_tokenize`` when available, but works without
    it so the module has no hard NLTK dependency for basic operation.
    """
    try:
        from nltk.tokenize import sent_tokenize  # type: ignore[import-untyped]
        return sent_tokenize(text)
    except (ImportError, LookupError):
        sentences = _SENTENCE_RE.split(text.strip())
        return [s.strip() for s in sentences if s.strip()]


# ---------------------------------------------------------------------------
# MythSummarizer
# ---------------------------------------------------------------------------

class MythSummarizer:
    """Generate concise summaries of Greek mythology texts.

    Parameters
    ----------
    method : ``'extractive'`` | ``'abstractive'``
        Default summarisation strategy used by :meth:`summarize`.
    model_name : str | None
        HuggingFace model identifier for abstractive mode.  Defaults to
        ``'sshleifer/distilbart-cnn-12-6'``.
    device : int
        PyTorch device ordinal (``-1`` for CPU, ``0`` for first GPU).

    Examples
    --------
    >>> s = MythSummarizer(method="extractive")
    >>> s.summarize("Zeus ruled Mount Olympus. He wielded thunderbolts.")
    'Zeus ruled Mount Olympus. He wielded thunderbolts.'
    """

    SUPPORTED_METHODS: tuple[str, ...] = ("extractive", "abstractive")

    def __init__(
        self,
        method: Literal["extractive", "abstractive"] = "extractive",
        model_name: str | None = None,
        device: int = -1,
    ) -> None:
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(
                f"Unknown method '{method}'. Choose from {self.SUPPORTED_METHODS}."
            )
        self.method = method
        self.model_name = model_name or "sshleifer/distilbart-cnn-12-6"
        self.device = device

        # Lazy-loaded HuggingFace pipeline (only created when needed)
        self._pipeline: Any | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def summarize(self, text: str, max_sentences: int = 2) -> str:
        """Produce a summary using the configured ``method``.

        Parameters
        ----------
        text : str
            Full myth text to summarise.
        max_sentences : int
            Maximum number of sentences in the extractive summary (ignored
            when using the abstractive method — use ``max_length`` there).

        Returns
        -------
        str
            The generated summary.
        """
        if self.method == "extractive":
            return self.extractive_summary(text, max_sentences=max_sentences)
        return self.abstractive_summary(text)

    # -- Extractive ----------------------------------------------------

    def extractive_summary(self, text: str, max_sentences: int = 2) -> str:
        """Rank sentences by TF-IDF similarity to the document and pick the top ones.

        Algorithm
        ---------
        1. Split *text* into sentences.
        2. Build a TF-IDF matrix over the sentences.
        3. Represent the full document as the mean of sentence TF-IDF vectors.
        4. Score each sentence by cosine similarity to the document vector.
        5. Return the top-*k* sentences **in their original order** so the
           summary reads naturally.

        Parameters
        ----------
        text : str
            Source text.
        max_sentences : int
            Number of sentences to include (capped at available count).

        Returns
        -------
        str
            Extractive summary string.
        """
        sentences = _split_sentences(text)
        if not sentences:
            return ""
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        # Build TF-IDF matrix (sentences × terms)
        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            tfidf_matrix: NDArray[np.floating[Any]] = vectorizer.fit_transform(
                sentences
            ).toarray()  # type: ignore[union-attr]
        except ValueError:
            # All sentences may be stop-words only
            return " ".join(sentences[:max_sentences])

        # Document vector = mean of all sentence vectors
        doc_vector = tfidf_matrix.mean(axis=0).reshape(1, -1)

        # Cosine similarity of each sentence to the document
        scores: NDArray[np.floating[Any]] = cosine_similarity(
            tfidf_matrix, doc_vector
        ).flatten()

        # Indices of top-scoring sentences, then sort to preserve order
        top_indices = scores.argsort()[-max_sentences:]
        top_indices_sorted = sorted(top_indices)

        return " ".join(sentences[i] for i in top_indices_sorted)

    # -- Abstractive ---------------------------------------------------

    def abstractive_summary(self, text: str, max_length: int = 60) -> str:
        """Generate an abstractive summary via a HuggingFace ``summarization`` pipeline.

        On first call the model is downloaded / loaded into memory.  Subsequent
        calls reuse the cached pipeline.

        Parameters
        ----------
        text : str
            Source text.
        max_length : int
            Maximum token length for the generated summary.

        Returns
        -------
        str
            Abstractive summary string.
        """
        pipeline = self._get_pipeline()

        # The pipeline expects a minimum input length; pad very short texts.
        min_length = min(10, max_length // 2)
        try:
            result = pipeline(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True,
            )
        except Exception:
            logger.exception("Abstractive summarisation failed; falling back to extractive.")
            return self.extractive_summary(text)

        if result and isinstance(result, list) and "summary_text" in result[0]:
            return str(result[0]["summary_text"]).strip()
        return ""

    # -- Corpus helpers ------------------------------------------------

    def summarize_corpus(self, myths: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Add an ``'auto_summary'`` field to each myth dictionary.

        Each dict is expected to have a ``'text'`` key containing the full
        myth narrative.  A deep copy is returned so the originals are not
        mutated.

        Parameters
        ----------
        myths : list[dict]
            Corpus of myth dictionaries.

        Returns
        -------
        list[dict]
            Copies of the input dicts with the ``'auto_summary'`` key added.
        """
        results: list[dict[str, Any]] = []
        for myth in myths:
            entry = deepcopy(myth)
            text = entry.get("text", "")
            if text:
                entry["auto_summary"] = self.summarize(text)
            else:
                entry["auto_summary"] = ""
            results.append(entry)
        return results

    # -- Evaluation ----------------------------------------------------

    def evaluate_summaries(
        self,
        generated: list[str],
        reference: list[str],
    ) -> dict[str, dict[str, float]]:
        """Compute ROUGE-1, ROUGE-2, and ROUGE-L scores.

        Uses the ``rouge-score`` library (``pip install rouge-score``).

        Parameters
        ----------
        generated : list[str]
            Model-generated summaries.
        reference : list[str]
            Human-written reference summaries.

        Returns
        -------
        dict[str, dict[str, float]]
            Mapping from metric name (e.g. ``'rouge1'``) to a dict of
            ``precision``, ``recall``, and ``fmeasure`` averaged over all
            pairs.

        Raises
        ------
        ValueError
            If the two lists differ in length.
        ImportError
            If *rouge-score* is not installed.
        """
        if len(generated) != len(reference):
            raise ValueError(
                f"Length mismatch: {len(generated)} generated vs "
                f"{len(reference)} reference summaries."
            )

        try:
            from rouge_score import rouge_scorer  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "The 'rouge-score' package is required for evaluation. "
                "Install it with: pip install rouge-score"
            ) from exc

        scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"], use_stemmer=True
        )

        aggregated: dict[str, dict[str, list[float]]] = {
            metric: {"precision": [], "recall": [], "fmeasure": []}
            for metric in ("rouge1", "rouge2", "rougeL")
        }

        for gen, ref in zip(generated, reference):
            scores = scorer.score(ref, gen)
            for metric in aggregated:
                aggregated[metric]["precision"].append(scores[metric].precision)
                aggregated[metric]["recall"].append(scores[metric].recall)
                aggregated[metric]["fmeasure"].append(scores[metric].fmeasure)

        results: dict[str, dict[str, float]] = {}
        for metric, values in aggregated.items():
            results[metric] = {
                k: float(np.mean(v)) for k, v in values.items()
            }
        return results

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get_pipeline(self) -> Any:
        """Lazily initialise the HuggingFace summarisation pipeline."""
        if self._pipeline is None:
            logger.info("Loading summarisation model '%s' …", self.model_name)
            from transformers import pipeline as hf_pipeline  # type: ignore[import-untyped]

            self._pipeline = hf_pipeline(
                "summarization",
                model=self.model_name,
                device=self.device,
            )
        return self._pipeline

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"{self.__class__.__name__}(method={self.method!r}, "
            f"model_name={self.model_name!r})"
        )
