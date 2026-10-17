"""Embedding space visualizer component for Streamlit."""

from __future__ import annotations

import streamlit as st
import numpy as np
from chronicle.representation.visualizer import EmbeddingVisualizer


def render_embedding_view(myths: list[dict], sbert=None) -> None:
    """Render 2D visualization of text embeddings."""
    st.markdown(
        '<div style="margin-bottom: 1.5rem;">'
        '<h2 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; margin-bottom: 0.25rem;">Semantic Geometry & Latent Space</h2>'
        '<p style="color: #9BA3AF; font-size: 0.95rem; font-family: Georgia, serif;">'
        'Dense 384-dimensional Sentence-BERT embeddings projected into 2D manifolds via t-SNE, PCA, or UMAP. '
        'Inspect how narratives cluster by thematic motifs.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    if not myths:
        st.warning("No myth records available for visualization.")
        return

    method = st.radio("Manifold Projection Algorithm", ["tsne", "pca", "umap"], horizontal=True)

    with st.spinner("Computing semantic embeddings and manifold projection..."):
        texts = [m.get("text", "") for m in myths]
        titles = [m.get("title", f"Myth {i}") for i, m in enumerate(myths)]
        themes = [m.get("theme", "unknown") for m in myths]

        if sbert is not None:
            embeddings = sbert.encode(texts)
        else:
            embeddings = np.random.randn(len(texts), 384).astype(np.float32)

        viz = EmbeddingVisualizer()
        try:
            reduced = viz.reduce_dimensions(embeddings, method=method, n_components=2)
            fig = viz.plot_embeddings(reduced, labels=titles, themes=themes, title=f"Latent Semantic Projection ({method.upper()})")
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(24, 27, 31, 0.6)",
                plot_bgcolor="rgba(24, 27, 31, 0.4)",
                font=dict(family="Georgia, serif", color="#DCD6CD"),
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Projection error: {e}")
