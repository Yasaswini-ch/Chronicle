"""Story card component: renders a rich myth detail card in Streamlit."""

from __future__ import annotations

import json
import re
from typing import Any

import streamlit as st

from chronicle.app.config import CHARACTER_ICONS, THEME_COLORS


def _theme_badge(theme: str) -> str:
    """Return an HTML badge for theme using the configured palette."""
    colour = THEME_COLORS.get(theme.lower(), "#4A5568")
    return (
        f'<span style="border: 1px solid {colour}; color: #E8E2D8; '
        f'padding: 2px 10px; font-size: 0.75rem; text-transform: uppercase; '
        f'letter-spacing: 1.5px; font-weight: 600; background: rgba(0,0,0,0.2);">'
        f"{theme}</span>"
    )


def _character_chip(name: str, char_type: str) -> str:
    """Return a styled text chip for a character with entity classification."""
    type_label = CHARACTER_ICONS.get(char_type.lower(), char_type.upper() if char_type else "FIGURE")
    return (
        f'<span style="display: inline-block; border: 1px solid #333842; '
        f'background: #1A1D21; padding: 2px 8px; margin: 2px 6px 4px 0; '
        f'font-size: 0.8rem; color: #DCD6CD; letter-spacing: 0.5px;">'
        f'{name} <span style="color: #8C94A0; font-size: 0.7rem; font-weight: 600;">[{type_label}]</span></span>'
    )


def render_story_card(myth: dict[str, Any]) -> None:
    """Render an editorial story card and structured lore dossier for a myth.

    Parameters
    ----------
    myth : dict
        Myth record containing title, theme, text, characters, relationships,
        moral, source, locations, artifacts.
    """
    title: str = myth.get("title", "Untitled Myth")
    theme: str = myth.get("theme", "mythology")
    text: str = myth.get("text", "")
    characters: list[dict[str, str]] | list[str] = myth.get("characters", [])
    relationships: list[dict[str, str]] = myth.get("relationships", [])
    moral: str = myth.get("moral", "")
    source: str = myth.get("source", "")
    locations: list[str] = myth.get("locations", [])
    artifacts: list[str] = myth.get("artifacts", [])

    char_names = [
        c.get("name") if isinstance(c, dict) else str(c)
        for c in characters
    ]

    # Format relationship snippet
    rel_snippet = myth.get("relationship_snippet")
    if not rel_snippet and relationships:
        snippets = [
            f"{r.get('source')} ({r.get('relation', 'related to').replace('_', ' ')}) {r.get('target')}"
            for r in relationships[:3]
        ]
        rel_snippet = "; ".join(snippets)

    summary_text = moral if moral else (text[:160] + "..." if text else "Classical Greek narrative.")

    with st.container():
        st.markdown(
            f'<div style="display: flex; justify-content: space-between; align-items: baseline; '
            f'border-bottom: 1px solid #2B2F36; padding-bottom: 8px; margin-bottom: 12px;">'
            f'<span style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
            f'font-size: 1.25rem; font-weight: 600; color: #E8E2D8;">{title}</span>'
            f'{_theme_badge(theme)}'
            f'</div>',
            unsafe_allow_html=True,
        )

        if characters:
            chips = "".join(
                _character_chip(
                    c.get("name", "?") if isinstance(c, dict) else str(c),
                    c.get("type", "") if isinstance(c, dict) else "",
                )
                for c in characters
            )
            st.markdown(
                f'<div style="margin: 4px 0 12px 0;">{chips}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div style="border-left: 2px solid #8B2635; padding: 6px 12px; margin-bottom: 12px; '
            f'background: #171A1E; color: #DCD6CD; font-family: Georgia, serif; font-style: italic;">'
            f'<b>Moral & Core Insight:</b> {summary_text}'
            f'</div>',
            unsafe_allow_html=True,
        )

        if rel_snippet:
            st.markdown(f"**Tracked Relationships:** `{rel_snippet}`")

        with st.expander("Full Narrative Text", expanded=False):
            st.markdown(
                f'<div style="font-family: Garamond, Georgia, serif; font-size: 1.05rem; '
                f'line-height: 1.6; color: #DCD6CD;">{text}</div>',
                unsafe_allow_html=True,
            )

        col1, col2 = st.columns(2)
        with col1:
            if source:
                st.markdown(f"**Source Provenance:** {source}")
            if locations:
                st.markdown(f"**Canonical Locations:** {', '.join(locations)}")
        with col2:
            if artifacts:
                st.markdown(f"**Relics & Artifacts:** {', '.join(artifacts)}")
            if relationships:
                st.markdown(f"**Graph Links:** {len(relationships)} cataloged connection(s)")

        if relationships:
            with st.expander("All Genealogical & Mythic Ties", expanded=False):
                for rel in relationships:
                    src = rel.get("source", "?")
                    tgt = rel.get("target", "?")
                    relation = rel.get("relation", "related_to").replace("_", " ")
                    st.markdown(f"- **{src}** -> *{relation}* -> **{tgt}**")

        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "story_card"
        card_data = {
            "title": title,
            "theme": theme,
            "characters": char_names,
            "summary": summary_text,
            "relationship_snippet": rel_snippet or "None",
            "relationships": relationships,
            "moral": moral,
            "source": source,
            "locations": locations,
            "artifacts": artifacts,
            "text": text,
        }

        md_export = f"""# {title}
Theme: {theme.capitalize()}
Characters: {', '.join(char_names)}
Summary: {summary_text}
Relationships: {rel_snippet or 'None'}
Locations: {', '.join(locations) if locations else 'None'}
Artifacts: {', '.join(artifacts) if artifacts else 'None'}

## Narrative
{text}
"""

        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button(
                label="Export Dossier (JSON)",
                data=json.dumps(card_data, indent=2),
                file_name=f"{slug}_dossier.json",
                mime="application/json",
                key=f"dl_json_{slug}",
                use_container_width=True,
            )
        with c_exp2:
            st.download_button(
                label="Export Story (Markdown)",
                data=md_export,
                file_name=f"{slug}_story.md",
                mime="text/markdown",
                key=f"dl_md_{slug}",
                use_container_width=True,
            )

        st.markdown(
            '<hr style="border: none; border-top: 1px solid #2B2F36; margin: 16px 0;">',
            unsafe_allow_html=True,
        )
