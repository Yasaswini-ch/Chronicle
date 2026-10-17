"""Interactive dashboards for myth corpus insights.

``InsightsDashboard`` generates Plotly figures that summarise theme
distributions, character prominence, theme–character associations, and myth
length statistics.  The figures can be displayed in Streamlit, Jupyter, or
exported as standalone HTML.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from typing import Any

import numpy as np
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flatten_field(
    myths: list[dict[str, Any]],
    field: str,
) -> list[str]:
    """Collect all values from a list-valued or string *field* across myths."""
    items: list[str] = []
    for myth in myths:
        value = myth.get(field)
        if value is None and field in ("themes", "theme"):
            value = myth.get("theme") if field == "themes" else myth.get("themes")
        if isinstance(value, list):
            for v in value:
                if isinstance(v, dict) and "name" in v:
                    items.append(str(v["name"]))
                else:
                    items.append(str(v))
        elif isinstance(value, str):
            items.append(value)
        elif isinstance(value, dict) and "name" in value:
            items.append(str(value["name"]))
    return items


def _count_field(
    myths: list[dict[str, Any]],
    field: str,
) -> Counter[str]:
    """Return a ``Counter`` of values in *field* across all myths."""
    return Counter(_flatten_field(myths, field))


# ---------------------------------------------------------------------------
# InsightsDashboard
# ---------------------------------------------------------------------------

class InsightsDashboard:
    """Generate Plotly charts from a corpus of annotated myth dictionaries.

    Expected dictionary keys used by the various methods:

    * ``themes`` — list[str] of thematic labels (e.g. ``["hubris", "fate"]``)
    * ``characters`` — list[str] of character names
    * ``text`` — full narrative text

    All methods are **static-style** (no mutable state), but kept as instance
    methods so the class can be extended or configured in the future.

    Examples
    --------
    >>> dash = InsightsDashboard()
    >>> myths = [
    ...     {"themes": ["fate", "hubris"], "characters": ["Oedipus"], "text": "Long ago…"},
    ... ]
    >>> fig = dash.theme_distribution(myths)
    """

    # ------------------------------------------------------------------
    # Theme distribution
    # ------------------------------------------------------------------

    def theme_distribution(self, myths: list[dict[str, Any]]) -> go.Figure:
        """Pie / bar chart of theme frequencies across the corpus.

        Parameters
        ----------
        myths : list[dict]
            Corpus dictionaries with a ``'themes'`` key.

        Returns
        -------
        plotly.graph_objects.Figure
            A figure containing both a pie chart and a horizontal bar chart
            as two subplots side-by-side.
        """
        counts = _count_field(myths, "themes")
        if not counts:
            return _empty_figure("No theme data available")

        sorted_items = counts.most_common()
        labels = [label for label, _ in sorted_items]
        values = [count for _, count in sorted_items]

        from plotly.subplots import make_subplots  # type: ignore[import-untyped]

        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "pie"}, {"type": "bar"}]],
            subplot_titles=("Theme Share", "Theme Counts"),
        )

        # Pie chart
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                textinfo="label+percent",
                hole=0.35,
                marker=dict(line=dict(color="white", width=1)),
            ),
            row=1,
            col=1,
        )

        # Horizontal bar chart
        fig.add_trace(
            go.Bar(
                y=labels[::-1],
                x=values[::-1],
                orientation="h",
                marker_color="#AB63FA",
                text=values[::-1],
                textposition="outside",
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title_text="Theme Distribution Across Myths",
            showlegend=False,
            template="plotly_white",
            width=1100,
            height=550,
        )
        return fig

    # ------------------------------------------------------------------
    # Character leaderboard
    # ------------------------------------------------------------------

    def character_leaderboard(
        self,
        myths: list[dict[str, Any]],
        top_n: int = 15,
    ) -> go.Figure:
        """Horizontal bar chart of the *top_n* most-mentioned characters.

        Parameters
        ----------
        myths : list[dict]
            Corpus dictionaries with a ``'characters'`` key.
        top_n : int
            Number of characters to display.

        Returns
        -------
        plotly.graph_objects.Figure
        """
        counts = _count_field(myths, "characters")
        if not counts:
            return _empty_figure("No character data available")

        top = counts.most_common(top_n)
        names = [n for n, _ in top][::-1]
        values = [c for _, c in top][::-1]

        # Colour gradient by rank
        colours = [
            f"rgba(99, 110, 250, {0.4 + 0.6 * i / max(len(names) - 1, 1)})"
            for i in range(len(names))
        ]

        fig = go.Figure(
            data=go.Bar(
                y=names,
                x=values,
                orientation="h",
                marker_color=colours,
                text=values,
                textposition="outside",
                hovertemplate="<b>%{y}</b>: %{x} appearances<extra></extra>",
            )
        )
        fig.update_layout(
            title=f"Top {top_n} Characters by Mention Frequency",
            xaxis_title="Appearances",
            yaxis_title="",
            template="plotly_white",
            width=800,
            height=max(400, top_n * 30),
            margin=dict(l=140),
        )
        return fig

    def get_leaderboard_stats(
        self,
        myths: list[dict[str, Any]],
        knowledge_graph: Any = None,
        top_n: int = 10,
    ) -> dict[str, Any]:
        """Compute derived character leaderboard statistics.

        Calculates:
        1. Most-mentioned character across myth texts and annotations.
        2. Most-connected character (highest degree in knowledge graph/relationships).
        3. Character appearing across the most distinct themes.

        Parameters
        ----------
        myths : list[dict[str, Any]]
            List of myth dictionaries.
        knowledge_graph : Any, optional
            KnowledgeGraph instance or NetworkX DiGraph.
        top_n : int
            Number of top characters to return in the summary list.

        Returns
        -------
        dict[str, Any]
            Dictionary containing derived stats and leaderboard.
        """
        char_mentions: Counter[str] = Counter()
        char_themes: dict[str, set[str]] = defaultdict(set)
        char_connections: Counter[str] = Counter()

        for myth in myths:
            theme_val = myth.get("theme") or myth.get("themes")
            theme_list: list[str] = []
            if isinstance(theme_val, list):
                theme_list = [str(t) for t in theme_val]
            elif isinstance(theme_val, str) and theme_val:
                theme_list = [theme_val]

            myth_chars: list[str] = []
            raw_chars = myth.get("characters", [])
            if isinstance(raw_chars, list):
                for c in raw_chars:
                    if isinstance(c, dict) and "name" in c:
                        myth_chars.append(str(c["name"]))
                    elif isinstance(c, str):
                        myth_chars.append(c)
            elif isinstance(raw_chars, str):
                myth_chars.append(raw_chars)

            for char in myth_chars:
                char_mentions[char] += 1
                for t in theme_list:
                    char_themes[char].add(t)

            for rel in myth.get("relationships", []):
                src = rel.get("source")
                tgt = rel.get("target")
                if src:
                    char_connections[src] += 1
                if tgt:
                    char_connections[tgt] += 1

        # Check knowledge graph degree if provided
        if knowledge_graph is not None:
            if hasattr(knowledge_graph, "nodes"):
                for node in knowledge_graph.nodes():
                    deg = int(knowledge_graph.degree(node))
                    char_connections[str(node)] = max(char_connections[str(node)], deg)
            elif hasattr(knowledge_graph, "_graph"):
                for node in knowledge_graph._graph.nodes():
                    deg = int(knowledge_graph._graph.degree(node))
                    char_connections[str(node)] = max(char_connections[str(node)], deg)

        most_mentioned = {"character": "None", "count": 0}
        if char_mentions:
            name, count = char_mentions.most_common(1)[0]
            most_mentioned = {"character": name, "count": count}

        most_connected = {"character": "None", "connections": 0}
        if char_connections:
            name, conns = char_connections.most_common(1)[0]
            most_connected = {"character": name, "connections": conns}

        most_thematic_diversity = {"character": "None", "num_themes": 0, "themes": []}
        if char_themes:
            sorted_by_theme = sorted(
                char_themes.items(),
                key=lambda x: (len(x[1]), char_mentions[x[0]]),
                reverse=True,
            )
            name, themes_set = sorted_by_theme[0]
            most_thematic_diversity = {
                "character": name,
                "num_themes": len(themes_set),
                "themes": sorted(list(themes_set)),
            }

        # Build combined leaderboard list
        all_chars = set(char_mentions.keys()) | set(char_connections.keys())
        leaderboard = []
        for char in all_chars:
            leaderboard.append({
                "character": char,
                "mentions": char_mentions.get(char, 0),
                "connections": char_connections.get(char, 0),
                "themes_count": len(char_themes.get(char, set())),
                "themes": sorted(list(char_themes.get(char, set()))),
            })
        leaderboard.sort(key=lambda x: (x["mentions"], x["connections"]), reverse=True)

        return {
            "most_mentioned": most_mentioned,
            "most_connected": most_connected,
            "most_thematic_diversity": most_thematic_diversity,
            "leaderboard": leaderboard[:top_n],
        }

    # ------------------------------------------------------------------
    # Theme × Character heatmap
    # ------------------------------------------------------------------

    def theme_character_heatmap(
        self,
        myths: list[dict[str, Any]],
    ) -> go.Figure:
        """Heatmap showing co-occurrence of characters and themes.

        A cell *(theme, character)* counts the number of myths where both the
        character and the theme appear together.

        Parameters
        ----------
        myths : list[dict]
            Corpus dictionaries with ``'themes'`` and ``'characters'`` keys.

        Returns
        -------
        plotly.graph_objects.Figure
        """
        # Collect unique themes and characters
        all_themes = _count_field(myths, "themes")
        all_chars = _count_field(myths, "characters")
        if not all_themes or not all_chars:
            return _empty_figure("Insufficient data for heatmap")

        # Keep top themes / characters to avoid clutter
        top_themes = [t for t, _ in all_themes.most_common(15)]
        top_chars = [c for c, _ in all_chars.most_common(20)]

        # Build co-occurrence matrix
        matrix = np.zeros((len(top_themes), len(top_chars)), dtype=int)
        theme_idx = {t: i for i, t in enumerate(top_themes)}
        char_idx = {c: i for i, c in enumerate(top_chars)}

        for myth in myths:
            myth_themes = myth.get("themes") or myth.get("theme", [])
            raw_chars = myth.get("characters", [])
            myth_chars = [
                c.get("name") if isinstance(c, dict) else str(c)
                for c in (raw_chars if isinstance(raw_chars, list) else [raw_chars])
            ]
            if isinstance(myth_themes, str):
                myth_themes = [myth_themes]
            for theme in myth_themes:
                if theme in theme_idx:
                    for char in myth_chars:
                        if char in char_idx:
                            matrix[theme_idx[theme], char_idx[char]] += 1

        fig = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=top_chars,
                y=top_themes,
                colorscale="YlOrRd",
                text=matrix,
                texttemplate="%{text}",
                hovertemplate=(
                    "Theme: <b>%{y}</b><br>"
                    "Character: <b>%{x}</b><br>"
                    "Co-occurrences: %{z}<extra></extra>"
                ),
            )
        )
        fig.update_layout(
            title="Theme × Character Co-occurrence",
            xaxis_title="Characters",
            yaxis_title="Themes",
            template="plotly_white",
            width=max(700, len(top_chars) * 50),
            height=max(450, len(top_themes) * 35),
            xaxis=dict(tickangle=-45),
            margin=dict(b=120),
        )
        return fig

    # ------------------------------------------------------------------
    # Myth length distribution
    # ------------------------------------------------------------------

    def myth_length_distribution(
        self,
        myths: list[dict[str, Any]],
    ) -> go.Figure:
        """Histogram of myth text lengths (word count).

        Parameters
        ----------
        myths : list[dict]
            Corpus dictionaries with a ``'text'`` key.

        Returns
        -------
        plotly.graph_objects.Figure
        """
        lengths = [
            len(myth.get("text", "").split()) for myth in myths if myth.get("text")
        ]
        if not lengths:
            return _empty_figure("No text data available")

        titles = [
            myth.get("title", myth.get("name", f"Myth {i}"))
            for i, myth in enumerate(myths)
            if myth.get("text")
        ]

        fig = go.Figure()

        # Histogram
        fig.add_trace(
            go.Histogram(
                x=lengths,
                nbinsx=20,
                marker_color="#19D3F3",
                opacity=0.75,
                name="Distribution",
                hovertemplate="Word count range: %{x}<br>Count: %{y}<extra></extra>",
            )
        )

        # Add rug plot (strip of individual points) at the bottom
        fig.add_trace(
            go.Scatter(
                x=lengths,
                y=[0] * len(lengths),
                mode="markers",
                marker=dict(symbol="line-ns-open", size=10, color="#EF553B"),
                text=titles,
                name="Individual myths",
                hovertemplate="<b>%{text}</b><br>Words: %{x}<extra></extra>",
            )
        )

        mean_len = float(np.mean(lengths))
        fig.add_vline(
            x=mean_len,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_len:.0f}",
        )

        fig.update_layout(
            title="Myth Length Distribution (Word Count)",
            xaxis_title="Word Count",
            yaxis_title="Number of Myths",
            template="plotly_white",
            width=800,
            height=450,
            bargap=0.05,
            showlegend=True,
        )
        return fig

    # ------------------------------------------------------------------
    # All charts
    # ------------------------------------------------------------------

    def generate_all_charts(
        self,
        myths: list[dict[str, Any]],
    ) -> dict[str, go.Figure]:
        """Generate every dashboard chart at once.

        Parameters
        ----------
        myths : list[dict]
            Corpus of myth dictionaries.

        Returns
        -------
        dict[str, go.Figure]
            Mapping of chart name to Plotly figure.
        """
        return {
            "theme_distribution": self.theme_distribution(myths),
            "character_leaderboard": self.character_leaderboard(myths),
            "theme_character_heatmap": self.theme_character_heatmap(myths),
            "myth_length_distribution": self.myth_length_distribution(myths),
        }


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _empty_figure(message: str) -> go.Figure:
    """Return a blank figure with a centred annotation."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=18, color="gray"),
    )
    fig.update_layout(
        template="plotly_white",
        width=600,
        height=400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig
