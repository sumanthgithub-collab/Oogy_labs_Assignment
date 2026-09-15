import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.models.database import TranscriptChunkModel, SessionLocal
from app.config import settings

logger = logging.getLogger(__name__)

class RetrievalEngine:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.chunks_cache: List[TranscriptChunkModel] = []
        self._is_indexed = False

    def index_chunks(self, db: Session = None):
        """Builds TF-IDF vector index over all transcript chunks in DB."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            chunks = db.query(TranscriptChunkModel).all()
            if not chunks:
                logger.warning("No chunks to index in RetrievalEngine.")
                self._is_indexed = False
                return

            self.chunks_cache = chunks
            corpus = [f"{c.guest_name} {c.episode_title} {' '.join(c.topics or [])} {c.content}" for c in chunks]
            
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            self._is_indexed = True
            logger.info(f"Indexed {len(chunks)} transcript chunks into TF-IDF vector store.")
        except Exception as e:
            logger.error(f"Error indexing chunks: {e}")
            self._is_indexed = False
        finally:
            if close_db:
                db.close()

    def search(self, query: str, top_k: int = 4, db: Session = None) -> Tuple[List[Dict[str, Any]], float]:
        """
        Searches knowledge base for top matching chunks.
        Returns tuple of (ranked_results, max_score).
        """
        if not self._is_indexed or self.tfidf_matrix is None:
            self.index_chunks(db=db)

        if not self._is_indexed or not self.chunks_cache:
            return [], 0.0

        # Transform query
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        if len(similarities) == 0:
            return [], 0.0

        top_indices = np.argsort(similarities)[::-1][:top_k]
        max_score = float(similarities[top_indices[0]]) if len(top_indices) > 0 else 0.0

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.01: # Filter absolute zero match noise
                chunk = self.chunks_cache[idx]
                results.append({
                    "chunk_id": chunk.id,
                    "guest_name": chunk.guest_name,
                    "guest_title": chunk.guest_title,
                    "episode_title": chunk.episode_title,
                    "episode_id": chunk.episode_id,
                    "timestamp": chunk.timestamp or "00:00:00",
                    "speaker": chunk.speaker or chunk.guest_name,
                    "content": chunk.content,
                    "topics": chunk.topics or [],
                    "relevance_score": round(score, 4)
                })

        return results, max_score

retrieval_engine = RetrievalEngine()
