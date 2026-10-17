"""Tests for the Flask API and the theme/session behaviour behind it."""

from __future__ import annotations

import os

os.environ["CHRONICLE_DISABLE_SBERT"] = "1"  # must precede the app import

import pytest

from chronicle.api import app as api_module
from chronicle.chatbot.intent import IntentDetector
from chronicle.chatbot.slots import SlotFiller


@pytest.fixture()
def client():
    api_module.app.config["TESTING"] = True
    # Errors must go through the JSON handler, as in production.
    api_module.app.config["PROPAGATE_EXCEPTIONS"] = False
    return api_module.app.test_client()


def test_health_and_ready(client):
    assert client.get("/api/health").get_json()["status"] == "healthy"
    r = client.get("/api/ready")
    assert r.status_code == 200 and r.get_json()["ready"] is True


def test_myths_filter_and_lookup(client):
    all_myths = client.get("/api/myths").get_json()
    hubris = client.get("/api/myths?theme=hubris").get_json()
    assert 0 < len(hubris) < len(all_myths)
    assert all(m["theme"] == "hubris" for m in hubris)
    first = all_myths[0]
    assert client.get(f"/api/myths/{first['id']}").get_json()["title"] == first["title"]
    assert client.get("/api/myths/nope").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [None, [], {"query": 5}, {}, {"query": "x" * 501}, {"query": "hi", "session_id": "bad id!"}],
)
def test_chat_rejects_bad_input(client, payload):
    r = client.post("/api/chat", json=payload)
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_chat_non_json_body(client):
    r = client.post("/api/chat", data="not json", content_type="text/plain")
    assert r.status_code == 400


def test_chat_answers_and_returns_session(client):
    r = client.post("/api/chat", json={"query": "Who is Athena?"})
    body = r.get_json()
    assert r.status_code == 200
    assert body["intent"] == "character_info"
    assert len(body["session_id"]) >= 8


def test_follow_up_memory_is_per_session(client):
    a, b = "session-aaaaaaaa", "session-bbbbbbbb"
    client.post("/api/chat", json={"query": "Tell me the story of Icarus", "session_id": a})

    followed = client.post("/api/chat", json={"query": "tell me more", "session_id": a}).get_json()
    assert followed["intent"] == "myth_summary"
    assert "Icarus" in followed["response"]

    # A different visitor has no previous myth to follow up on.
    other = client.post("/api/chat", json={"query": "tell me more", "session_id": b}).get_json()
    assert other["intent"] == "unknown"


def test_theme_question_is_understood(client):
    body = client.post("/api/chat", json={"query": "Which myths are about hubris?"}).get_json()
    assert body["intent"] == "theme"
    assert body["slots"]["theme"] == "hubris"
    assert "hubris" in body["response"].lower()


def test_similar_validates_top_k(client):
    assert client.get("/api/similar/Icarus?top_k=0").status_code == 400
    assert client.get("/api/similar/Icarus?top_k=abc").status_code == 400


def test_graph_path_validation(client):
    assert client.get("/api/graph/path").status_code == 400
    ok = client.get("/api/graph/path?source=Zeus&target=Hera")
    assert ok.status_code == 200


def test_unknown_api_route_is_json_404(client):
    r = client.get("/api/does-not-exist")
    assert r.status_code == 404
    assert r.get_json()["error"]


def test_security_headers(client):
    r = client.get("/api/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    "query,theme",
    [("hubris", "hubris"), ("stories about revenge", "revenge"), ("myths involving envy", "jealousy")],
)
def test_theme_intent_and_slot(query, theme):
    assert IntentDetector().detect(query)["intent"] == "theme"
    assert SlotFiller().fill(query, "theme")["theme"] == theme


# ---------------------------------------------------------------- new endpoints
def test_characters_list_and_profile(client):
    rows = client.get("/api/characters").get_json()
    assert rows and rows[0]["myth_count"] >= rows[-1]["myth_count"]
    gods = client.get("/api/characters?type=god").get_json()
    assert gods and all(r["type"] == "god" for r in gods)

    p = client.get("/api/characters/Minerva").get_json()  # Roman name resolves
    assert p["name"] == "Athena" and "Zeus" in p["family"]["parents"]
    assert client.get("/api/characters/Nobody%20Atall").status_code == 404


def test_compare_endpoint(client):
    r = client.get("/api/compare?a=Hera&b=Zeus").get_json()
    assert r["relationship"] == "Hera is Zeus's wife and sister."
    assert client.get("/api/compare?a=Hera").status_code == 400
    assert client.get("/api/compare?a=Hera&b=Nobody").status_code == 404
    assert client.get("/api/compare?a=" + "x" * 101 + "&b=Zeus").status_code == 400


def test_motif_endpoints(client):
    motifs = client.get("/api/motifs").get_json()
    assert len(motifs) >= 8 and all(m["count"] > 0 for m in motifs)
    rows = client.get("/api/motifs/transformation").get_json()
    assert rows and rows[0]["snippet"]
    assert client.get("/api/motifs/nope").status_code == 404


def test_search_endpoint(client):
    hits = client.get("/api/search?q=sculptor+statue+love").get_json()
    assert hits and "Pygmalion" in hits[0]["title"]
    assert client.get("/api/search").status_code == 400
    assert client.get("/api/search?q=x&top_k=99").status_code == 400
    assert client.get("/api/search?q=x&top_k=abc").status_code == 400


def test_quiz_endpoint(client):
    q = client.get("/api/quiz?n=5&seed=3").get_json()
    assert len(q) == 5 and q == client.get("/api/quiz?n=5&seed=3").get_json()
    assert client.get("/api/quiz?n=0").status_code == 400
    assert client.get("/api/quiz?seed=abc").status_code == 400


def test_graph_separates_places_from_people(client):
    g = client.get("/api/graph").get_json()
    names = {n["id"] for n in g["nodes"]}
    assert "Zeus" in names and "Delphi" not in names
    assert "Delphi" in g["locations"] or g["locations"]
    assert all(n["type"].upper() != "LOCATION" for n in g["nodes"])
    # genealogy is in the graph: Cronus -> Zeus
    assert any(e["source"] == "Cronus" and e["target"] == "Zeus" for e in g["edges"])
