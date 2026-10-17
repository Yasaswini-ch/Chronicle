"""Character knowledge graph for Greek mythology.

Builds and queries a directed knowledge graph of mythology characters
and their relationships using NetworkX.  Provides interactive visualization
via Plotly and PyVis.
"""

from __future__ import annotations

import logging
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import networkx as nx
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# Node color palette by entity type.
ENTITY_COLORS: dict[str, str] = {
    "GOD": "#FFD700",       # gold
    "MORTAL": "#4A90D9",    # blue
    "CREATURE": "#E74C3C",  # red
    "TITAN": "#9B59B6",     # purple
    "LOCATION": "#2ECC71",  # green
    "ARTIFACT": "#E67E22",  # orange
}

# Default color for unknown entity types.
_DEFAULT_COLOR = "#95A5A6"  # grey

# Edge color palette by relation type.
RELATION_COLORS: dict[str, str] = {
    "parent_of": "#2C3E50",
    "child_of": "#2980B9",
    "lover_of": "#E91E63",
    "enemy_of": "#C0392B",
    "sibling_of": "#27AE60",
    "mentor_of": "#F39C12",
    "killed_by": "#7F8C8D",
    "married_to": "#E91E63",
    "associated_with": "#BDC3C7",
}


class MythKnowledgeGraph:
    """Directed knowledge graph of mythology characters and relationships.

    Wraps a :class:`networkx.DiGraph` with mythology-specific convenience
    methods for querying character connections, finding paths, and
    generating interactive visualizations.

    Example::

        kg = MythKnowledgeGraph()
        kg.build_graph(relations)
        fig = kg.visualize()
        fig.show()
    """

    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def build_graph(
        self,
        relations: list[dict[str, str]],
        entity_types: dict[str, str] | None = None,
    ) -> nx.DiGraph:
        """Build the knowledge graph from a list of relations.

        Parameters
        ----------
        relations :
            Each dict must have keys ``source``, ``target``, ``relation``,
            and optionally ``myth_id``.
        entity_types :
            Optional mapping of character names to their entity type
            (e.g. ``{"Zeus": "GOD"}``).  Used to set node attributes
            for colour-coding.

        Returns
        -------
        nx.DiGraph
            The constructed graph (also stored internally).
        """
        self._graph = nx.DiGraph()
        entity_types = entity_types or {}

        # Track which myths each character appears in
        character_myths: dict[str, set[str]] = defaultdict(set)

        for rel in relations:
            source = rel["source"]
            target = rel["target"]
            relation_type = rel.get("relation", "associated_with")
            myth_id = rel.get("myth_id", "unknown")

            # Add / update nodes
            for name in (source, target):
                if not self._graph.has_node(name):
                    etype = entity_types.get(name, "MORTAL")
                    self._graph.add_node(
                        name,
                        entity_type=etype,
                        color=ENTITY_COLORS.get(etype, _DEFAULT_COLOR),
                    )
                character_myths[name].add(myth_id)

            # Add edge (accumulate myth_ids if edge already exists)
            if self._graph.has_edge(source, target):
                edge_data = self._graph[source][target]
                existing_myths = set(edge_data.get("myth_ids", []))
                existing_myths.add(myth_id)
                edge_data["myth_ids"] = list(existing_myths)
                # Keep all relation types
                existing_relations = set(edge_data.get("relations", []))
                existing_relations.add(relation_type)
                edge_data["relations"] = list(existing_relations)
            else:
                self._graph.add_edge(
                    source,
                    target,
                    relation=relation_type,
                    relations=[relation_type],
                    myth_ids=[myth_id],
                    color=RELATION_COLORS.get(relation_type, _DEFAULT_COLOR),
                )

        # Store myth participation on nodes
        for name, myths in character_myths.items():
            self._graph.nodes[name]["myths"] = sorted(myths)
            self._graph.nodes[name]["myth_count"] = len(myths)

        logger.info(
            "Knowledge graph built: %d nodes, %d edges",
            self._graph.number_of_nodes(),
            self._graph.number_of_edges(),
        )
        return self._graph

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def get_character_info(self, character: str) -> dict[str, Any]:
        """Return detailed information about a character node.

        Parameters
        ----------
        character :
            Character name (case-sensitive, must match node key).

        Returns
        -------
        dict
            Node attributes plus computed metrics: in-degree, out-degree,
            total degree, connections, and myths appeared in.

        Raises
        ------
        KeyError
            If *character* is not in the graph.
        """
        if character not in self._graph:
            raise KeyError(f"Character '{character}' not found in graph")

        node_data = dict(self._graph.nodes[character])
        in_deg = self._graph.in_degree(character)
        out_deg = self._graph.out_degree(character)

        # Gather connections
        predecessors = [
            {
                "character": pred,
                "relation": self._graph[pred][character].get("relation", "unknown"),
            }
            for pred in self._graph.predecessors(character)
        ]
        successors = [
            {
                "character": succ,
                "relation": self._graph[character][succ].get("relation", "unknown"),
            }
            for succ in self._graph.successors(character)
        ]

        return {
            **node_data,
            "name": character,
            "in_degree": in_deg,
            "out_degree": out_deg,
            "total_degree": in_deg + out_deg,
            "connections_in": predecessors,
            "connections_out": successors,
            "myths": node_data.get("myths", []),
        }

    def get_most_connected(self, top_n: int = 10) -> list[tuple[str, int]]:
        """Return the most connected characters by total degree.

        Parameters
        ----------
        top_n :
            Number of top characters to return.

        Returns
        -------
        list[tuple[str, int]]
            ``(character_name, degree)`` pairs, sorted descending.
        """
        undirected = self._graph.to_undirected()
        degrees = sorted(
            undirected.degree(), key=lambda x: x[1], reverse=True
        )
        return degrees[:top_n]

    def get_most_mentioned(
        self,
        myths: list[dict[str, Any]],
        top_n: int = 10,
    ) -> list[tuple[str, int]]:
        """Return the most mentioned characters across the myth corpus.

        Counts character appearances in the ``characters`` field of each
        myth document, supplemented by full-text occurrences.

        Parameters
        ----------
        myths :
            List of myth documents from the Chronicle dataset.
        top_n :
            Number of top characters to return.

        Returns
        -------
        list[tuple[str, int]]
            ``(character_name, mention_count)`` pairs, sorted descending.
        """
        mention_counts: Counter[str] = Counter()

        for myth in myths:
            # Count from structured character lists
            characters = myth.get("characters", [])
            for char in characters:
                name = char if isinstance(char, str) else char.get("name", "")
                if name:
                    mention_counts[name] += 1

            # Count text occurrences (simple substring matching)
            text = myth.get("text", myth.get("summary", ""))
            if text:
                for node in self._graph.nodes:
                    count = text.lower().count(node.lower())
                    if count > 0:
                        mention_counts[node] += count

        return mention_counts.most_common(top_n)

    def get_character_themes(
        self,
        character: str,
        myths: list[dict[str, Any]],
    ) -> list[str]:
        """Return themes associated with a character across the corpus.

        Parameters
        ----------
        character :
            Character name.
        myths :
            List of myth documents with ``themes`` fields.

        Returns
        -------
        list[str]
            Deduplicated list of theme strings.
        """
        char_lower = character.lower()
        themes: set[str] = set()

        for myth in myths:
            # Check if the character appears in this myth
            characters = myth.get("characters", [])
            char_names = []
            for c in characters:
                if isinstance(c, str):
                    char_names.append(c.lower())
                elif isinstance(c, dict):
                    char_names.append(c.get("name", "").lower())

            if char_lower in char_names:
                for theme in myth.get("themes", []):
                    themes.add(theme if isinstance(theme, str) else str(theme))

        return sorted(themes)

    def get_shortest_path(
        self,
        source: str,
        target: str,
    ) -> list[str]:
        """Find the shortest path between two characters.

        Uses the undirected view of the graph so relationship direction
        does not block path discovery.

        Parameters
        ----------
        source :
            Starting character.
        target :
            Ending character.

        Returns
        -------
        list[str]
            Ordered list of character names forming the path.

        Raises
        ------
        KeyError
            If either character is not in the graph.
        nx.NetworkXNoPath
            If no path exists between the characters.
        """
        for name in (source, target):
            if name not in self._graph:
                raise KeyError(f"Character '{name}' not found in graph")

        undirected = self._graph.to_undirected()
        return nx.shortest_path(undirected, source, target)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """Compute summary statistics for the knowledge graph.

        Returns
        -------
        dict
            Keys: ``nodes``, ``edges``, ``density``, ``avg_degree``,
            ``connected_components``, ``most_central`` (by betweenness),
            ``entity_type_counts``, ``relation_type_counts``.
        """
        g = self._graph
        n_nodes = g.number_of_nodes()
        n_edges = g.number_of_edges()

        # Entity type distribution
        type_counts: Counter[str] = Counter()
        for _, data in g.nodes(data=True):
            type_counts[data.get("entity_type", "UNKNOWN")] += 1

        # Relation type distribution
        rel_counts: Counter[str] = Counter()
        for _, _, data in g.edges(data=True):
            rel_counts[data.get("relation", "unknown")] += 1

        # Centrality (only if graph is non-empty)
        most_central: list[tuple[str, float]] = []
        if n_nodes > 0:
            betweenness = nx.betweenness_centrality(g)
            most_central = sorted(
                betweenness.items(), key=lambda x: x[1], reverse=True
            )[:5]

        # Connected components on undirected view
        undirected = g.to_undirected()
        n_components = nx.number_connected_components(undirected)

        avg_degree = (2.0 * n_edges / n_nodes) if n_nodes > 0 else 0.0

        return {
            "nodes": n_nodes,
            "edges": n_edges,
            "density": round(nx.density(g), 4) if n_nodes > 0 else 0.0,
            "avg_degree": round(avg_degree, 2),
            "connected_components": n_components,
            "most_central": [
                {"character": name, "centrality": round(score, 4)}
                for name, score in most_central
            ],
            "entity_type_counts": dict(type_counts),
            "relation_type_counts": dict(rel_counts),
        }

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    def visualize(
        self,
        output_path: str | None = None,
        title: str = "Chronicle — Mythology Knowledge Graph",
        width: int = 1200,
        height: int = 800,
    ) -> go.Figure:
        """Create an interactive Plotly network graph visualization.

        Nodes are colour-coded by entity type and sized by degree
        centrality.

        Parameters
        ----------
        output_path :
            If provided, save the figure as an HTML file.
        title :
            Figure title.
        width :
            Figure width in pixels.
        height :
            Figure height in pixels.

        Returns
        -------
        plotly.graph_objects.Figure
            The Plotly figure object.
        """
        if self._graph.number_of_nodes() == 0:
            logger.warning("Cannot visualize an empty graph")
            fig = go.Figure()
            fig.update_layout(
                title="Empty Knowledge Graph",
                annotations=[
                    {
                        "text": "No data to display",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 20},
                    }
                ],
            )
            return fig

        # Compute layout
        pos = nx.spring_layout(self._graph, k=2.0, iterations=50, seed=42)

        # Compute degree for node sizing
        undirected = self._graph.to_undirected()
        degrees = dict(undirected.degree())
        max_degree = max(degrees.values()) if degrees else 1

        # --- Edge traces ---
        edge_traces: list[go.Scatter] = []
        for source, target, data in self._graph.edges(data=True):
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            relation = data.get("relation", "unknown")
            color = data.get("color", RELATION_COLORS.get(relation, _DEFAULT_COLOR))

            edge_traces.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode="lines",
                    line={"width": 1.5, "color": color},
                    hoverinfo="text",
                    text=f"{source} —[{relation}]→ {target}",
                    showlegend=False,
                )
            )

        # --- Node traces (one per entity type for legend grouping) ---
        nodes_by_type: dict[str, list[str]] = defaultdict(list)
        for node, data in self._graph.nodes(data=True):
            etype = data.get("entity_type", "UNKNOWN")
            nodes_by_type[etype].append(node)

        node_traces: list[go.Scatter] = []
        for etype, nodes in nodes_by_type.items():
            color = ENTITY_COLORS.get(etype, _DEFAULT_COLOR)
            x_vals = [pos[n][0] for n in nodes]
            y_vals = [pos[n][1] for n in nodes]
            sizes = [
                max(15, 10 + 30 * (degrees.get(n, 0) / max_degree))
                for n in nodes
            ]
            hover_texts = [
                (
                    f"<b>{n}</b><br>"
                    f"Type: {etype}<br>"
                    f"Degree: {degrees.get(n, 0)}<br>"
                    f"Myths: {self._graph.nodes[n].get('myth_count', 0)}"
                )
                for n in nodes
            ]
            labels = nodes

            node_traces.append(
                go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode="markers+text",
                    marker={
                        "size": sizes,
                        "color": color,
                        "line": {"width": 1.5, "color": "#2C3E50"},
                        "opacity": 0.9,
                    },
                    text=labels,
                    textposition="top center",
                    textfont={"size": 9},
                    hovertext=hover_texts,
                    hoverinfo="text",
                    name=etype,
                    legendgroup=etype,
                )
            )

        # --- Assemble figure ---
        fig = go.Figure(data=edge_traces + node_traces)
        fig.update_layout(
            title={
                "text": title,
                "x": 0.5,
                "font": {"size": 18},
            },
            showlegend=True,
            legend={"title": "Entity Type", "font": {"size": 12}},
            hovermode="closest",
            width=width,
            height=height,
            xaxis={
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
            },
            yaxis={
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
            },
            plot_bgcolor="#FAFAFA",
            margin={"l": 40, "r": 40, "t": 60, "b": 40},
        )

        if output_path:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(output))
            logger.info("Visualization saved to %s", output)

        return fig

    def to_pyvis(
        self,
        output_path: str,
        height: str = "800px",
        width: str = "100%",
        notebook: bool = False,
    ) -> None:
        """Export the graph to a PyVis interactive HTML file.

        Parameters
        ----------
        output_path :
            Path to write the HTML file.
        height :
            Height of the visualization canvas.
        width :
            Width of the visualization canvas.
        notebook :
            Whether to render inline in a Jupyter notebook.
        """
        from pyvis.network import Network

        net = Network(
            height=height,
            width=width,
            directed=True,
            notebook=notebook,
            bgcolor="#FAFAFA",
            font_color="#2C3E50",
        )

        # Physics settings for better layout
        net.set_options(
            """
            {
                "physics": {
                    "forceAtlas2Based": {
                        "gravitationalConstant": -80,
                        "centralGravity": 0.01,
                        "springLength": 200,
                        "springConstant": 0.08
                    },
                    "solver": "forceAtlas2Based",
                    "stabilization": {"iterations": 150}
                },
                "interaction": {
                    "hover": true,
                    "tooltipDelay": 200
                }
            }
            """
        )

        # Compute sizes
        undirected = self._graph.to_undirected()
        degrees = dict(undirected.degree())
        max_degree = max(degrees.values()) if degrees else 1

        # Add nodes
        for node, data in self._graph.nodes(data=True):
            etype = data.get("entity_type", "UNKNOWN")
            color = ENTITY_COLORS.get(etype, _DEFAULT_COLOR)
            size = max(15, 10 + 30 * (degrees.get(node, 0) / max_degree))
            myths = data.get("myths", [])
            title = (
                f"<b>{node}</b><br>"
                f"Type: {etype}<br>"
                f"Degree: {degrees.get(node, 0)}<br>"
                f"Myths: {', '.join(myths[:5])}"
            )
            net.add_node(
                node,
                label=node,
                color=color,
                size=size,
                title=title,
                shape="dot",
            )

        # Add edges
        for source, target, data in self._graph.edges(data=True):
            relation = data.get("relation", "unknown")
            color = RELATION_COLORS.get(relation, _DEFAULT_COLOR)
            net.add_edge(
                source,
                target,
                title=relation,
                color=color,
                label=relation,
                font={"size": 8, "color": "#7F8C8D"},
            )

        # Write output
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        net.save_graph(str(output))
        logger.info("PyVis graph exported to %s", output)

    # ------------------------------------------------------------------
    # Graph access
    # ------------------------------------------------------------------

    @property
    def graph(self) -> nx.DiGraph:
        """The underlying NetworkX directed graph."""
        return self._graph

    @property
    def characters(self) -> list[str]:
        """Sorted list of all character names in the graph."""
        return sorted(self._graph.nodes)

    def __repr__(self) -> str:
        return (
            f"MythKnowledgeGraph(nodes={self._graph.number_of_nodes()}, "
            f"edges={self._graph.number_of_edges()})"
        )

    def __len__(self) -> int:
        return self._graph.number_of_nodes()

    def __contains__(self, character: str) -> bool:
        return character in self._graph


class KnowledgeGraph(MythKnowledgeGraph):
    """Knowledge graph subclass providing convenience methods for annotation-based loading and queries."""

    def build_from_annotations(self, annotations: list[dict[str, Any]]) -> None:
        """Build graph directly from a list of myth annotation dictionaries."""
        self._graph = nx.DiGraph()
        character_myths: dict[str, set[str]] = defaultdict(set)

        for item in annotations:
            myth_name = item.get("myth", item.get("title", "unknown"))
            characters = item.get("characters", [])
            for c in characters:
                c_name = c.get("name", "") if isinstance(c, dict) else str(c)
                c_type = c.get("type", "CHARACTER") if isinstance(c, dict) else "CHARACTER"
                if not c_name:
                    continue
                if c_name not in self._graph:
                    self._graph.add_node(c_name, name=c_name, type=c_type)
                character_myths[c_name].add(myth_name)
            locations = item.get("locations", [])
            for loc in locations:
                l_name = loc.get("name", "") if isinstance(loc, dict) else str(loc)
                if l_name and l_name not in self._graph:
                    self._graph.add_node(l_name, name=l_name, type="LOCATION")
            rels = item.get("relations") or item.get("relationships") or []
            for r in rels:
                s = r.get("subject") or r.get("source", "")
                p = r.get("predicate") or r.get("relation", "")
                o = r.get("object") or r.get("target", "")
                if s and o and p:
                    if s not in self._graph:
                        self._graph.add_node(s, name=s)
                    if o not in self._graph:
                        self._graph.add_node(o, name=o)
                    self._graph.add_edge(s, o, relation=p, predicate=p, myth=myth_name)

        for name, myths in character_myths.items():
            self._graph.nodes[name]["myths"] = sorted(myths)
            self._graph.nodes[name]["myth_count"] = len(myths)

    def add_family(self, tree: Any, types: dict[str, str] | None = None) -> int:
        """Add curated family edges (parent_of, married_to, lover_of) from a ``FamilyTree``.

        Existing story edges between the same pair are kept untouched. Returns
        the number of edges added.
        """
        types = types or {}
        added = 0

        def link(u: str, v: str, relation: str, symmetric: bool) -> None:
            nonlocal added
            for name in (u, v):
                if name not in self._graph:
                    self._graph.add_node(name, name=name, type=types.get(name, "CHARACTER"))
            if self._graph.has_edge(u, v) or (symmetric and self._graph.has_edge(v, u)):
                return
            self._graph.add_edge(u, v, relation=relation, predicate=relation, myth=None, kind="family")
            added += 1

        for child, parents in tree.parents.items():
            for parent in parents:
                link(parent, child, "parent_of", False)
        for a, others in tree.spouses.items():
            for b in others:
                if a < b:
                    link(a, b, "married_to", True)
        for a, others in tree.lovers.items():
            for b in others:
                if a < b:
                    link(a, b, "lover_of", True)
        return added

    def get_nodes(self) -> list[dict[str, Any]]:
        """Return list of node dictionaries containing at least 'name'."""
        return [{"name": n, **self._graph.nodes[n]} for n in self._graph.nodes]

    def get_edges(self) -> list[dict[str, Any]]:
        """Return list of edge dictionaries."""
        return [
            {
                "source": u,
                "target": v,
                "subject": u,
                "object": v,
                "predicate": data.get("predicate", data.get("relation", "")),
                "relation": data.get("relation", ""),
            }
            for u, v, data in self._graph.edges(data=True)
        ]

    def get_neighbors(self, node: str) -> list[str]:
        """Return all neighbors of *node* (both incoming and outgoing)."""
        if node not in self._graph:
            return []
        neighbors = set(self._graph.predecessors(node)) | set(self._graph.successors(node))
        return list(neighbors)

    def query(
        self,
        subject: str | None = None,
        predicate: str | None = None,
        object: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query relations matching given subject, predicate, or object filters."""
        results = []
        for u, v, data in self._graph.edges(data=True):
            p = data.get("predicate", data.get("relation", ""))
            if subject is not None and u != subject:
                continue
            if object is not None and v != object:
                continue
            if predicate is not None and p != predicate and data.get("relation") != predicate:
                continue
            results.append({"subject": u, "predicate": p, "object": v, "relation": p})
        return results

    def find_path(self, source: str, target: str) -> list[str] | None:
        """Find shortest undirected path between source and target."""
        if source not in self._graph or target not in self._graph:
            return None
        try:
            return nx.shortest_path(self._graph.to_undirected(), source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def degree(self, node: str) -> int:
        """Return the degree of *node* in the graph."""
        if node not in self._graph:
            return 0
        return int(self._graph.degree(node))

    def statistics(self) -> dict[str, Any]:
        """Return summary statistics of the graph."""
        return {
            "num_nodes": self._graph.number_of_nodes(),
            "num_edges": self._graph.number_of_edges(),
            "density": nx.density(self._graph),
            "is_connected": nx.is_weakly_connected(self._graph) if len(self._graph) > 0 else False,
        }
