"""Corpus insights and analytics dashboard component for Streamlit."""

from __future__ import annotations

import streamlit as st
from chronicle.insights.dashboard import InsightsDashboard


def _apply_theme(fig):
    """Apply consistent classical editorial dark styling to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(24, 27, 31, 0.6)",
        plot_bgcolor="rgba(24, 27, 31, 0.4)",
        font=dict(family="Georgia, serif", color="#DCD6CD"),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def render_dashboard(myths: list[dict]) -> None:
    """Render the corpus analytics dashboard."""
    st.markdown(
        '<div style="margin-bottom: 1.5rem;">'
        '<h2 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; margin-bottom: 0.25rem;">Corpus Thematic & Entity Analytics</h2>'
        '<p style="color: #9BA3AF; font-size: 0.95rem; font-family: Georgia, serif;">'
        'Statistical distribution of thematic motifs, character centralities, and lexical density across the classical canon.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    if not myths:
        st.warning("No myth records available.")
        return

    dashboard = InsightsDashboard()

    # Telemetry metrics bar (2x2 layout)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f'<div style="border: 1px solid #2B2F36; background: #1A1D21; padding: 12px 16px; margin-bottom: 12px;">'
            f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Corpus Volume</div>'
            f'<div style="font-size: 1.5rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{len(myths)} Narratives '
            f'<span style="font-size: 0.9rem; color: #8C94A0; font-weight: normal;">({sum(len(m.get("text", "").split()) for m in myths):,} words)</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        unique_themes = len({m.get("theme") for m in myths if m.get("theme")})
        all_chars = set()
        for m in myths:
            for c in m.get("characters", []):
                name = c.get("name") if isinstance(c, dict) else str(c)
                all_chars.add(name)
        st.markdown(
            f'<div style="border: 1px solid #2B2F36; background: #1A1D21; padding: 12px 16px; margin-bottom: 12px;">'
            f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #8C94A0;">Diversity Scope</div>'
            f'<div style="font-size: 1.5rem; font-family: Georgia, serif; color: #E8E2D8; font-weight: 600;">{unique_themes} Thematic Classes '
            f'<span style="font-size: 0.9rem; color: #8C94A0; font-weight: normal;">({len(all_chars)} extracted mythological figures)</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border: none; border-top: 1px solid #2B2F36; margin: 16px 0 24px 0;">', unsafe_allow_html=True)

    # Derived Pantheon Prominence Section (2x2 layout, no three-in-a-row)
    stats = dashboard.get_leaderboard_stats(myths)
    st.markdown(
        '<h3 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; font-size: 1.2rem; margin-bottom: 1rem;">Pantheon Prominence & Network Centrality</h3>',
        unsafe_allow_html=True,
    )

    p1, p2 = st.columns(2)
    most_m = stats["most_mentioned"]
    most_c = stats["most_connected"]
    most_d = stats["most_thematic_diversity"]

    with p1:
        st.markdown(
            f'<div style="border: 1px solid #333842; background: #171A1E; padding: 14px 18px; margin-bottom: 12px;">'
            f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.2px; color: #C5A059;">Most Frequent Figure</div>'
            f'<div style="font-size: 1.3rem; font-family: Georgia, serif; color: #E8E2D8; margin-top: 4px;">{most_m["character"]}</div>'
            f'<div style="font-size: 0.85rem; color: #8C94A0; margin-top: 2px;">Appears across {most_m["count"]} classical narratives</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="border: 1px solid #333842; background: #171A1E; padding: 14px 18px;">'
            f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.2px; color: #C5A059;">Highest Thematic Breadth</div>'
            f'<div style="font-size: 1.3rem; font-family: Georgia, serif; color: #E8E2D8; margin-top: 4px;">{most_d["character"]}</div>'
            f'<div style="font-size: 0.85rem; color: #8C94A0; margin-top: 2px;">Spans {most_d["num_themes"]} distinct themes: {", ".join(most_d["themes"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            f'<div style="border: 1px solid #333842; background: #171A1E; padding: 14px 18px; margin-bottom: 12px;">'
            f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.2px; color: #C5A059;">Most Connected Node</div>'
            f'<div style="font-size: 1.3rem; font-family: Georgia, serif; color: #E8E2D8; margin-top: 4px;">{most_c["character"]}</div>'
            f'<div style="font-size: 0.85rem; color: #8C94A0; margin-top: 2px;">{most_c["connections"]} cataloged genealogical and adversarial ties</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        avg_len = int(sum(len(m.get("text", "").split()) for m in myths) / len(myths)) if myths else 0
        st.markdown(
            f'<div style="border: 1px solid #333842; background: #171A1E; padding: 14px 18px;">'
            f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.2px; color: #C5A059;">Average Narrative Length</div>'
            f'<div style="font-size: 1.3rem; font-family: Georgia, serif; color: #E8E2D8; margin-top: 4px;">{avg_len} Words / Myth</div>'
            f'<div style="font-size: 0.85rem; color: #8C94A0; margin-top: 2px;">Rich, continuous prose retellings from classical anthologies</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border: none; border-top: 1px solid #2B2F36; margin: 24px 0;">', unsafe_allow_html=True)

    # Charts Section
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(
            '<h4 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
            'color: #E8E2D8; margin-bottom: 0.5rem;">Thematic Share & Frequency</h4>',
            unsafe_allow_html=True,
        )
        theme_fig = _apply_theme(dashboard.theme_distribution(myths))
        st.plotly_chart(theme_fig, use_container_width=True)

    with col_right:
        st.markdown(
            '<h4 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
            'color: #E8E2D8; margin-bottom: 0.5rem;">Character Mention Rankings</h4>',
            unsafe_allow_html=True,
        )
        char_fig = _apply_theme(dashboard.character_leaderboard(myths, top_n=12))
        st.plotly_chart(char_fig, use_container_width=True)

    st.markdown('<hr style="border: none; border-top: 1px solid #2B2F36; margin: 24px 0;">', unsafe_allow_html=True)

    st.markdown(
        '<h4 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; margin-bottom: 0.5rem;">Thematic-Character Co-occurrence Matrix</h4>',
        unsafe_allow_html=True,
    )
    heatmap_fig = _apply_theme(dashboard.theme_character_heatmap(myths))
    st.plotly_chart(heatmap_fig, use_container_width=True)
