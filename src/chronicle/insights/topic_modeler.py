"""Topic modelling for Greek mythology corpora.

Provides ``MythTopicModeler`` with two back-ends:

* **BERTopic** — sentence-transformer embeddings → UMAP → HDBSCAN → c-TF-IDF.
* **LDA** — classical Latent Dirichlet Allocation via *gensim*.

Both share a unified API for fitting, querying topics, computing coherence, and
generating Plotly visualisations.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Any, Literal

import numpy as np
import plotly.graph_objects as go
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lightweight tokeniser (avoids a hard spaCy dependency at import time)
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\b[a-zA-Z]{3,}\b")
_STOPWORDS: set[str] | None = None


def _get_stopwords() -> set[str]:
    """Return a set of English stop-words (NLTK or sklearn fallback)."""
    global _STOPWORDS  # noqa: PLW0603
    if _STOPWORDS is None:
        try:
            from nltk.corpus import stopwords as _sw  # type: ignore[import-untyped]
            _STOPWORDS = set(_sw.words("english"))
        except (ImportError, LookupError):
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            _STOPWORDS = set(ENGLISH_STOP_WORDS)
    return _STOPWORDS


def _simple_tokenize(text: str) -> list[str]:
    """Lowercase tokenise, remove short tokens & stop-words."""
    stops = _get_stopwords()
    return [
        tok.lower()
        for tok in _TOKEN_RE.findall(text)
        if tok.lower() not in stops
    ]


# ---------------------------------------------------------------------------
# MythTopicModeler
# ---------------------------------------------------------------------------

# Function words typical of 19th-century retellings, which carry no topic signal.
_ARCHAIC_STOPWORDS = frozenset(
    "thou thee thy thine hath doth art ye shalt wilt unto upon whom whose said say saith would could "
    "shall one two came come went gone did done made make took taken thus therefore however yet "
    "great god gods goddess king queen son daughter father mother man men woman".split()
)


class MythTopicModeler:
    """Discover latent topics in a mythology corpus.

    Parameters
    ----------
    method : ``'bertopic'`` | ``'lda'``
        Modelling backend.
    n_topics : int | None
        Number of topics.  For BERTopic ``None`` lets HDBSCAN decide
        automatically; for LDA it defaults to **10**.
    embedding_model : str
        Sentence-transformer model name (BERTopic only).
    random_state : int
        Seed for reproducibility.

    Examples
    --------
    >>> modeler = MythTopicModeler(method="lda", n_topics=5)
    >>> modeler.fit(["Zeus threw thunderbolts.", "Hades ruled the underworld."])
    >>> modeler.get_topics()  # doctest: +SKIP
    [{'topic_id': 0, 'words': [...], 'representative_docs': [...]}, ...]
    """

    SUPPORTED_METHODS: tuple[str, ...] = ("bertopic", "lda")

    def __init__(
        self,
        method: Literal["bertopic", "lda"] = "bertopic",
        n_topics: int | None = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        random_state: int = 42,
    ) -> None:
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(
                f"Unknown method '{method}'. Choose from {self.SUPPORTED_METHODS}."
            )
        self.method = method
        self.n_topics = n_topics
        self.embedding_model = embedding_model
        self.random_state = random_state

        # State populated by :meth:`fit`
        self._texts: list[str] = []
        self._topic_assignments: list[int] = []
        self._topics: list[dict[str, Any]] = []
        self._is_fitted: bool = False

        # Back-end specific models (lazy)
        self._bertopic_model: Any | None = None
        self._lda_model: Any | None = None
        self._dictionary: Any | None = None
        self._corpus_bow: Any | None = None
        self._embeddings: NDArray[np.floating[Any]] | None = None

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------

    def fit(self, texts: list[str]) -> None:
        """Fit the topic model on *texts*.

        Parameters
        ----------
        texts : list[str]
            Raw document strings.
        """
        if not texts:
            raise ValueError("Cannot fit on an empty corpus.")

        self._texts = list(texts)

        if self.method == "bertopic":
            self._fit_bertopic(texts)
        else:
            self._fit_lda(texts)

        self._is_fitted = True
        logger.info(
            "Fitted %s model — discovered %d topics from %d documents.",
            self.method,
            len(self._topics),
            len(texts),
        )

    # -- BERTopic ------------------------------------------------------

    def _fit_bertopic(self, texts: list[str]) -> None:
        """Fit using BERTopic (sentence-transformers + UMAP + HDBSCAN)."""
        from bertopic import BERTopic  # type: ignore[import-untyped]
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
        from umap import UMAP  # type: ignore[import-untyped]
        from hdbscan import HDBSCAN  # type: ignore[import-untyped]

        # Embeddings
        st_model = SentenceTransformer(self.embedding_model)
        self._embeddings = st_model.encode(
            texts, show_progress_bar=False, convert_to_numpy=True
        )

        # Dimensionality reduction
        umap_model = UMAP(
            n_neighbors=min(15, len(texts) - 1),
            n_components=min(5, len(texts) - 1),
            min_dist=0.0,
            metric="cosine",
            random_state=self.random_state,
        )

        # Clustering
        min_cluster = max(2, len(texts) // 10)
        hdbscan_model = HDBSCAN(
            min_cluster_size=min_cluster,
            min_samples=1,
            metric="euclidean",
            prediction_data=True,
        )

        nr_topics = self.n_topics if self.n_topics else "auto"

        # Without a stop-word-aware vectorizer BERTopic labels every topic "the / and / of / to".
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

        vectorizer = CountVectorizer(
            stop_words=sorted(ENGLISH_STOP_WORDS | _ARCHAIC_STOPWORDS),
            min_df=2,
            max_df=0.6,
        )
        self._bertopic_model = BERTopic(
            embedding_model=st_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer,
            nr_topics=nr_topics,
            verbose=False,
        )

        topics, _ = self._bertopic_model.fit_transform(texts, self._embeddings)
        self._topic_assignments = list(topics)

        # Extract topic info
        topic_info = self._bertopic_model.get_topic_info()
        self._topics = []
        for _, row in topic_info.iterrows():
            tid = int(row["Topic"])
            if tid == -1:
                continue  # skip outlier topic
            top_words = self._bertopic_model.get_topic(tid)
            rep_docs = [
                texts[i]
                for i, t in enumerate(self._topic_assignments)
                if t == tid
            ][:3]
            self._topics.append(
                {
                    "topic_id": tid,
                    "words": [w for w, _ in top_words[:10]],
                    "word_scores": {w: round(float(s), 4) for w, s in top_words[:10]},
                    "count": int(row["Count"]),
                    "representative_docs": rep_docs,
                }
            )

    # -- LDA -----------------------------------------------------------

    def _fit_lda(self, texts: list[str]) -> None:
        """Fit using gensim LDA."""
        from gensim.corpora import Dictionary  # type: ignore[import-untyped]
        from gensim.models import LdaModel  # type: ignore[import-untyped]

        tokenized = [_simple_tokenize(t) for t in texts]

        self._dictionary = Dictionary(tokenized)
        # Filter extremes for better topics
        if len(tokenized) > 10:
            self._dictionary.filter_extremes(no_below=2, no_above=0.9)
        self._corpus_bow = [self._dictionary.doc2bow(doc) for doc in tokenized]

        n_topics = self.n_topics or 10

        self._lda_model = LdaModel(
            corpus=self._corpus_bow,
            id2word=self._dictionary,
            num_topics=n_topics,
            random_state=self.random_state,
            passes=15,
            alpha="auto",
            eta="auto",
            per_word_topics=True,
        )

        # Topic assignments — pick highest-probability topic per doc
        self._topic_assignments = []
        for bow in self._corpus_bow:
            topic_dist = self._lda_model.get_document_topics(
                bow, minimum_probability=0.0
            )
            if topic_dist:
                best = max(topic_dist, key=lambda x: x[1])
                self._topic_assignments.append(best[0])
            else:
                self._topic_assignments.append(-1)

        # Build topic info list
        self._topics = []
        topic_counts = Counter(self._topic_assignments)
        for tid in range(n_topics):
            word_probs = self._lda_model.show_topic(tid, topn=10)
            rep_docs = [
                texts[i]
                for i, t in enumerate(self._topic_assignments)
                if t == tid
            ][:3]
            self._topics.append(
                {
                    "topic_id": tid,
                    "words": [w for w, _ in word_probs],
                    "word_scores": {w: round(float(p), 4) for w, p in word_probs},
                    "count": topic_counts.get(tid, 0),
                    "representative_docs": rep_docs,
                }
            )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def _check_fitted(self) -> None:
        if not self._is_fitted:
            raise RuntimeError("Model has not been fitted yet. Call fit() first.")

    def get_topics(self) -> list[dict[str, Any]]:
        """Return all discovered topics with top words and representative docs.

        Returns
        -------
        list[dict]
            Each dict contains ``topic_id``, ``words``, ``word_scores``,
            ``count``, and ``representative_docs``.
        """
        self._check_fitted()
        return list(self._topics)

    def get_topic_for_document(self, doc_idx: int) -> dict[str, Any]:
        """Get the topic assignment for document at *doc_idx*.

        Parameters
        ----------
        doc_idx : int
            Zero-based index into the corpus passed to :meth:`fit`.

        Returns
        -------
        dict
            Keys: ``doc_idx``, ``topic_id``, ``topic_words``, ``text_preview``.
        """
        self._check_fitted()
        if doc_idx < 0 or doc_idx >= len(self._texts):
            raise IndexError(
                f"doc_idx {doc_idx} out of range [0, {len(self._texts)})."
            )

        tid = self._topic_assignments[doc_idx]
        topic_words: list[str] = []
        for topic in self._topics:
            if topic["topic_id"] == tid:
                topic_words = topic["words"]
                break

        return {
            "doc_idx": doc_idx,
            "topic_id": tid,
            "topic_words": topic_words,
            "text_preview": self._texts[doc_idx][:200],
        }

    def get_topic_distribution(self) -> dict[int, int]:
        """Return a mapping of topic ID → document count.

        Returns
        -------
        dict[int, int]
            Frequency distribution across topics.
        """
        self._check_fitted()
        return dict(Counter(self._topic_assignments))

    # ------------------------------------------------------------------
    # Coherence
    # ------------------------------------------------------------------

    def get_coherence_score(self) -> float:
        """Compute the *C_v* topic coherence score.

        Uses ``gensim.models.CoherenceModel``.

        Returns
        -------
        float
            Coherence score (higher is better, typically 0.3–0.7).
        """
        self._check_fitted()

        from gensim.corpora import Dictionary  # type: ignore[import-untyped]
        from gensim.models import CoherenceModel  # type: ignore[import-untyped]

        tokenized = [_simple_tokenize(t) for t in self._texts]
        dictionary = self._dictionary or Dictionary(tokenized)

        topic_word_lists = [t["words"] for t in self._topics]

        cm = CoherenceModel(
            topics=topic_word_lists,
            texts=tokenized,
            dictionary=dictionary,
            coherence="c_v",
        )
        return float(cm.get_coherence())

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def visualize_topics(self) -> go.Figure:
        """Create a 2-D scatter plot of documents coloured by topic.

        Uses UMAP to project embeddings (or TF-IDF vectors for LDA) into 2-D.

        Returns
        -------
        plotly.graph_objects.Figure
        """
        self._check_fitted()

        from umap import UMAP  # type: ignore[import-untyped]

        # Get or compute 2-D coordinates
        if self._embeddings is not None:
            coords_input = self._embeddings
        else:
            # Fall back to TF-IDF for LDA
            from sklearn.feature_extraction.text import TfidfVectorizer

            vec = TfidfVectorizer(max_features=5000, stop_words="english")
            coords_input = vec.fit_transform(self._texts).toarray()

        n_neighbors = min(15, len(self._texts) - 1)
        reducer = UMAP(
            n_components=2,
            n_neighbors=max(2, n_neighbors),
            random_state=self.random_state,
            metric="cosine",
        )
        coords: NDArray[np.floating[Any]] = reducer.fit_transform(coords_input)

        labels = [
            f"Topic {t}" if t >= 0 else "Outlier"
            for t in self._topic_assignments
        ]
        previews = [txt[:80] + "…" if len(txt) > 80 else txt for txt in self._texts]

        fig = go.Figure(
            data=go.Scatter(
                x=coords[:, 0],
                y=coords[:, 1],
                mode="markers",
                marker=dict(
                    color=self._topic_assignments,
                    colorscale="Viridis",
                    size=8,
                    opacity=0.75,
                    showscale=True,
                    colorbar=dict(title="Topic"),
                ),
                text=previews,
                customdata=list(zip(labels, previews)),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{customdata[1]}<extra></extra>"
                ),
            )
        )
        fig.update_layout(
            title="Topic Clusters (UMAP Projection)",
            xaxis_title="UMAP-1",
            yaxis_title="UMAP-2",
            template="plotly_white",
            width=900,
            height=600,
        )
        return fig

    def visualize_topic_distribution(self) -> go.Figure:
        """Bar chart of topic frequency distribution.

        Returns
        -------
        plotly.graph_objects.Figure
        """
        self._check_fitted()

        dist = self.get_topic_distribution()
        # Sort by topic id, move outlier (-1) to end
        sorted_items = sorted(dist.items(), key=lambda kv: (kv[0] == -1, kv[0]))

        topic_labels = [
            f"Topic {tid}" if tid >= 0 else "Outlier" for tid, _ in sorted_items
        ]
        counts = [c for _, c in sorted_items]

        # Build word hints for hover
        word_hints: list[str] = []
        topic_lookup = {t["topic_id"]: t for t in self._topics}
        for tid, _ in sorted_items:
            info = topic_lookup.get(tid)
            if info:
                word_hints.append(", ".join(info["words"][:5]))
            else:
                word_hints.append("—")

        fig = go.Figure(
            data=go.Bar(
                x=topic_labels,
                y=counts,
                marker_color="#636EFA",
                text=counts,
                textposition="outside",
                customdata=word_hints,
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Documents: %{y}<br>"
                    "Top words: %{customdata}<extra></extra>"
                ),
            )
        )
        fig.update_layout(
            title="Topic Distribution",
            xaxis_title="Topic",
            yaxis_title="Number of Documents",
            template="plotly_white",
            width=800,
            height=500,
        )
        return fig

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        status = "fitted" if self._is_fitted else "unfitted"
        return (
            f"{self.__class__.__name__}(method={self.method!r}, "
            f"n_topics={self.n_topics!r}, status={status!r})"
        )
