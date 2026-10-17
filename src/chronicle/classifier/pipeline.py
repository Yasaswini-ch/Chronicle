"""Classification pipeline orchestrating classical and neural classifiers.

Provides high-level methods to run individual classifier families or a
full comparison across all available models on a mythology corpus.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from chronicle.classifier.classical import ClassicalClassifier
from chronicle.classifier.evaluator import ClassifierEvaluator
from chronicle.classifier.neural import NeuralClassifier

logger = logging.getLogger(__name__)

#: Default theme labels used throughout Chronicle.
THEME_LABELS: list[str] = [
    "hubris",
    "love",
    "betrayal",
    "revenge",
    "wisdom",
    "jealousy",
]


def _extract_texts_and_labels(
    myths: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    """Pull ``text`` and ``theme`` from a list of myth dicts.

    Each myth dict is expected to have at least::

        {"text": "...", "theme": "hubris"}

    Parameters
    ----------
    myths : list[dict]
        List of myth dictionaries.

    Returns
    -------
    tuple[list[str], list[str]]
        ``(texts, labels)``

    Raises
    ------
    ValueError
        If *myths* is empty or any entry is missing required keys.
    """
    if not myths:
        raise ValueError("myths list is empty — nothing to classify.")

    texts: list[str] = []
    labels: list[str] = []
    for i, m in enumerate(myths):
        if "text" not in m:
            raise ValueError(f"Myth at index {i} is missing 'text' key.")
        if "theme" not in m:
            raise ValueError(f"Myth at index {i} is missing 'theme' key.")
        texts.append(m["text"])
        labels.append(m["theme"])

    return texts, labels


class ClassificationPipeline:
    """High-level orchestrator for running and comparing classifiers.

    Parameters
    ----------
    tfidf_max_features : int
        Maximum vocabulary size for the TF-IDF vectoriser.
    neural_epochs : int
        Training epochs for the neural MLP classifier.
    neural_lr : float
        Learning rate for the neural MLP classifier.

    Examples
    --------
    >>> pipeline = ClassificationPipeline()
    >>> results = pipeline.run_full_comparison(myths)
    >>> print(results["report"])
    """

    def __init__(
        self,
        tfidf_max_features: int = 5000,
        neural_epochs: int = 50,
        neural_lr: float = 0.001,
    ) -> None:
        self.tfidf_max_features = tfidf_max_features
        self.neural_epochs = neural_epochs
        self.neural_lr = neural_lr

        self._tfidf_vectoriser: TfidfVectorizer | None = None
        self._evaluator = ClassifierEvaluator()

        logger.info("ClassificationPipeline initialised.")

    # ------------------------------------------------------------------
    # Feature extraction helpers
    # ------------------------------------------------------------------

    def _build_tfidf(self, texts: list[str]) -> np.ndarray:
        """Fit a TF-IDF vectoriser and transform texts.

        Parameters
        ----------
        texts : list[str]
            Raw document strings.

        Returns
        -------
        np.ndarray
            Dense TF-IDF feature matrix.
        """
        self._tfidf_vectoriser = TfidfVectorizer(
            max_features=self.tfidf_max_features,
            sublinear_tf=True,
            ngram_range=(1, 2),
            stop_words="english",
        )
        X = self._tfidf_vectoriser.fit_transform(texts)
        logger.info(
            "TF-IDF matrix: %d docs × %d features", X.shape[0], X.shape[1],
        )
        return X.toarray()

    @staticmethod
    def _build_sbert_embeddings(texts: list[str]) -> np.ndarray:
        """Compute SBERT embeddings for a list of texts.

        Uses ``all-MiniLM-L6-v2`` by default.  Falls back to random
        embeddings (with a warning) if ``sentence-transformers`` is
        unavailable, so that the pipeline remains testable.

        Parameters
        ----------
        texts : list[str]
            Raw document strings.

        Returns
        -------
        np.ndarray
            Embedding matrix of shape ``(n_docs, 384)``.
        """
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(texts, show_progress_bar=False)
            return np.asarray(embeddings)
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Using random embeddings as fallback (results will be meaningless)."
            )
            rng = np.random.RandomState(42)
            return rng.randn(len(texts), 384).astype(np.float32)

    # ------------------------------------------------------------------
    # Classical pipeline
    # ------------------------------------------------------------------

    def run_classical(
        self,
        myths: list[dict[str, Any]],
        representation_type: str = "tfidf",
    ) -> dict[str, dict[str, Any]]:
        """Run both logistic regression and SVM classifiers.

        Parameters
        ----------
        myths : list[dict]
            Myth dicts with ``text`` and ``theme`` keys.
        representation_type : str
            Feature type — currently only ``'tfidf'`` is supported.

        Returns
        -------
        dict[str, dict]
            Keyed by model name (``"Logistic Regression"``,
            ``"SVM"``), values are metric dictionaries.
        """
        texts, labels = _extract_texts_and_labels(myths)

        if representation_type == "tfidf":
            X = self._build_tfidf(texts)
        else:
            raise ValueError(
                f"Unsupported representation_type '{representation_type}'. "
                "Use 'tfidf'."
            )

        results: dict[str, dict[str, Any]] = {}

        for model_type, display_name in [
            ("logistic_regression", "Logistic Regression"),
            ("svm", "SVM"),
        ]:
            logger.info("Running classical classifier: %s", display_name)
            clf = ClassicalClassifier(model_type=model_type)
            metrics = clf.train(X, labels)
            results[display_name] = metrics

        return results

    # ------------------------------------------------------------------
    # Neural pipeline
    # ------------------------------------------------------------------

    def run_neural(
        self,
        myths: list[dict[str, Any]],
        sbert_embeddings: np.ndarray | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Run the neural MLP classifier on SBERT embeddings.

        Parameters
        ----------
        myths : list[dict]
            Myth dicts with ``text`` and ``theme`` keys.
        sbert_embeddings : np.ndarray, optional
            Pre-computed embeddings.  If *None* they will be computed
            automatically via sentence-transformers.

        Returns
        -------
        dict[str, dict]
            Single entry ``"Neural MLP"`` → metrics.
        """
        texts, labels = _extract_texts_and_labels(myths)

        if sbert_embeddings is None:
            sbert_embeddings = self._build_sbert_embeddings(texts)

        if sbert_embeddings.shape[0] != len(labels):
            raise ValueError(
                f"Embedding count ({sbert_embeddings.shape[0]}) does not "
                f"match label count ({len(labels)})."
            )

        embedding_dim = sbert_embeddings.shape[1]
        num_classes = len(set(labels))

        clf = NeuralClassifier(
            embedding_dim=embedding_dim,
            num_classes=num_classes,
        )
        metrics = clf.train(
            sbert_embeddings,
            labels,
            epochs=self.neural_epochs,
            lr=self.neural_lr,
        )

        return {"Neural MLP": metrics}

    # ------------------------------------------------------------------
    # Full comparison
    # ------------------------------------------------------------------

    def run_full_comparison(
        self,
        myths: list[dict[str, Any]],
        sbert_embeddings: np.ndarray | None = None,
    ) -> dict[str, Any]:
        """Run all classifiers and produce a unified comparison.

        This method:
        1. Runs Logistic Regression and SVM on TF-IDF features.
        2. Runs the Neural MLP on SBERT embeddings.
        3. Generates comparison table, charts, and a text report.

        Parameters
        ----------
        myths : list[dict]
            Myth dicts with ``text`` and ``theme`` keys.
        sbert_embeddings : np.ndarray, optional
            Pre-computed SBERT embeddings (computed automatically if
            not provided).

        Returns
        -------
        dict[str, Any]
            Keys:

            - ``"model_results"`` — per-model metric dicts
            - ``"comparison_df"`` — pandas DataFrame
            - ``"confusion_fig"`` — Plotly figure
            - ``"comparison_fig"`` — Plotly figure
            - ``"report"`` — text summary
        """
        logger.info("Starting full classifier comparison.")

        # Collect all model results
        all_results: dict[str, dict[str, Any]] = {}

        # Classical
        classical_results = self.run_classical(myths)
        all_results.update(classical_results)

        # Neural
        neural_results = self.run_neural(myths, sbert_embeddings)
        all_results.update(neural_results)

        # Evaluate & compare
        comparison_df = self._evaluator.compare_models(all_results)
        confusion_fig = self._evaluator.plot_confusion_matrices(
            all_results, class_names=THEME_LABELS,
        )
        comparison_fig = self._evaluator.plot_comparison_chart(all_results)
        report = self._evaluator.generate_report(all_results)

        logger.info("Full comparison complete.")

        return {
            "model_results": all_results,
            "comparison_df": comparison_df,
            "confusion_fig": confusion_fig,
            "comparison_fig": comparison_fig,
            "report": report,
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"ClassificationPipeline(tfidf_max_features={self.tfidf_max_features}, "
            f"neural_epochs={self.neural_epochs})"
        )
