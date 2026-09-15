import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db, SessionModel, MessageModel, ArtifactModel, TranscriptChunkModel
from app.models.schemas import (
    SessionCreateSchema, SessionResponseSchema,
    MessageResponseSchema, ChatRequest,
    ModelConfigSchema, ArtifactResponseSchema, ArtifactCreateSchema
)
from app.providers.router import provider_router
from app.agent.orchestrator import agent_orchestrator
from app.agent.tools import generate_ship30_essay_tool, generate_ui_artifact_tool

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        chunks_count = db.query(TranscriptChunkModel).count()
        sessions_count = db.query(SessionModel).count()
        return {
            "status": "healthy",
            "database": "connected",
            "indexed_transcript_chunks": chunks_count,
            "active_sessions": sessions_count,
            "active_llm_provider": provider_router._active_provider_name
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database connectivity failed: {str(e)}")

# ==================== SESSIONS ====================

@router.get("/sessions", response_model=List[SessionResponseSchema], tags=["Sessions"])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    results = []
    for s in sessions:
        msg_count = db.query(MessageModel).filter(MessageModel.session_id == s.id).count()
        results.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "message_count": msg_count
        })
    return results

@router.post("/sessions", response_model=SessionResponseSchema, tags=["Sessions"])
def create_session(payload: SessionCreateSchema = SessionCreateSchema(), db: Session = Depends(get_db)):
    session_obj = SessionModel(title=payload.title or "New Growth Conversation")
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return {
        "id": session_obj.id,
        "title": session_obj.title,
        "created_at": session_obj.created_at,
        "updated_at": session_obj.updated_at,
        "message_count": 0
    }

@router.delete("/sessions/{session_id}", tags=["Sessions"])
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session_obj)
    db.commit()
    return {"message": "Session deleted successfully"}

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponseSchema], tags=["Sessions"])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(MessageModel)
        .filter(MessageModel.session_id == session_id)
        .order_by(MessageModel.created_at.asc())
        .all()
    )
    results = []
    for m in messages:
        artifacts = (
            db.query(ArtifactModel)
            .filter(ArtifactModel.message_id == m.id)
            .all()
        )
        art_dicts = [
            {
                "id": a.id,
                "title": a.title,
                "artifact_type": a.artifact_type,
                "content": a.content,
                "created_at": a.created_at.isoformat()
            }
            for a in artifacts
        ]
        results.append({
            "id": m.id,
            "session_id": m.session_id,
            "role": m.role,
            "content": m.content,
            "citations": m.citations or [],
            "created_at": m.created_at,
            "artifacts": art_dicts
        })
    return results

# ==================== CHAT ====================

@router.post("/chat", tags=["Chat"])
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    session_obj = db.query(SessionModel).filter(SessionModel.id == req.session_id).first()
    if not session_obj:
        session_obj = SessionModel(id=req.session_id, title=req.prompt[:35] + "...")
        db.add(session_obj)
        db.commit()

    # If first message, update session title from prompt
    first_msg = db.query(MessageModel).filter(MessageModel.session_id == req.session_id).first()
    if not first_msg:
        session_obj.title = req.prompt[:35] + "..."
        db.commit()

    result = await agent_orchestrator.process_user_query(
        session_id=req.session_id,
        user_prompt=req.prompt,
        db=db,
        force_artifact=req.force_artifact
    )

    asst_msg = result["message"]
    artifacts = result["artifacts"]

    art_dicts = [
        {
            "id": a.id,
            "title": a.title,
            "artifact_type": a.artifact_type,
            "content": a.content,
            "metadata": a.metadata_json or {},
            "created_at": a.created_at.isoformat()
        }
        for a in artifacts
    ]

    return {
        "id": asst_msg.id,
        "session_id": asst_msg.session_id,
        "role": asst_msg.role,
        "content": asst_msg.content,
        "citations": asst_msg.citations or [],
        "created_at": asst_msg.created_at,
        "artifacts": art_dicts
    }

# ==================== MODEL CONFIG ====================

@router.get("/config/model", response_model=ModelConfigSchema, tags=["Model Config"])
def get_model_config():
    return provider_router.get_config()

@router.post("/config/model", response_model=ModelConfigSchema, tags=["Model Config"])
def update_model_config(payload: dict):
    provider = payload.get("provider")
    model_name = payload.get("model_name")
    if not provider:
        raise HTTPException(status_code=400, detail="Field 'provider' is required")
    try:
        return provider_router.set_provider(provider_name=provider, model_name=model_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== ARTIFACTS ====================

@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponseSchema, tags=["Artifacts"])
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    art = db.query(ArtifactModel).filter(ArtifactModel.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {
        "id": art.id,
        "session_id": art.session_id,
        "message_id": art.message_id,
        "title": art.title,
        "artifact_type": art.artifact_type,
        "content": art.content,
        "metadata": art.metadata_json or {},
        "created_at": art.created_at
    }

@router.get("/sessions/{session_id}/artifacts", response_model=List[ArtifactResponseSchema], tags=["Artifacts"])
def get_session_artifacts(session_id: str, db: Session = Depends(get_db)):
    artifacts = (
        db.query(ArtifactModel)
        .filter(ArtifactModel.session_id == session_id)
        .order_by(ArtifactModel.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "session_id": a.session_id,
            "message_id": a.message_id,
            "title": a.title,
            "artifact_type": a.artifact_type,
            "content": a.content,
            "metadata": a.metadata_json or {},
            "created_at": a.created_at
        }
        for a in artifacts
    ]

@router.post("/artifacts/generate", response_model=ArtifactResponseSchema, tags=["Artifacts"])
async def generate_artifact_endpoint(payload: dict, db: Session = Depends(get_db)):
    session_id = payload.get("session_id")
    message_id = payload.get("message_id")
    artifact_type = payload.get("artifact_type", "essay") # 'essay' or 'html'
    topic = payload.get("topic", "Product & Growth Framework")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    # Fetch context from message if available
    context = ""
    if message_id:
        msg = db.query(MessageModel).filter(MessageModel.id == message_id).first()
        if msg:
            context = msg.content

    if artifact_type == "essay":
        content = await generate_ship30_essay_tool(topic=topic, grounded_context=context or topic)
        title = f"Ship 30 Essay: {topic[:40]}"
    else:
        content = await generate_ui_artifact_tool(title=topic, topic=topic, grounded_context=context or topic)
        title = f"Visual Card: {topic[:40]}"

    art = ArtifactModel(
        session_id=session_id,
        message_id=message_id,
        title=title,
        artifact_type=artifact_type,
        content=content,
        metadata_json={"generated_via": "explicit_action"}
    )
    db.add(art)
    db.commit()
    db.refresh(art)

    return {
        "id": art.id,
        "session_id": art.session_id,
        "message_id": art.message_id,
        "title": art.title,
        "artifact_type": art.artifact_type,
        "content": art.content,
        "metadata": art.metadata_json or {},
        "created_at": art.created_at
    }
