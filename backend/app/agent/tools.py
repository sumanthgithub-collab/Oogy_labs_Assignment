import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.rag.retrieval import retrieval_engine
from app.providers.router import provider_router
from app.config import settings

logger = logging.getLogger(__name__)

async def search_transcripts_tool(query: str, top_k: int = 4, db: Session = None) -> Tuple[List[Dict[str, Any]], float]:
    """Retrieves relevant transcript chunks with metadata and similarity score."""
    return retrieval_engine.search(query=query, top_k=top_k, db=db)

async def generate_ship30_essay_tool(topic: str, grounded_context: str) -> str:
    """Generates a viral Ship 30 for 30 style essay based on grounded context."""
    system_prompt = (
        "You are an expert growth writer specializing in the 'Ship 30 for 30' essay format. "
        "Create an engaging, highly readable, actionable essay based strictly on the provided transcript context. "
        "Format requirements:\n"
        "- Title: Actionable headline\n"
        "- Hook: Strong opening pattern-interrupt statement\n"
        "- 3 Bullet Takeaways: Clear subheadings with tactical advice\n"
        "- TL;DR & One Action Step: Concise summary at the end."
    )
    prompt = f"Topic: {topic}\n\nGrounded Transcript Context:\n{grounded_context}\n\nWrite a complete Ship 30 for 30 essay now."
    return await provider_router.generate(prompt=prompt, system_prompt=system_prompt)

async def generate_ui_artifact_tool(title: str, topic: str, grounded_context: str) -> str:
    """Generates a standalone responsive HTML/CSS visual card artifact based on grounded context."""
    system_prompt = (
        "You are a master UI developer. Generate a complete standalone HTML document with embedded CSS. "
        "Do NOT include markdown backticks around the HTML. Output ONLY raw `<!DOCTYPE html>...</html>`. "
        "Design guidelines:\n"
        "- Modern dark theme matching slate (#0f172a, #1e293b) with Lenny orange accents (#ff6b00)\n"
        "- Clean card layout with clear typography, badge icons, and structured points\n"
        "- Responsive, elegant, wows at first glance."
    )
    prompt = f"Title: {title}\nTopic: {topic}\n\nGrounded Context:\n{grounded_context}\n\nGenerate standalone HTML document now."
    return await provider_router.generate(prompt=prompt, system_prompt=system_prompt)
