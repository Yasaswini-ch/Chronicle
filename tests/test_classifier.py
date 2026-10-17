"""Tests for the Chronicle classifier module.

Covers:
- ClassicalClassifier: training and prediction with SVM and Naive Bayes.
- NeuralClassifier: training and prediction with a simple NN.
- ClassifierEvaluator: comparison report generation.
"""

from __future__ import annotations

from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Sample data for classification
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def classification_data() -> dict[str, Any]:
    """Return a small labelled dataset for classifier testing.

    Contains texts from three categories with enough samples for
    train/test splits.
    """
    texts = [
        # creation myths
        "Prometheus stole fire from the gods and gave it to humanity",
        "Pandora opened the jar releasing all evils into the world",
        "The gods created the first humans from clay and divine breath",
        "Gaia emerged from Chaos and gave birth to Uranus the sky",
        "Deucalion and Pyrrha repopulated the earth by throwing stones",
        "Zeus ordered the creation of Pandora as punishment for mortals",
        # heroic myths
        "Heracles slew the Nemean Lion and wore its golden pelt",
        "Perseus flew on winged sandals and slew the Gorgon Medusa",
        "Theseus entered the labyrinth and killed the Minotaur",
        "Jason sailed aboard the Argo to retrieve the Golden Fleece",
        "Achilles fought bravely at Troy and slew mighty Hector",
        "Odysseus devised a cunning plan to escape the Cyclops cave",
        # divine myths
        "Hades abducted Persephone and took her to the underworld",
        "Zeus battled the Titans in a war that shook the cosmos",
        "Apollo and Artemis were born on the island of Delos",
        "Aphrodite rose from the sea foam near the island of Cythera",
        "Demeter mourned Persephone and all crops withered and died",
        "Dionysus was born twice and wandered the earth teaching wine making",
    ]
    labels = (
        ["creation"] * 6
        + ["heroic"] * 6
        + ["divine"] * 6
    )
    return {"texts": texts, "labels": labels}


# ---------------------------------------------------------------------------
# ClassicalClassifier tests
# ---------------------------------------------------------------------------

class TestClassicalClassifier:
    """Tests for :class:`ClassicalClassifier`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.classifier.classical import ClassicalClassifier
            self.ClassifierClass = ClassicalClassifier
        except ImportError:
            pytest.skip("ClassicalClassifier not yet implemented")

    @pytest.mark.parametrize("model_type", ["svm", "naive_bayes"])
    def test_train_and_predict(
        self,
        model_type: str,
        classification_data: dict[str, Any],
    ) -> None:
        clf = self.ClassifierClass(model_type=model_type)
        clf.train(
            classification_data["texts"],
            classification_data["labels"],
        )
        predictions = clf.predict(classification_data["texts"][:3])
        assert len(predictions) == 3
        assert all(isinstance(p, str) for p in predictions)

    @pytest.mark.parametrize("model_type", ["svm", "naive_bayes"])
    def test_predictions_are_valid_labels(
        self,
        model_type: str,
        classification_data: dict[str, Any],
    ) -> None:
        clf = self.ClassifierClass(model_type=model_type)
        clf.train(
            classification_data["texts"],
            classification_data["labels"],
        )
        preds = clf.predict(classification_data["texts"])
        valid = {"creation", "heroic", "divine"}
        assert all(p in valid for p in preds)

    def test_predict_before_train_raises(self) -> None:
        clf = self.ClassifierClass(model_type="svm")
        with pytest.raises((RuntimeError, AttributeError)):
            clf.predict(["some text"])

    def test_predict_proba(
        self,
        classification_data: dict[str, Any],
    ) -> None:
        clf = self.ClassifierClass(model_type="naive_bayes")
        clf.train(
            classification_data["texts"],
            classification_data["labels"],
        )
        probas = clf.predict_proba(classification_data["texts"][:2])
        assert len(probas) == 2
        # Each prediction should have probabilities that sum to ~1
        for proba in probas:
            assert abs(sum(proba.values()) - 1.0) < 0.01

    def test_evaluate(
        self,
        classification_data: dict[str, Any],
    ) -> None:
        clf = self.ClassifierClass(model_type="svm")
        clf.train(
            classification_data["texts"],
            classification_data["labels"],
        )
        report = clf.evaluate(
            classification_data["texts"],
            classification_data["labels"],
        )
        assert isinstance(report, dict)
        assert "accuracy" in report


# ---------------------------------------------------------------------------
# NeuralClassifier tests
# ---------------------------------------------------------------------------

class TestNeuralClassifier:
    """Tests for :class:`NeuralClassifier`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.classifier.neural import NeuralClassifier
            self.NeuralClass = NeuralClassifier
        except ImportError:
            pytest.skip("NeuralClassifier not yet implemented")

    def test_train_and_predict(
        self,
        classification_data: dict[str, Any],
    ) -> None:
        clf = self.NeuralClass(epochs=5, batch_size=4)
        clf.train(
            classification_data["texts"],
            classification_data["labels"],
        )
        predictions = clf.predict(classification_data["texts"][:3])
        assert len(predictions) == 3
        assert all(isinstance(p, str) for p in predictions)

    def test_predictions_are_valid_labels(
        self,
        classification_data: dict[str, Any],
    ) -> None:
        clf = self.NeuralClass(epochs=10, batch_size=4)
        clf.train(
            classification_data["texts"],
            classification_data["labels"],
        )
        preds = clf.predict(classification_data["texts"])
        valid = {"creation", "heroic", "divine"}
        assert all(p in valid for p in preds)

    def test_predict_before_train_raises(self) -> None:
        clf = self.NeuralClass()
        with pytest.raises((RuntimeError, AttributeError)):
            clf.predict(["some text"])

    def test_training_loss_decreases(
        self,
        classification_data: dict[str, Any],
    ) -> None:
        clf = self.NeuralClass(epochs=20, batch_size=4)
        history = clf.train(
            classification_data["texts"],
            classification_data["labels"],
        )
        if history and "loss" in history:
            losses = history["loss"]
            # Loss should generally decrease (last < first)
            assert losses[-1] < losses[0]


# ---------------------------------------------------------------------------
# ClassifierEvaluator tests
# ---------------------------------------------------------------------------

class TestClassifierEvaluator:
    """Tests for :class:`ClassifierEvaluator`."""

    @pytest.fixture(autouse=True)
    def _try_import(self) -> None:
        try:
            from chronicle.classifier.evaluator import ClassifierEvaluator
            self.EvaluatorClass = ClassifierEvaluator
        except ImportError:
            pytest.skip("ClassifierEvaluator not yet implemented")

    def test_comparison_report(
        self,
        classification_data: dict[str, Any],
    ) -> None:
        evaluator = self.EvaluatorClass()
        # Build mock results
        mock_results = {
            "svm": {
                "accuracy": 0.85,
                "precision": 0.84,
                "recall": 0.83,
                "f1": 0.835,
            },
            "naive_bayes": {
                "accuracy": 0.78,
                "precision": 0.77,
                "recall": 0.76,
                "f1": 0.765,
            },
        }
        report = evaluator.generate_comparison_report(mock_results)
        assert isinstance(report, (str, dict))
        # Report should mention both models
        report_str = str(report)
        assert "svm" in report_str.lower() or "SVM" in report_str

    def test_best_model_selection(self) -> None:
        evaluator = self.EvaluatorClass()
        results = {
            "svm": {"accuracy": 0.90, "f1": 0.89},
            "naive_bayes": {"accuracy": 0.80, "f1": 0.79},
            "neural": {"accuracy": 0.85, "f1": 0.84},
        }
        best = evaluator.best_model(results, metric="f1")
        assert best == "svm"
