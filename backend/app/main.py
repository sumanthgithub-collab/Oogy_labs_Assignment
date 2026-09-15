import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db, SessionLocal
from app.rag.ingestion import load_and_ingest_transcripts
from app.rag.retrieval import retrieval_engine
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lenny_growth_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Lenney Growth Assistant Backend...")
    # 1. Init Database Schemas
    init_db()
    
    # 2. Ingest Transcripts
    db = SessionLocal()
    try:
        count = load_and_ingest_transcripts(db=db)
        logger.info(f"Ingested {count} transcript chunks into DB.")
        
        # 3. Index Retrieval Engine
        retrieval_engine.index_chunks(db=db)
    finally:
        db.close()
        
    logger.info("Backend Startup Complete!")
    yield
    logger.info("Shutting down Lenney Growth Assistant Backend...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Conversational Product Management & Growth Assistant powered by grounded transcript RAG.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix=settings.API_V1_PREFIX)
app.include_router(router) # Also mount health directly at root /health
