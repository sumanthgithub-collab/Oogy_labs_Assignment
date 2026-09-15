from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime

class CitationSchema(BaseModel):
    guest_name: str
    episode_title: str
    episode_id: str
    timestamp: Optional[str] = "00:00:00"
    snippet: str
    relevance_score: float

class MessageCreateSchema(BaseModel):
    session_id: str
    prompt: str

class MessageResponseSchema(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: List[CitationSchema] = []
    created_at: datetime.datetime
    artifacts: List[Dict[str, Any]] = []

class SessionCreateSchema(BaseModel):
    title: Optional[str] = "New Growth Conversation"

class SessionResponseSchema(BaseModel):
    id: str
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    message_count: Optional[int] = 0

class ModelConfigSchema(BaseModel):
    provider: str # 'ollama', 'anthropic', 'openai', 'mock'
    model_name: str
    status: str = "active"
    available_providers: List[str] = ["ollama", "anthropic", "openai", "mock"]

class ArtifactCreateSchema(BaseModel):
    session_id: str
    message_id: Optional[str] = None
    title: str
    artifact_type: str # 'markdown', 'html', 'essay'
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class ArtifactResponseSchema(BaseModel):
    id: str
    session_id: str
    message_id: Optional[str] = None
    title: str
    artifact_type: str
    content: str
    metadata: Dict[str, Any] = {}
    created_at: datetime.datetime

class ChatRequest(BaseModel):
    session_id: str
    prompt: str
    force_artifact: Optional[str] = None # 'essay', 'html', 'markdown' or None
