import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import Base, engine, SessionLocal, init_db
from app.rag.ingestion import load_and_ingest_transcripts
from app.rag.retrieval import retrieval_engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    load_and_ingest_transcripts(db=db)
    retrieval_engine.index_chunks(db=db)
    db.close()
    yield

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["indexed_transcript_chunks"] > 0

def test_sessions_crud():
    # 1. Create session
    create_res = client.post("/api/v1/sessions", json={"title": "Test Strategy Session"})
    assert create_res.status_code == 200
    sess_data = create_res.json()
    session_id = sess_data["id"]
    assert sess_data["title"] == "Test Strategy Session"

    # 2. List sessions
    list_res = client.get("/api/v1/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert any(s["id"] == session_id for s in sessions)

    # 3. Delete session
    del_res = client.delete(f"/api/v1/sessions/{session_id}")
    assert del_res.status_code == 200

def test_model_config_endpoint():
    # Get config
    get_res = client.get("/api/v1/config/model")
    assert get_res.status_code == 200
    config = get_res.json()
    assert "provider" in config

    # Update config to mock
    post_res = client.post("/api/v1/config/model", json={"provider": "mock", "model_name": "mock-test"})
    assert post_res.status_code == 200
    updated = post_res.json()
    assert updated["provider"] == "mock"

def test_chat_grounded_query():
    # Force provider to mock for fast test execution
    client.post("/api/v1/config/model", json={"provider": "mock"})

    # Create session
    sess_res = client.post("/api/v1/sessions", json={"title": "LNO Query"})
    session_id = sess_res.json()["id"]

    # Send grounded question
    chat_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "prompt": "What is Shreyas Doshi's LNO framework for time management?"
    })
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["role"] == "assistant"
    assert len(chat_data["citations"]) > 0
    assert any("Shreyas Doshi" in c["guest_name"] for c in chat_data["citations"])

def test_chat_out_of_domain_refusal():
    # Force provider to mock
    client.post("/api/v1/config/model", json={"provider": "mock"})

    sess_res = client.post("/api/v1/sessions", json={"title": "Out of domain"})
    session_id = sess_res.json()["id"]

    # Ask ungrounded question
    chat_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "prompt": "How do I make chocolate chip cookies in an air fryer?"
    })
    assert chat_res.status_code == 200
    data = chat_res.json()
    # Citations should be empty due to refusal threshold
    assert len(data["citations"]) == 0
    assert "does not contain" in data["content"] or "knowledge base" in data["content"]

def test_artifact_generation_and_fetch():
    client.post("/api/v1/config/model", json={"provider": "mock"})

    sess_res = client.post("/api/v1/sessions", json={"title": "Artifact Session"})
    session_id = sess_res.json()["id"]

    # Generate essay artifact explicitly
    art_res = client.post("/api/v1/artifacts/generate", json={
        "session_id": session_id,
        "artifact_type": "essay",
        "topic": "Shreyas Doshi LNO Framework"
    })
    assert art_res.status_code == 200
    art_data = art_res.json()
    assert art_data["artifact_type"] == "essay"
    assert "Ship 30" in art_data["title"] or "Essay" in art_data["title"]

    # Fetch by ID
    get_art = client.get(f"/api/v1/artifacts/{art_data['id']}")
    assert get_art.status_code == 200
    assert get_art.json()["id"] == art_data["id"]
