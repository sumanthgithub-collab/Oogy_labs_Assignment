import os
import json
import glob
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import TranscriptChunkModel, SessionLocal

logger = logging.getLogger(__name__)

TRANSCRIPT_DIR = os.getenv("TRANSCRIPT_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "transcripts"))

def load_and_ingest_transcripts(db: Session = None) -> int:
    """
    Ingests all transcript JSON files from data/transcripts into database.
    Returns the total number of chunks ingested.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # Search for transcript JSON files
        search_pattern = os.path.join(os.path.abspath(TRANSCRIPT_DIR), "*.json")
        json_files = glob.glob(search_pattern)
        
        if not json_files:
            logger.warning(f"No transcript files found at pattern: {search_pattern}")
            return 0

        # Check existing count
        existing_count = db.query(TranscriptChunkModel).count()
        if existing_count > 0:
            logger.info(f"Database already contains {existing_count} transcript chunks.")
            return existing_count

        total_ingested = 0
        for file_path in json_files:
            logger.info(f"Processing transcript file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            episode_id = data.get("episode_id", "ep-unknown")
            episode_title = data.get("title", "Lenny's Podcast Episode")
            guest_name = data.get("guest", "Expert Guest")
            guest_title = data.get("guest_title", "")
            topics = data.get("topics", [])
            segments = data.get("segments", [])

            for seg in segments:
                timestamp = seg.get("timestamp", "00:00:00")
                speaker = seg.get("speaker", guest_name)
                text = seg.get("text", "").strip()

                if not text:
                    continue

                chunk = TranscriptChunkModel(
                    episode_id=episode_id,
                    episode_title=episode_title,
                    guest_name=guest_name,
                    guest_title=guest_title,
                    timestamp=timestamp,
                    speaker=speaker,
                    topics=topics,
                    content=text
                )
                db.add(chunk)
                total_ingested += 1

        db.commit()
        logger.info(f"Successfully ingested {total_ingested} transcript chunks into database.")
        return total_ingested

    except Exception as e:
        logger.error(f"Error ingesting transcripts: {e}", exc_info=True)
        db.rollback()
        return 0
    finally:
        if close_db:
            db.close()
