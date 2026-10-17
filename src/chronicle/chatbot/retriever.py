"""Myth retrieval engine for the Chronicle chatbot.

Retrieves myths by character, theme, title, or semantic similarity
using vector embeddings and metadata filters.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from chronicle.text.bm25 import BM25

logger = logging.getLogger(__name__)


class MythRetriever:
    """Retrieves mythology texts and character knowledge."""

    def __init__(
        self,
        myths: list[dict[str, Any]] | None = None,
        myths_path: str | Path | None = None,
        sbert_model: Any | None = None,
    ) -> None:
        if myths is not None:
            self.myths = myths
        elif myths_path is not None:
            with open(myths_path, "r", encoding="utf-8") as f:
                self.myths = json.load(f)
        else:
            default_path = (
                Path(__file__).resolve().parents[3]
                / "data"
                / "processed"
                / "myths.json"
            )
            if default_path.exists():
                with open(default_path, "r", encoding="utf-8") as f:
                    self.myths = json.load(f)
            else:
                self.myths = []

        self.sbert = sbert_model
        self._embeddings: np.ndarray | None = None
        self._bm25 = BM25([self._doc(m) for m in self.myths]) if self.myths else None
        self._init_embeddings()

    @staticmethod
    def _doc(myth: dict[str, Any]) -> str:
        names = " ".join(c.get("name", "") if isinstance(c, dict) else str(c) for c in myth.get("characters", []))
        return f"{myth.get('title', '')} {myth.get('title', '')} {names} {names} {myth.get('text', '')}"

    def _init_embeddings(self) -> None:
        """Precompute SBERT embeddings for fast vector search if model available."""
        if self.sbert is not None and self.myths:
            try:
                texts = [m.get("text", "") for m in self.myths]
                self._embeddings = self.sbert.encode(texts)
            except Exception as e:
                logger.warning("Failed to encode corpus with SBERT: %s", e)

    def attach_sbert(self, sbert_model: Any) -> None:
        """Enable semantic search after construction (e.g. once a model has loaded in the background).

        Embeddings are computed first and the model is published last, so a concurrent query
        sees either the BM25-only state or the complete hybrid state, never a half-built one.
        """
        texts = [m.get("text", "") for m in self.myths]
        embeddings = sbert_model.encode(texts)
        self._embeddings = embeddings
        self.sbert = sbert_model

    def retrieve_by_title(self, title: str) -> dict[str, Any] | None:
        """Find a myth by exact or partial title match."""
        title_lower = title.lower()
        for myth in self.myths:
            if title_lower in myth.get("title", "").lower():
                return myth
            if title_lower in myth.get("id", "").lower():
                return myth
        return None

    def retrieve_by_character(
        self, character: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve myths featuring *character*."""
        char_lower = character.lower()
        results = []
        for myth in self.myths:
            chars = myth.get("characters", [])
            for c in chars:
                c_name = c.get("name", "") if isinstance(c, dict) else str(c)
                if char_lower in c_name.lower():
                    results.append(myth)
                    break
                # Also check aliases
                c_alias = c.get("canonical_name", "") if isinstance(c, dict) else ""
                if c_alias and char_lower in c_alias.lower():
                    results.append(myth)
                    break
            if len(results) >= limit:
                break
        return results

    def retrieve_by_theme(
        self, theme: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve myths matching a moral/theme category."""
        theme_lower = theme.lower()
        results = [
            m for m in self.myths
            if theme_lower == m.get("theme", "").lower()
        ]
        return results[:limit]

    def retrieve_similar(
        self, myth_id_or_title: str, top_k: int = 3
    ) -> list[dict[str, Any]]:
        """Retrieve top-k most similar myths to a given myth by embedding distance."""
        ref_myth = self.retrieve_by_title(myth_id_or_title)
        if not ref_myth:
            # Try searching by character
            matches = self.retrieve_by_character(myth_id_or_title, limit=1)
            if matches:
                ref_myth = matches[0]

        if not ref_myth:
            return self.retrieve_by_query(myth_id_or_title, top_k=top_k)

        ref_id = ref_myth.get("id")
        ref_text = ref_myth.get("text", "")
        candidates = self.retrieve_by_query(ref_text, top_k=top_k + 1)
        # Exclude the reference myth itself
        similar = [m for m in candidates if m.get("id") != ref_id]
        return similar[:top_k]

    def retrieve_by_query(
        self, query: str, top_k: int = 3
    ) -> list[dict[str, Any]]:
        """Retrieve most semantically similar myths for free-form query."""
        if not self.myths:
            return []

        # Vector search if SBERT embeddings available
        if self.sbert is not None and self._embeddings is not None:
            try:
                query_vec = self.sbert.encode(query)
                # Compute cosine similarities
                norm_q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
                norm_corp = self._embeddings / (
                    np.linalg.norm(self._embeddings, axis=1, keepdims=True) + 1e-9
                )
                sims = np.dot(norm_corp, norm_q)
                dense_rank = [int(i) for i in np.argsort(sims)[::-1]]
                if self._bm25 is None:
                    return [self.myths[i] for i in dense_rank[:top_k]]
                # Hybrid ranking. SBERT only reads the start of a long myth and BM25 only matches
                # words, so each misses what the other finds; reciprocal-rank fusion combines them.
                lexical = self._bm25.scores(query)
                lex_rank = sorted(range(len(self.myths)), key=lambda i: lexical[i], reverse=True)
                fused: dict[int, float] = {}
                for ranking in (dense_rank, lex_rank):
                    for pos, i in enumerate(ranking):
                        fused[i] = fused.get(i, 0.0) + 1.0 / (60 + pos)
                best = sorted(fused, key=fused.get, reverse=True)[:top_k]
                return [self.myths[i] for i in best]
            except Exception as e:
                logger.warning("Vector retrieval failed; falling back to lexical search: %s", e)

        # Lexical search fallback (BM25: rare words outweigh common ones, length is normalised)
        if self._bm25 is None:
            return []
        return [self.myths[i] for i, _ in self._bm25.top(query, top_k)]
