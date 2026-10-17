"""Neural (MLP) classifier for Greek mythology theme classification.

Uses a multi-layer perceptron on top of sentence-transformer embeddings
(SBERT) with PyTorch, including dropout regularisation and label encoding.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import DataLoader, TensorDataset

logger = logging.getLogger(__name__)


# ======================================================================
# MLP definition
# ======================================================================

class _ThemeMLP(nn.Module):
    """3-hidden-layer MLP with ReLU activations and dropout.

    Architecture
    ------------
    input → Linear(embedding_dim, hidden_dim) → ReLU → Dropout
          → Linear(hidden_dim, hidden_dim) → ReLU → Dropout
          → Linear(hidden_dim, hidden_dim // 2) → ReLU → Dropout
          → Linear(hidden_dim // 2, num_classes)
    """

    def __init__(
        self,
        embedding_dim: int,
        num_classes: int,
        hidden_dim: int = 128,
        dropout: float = 0.3,
    ) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # noqa: D401
        """Forward pass returning raw logits."""
        return self.net(x)


# ======================================================================
# Public classifier wrapper
# ======================================================================

class NeuralClassifier:
    """MLP classifier operating on pre-computed SBERT embeddings.

    Parameters
    ----------
    embedding_dim : int
        Dimensionality of the input embeddings (default 384 for
        ``all-MiniLM-L6-v2``).
    num_classes : int
        Number of target theme classes.
    hidden_dim : int
        Width of the hidden layers.
    dropout : float
        Dropout probability between hidden layers.

    Examples
    --------
    >>> clf = NeuralClassifier(embedding_dim=384, num_classes=6)
    >>> metrics = clf.train(embeddings, labels, epochs=50, lr=1e-3)
    >>> preds = clf.predict(new_embeddings)
    """

    def __init__(
        self,
        embedding_dim: int = 384,
        num_classes: int = 6,
        hidden_dim: int = 128,
        dropout: float = 0.3,
        epochs: int = 50,
        batch_size: int = 32,
        lr: float = 0.001,
        **kwargs: Any,
    ) -> None:
        self.embedding_dim = embedding_dim
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.dropout = dropout
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._label_encoder = LabelEncoder()
        self._model: _ThemeMLP | None = None
        self._is_trained = False
        self._sbert = None

        logger.info(
            "NeuralClassifier initialised (embedding_dim=%d, num_classes=%d, "
            "hidden_dim=%d, device=%s)",
            embedding_dim, num_classes, hidden_dim, self._device,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_sbert(self):
        if self._sbert is None:
            from chronicle.representation.sbert import SBERTRepresentation
            self._sbert = SBERTRepresentation()
        return self._sbert

    def _prepare_inputs(self, X: Any) -> np.ndarray:
        if isinstance(X, (list, tuple)) and len(X) > 0 and isinstance(X[0], str):
            sbert = self._get_sbert()
            return np.asarray(sbert.encode(list(X)), dtype=np.float32)
        if isinstance(X, np.ndarray) and X.ndim == 1 and X.dtype.kind in ("U", "O"):
            sbert = self._get_sbert()
            return np.asarray(sbert.encode(X.tolist()), dtype=np.float32)
        return np.asarray(X, dtype=np.float32)

    def _build_model(self) -> _ThemeMLP:
        """Create and move the MLP to the target device."""
        model = _ThemeMLP(
            embedding_dim=self.embedding_dim,
            num_classes=self.num_classes,
            hidden_dim=self.hidden_dim,
            dropout=self.dropout,
        )
        return model.to(self._device)

    def _ensure_trained(self) -> None:
        if not self._is_trained or self._model is None:
            raise RuntimeError(
                "Model has not been trained yet. Call .train() first."
            )

    @staticmethod
    def _to_tensor(arr: np.ndarray, dtype: torch.dtype = torch.float32) -> torch.Tensor:
        return torch.tensor(np.asarray(arr), dtype=dtype)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(
        self,
        embeddings: Any,
        labels: list[str],
        epochs: int | None = None,
        lr: float | None = None,
        batch_size: int | None = None,
        val_split: float = 0.2,
    ) -> dict[str, Any]:
        """Train the MLP classifier.

        Parameters
        ----------
        embeddings : np.ndarray | list[str]
            Pre-computed embeddings or raw text strings.
        labels : list[str]
            String labels for each sample.
        epochs : int, optional
            Number of training epochs.
        lr : float, optional
            Learning rate for Adam optimiser.
        batch_size : int, optional
            Mini-batch size.
        val_split : float
            Fraction of data held out for validation.
        """
        epochs = epochs if epochs is not None else self.epochs
        lr = lr if lr is not None else self.lr
        batch_size = batch_size if batch_size is not None else self.batch_size

        embeddings = self._prepare_inputs(embeddings)
        self.embedding_dim = embeddings.shape[1]
        labels_arr = np.asarray(labels)

        # Fit label encoder
        self._label_encoder.fit(labels_arr)
        encoded = self._label_encoder.transform(labels_arr)
        self.num_classes = len(self._label_encoder.classes_)

        # Train / validation split (deterministic)
        n_val = max(1, int(len(embeddings) * val_split))
        rng = np.random.RandomState(42)
        indices = rng.permutation(len(embeddings))
        val_idx, train_idx = indices[:n_val], indices[n_val:]

        X_train = self._to_tensor(embeddings[train_idx])
        y_train = self._to_tensor(encoded[train_idx], dtype=torch.long)
        X_val = self._to_tensor(embeddings[val_idx])
        y_val = self._to_tensor(encoded[val_idx], dtype=torch.long)

        train_ds = TensorDataset(X_train, y_train)
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

        # Build model + optimiser + loss
        self._model = self._build_model()
        optimiser = torch.optim.Adam(self._model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()

        train_losses: list[float] = []
        val_losses: list[float] = []

        for epoch in range(1, epochs + 1):
            # -- Training --
            self._model.train()
            epoch_loss = 0.0
            for X_batch, y_batch in train_loader:
                X_batch = X_batch.to(self._device)
                y_batch = y_batch.to(self._device)

                optimiser.zero_grad()
                logits = self._model(X_batch)
                loss = criterion(logits, y_batch)
                loss.backward()
                optimiser.step()
                epoch_loss += loss.item() * len(X_batch)

            avg_train_loss = epoch_loss / len(train_ds)
            train_losses.append(avg_train_loss)

            # -- Validation --
            self._model.eval()
            with torch.no_grad():
                val_logits = self._model(X_val.to(self._device))
                avg_val_loss = criterion(val_logits, y_val.to(self._device)).item()
            val_losses.append(avg_val_loss)

            if epoch % max(1, epochs // 5) == 0 or epoch == 1:
                logger.info(
                    "Epoch %3d/%d — train_loss=%.4f  val_loss=%.4f",
                    epoch, epochs, avg_train_loss, avg_val_loss,
                )

        self._is_trained = True

        # Final validation evaluation
        val_metrics = self._evaluate_tensors(X_val, y_val)

        return {
            "accuracy": val_metrics["accuracy"],
            "f1_macro": val_metrics["f1_macro"],
            "classification_report": val_metrics["classification_report"],
            "confusion_matrix": val_metrics["confusion_matrix"],
            "loss": train_losses,
            "train_losses": train_losses,
            "val_losses": val_losses,
            "epochs": epochs,
        }

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, embeddings: Any) -> list[str]:
        """Predict theme labels from embeddings or texts.

        Parameters
        ----------
        embeddings : np.ndarray | list[str]
            Array of shape ``(n_samples, embedding_dim)`` or list of texts.

        Returns
        -------
        list[str]
            Predicted theme names.
        """
        self._ensure_trained()
        assert self._model is not None

        embeddings = self._prepare_inputs(embeddings)
        X = self._to_tensor(embeddings).to(self._device)

        self._model.eval()
        with torch.no_grad():
            logits = self._model(X)
            indices = logits.argmax(dim=1).cpu().numpy()

        return self._label_encoder.inverse_transform(indices).tolist()

    def predict_proba(self, embeddings: np.ndarray) -> np.ndarray:
        """Return class probability estimates (softmax over logits).

        Parameters
        ----------
        embeddings : np.ndarray
            Array of shape ``(n_samples, embedding_dim)``.

        Returns
        -------
        np.ndarray
            Probability matrix of shape ``(n_samples, num_classes)``.
        """
        self._ensure_trained()
        assert self._model is not None

        X = self._to_tensor(np.asarray(embeddings, dtype=np.float32)).to(self._device)

        self._model.eval()
        with torch.no_grad():
            logits = self._model(X)
            probs = torch.softmax(logits, dim=1).cpu().numpy()

        return probs

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def _evaluate_tensors(
        self, X: torch.Tensor, y: torch.Tensor,
    ) -> dict[str, Any]:
        """Core evaluation on tensors (already label-encoded)."""
        assert self._model is not None
        self._model.eval()
        with torch.no_grad():
            logits = self._model(X.to(self._device))
            preds = logits.argmax(dim=1).cpu().numpy()

        y_np = y.numpy()
        class_names = self._label_encoder.classes_.tolist()
        all_labels = list(range(len(class_names)))
        acc = float(accuracy_score(y_np, preds))
        f1 = float(f1_score(y_np, preds, average="macro", zero_division=0))
        report = classification_report(
            y_np, preds, labels=all_labels, target_names=class_names, zero_division=0, output_dict=True,
        )
        cm = confusion_matrix(y_np, preds, labels=all_labels)

        return {
            "accuracy": acc,
            "f1_macro": f1,
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
        }

    def evaluate(
        self, embeddings: np.ndarray, labels: list[str],
    ) -> dict[str, Any]:
        """Evaluate the trained model on labelled data.

        Parameters
        ----------
        embeddings : np.ndarray
            Input embeddings.
        labels : list[str]
            Ground-truth string labels.

        Returns
        -------
        dict[str, Any]
            Dictionary with ``accuracy``, ``f1_macro``,
            ``classification_report``, and ``confusion_matrix``.
        """
        self._ensure_trained()

        encoded = self._label_encoder.transform(np.asarray(labels))
        X = self._to_tensor(np.asarray(embeddings, dtype=np.float32))
        y = self._to_tensor(encoded, dtype=torch.long)

        result = self._evaluate_tensors(X, y)
        logger.info(
            "Neural evaluation — accuracy=%.4f  f1_macro=%.4f",
            result["accuracy"], result["f1_macro"],
        )
        return result

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save model weights, label encoder, and architecture config.

        Creates:
        - ``<path>.pt`` — PyTorch state dict
        - ``<path>.meta.json`` — architecture params + label mapping

        Parameters
        ----------
        path : str | Path
            Base path (without extension).
        """
        self._ensure_trained()
        assert self._model is not None

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        weights_path = path.with_suffix(".pt")
        meta_path = path.with_name(path.stem + ".meta.json")

        torch.save(self._model.state_dict(), weights_path)

        meta = {
            "embedding_dim": self.embedding_dim,
            "num_classes": self.num_classes,
            "hidden_dim": self.hidden_dim,
            "dropout": self.dropout,
            "label_classes": self._label_encoder.classes_.tolist(),
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        logger.info("Neural model saved to %s", weights_path)

    @classmethod
    def load(cls, path: str | Path) -> "NeuralClassifier":
        """Restore a persisted :class:`NeuralClassifier`.

        Parameters
        ----------
        path : str | Path
            Base path used during :meth:`save` (without extension).

        Returns
        -------
        NeuralClassifier
            Ready-to-predict classifier.
        """
        path = Path(path)
        weights_path = path.with_suffix(".pt")
        meta_path = path.with_name(path.stem + ".meta.json")

        if not weights_path.exists():
            raise FileNotFoundError(f"Weights file not found: {weights_path}")

        meta: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))

        instance = cls(
            embedding_dim=meta["embedding_dim"],
            num_classes=meta["num_classes"],
            hidden_dim=meta["hidden_dim"],
            dropout=meta.get("dropout", 0.3),
        )
        instance._label_encoder = LabelEncoder()
        instance._label_encoder.classes_ = np.array(meta["label_classes"])

        instance._model = instance._build_model()
        instance._model.load_state_dict(
            torch.load(weights_path, map_location=instance._device, weights_only=True),
        )
        instance._model.eval()
        instance._is_trained = True

        logger.info("Neural model loaded from %s", weights_path)
        return instance

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        status = "trained" if self._is_trained else "untrained"
        return (
            f"NeuralClassifier(embedding_dim={self.embedding_dim}, "
            f"num_classes={self.num_classes}, hidden_dim={self.hidden_dim}, "
            f"{status})"
        )
