"""Embedding visualisation utilities for Chronicle.

Reduces high-dimensional embeddings to 2-D / 3-D with t-SNE or UMAP,
then produces interactive Plotly scatter plots colour-coded by theme.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from numpy.typing import NDArray
from sklearn.manifold import TSNE

logger = logging.getLogger(__name__)

# UMAP is optional — imported lazily so the rest of the module works
# even when umap-learn is not installed.
_UMAP_AVAILABLE: bool
try:
    import umap  # noqa: F401

    _UMAP_AVAILABLE = True
except ModuleNotFoundError:
    _UMAP_AVAILABLE = False


class EmbeddingVisualizer:
    """Reduce dimensionality and create interactive embedding plots.

    All methods are stateless — the class groups related functionality
    but does not hold mutable state between calls.
    """

    # ------------------------------------------------------------------
    # Dimensionality reduction
    # ------------------------------------------------------------------

    @staticmethod
    def reduce_dimensions(
        embeddings: NDArray[np.float32],
        method: Literal["tsne", "umap"] = "tsne",
        n_components: int = 2,
        perplexity: float = 10.0,
        random_state: int = 42,
        **kwargs,
    ) -> NDArray[np.float32]:
        """Project *embeddings* down to *n_components* dimensions.

        Parameters
        ----------
        embeddings : np.ndarray
            Input matrix of shape ``(n_samples, n_features)``.
        method : ``"tsne"`` | ``"umap"``
            Reduction algorithm.
        n_components : int
            Target dimensionality (typically 2 or 3).
        perplexity : float
            t-SNE perplexity.  Automatically clamped to
            ``n_samples - 1`` when the corpus is small.
        random_state : int
            Seed for reproducibility.
        **kwargs
            Extra keyword arguments forwarded to the underlying reducer.

        Returns
        -------
        np.ndarray
            Reduced coordinates of shape ``(n_samples, n_components)``.
        """
        n_samples = embeddings.shape[0]
        if n_samples < 2:
            raise ValueError("Need at least 2 samples for dimensionality reduction.")

        method = method.lower()  # type: ignore[assignment]

        if method == "tsne":
            # Perplexity must be < n_samples
            effective_perplexity = min(perplexity, n_samples - 1)
            if effective_perplexity != perplexity:
                logger.warning(
                    "Clamped t-SNE perplexity from %.1f to %.1f (n_samples=%d)",
                    perplexity,
                    effective_perplexity,
                    n_samples,
                )
            reducer = TSNE(
                n_components=n_components,
                perplexity=effective_perplexity,
                random_state=random_state,
                init="pca" if embeddings.shape[1] >= n_components else "random",
                **kwargs,
            )
            reduced = reducer.fit_transform(embeddings)

        elif method == "umap":
            if not _UMAP_AVAILABLE:
                raise ImportError(
                    "umap-learn is required for UMAP reduction.  "
                    "Install it with: pip install umap-learn"
                )
            effective_n_neighbors = min(kwargs.pop("n_neighbors", 15), n_samples - 1)
            reducer = umap.UMAP(  # type: ignore[union-attr]
                n_components=n_components,
                n_neighbors=effective_n_neighbors,
                random_state=random_state,
                **kwargs,
            )
            reduced = reducer.fit_transform(embeddings)

        else:
            raise ValueError(f"Unknown reduction method '{method}'. Use 'tsne' or 'umap'.")

        logger.info(
            "Reduced embeddings %s -> %s with %s",
            embeddings.shape,
            reduced.shape,
            method.upper(),
        )
        return reduced.astype(np.float32)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    @staticmethod
    def plot_embeddings(
        reduced: NDArray[np.float32],
        labels: list[str],
        themes: list[str] | None = None,
        title: str = "Myth Embedding Space",
        width: int = 900,
        height: int = 650,
    ) -> go.Figure:
        """Create an interactive Plotly scatter of the embedding space.

        Parameters
        ----------
        reduced : np.ndarray
            2-D or 3-D coordinates of shape ``(n, 2)`` or ``(n, 3)``.
        labels : list[str]
            Display labels for each point (e.g. myth titles).
        themes : list[str] | None
            Optional category for colour-coding each point.
        title : str
            Plot title.
        width, height : int
            Figure dimensions in pixels.

        Returns
        -------
        plotly.graph_objects.Figure
            Interactive Plotly figure.
        """
        n_points, n_dims = reduced.shape
        if len(labels) != n_points:
            raise ValueError(
                f"labels length ({len(labels)}) must match "
                f"reduced rows ({n_points})"
            )

        if themes is not None and len(themes) != n_points:
            raise ValueError(
                f"themes length ({len(themes)}) must match "
                f"reduced rows ({n_points})"
            )

        # Build a data dict understood by Plotly Express
        data: dict[str, list] = {
            "x": reduced[:, 0].tolist(),
            "y": reduced[:, 1].tolist(),
            "Myth": labels,
        }
        if themes is not None:
            data["Theme"] = themes

        if n_dims == 3:
            data["z"] = reduced[:, 2].tolist()

        hover_template = "<b>%{customdata[0]}</b><extra></extra>"

        if n_dims == 3:
            fig = px.scatter_3d(
                data,
                x="x",
                y="y",
                z="z",
                color="Theme" if themes is not None else None,
                hover_name="Myth",
                title=title,
                width=width,
                height=height,
            )
        else:
            fig = px.scatter(
                data,
                x="x",
                y="y",
                color="Theme" if themes is not None else None,
                hover_name="Myth",
                title=title,
                width=width,
                height=height,
            )

        # Aesthetic tweaks
        fig.update_traces(
            marker=dict(size=10, opacity=0.85, line=dict(width=1, color="white")),
            customdata=np.array(labels).reshape(-1, 1),
            hovertemplate=hover_template,
        )
        fig.update_layout(
            template="plotly_white",
            legend_title_text="Theme" if themes is not None else "",
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            font=dict(family="Inter, sans-serif", size=12),
        )

        logger.info("Created embedding plot '%s' with %d points", title, n_points)
        return fig

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    @staticmethod
    def save_plot(fig: go.Figure, path: str | Path) -> None:
        """Save a Plotly figure as a self-contained HTML file.

        Parameters
        ----------
        fig : plotly.graph_objects.Figure
            The figure to save.
        path : str | Path
            Destination HTML file path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(path), include_plotlyjs="cdn")
        logger.info("Saved plot to %s", path)
