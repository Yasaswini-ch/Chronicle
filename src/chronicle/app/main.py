"""Chronicle: Streamlit Web Application Entry Point.

An End-to-End NLP System for Greek Mythology Analysis and Conversational Storytelling.
"""

from __future__ import annotations

import json
from pathlib import Path
import streamlit as st

from chronicle.app.config import MYTHS_JSON, CHARACTER_ALIASES_JSON
from chronicle.app.components.chat_interface import render_chat_interface
from chronicle.app.components.graph_viewer import render_graph_viewer
from chronicle.app.components.dashboard_view import render_dashboard
from chronicle.app.components.explorer_view import render_explorer
from chronicle.app.components.embedding_view import render_embedding_view
from chronicle.app.components.model_view import render_model_view
from chronicle.chatbot.engine import ChatEngine
from chronicle.ner.knowledge_graph import KnowledgeGraph
from chronicle.representation.sbert import SBERTRepresentation


# Configure Streamlit page layout and branding
st.set_page_config(
    page_title="Chronicle: Greek Mythology NLP System",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom High-Level Editorial CSS Theme (No sidebar, no drop shadows, no emojis, no harsh gradients)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

    /* Canvas & Global Typography */
    html, body, [class*="css"] {
        font-family: 'Cormorant Garamond', 'Garamond', Georgia, serif;
        background-color: #141618;
        color: #DCD6CD;
    }

    /* Hide Sidebar Completely */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], div[data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cinzel', 'Palatino Linotype', 'Book Antiqua', Georgia, serif !important;
        letter-spacing: 0.75px;
        font-weight: 600;
        color: #E8E2D8 !important;
    }

    /* Eliminate Drop Shadows & Rounded Bubbles */
    *, [class*="st-"] {
        box-shadow: none !important;
        border-radius: 2px !important;
    }

    /* Top Horizontal Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Cinzel', Georgia, serif !important;
        font-size: 0.82rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        color: #8C94A0 !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
        padding: 10px 18px !important;
        margin-right: 6px !important;
        transition: none !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #E8E2D8 !important;
        border: 1px solid #3B424E !important;
        background-color: #1A1E24 !important;
        border-bottom: 2px solid #C5A059 !important;
    }

    /* Input & Textareas */
    input, textarea, [data-baseweb="input"] {
        background-color: #171A1E !important;
        color: #E8E2D8 !important;
        border: 1px solid #333842 !important;
        font-family: 'Cormorant Garamond', Georgia, serif !important;
        font-size: 1rem !important;
    }

    /* Buttons */
    .stButton button {
        background-color: #1A1E24 !important;
        color: #DCD6CD !important;
        border: 1px solid #3B424E !important;
        font-family: 'Cinzel', Georgia, serif !important;
        font-size: 0.75rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: none !important;
    }

    .stButton button:hover {
        border-color: #C5A059 !important;
        color: #C5A059 !important;
    }

    /* Primary button */
    .stButton button[kind="primary"] {
        background-color: #21262F !important;
        border: 1px solid #C5A059 !important;
        color: #C5A059 !important;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-family: 'Cinzel', Georgia, serif !important;
        color: #E8E2D8 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        color: #8C94A0 !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid #2B2F36 !important;
        background-color: #171A1E !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_corpus() -> list[dict]:
    """Load pre-processed myth corpus from JSON."""
    if MYTHS_JSON.exists():
        with open(MYTHS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@st.cache_resource
def load_sbert():
    """Load SBERT representation model (cached across sessions)."""
    try:
        return SBERTRepresentation()
    except Exception as e:
        st.warning(f"Could not load Sentence-BERT model: {e}")
        return None


@st.cache_resource
def load_knowledge_graph(myths_tuple):
    """Build character knowledge graph from corpus."""
    kg = KnowledgeGraph()
    if myths_tuple:
        kg.build_from_annotations(list(myths_tuple))
    return kg


def render_system_overview(myths: list[dict]):
    """Render the system architecture and corpus provenance overview."""
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown(
            """
            <h3 style="font-size: 1.25rem; color: #E8E2D8; margin-bottom: 0.5rem;">
                System Architecture & Methodology
            </h3>
            <p style="font-size: 1rem; line-height: 1.6; color: #DCD6CD;">
                Chronicle demonstrates an integrated natural language processing lifecycle on classical mythic prose.
                Authentic narratives sourced from Bulfinch's <i>Age of Fable</i>, the Perseus Digital Library,
                and Homeric translations are preprocessed to resolve archaic vocabulary, standardize Greek and Roman
                alias variants, and extract canonical character ties. Dual vector representations
                (sparse TF-IDF n-grams and dense Sentence-BERT contextual embeddings) power supervised classification,
                topological knowledge extraction, and conversational lore retrieval.
            </p>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <h3 style="font-size: 1.25rem; color: #E8E2D8; margin: 1.5rem 0 0.5rem 0;">
                Pipeline Architecture Flow
            </h3>
            <div style="border: 1px solid #2B2F36; background: #171A1E; padding: 16px; font-family: Georgia, serif; font-size: 0.95rem; line-height: 1.8; color: #DCD6CD;">
                <div style="color: #C5A059; font-weight: 600;">Stage 1: Ingestion & Normalization</div>
                Archaic English cleansing, Greek-Roman alias unification, and spaCy lemmatization.
                <div style="color: #C5A059; font-weight: 600; margin-top: 8px;">Stage 2: Dual Vector Geometry</div>
                Sparse TF-IDF n-gram matrices and dense 384-dimensional Sentence-BERT embeddings.
                <div style="color: #C5A059; font-weight: 600; margin-top: 8px;">Stage 3: Inference & Topological Extraction</div>
                Supervised theme classifiers, entity recognizers, and a NetworkX directed knowledge graph.
                <div style="color: #C5A059; font-weight: 600; margin-top: 8px;">Stage 4: Dialogue & Narrative Retrieval</div>
                Conversational intent classification, slot extraction, cosine semantic retrieval, and structured story dossiers.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <h3 style="font-size: 1.25rem; color: #E8E2D8; margin-bottom: 0.5rem;">
                Corpus Metrics & Provenance
            </h3>
            """,
            unsafe_allow_html=True,
        )
        total_myths = len(myths)
        total_words = sum(len(m.get("text", "").split()) for m in myths)
        themes = sorted({m.get("theme") for m in myths if m.get("theme")})
        all_chars = set()
        for m in myths:
            for c in m.get("characters", []):
                name = c.get("name") if isinstance(c, dict) else str(c)
                all_chars.add(name)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f'<div style="border: 1px solid #2B2F36; background: #171A1E; padding: 12px 14px; margin-bottom: 12px;">'
                f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Canonical Myths</div>'
                f'<div style="font-size: 1.4rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{total_myths}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="border: 1px solid #2B2F36; background: #171A1E; padding: 12px 14px;">'
                f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Thematic Classes</div>'
                f'<div style="font-size: 1.4rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{len(themes)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div style="border: 1px solid #2B2F36; background: #171A1E; padding: 12px 14px; margin-bottom: 12px;">'
                f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Corpus Word Count</div>'
                f'<div style="font-size: 1.4rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{total_words:,}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="border: 1px solid #2B2F36; background: #171A1E; padding: 12px 14px;">'
                f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Cataloged Entities</div>'
                f'<div style="font-size: 1.4rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{len(all_chars)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def main():
    """Main application navigation controller."""
    myths = load_corpus()
    sbert = load_sbert()
    kg = load_knowledge_graph(tuple(myths))

    # Initialize chat engine in session state
    if "chat_engine" not in st.session_state:
        st.session_state.chat_engine = ChatEngine(
            myths=myths,
            sbert_model=sbert,
            knowledge_graph=kg,
        )

    # Site Header: Elegant title banner with quick corpus telemetry
    total_words = sum(len(m.get("text", "").split()) for m in myths)
    st.markdown(
        f"""
        <div style="border-bottom: 1px solid #2B2F36; padding: 0.75rem 0 0.85rem 0; margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: baseline;">
            <div>
                <span style="font-family: 'Cinzel', Georgia, serif; font-size: 1.7rem; font-weight: 700; color: #E8E2D8; letter-spacing: 1.5px;">CHRONICLE</span>
                <span style="font-size: 0.9rem; color: #8C94A0; margin-left: 14px; letter-spacing: 0.5px;">Greek Mythology Natural Language Processing Architecture</span>
            </div>
            <div style="font-size: 0.75rem; color: #C5A059; letter-spacing: 1.2px; text-transform: uppercase;">
                {len(myths)} Narratives &bull; {total_words:,} Words &bull; {len({m.get('theme') for m in myths if m.get('theme')})} Themes
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Logical Top Navigation: Ordered by storytelling and exploration workflow
    tab_anthology, tab_oracle, tab_network, tab_themes, tab_geometry, tab_models, tab_architecture = st.tabs([
        "Myth Anthology",
        "Oracle Dialogue",
        "Pantheon Network",
        "Thematic Landscape",
        "Semantic Space",
        "Model Benchmarks",
        "System Architecture",
    ])

    with tab_anthology:
        render_explorer(myths, retriever=st.session_state.chat_engine.retriever)

    with tab_oracle:
        render_chat_interface(st.session_state.chat_engine)

    with tab_network:
        render_graph_viewer(kg, myths)

    with tab_themes:
        render_dashboard(myths)

    with tab_geometry:
        render_embedding_view(myths, sbert=sbert)

    with tab_models:
        render_model_view(myths, sbert=sbert)

    with tab_architecture:
        render_system_overview(myths)


if __name__ == "__main__":
    main()
