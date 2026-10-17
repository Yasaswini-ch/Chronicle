"""Corpus explorer component: immersive myth reading room and archive."""

from __future__ import annotations

import streamlit as st
from chronicle.app.components.story_card import render_story_card


def render_explorer(myths: list[dict], retriever=None) -> None:
    """Render an interactive master-detail myth reading room and archive."""
    st.markdown(
        '<div style="margin-bottom: 1.5rem;">'
        '<h2 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; margin-bottom: 0.25rem;">Myth Anthology & Reading Room</h2>'
        '<p style="color: #9BA3AF; font-size: 0.95rem; font-family: Georgia, serif;">'
        'Immerse in unabridged retellings from Bulfinch, Perseus, and Homeric traditions with structured narrative analytics.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    if not myths:
        st.warning("No myth records found in corpus.")
        return

    # Master-detail layout
    col_nav, col_read = st.columns([1, 2], gap="large")

    with col_nav:
        st.markdown(
            '<div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; '
            'color: #C5A059; margin-bottom: 8px; font-weight: 600;">Archive Index</div>',
            unsafe_allow_html=True,
        )

        all_themes = sorted({m.get("theme", "unknown") for m in myths})
        selected_theme = st.selectbox("Theme Filter", ["All Themes"] + all_themes, label_visibility="collapsed")
        search_query = st.text_input("Search Title or Character", "", placeholder="Filter by keyword...", label_visibility="collapsed")

        filtered = myths
        if selected_theme != "All Themes":
            filtered = [m for m in filtered if m.get("theme") == selected_theme]

        if search_query.strip():
            q = search_query.strip().lower()
            filtered = [
                m for m in filtered
                if q in m.get("title", "").lower()
                or any(q in (c.get("name", "") if isinstance(c, dict) else str(c)).lower() for c in m.get("characters", []))
                or q in m.get("text", "").lower()
            ]

        st.caption(f"Showing {len(filtered)} of {len(myths)} narratives")

        titles = [m.get("title", f"Myth {i}") for i, m in enumerate(filtered)]
        if not titles:
            st.info("No narratives match your query.")
            return

        # Radio or selectbox for active myth
        default_index = 0
        if "selected_myth_title" in st.session_state and st.session_state.selected_myth_title in titles:
            default_index = titles.index(st.session_state.selected_myth_title)

        selected_title = st.radio(
            "Select Narrative",
            titles,
            index=default_index,
            label_visibility="collapsed",
        )

    # Locate chosen myth
    chosen_myth = next((m for m in filtered if m.get("title") == selected_title), filtered[0])

    with col_read:
        render_story_card(chosen_myth)

        # Semantically Related Narratives
        if retriever is not None:
            st.markdown(
                '<h4 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
                'color: #E8E2D8; font-size: 1.1rem; margin: 1.5rem 0 0.5rem 0;">'
                'Semantically Related Narratives</h4>',
                unsafe_allow_html=True,
            )
            similar = retriever.retrieve_similar(chosen_myth.get("title", ""), top_k=3)
            if similar:
                for sim in similar:
                    sim_title = sim.get("title", "Untitled")
                    sim_theme = sim.get("theme", "myth")
                    sim_moral = sim.get("moral") or (sim.get("text", "")[:120] + "...")
                    st.markdown(
                        f'<div style="border-left: 2px solid #333842; padding: 4px 10px; margin-bottom: 8px; background: #171A1E;">'
                        f'<span style="color: #E8E2D8; font-weight: 600;">{sim_title}</span> '
                        f'<span style="font-size: 0.75rem; color: #8C94A0; text-transform: uppercase;">[{sim_theme}]</span><br>'
                        f'<span style="font-size: 0.85rem; color: #B5AFA6; font-family: Georgia, serif;">{sim_moral}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
