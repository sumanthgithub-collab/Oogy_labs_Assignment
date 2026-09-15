import pytest
from app.models.database import SessionLocal, init_db
from app.rag.ingestion import load_and_ingest_transcripts
from app.rag.retrieval import retrieval_engine

@pytest.fixture(autouse=True)
def setup_rag():
    init_db()
    db = SessionLocal()
    load_and_ingest_transcripts(db=db)
    retrieval_engine.index_chunks(db=db)
    db.close()
    yield

def test_ingestion_populates_chunks():
    db = SessionLocal()
    chunks = retrieval_engine.chunks_cache
    assert len(chunks) >= 6
    guests = [c.guest_name for c in chunks]
    assert "Shreyas Doshi" in guests
    assert "Elena Verna" in guests
    assert "Gibson Biddle" in guests
    db.close()

def test_retrieval_precision_for_known_frameworks():
    # Test 1: DHM Model
    results, max_score = retrieval_engine.search("What is Gibson Biddle DHM model?")
    assert len(results) > 0
    assert results[0]["guest_name"] == "Gibson Biddle"
    assert max_score > 0.15

    # Test 2: Product Led Growth
    results_plg, score_plg = retrieval_engine.search("Elena Verna product led growth loops freemium")
    assert len(results_plg) > 0
    assert results_plg[0]["guest_name"] == "Elena Verna"

def test_out_of_domain_query_scores_low():
    results, max_score = retrieval_engine.search("Quantum physics string theory particle accelerator")
    # Low or 0 score
    assert max_score < 0.15
