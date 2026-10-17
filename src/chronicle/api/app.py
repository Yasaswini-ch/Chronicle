"""Flask backend service for the Chronicle Greek Mythology NLP platform.

Serves the myth corpus, the conversational ChatEngine, the knowledge graph,
semantic similarity search and analytical insights to the React frontend, and
serves the built frontend itself when ``frontend/dist`` exists.

Configuration (environment variables):

``CHRONICLE_ROOT``
    Directory holding ``data/`` and ``frontend/dist`` (defaults to the source
    checkout; the Docker image sets it to ``/app`` because the package is
    installed into site-packages).
``CHRONICLE_HOST`` / ``CHRONICLE_PORT``
    Bind address (default ``127.0.0.1:8000``; the Docker image sets ``0.0.0.0``).
``CHRONICLE_CORS_ORIGINS``
    Comma-separated allowed origins. CORS is disabled unless this is set; the
    Vite dev server proxies ``/api`` so it is not needed in development.
``CHRONICLE_ENABLE_SBERT``
    Set to ``1`` to also load Sentence-BERT (needs the ``ml`` extra). It loads in the
    background after the server is already answering, and search then combines it with
    BM25. Off by default: BM25 alone scored as well or better on the gold set and starts
    instantly. ``CHRONICLE_DISABLE_SBERT=1`` forces it off.
``CHRONICLE_LOG_LEVEL``
    Logging level (default ``INFO``).
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import threading
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import Any

# Ensure project src/ is on sys.path when run as a script
PROJECT_ROOT = Path(
    os.environ.get("CHRONICLE_ROOT") or Path(__file__).resolve().parent.parent.parent.parent
)
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from chronicle.chatbot.engine import ChatEngine
from chronicle.insights.dashboard import InsightsDashboard
from chronicle.insights.knowledge import MythKnowledge
from chronicle.ner.knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)

MYTHS_PATH = PROJECT_ROOT / "data" / "processed" / "myths.json"
RESULTS_PATH = PROJECT_ROOT / "data" / "output" / "pipeline_results.json"
DIST_DIR = PROJECT_ROOT / "frontend" / "dist"

MAX_QUERY_CHARS = 500
MAX_PATH_PARAM_CHARS = 100
MAX_SESSIONS = 1000
MAX_TURNS_PER_SESSION = 20
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

app = Flask(
    __name__,
    static_folder=str(DIST_DIR) if DIST_DIR.exists() else None,
    static_url_path="",
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024  # chat payloads are tiny
app.json.sort_keys = False

_cors_origins = [o.strip() for o in os.environ.get("CHRONICLE_CORS_ORIGINS", "").split(",") if o.strip()]
if _cors_origins:
    from flask_cors import CORS

    CORS(app, origins=_cors_origins)

# Global in-memory resources (read-only after start-up, except chat sessions)
myths_data: list[dict[str, Any]] = []
knowledge_graph = KnowledgeGraph()
chat_engine: ChatEngine | None = None
dashboard_engine = InsightsDashboard()
sbert_loaded = False


class SessionStore:
    """Thread-safe, size-bounded per-session chat history.

    Follow-up questions ("tell me more") need memory of the previous turn, but
    that memory must never leak between visitors, and must not grow forever.
    """

    def __init__(self, max_sessions: int = MAX_SESSIONS, max_turns: int = MAX_TURNS_PER_SESSION):
        self._sessions: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
        self._lock = threading.Lock()
        self._max_sessions = max_sessions
        self._max_turns = max_turns

    def get(self, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            history = self._sessions.setdefault(session_id, [])
            self._sessions.move_to_end(session_id)
            while len(self._sessions) > self._max_sessions:
                self._sessions.popitem(last=False)
            return history

    def trim(self, history: list[dict[str, Any]]) -> None:
        with self._lock:
            del history[: max(0, len(history) - self._max_turns)]


sessions = SessionStore()
# ChatEngine mutates the supplied history list; serialise engine calls per
# process so a history list is never appended to concurrently.
_chat_lock = threading.Lock()


def _semantic_search_enabled() -> bool:
    """Sentence-BERT is opt-in (CHRONICLE_ENABLE_SBERT=1); the default is instant BM25 search."""
    return os.environ.get("CHRONICLE_ENABLE_SBERT") == "1" and os.environ.get("CHRONICLE_DISABLE_SBERT") != "1"


def _load_semantic_search() -> None:
    """Load Sentence-BERT and enable hybrid search; failures leave BM25 in place."""
    global sbert_loaded
    try:
        from chronicle.representation.sbert import SBERTRepresentation

        chat_engine.retriever.attach_sbert(SBERTRepresentation())
        sbert_loaded = True
        logger.info("Semantic search ready (Sentence-BERT + BM25 hybrid)")
    except Exception as exc:  # noqa: BLE001 - semantic search is optional
        logger.warning("Semantic search unavailable, staying on BM25: %s", exc)


def init_app_state() -> None:
    """Load myth corpus, build knowledge graph, and initialize chat engine."""
    global myths_data, chat_engine, sbert_loaded

    if MYTHS_PATH.exists():
        with open(MYTHS_PATH, "r", encoding="utf-8") as f:
            myths_data = json.load(f)
    else:
        logger.error("Myth corpus not found at %s", MYTHS_PATH)

    knowledge_graph.build_from_annotations(myths_data)

    knowledge = MythKnowledge(myths_data)
    knowledge_graph.add_family(knowledge.family, knowledge._types)
    # Start answering immediately with BM25; Sentence-BERT (slow to import and to encode the
    # corpus) is loaded in the background and switched on when ready.
    chat_engine = ChatEngine(
        myths=myths_data,
        knowledge_graph=knowledge_graph,
        knowledge=knowledge,
    )
    semantic = _semantic_search_enabled()
    logger.info("Chronicle ready: %d myths (search: %s)", len(myths_data),
                "BM25, Sentence-BERT loading in background" if semantic else "BM25")
    if semantic:
        threading.Thread(target=_load_semantic_search, name="sbert-loader", daemon=True).start()


# Perform initialization at module import time
init_app_state()


# ---------------------------------------------------------------------------
# Cross-cutting: errors and headers
# ---------------------------------------------------------------------------

def _error(status: int, message: str):
    return jsonify({"error": message}), status


def _int_arg(name: str, default: int | None, lo: int, hi: int) -> tuple[int | None, tuple | None]:
    """Parse an optional integer query parameter strictly.

    ``request.args.get(type=int)`` silently falls back to the default on bad
    input, which would hide client bugs; here a malformed or out-of-range value
    is a 400. Returns ``(value, error_response)``.
    """
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default, None
    try:
        value = int(raw)
    except ValueError:
        return None, _error(400, f"'{name}' must be an integer between {lo} and {hi}")
    if not lo <= value <= hi:
        return None, _error(400, f"'{name}' must be an integer between {lo} and {hi}")
    return value, None


@app.errorhandler(HTTPException)
def handle_http_error(exc: HTTPException):
    if request.path.startswith("/api/"):
        return _error(exc.code or 500, exc.description or exc.name)
    return exc


@app.errorhandler(Exception)
def handle_unexpected_error(exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.path)
    return _error(500, "Internal server error")


@app.after_request
def add_security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if request.path.startswith("/api/"):
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """Liveness probe: the process is up."""
    return jsonify({"status": "healthy", "num_myths": len(myths_data)})


@app.route("/api/ready", methods=["GET"])
def ready():
    """Readiness probe: corpus loaded and chat engine initialised."""
    ok = bool(myths_data) and chat_engine is not None
    body = {
        "ready": ok,
        "num_myths": len(myths_data),
        "semantic_search": sbert_loaded,
    }
    return jsonify(body), (200 if ok else 503)


@app.route("/api/myths", methods=["GET"])
def get_myths():
    """Return all myths, optionally filtered by theme or keyword."""
    theme = request.args.get("theme", "")[:MAX_PATH_PARAM_CHARS]
    search = request.args.get("search", "")[:MAX_PATH_PARAM_CHARS]

    results = myths_data
    if theme and theme != "all":
        results = [m for m in results if m.get("theme", "").lower() == theme.lower()]
    if search.strip():
        q = search.strip().lower()
        results = [
            m for m in results
            if q in m.get("title", "").lower()
            or q in m.get("text", "").lower()
            or any(
                q in (c.get("name", "") if isinstance(c, dict) else str(c)).lower()
                for c in m.get("characters", [])
            )
        ]
    return jsonify(results)


@app.route("/api/myths/<myth_id>", methods=["GET"])
def get_myth(myth_id: str):
    """Retrieve a single myth by ID or title."""
    for m in myths_data:
        if m.get("id") == myth_id or m.get("title", "").lower() == myth_id.lower():
            return jsonify(m)
    return _error(404, "Myth not found")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process a conversational query through the Chronicle ChatEngine.

    Body: ``{"query": str, "session_id"?: str}``. When ``session_id`` is
    omitted a fresh one is generated, so the request is stateless; clients that
    want follow-ups send back the ``session_id`` from the previous response.
    """
    if chat_engine is None:
        return _error(503, "Chat engine initializing")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error(400, "Request body must be a JSON object")

    query = data.get("query")
    if not isinstance(query, str):
        return _error(400, "'query' must be a string")
    query = query.strip()
    if len(query) > MAX_QUERY_CHARS:
        return _error(400, f"'query' must be at most {MAX_QUERY_CHARS} characters")

    session_id = data.get("session_id")
    if session_id is None:
        session_id = uuid.uuid4().hex
    elif not isinstance(session_id, str) or not SESSION_ID_RE.match(session_id):
        return _error(400, "'session_id' must be 8-64 characters of [A-Za-z0-9_-]")

    history = sessions.get(session_id)
    with _chat_lock:
        result = chat_engine.chat(query, history=history)
        sessions.trim(history)

    # The stored turn is returned as-is, so copy before adding the session id.
    return jsonify({**result, "session_id": session_id})


@app.route("/api/characters", methods=["GET"])
def list_characters():
    """All characters with type and myth count, most prominent first."""
    if chat_engine is None:
        return _error(503, "Chat engine initializing")
    rows = chat_engine.knowledge.characters()
    kind = request.args.get("type", "").lower()
    if kind:
        rows = [r for r in rows if r["type"] == kind]
    return jsonify(rows)


@app.route("/api/characters/<name>", methods=["GET"])
def get_character(name: str):
    """Profile of one character: aliases, family, themes, myths, companions."""
    if chat_engine is None:
        return _error(503, "Chat engine initializing")
    profile = chat_engine.knowledge.profile(name[:MAX_PATH_PARAM_CHARS])
    if profile is None:
        return _error(404, "Character not found")
    return jsonify(profile)


@app.route("/api/compare", methods=["GET"])
def compare_characters():
    """Side-by-side comparison of two characters (``?a=Athena&b=Ares``)."""
    if chat_engine is None:
        return _error(503, "Chat engine initializing")
    a, b = request.args.get("a", "").strip(), request.args.get("b", "").strip()
    if not a or not b:
        return _error(400, "'a' and 'b' are required")
    if max(len(a), len(b)) > MAX_PATH_PARAM_CHARS:
        return _error(400, "'a' and 'b' are too long")
    result = chat_engine.knowledge.compare(a, b)
    if result is None:
        return _error(404, "Character not found")
    return jsonify(result)


@app.route("/api/motifs", methods=["GET"])
def list_motifs():
    """Recurring story patterns and how many myths show each."""
    if chat_engine is None:
        return _error(503, "Chat engine initializing")
    return jsonify(chat_engine.knowledge.motifs())


@app.route("/api/motifs/<motif_id>", methods=["GET"])
def get_motif(motif_id: str):
    """Myths showing one motif, strongest first, each with a quoted passage."""
    if chat_engine is None:
        return _error(503, "Chat engine initializing")
    rows = chat_engine.knowledge.motif_myths(motif_id)
    if rows is None:
        return _error(404, "Motif not found")
    return jsonify(rows)


@app.route("/api/search", methods=["GET"])
def search_myths():
    """Ranked free-text search (BM25) over titles, characters and text."""
    if chat_engine is None:
        return _error(503, "Chat engine initializing")
    q = request.args.get("q", "").strip()
    if not q:
        return _error(400, "'q' is required")
    if len(q) > MAX_QUERY_CHARS:
        return _error(400, f"'q' must be at most {MAX_QUERY_CHARS} characters")
    top_k, err = _int_arg("top_k", 8, 1, 20)
    if err:
        return err
    hits = chat_engine.knowledge.search(q, top_k=top_k)
    return jsonify([
        {"id": m["id"], "title": m["title"], "theme": m.get("theme"), "themes": m.get("themes", []),
         "source": m.get("source", ""), "characters": [c["name"] for c in m.get("characters", [])][:6],
         "snippet": m.get("text", "")[:220]}
        for m in hits
    ])


@app.route("/api/similar/<myth_title_or_id>", methods=["GET"])
def get_similar_myths(myth_title_or_id: str):
    """Retrieve semantically similar myths by embedding distance."""
    if chat_engine is None or not chat_engine.retriever:
        return _error(503, "Retriever not initialized")

    top_k, err = _int_arg("top_k", 3, 1, 10)
    if err:
        return err

    similar = chat_engine.retriever.retrieve_similar(
        myth_title_or_id[:MAX_PATH_PARAM_CHARS], top_k=top_k
    )
    return jsonify(similar)


@app.route("/api/graph", methods=["GET"])
def get_graph():
    """Return nodes and edges for the interactive Pantheon relational network."""
    nodes = []
    edges = []
    locations = []

    for node in knowledge_graph.characters:
        info = knowledge_graph.get_character_info(node)
        if str(info.get("type", "")).upper() == "LOCATION":
            locations.append(node)  # places carry no relations; keep them out of the people graph
            continue
        nodes.append({
            "id": node,
            "label": node,
            "type": info.get("type", "figure"),
            "degree": info.get("total_degree", 0),
            "myths": info.get("myths", []),
        })

    for u, v, data in knowledge_graph._graph.edges(data=True):
        rel = data.get("relation") or data.get("predicate") or "connected_to"
        edges.append({
            "source": u,
            "target": v,
            "relation": rel,
            "myth": data.get("myth"),
        })

    return jsonify({
        "nodes": nodes,
        "edges": edges,
        "locations": locations,
        "stats": knowledge_graph.statistics(),
    })


@app.route("/api/graph/path", methods=["GET"])
def get_path():
    """Trace shortest connection path between two figures."""
    source = request.args.get("source", "").strip()
    target = request.args.get("target", "").strip()
    if not source or not target:
        return _error(400, "'source' and 'target' are required")
    if max(len(source), len(target)) > MAX_PATH_PARAM_CHARS:
        return _error(400, "'source' and 'target' are too long")

    return jsonify({
        "source": source,
        "target": target,
        "path": knowledge_graph.find_path(source, target),
    })


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Return derived leaderboard statistics and theme frequencies."""
    stats = dashboard_engine.get_leaderboard_stats(myths_data, knowledge_graph)
    theme_counts: dict[str, int] = {}
    for m in myths_data:
        t = m.get("theme", "unknown")
        theme_counts[t] = theme_counts.get(t, 0) + 1

    return jsonify({
        "leaderboard": stats,
        "theme_distribution": theme_counts,
        "total_myths": len(myths_data),
        "total_words": sum(len(m.get("text", "").split()) for m in myths_data),
    })


@app.route("/api/benchmarks", methods=["GET"])
def get_benchmarks():
    """Return pipeline execution and model benchmarking metrics."""
    if RESULTS_PATH.exists():
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"status": "Pipeline results not yet generated"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path: str):
    """Serve the compiled React frontend if available."""
    if path.startswith("api/"):
        return _error(404, "Not found")
    if DIST_DIR.exists():
        target = DIST_DIR / path
        if path != "" and target.exists() and not target.is_dir():
            return send_from_directory(str(DIST_DIR), path)
        return send_from_directory(str(DIST_DIR), "index.html")
    return jsonify({"message": "Chronicle API is active. Frontend dist not found."})


def main() -> None:
    """Run the API with a production WSGI server (waitress)."""
    logging.basicConfig(
        level=os.environ.get("CHRONICLE_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    host = os.environ.get("CHRONICLE_HOST", "127.0.0.1")
    port = int(os.environ.get("CHRONICLE_PORT", "8000"))

    from waitress import serve

    logger.info("Serving Chronicle on http://%s:%d", host, port)
    serve(app, host=host, port=port, threads=8)


if __name__ == "__main__":
    main()
