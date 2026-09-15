import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Literal

class Settings(BaseSettings):
    APP_NAME: str = "The Lenny Growth Assistant"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # LLM Provider Configuration
    # Supported: "ollama", "anthropic", "openai", "mock"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "finetunned_model:latest")
    
    # Anthropic Settings
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lenny_growth.db")
    
    # RAG Settings
    RELEVANCE_THRESHOLD: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.20"))
    MAX_RAG_RESULTS: int = int(os.getenv("MAX_RAG_RESULTS", "4"))
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
