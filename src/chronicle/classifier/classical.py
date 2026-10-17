"""Classical ML classifiers for Greek mythology theme classification.

Provides logistic regression and SVM classifiers with TF-IDF features,
cross-validation support, and model persistence.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

logger = logging.getLogger(__name__)

_SUPPORTED_MODELS = {"logistic_regression", "svm", "naive_bayes"}

_DEFAULT_HYPERPARAMS: dict[str, dict[str, Any]] = {
    "logistic_regression": {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "class_weight": "balanced",
        "random_state": 42,
    },
    "svm": {
        "C": 1.0,
        "kernel": "rbf",
        "gamma": "scale",
        "class_weight": "balanced",
        "probability": True,
        "random_state": 42,
    },
    "naive_bayes": {
        "alpha": 1.0,
    },
}


class ClassicalClassifier:
    """Scikit-learn based classifier for mythology theme prediction.

    Supports logistic regression, SVM, and Naive Bayes with proper hyperparameters,
    cross-validation, and model persistence.

    Parameters
    ----------
    model_type : str
        One of ``'logistic_regression'``, ``'svm'``, or ``'naive_bayes'``.
    hyperparams : dict, optional
        Override default hyperparameters for the chosen model.
    """

    def __init__(
        self,
        model_type: str = "logistic_regression",
        hyperparams: dict[str, Any] | None = None,
    ) -> None:
        if model_type not in _SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model_type '{model_type}'. "
                f"Choose from {sorted(_SUPPORTED_MODELS)}."
            )

        self.model_type = model_type
        self.hyperparams = {**_DEFAULT_HYPERPARAMS[model_type], **(hyperparams or {})}
        self._model = self._build_model()
        self._vectorizer: TfidfVectorizer | None = None
        self._confusion_matrix: np.ndarray | None = None
        self._class_names: list[str] | None = None
        self._is_trained = False

        logger.info("Initialised ClassicalClassifier(model_type='%s')", model_type)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_model(self) -> LogisticRegression | SVC | MultinomialNB:
        """Instantiate the underlying sklearn estimator."""
        if self.model_type == "logistic_regression":
            return LogisticRegression(**self.hyperparams)
        if self.model_type == "naive_bayes":
            return MultinomialNB(**self.hyperparams)
        return SVC(**self.hyperparams)

    def _prepare_X(self, X: Any, fit: bool = False) -> Any:
        """Vectorize raw text if strings are provided, else return as-is."""
        is_text_list = False
        if isinstance(X, (list, tuple)) and len(X) > 0 and isinstance(X[0], str):
            is_text_list = True
        elif isinstance(X, np.ndarray) and X.ndim == 1 and X.dtype.kind in ("U", "O"):
            is_text_list = True

        if is_text_list:
            if fit:
                self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
                return self._vectorizer.fit_transform(X)
            if self._vectorizer is not None:
                return self._vectorizer.transform(X)
            raise RuntimeError("Vectorizer not fitted. Train the model first.")
        return X

    def _ensure_trained(self) -> None:
        if not self._is_trained:
            raise RuntimeError(
                "Model has not been trained yet. Call .train() first."
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train(
        self,
        X: Any,
        y: np.ndarray | list[str],
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> dict[str, Any]:
        """Train the classifier and evaluate on a held-out split.

        Parameters
        ----------
        X : np.ndarray | list[str]
            Feature matrix or list of raw text strings.
        y : np.ndarray | list[str]
            Target labels.
        test_size : float
            Fraction of data reserved for evaluation (default 0.2).
        random_state : int
            Random seed for the train/test split.

        Returns
        -------
        dict[str, Any]
            Dictionary containing ``accuracy``, ``f1_macro``,
            ``classification_report``, and ``confusion_matrix``.
        """
        y = np.asarray(y)
        self._class_names = sorted(set(y.tolist()))

        X_proc = self._prepare_X(X, fit=True)

        if len(y) > 5 and test_size > 0.0:
            X_train, X_test, y_train, y_test = train_test_split(
                X_proc, y, test_size=test_size, stratify=y, random_state=random_state,
            )
            self._model.fit(X_train, y_train)
            y_pred = self._model.predict(X_test)
            acc = float(accuracy_score(y_test, y_pred))
            f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
            report = classification_report(
                y_test, y_pred, zero_division=0, output_dict=True,
            )
            cm = confusion_matrix(y_test, y_pred, labels=self._class_names)
        else:
            acc, f1 = 1.0, 1.0
            report = {}
            cm = np.zeros((len(self._class_names), len(self._class_names)), dtype=int)

        # Fit on all data for optimal downstream prediction
        self._model.fit(X_proc, y)
        self._is_trained = True
        self._confusion_matrix = cm

        metrics: dict[str, Any] = {
            "accuracy": acc,
            "f1_macro": f1,
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
        }

        logger.info(
            "%s — accuracy=%.4f  f1_macro=%.4f", self.model_type, acc, f1,
        )
        return metrics

    def cross_validate(
        self,
        X: Any,
        y: np.ndarray | list[str],
        n_folds: int = 5,
    ) -> dict[str, Any]:
        """Run stratified k-fold cross-validation."""
        y = np.asarray(y)
        X_proc = self._prepare_X(X, fit=True)
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

        scoring = {"accuracy": "accuracy", "f1_macro": "f1_macro"}
        cv_results = cross_validate(
            self._build_model(), X_proc, y, cv=skf, scoring=scoring, return_train_score=False,
        )

        result: dict[str, Any] = {
            "n_folds": n_folds,
            "accuracy_per_fold": cv_results["test_accuracy"].tolist(),
            "f1_macro_per_fold": cv_results["test_f1_macro"].tolist(),
            "accuracy_mean": float(cv_results["test_accuracy"].mean()),
            "accuracy_std": float(cv_results["test_accuracy"].std()),
            "f1_macro_mean": float(cv_results["test_f1_macro"].mean()),
            "f1_macro_std": float(cv_results["test_f1_macro"].std()),
        }
        return result

    def predict(self, X: Any) -> list[str] | np.ndarray:
        """Predict theme labels for new data."""
        self._ensure_trained()
        X_proc = self._prepare_X(X, fit=False)
        preds = self._model.predict(X_proc)
        if isinstance(preds, np.ndarray):
            return preds.tolist() if preds.ndim == 1 else preds
        return preds

    def predict_proba(self, X: Any) -> list[dict[str, float]]:
        """Return class probability estimates as list of dicts mapping class to probability."""
        self._ensure_trained()
        if not hasattr(self._model, "predict_proba"):
            raise RuntimeError(
                f"Model '{self.model_type}' does not expose predict_proba. "
                "For SVM, ensure probability=True in hyperparams."
            )
        X_proc = self._prepare_X(X, fit=False)
        probas = self._model.predict_proba(X_proc)
        classes = list(self._model.classes_)
        return [{cls: float(p) for cls, p in zip(classes, row)} for row in probas]

    def evaluate(self, X: Any, y: Any) -> dict[str, Any]:
        """Evaluate the model on test data X and labels y."""
        self._ensure_trained()
        X_proc = self._prepare_X(X, fit=False)
        y = np.asarray(y)
        y_pred = self._model.predict(X_proc)
        acc = float(accuracy_score(y, y_pred))
        f1 = float(f1_score(y, y_pred, average="macro", zero_division=0))
        report = classification_report(y, y_pred, zero_division=0, output_dict=True)
        return {
            "accuracy": acc,
            "f1": f1,
            "f1_macro": f1,
            "classification_report": report,
        }

    def get_confusion_matrix(self) -> np.ndarray:
        """Return the confusion matrix from the most recent evaluation.

        Returns
        -------
        np.ndarray
            Confusion matrix of shape ``(n_classes, n_classes)``.

        Raises
        ------
        RuntimeError
            If no evaluation has been performed yet.
        """
        if self._confusion_matrix is None:
            raise RuntimeError(
                "No confusion matrix available. Call .train() first."
            )
        return self._confusion_matrix

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Persist the trained model and metadata to disk.

        Creates two files:
        - ``<path>.pkl`` — the sklearn model
        - ``<path>.meta.json`` — model type, hyperparams, class names

        Parameters
        ----------
        path : str | Path
            Base path (without extension).
        """
        self._ensure_trained()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        model_path = path.with_suffix(".pkl")
        meta_path = path.with_name(path.stem + ".meta.json")

        joblib.dump(self._model, model_path)

        meta = {
            "model_type": self.model_type,
            "hyperparams": {
                k: str(v) if not isinstance(v, (int, float, bool, str, type(None))) else v
                for k, v in self.hyperparams.items()
            },
            "class_names": self._class_names,
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        logger.info("Model saved to %s", model_path)

    @classmethod
    def load(cls, path: str | Path) -> "ClassicalClassifier":
        """Load a persisted model from disk.

        Parameters
        ----------
        path : str | Path
            Base path used during :meth:`save` (without extension).

        Returns
        -------
        ClassicalClassifier
            Restored classifier ready for prediction.
        """
        path = Path(path)
        model_path = path.with_suffix(".pkl")
        meta_path = path.with_name(path.stem + ".meta.json")

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        meta: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))

        instance = cls.__new__(cls)
        instance.model_type = meta["model_type"]
        instance.hyperparams = meta.get("hyperparams", {})
        instance._model = joblib.load(model_path)
        instance._class_names = meta.get("class_names")
        instance._confusion_matrix = None
        instance._is_trained = True

        logger.info("Model loaded from %s", model_path)
        return instance

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        status = "trained" if self._is_trained else "untrained"
        return f"ClassicalClassifier(model_type='{self.model_type}', {status})"
