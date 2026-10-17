"""Knowledge graph viewer component for Streamlit."""

from __future__ import annotations

import streamlit as st


def render_graph_viewer(knowledge_graph, myths: list[dict]) -> None:
    """Render the interactive character knowledge graph viewer."""
    st.markdown(
        '<div style="margin-bottom: 1.5rem;">'
        '<h2 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; margin-bottom: 0.25rem;">Pantheon Relational Knowledge Graph</h2>'
        '<p style="color: #9BA3AF; font-size: 0.95rem; font-family: Georgia, serif;">'
        'Explore genealogical, mentorship, and adversarial ties among Greek deities, heroes, and creatures extracted directly from the corpus.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    stats = knowledge_graph.statistics()
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown(
            f'<div style="border: 1px solid #2B2F36; background: #1A1D21; padding: 10px 16px; margin-bottom: 12px;">'
            f'<span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Entities Cataloged</span><br>'
            f'<span style="font-size: 1.3rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{stats.get("num_nodes", 0)} Figures</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with g_col2:
        st.markdown(
            f'<div style="border: 1px solid #2B2F36; background: #1A1D21; padding: 10px 16px; margin-bottom: 12px;">'
            f'<span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Graph Connectivity</span><br>'
            f'<span style="font-size: 1.3rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{stats.get("num_edges", 0)} Relationships '
            f'<small style="font-size: 0.85rem; color: #8C94A0;">(Density: {stats.get("density", 0.0):.3f})</small></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    tab_vis, tab_path, tab_char = st.tabs(["Network Canvas", "Connection Path Tracer", "Entity Profile Dossier"])

    with tab_vis:
        fig = knowledge_graph.visualize()
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(24, 27, 31, 0.6)",
            plot_bgcolor="rgba(24, 27, 31, 0.4)",
            font=dict(family="Georgia, serif", color="#DCD6CD"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_path:
        st.markdown(
            '<h4 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
            'color: #E8E2D8; margin: 1rem 0 0.5rem 0;">Shortest Path Between Figures</h4>',
            unsafe_allow_html=True,
        )
        characters = sorted(knowledge_graph.characters)
        if len(characters) >= 2:
            pcol1, pcol2 = st.columns(2)
            c1_sel = pcol1.selectbox("Origin Figure", characters, index=0)
            c2_sel = pcol2.selectbox("Destination Figure", characters, index=min(1, len(characters) - 1))

            if st.button("Trace Relational Path", key="btn_trace_path"):
                path = knowledge_graph.find_path(c1_sel, c2_sel)
                if path:
                    st.markdown(
                        f'<div style="border-left: 2px solid #2C5E7A; background: #171A1E; padding: 10px 14px; margin-top: 8px; color: #E8E2D8;">'
                        f'<b>Genealogical Path:</b> {" -> ".join(path)}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info(f"No direct genealogical path cataloged between {c1_sel} and {c2_sel}.")

    with tab_char:
        st.markdown(
            '<h4 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
            'color: #E8E2D8; margin: 1rem 0 0.5rem 0;">Character Entity Dossier</h4>',
            unsafe_allow_html=True,
        )
        char_sel = st.selectbox("Inspect Figure", sorted(knowledge_graph.characters))
        if char_sel:
            info = knowledge_graph.get_character_info(char_sel)
            st.markdown(
                f'<div style="border: 1px solid #333842; background: #171A1E; padding: 14px 18px; margin-top: 8px;">'
                f'<div style="font-size: 1.2rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{char_sel}</div>'
                f'<div style="font-size: 0.85rem; color: #8C94A0; margin-top: 2px;">Classification: {info.get("type", "Unknown").upper()} | Network Degree: {info.get("degree", 0)}</div>'
                f'<hr style="border: none; border-top: 1px solid #2B2F36; margin: 10px 0;">'
                f'<div style="font-size: 0.9rem; color: #DCD6CD;"><b>Narratives Featured:</b> {", ".join(info.get("myths", [])) or "None cataloged"}</div>'
                f'<div style="font-size: 0.9rem; color: #DCD6CD; margin-top: 4px;"><b>Direct Associates:</b> {", ".join(knowledge_graph.get_neighbors(char_sel)) or "None cataloged"}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
