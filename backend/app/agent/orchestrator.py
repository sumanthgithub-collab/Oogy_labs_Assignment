import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.agent.tools import (
    search_transcripts_tool,
    generate_ship30_essay_tool,
    generate_ui_artifact_tool
)
from app.providers.router import provider_router
from app.config import settings
from app.models.database import SessionModel, MessageModel, ArtifactModel

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    async def process_user_query(
        self,
        session_id: str,
        user_prompt: str,
        db: Session,
        force_artifact: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates retrieval, grounding check, answer synthesis, citations, and artifact generation.
        """
        # Fetch multi-turn session context (last 6 messages)
        history_msgs = (
            db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.desc())
            .limit(6)
            .all()
        )
        history_msgs.reverse()

        # Step 1: Retrieval
        results, max_score = await search_transcripts_tool(query=user_prompt, top_k=settings.MAX_RAG_RESULTS, db=db)

        # Step 2: Grounding / Relevance Threshold Check
        if not results or max_score < settings.RELEVANCE_THRESHOLD:
            refusal_text = (
                f"The Lenny Growth Assistant knowledge base does not contain sufficient grounded information to answer: "
                f"**\"{user_prompt}\"**.\n\n"
                "Our current knowledge base covers product management, growth strategies, PLG, and leadership frameworks "
                "from featured guests like **Shreyas Doshi** (LNO Framework), **Elena Verna** (PLG Growth Loops), "
                "**Gibson Biddle** (DHM Model), **Brian Balfour** (Four Fits), **Casey Winters** (Retention Engine), "
                "and **Marty Cagan** (Empowered Teams)."
            )
            
            # Save User Message
            user_msg = MessageModel(session_id=session_id, role="user", content=user_prompt)
            db.add(user_msg)
            db.flush()

            # Save Assistant Refusal Message
            asst_msg = MessageModel(
                session_id=session_id,
                role="assistant",
                content=refusal_text,
                citations=[]
            )
            db.add(asst_msg)
            db.commit()

            return {
                "message": asst_msg,
                "citations": [],
                "artifacts": []
            }

        # Format Citations & Context
        citations = []
        context_blocks = []
        for r in results:
            cit = {
                "guest_name": r["guest_name"],
                "episode_title": r["episode_title"],
                "episode_id": r["episode_id"],
                "timestamp": r["timestamp"],
                "snippet": r["content"][:200] + "...",
                "relevance_score": r["relevance_score"]
            }
            citations.append(cit)
            context_blocks.append(
                f"[{r['guest_name']} - {r['episode_title']} @ {r['timestamp']}]\n{r['content']}"
            )

        grounded_context = "\n\n---\n\n".join(context_blocks)

        # Step 3: Synthesize Grounded Answer
        system_prompt = (
            "You are The Lenny Growth Assistant, a world-class product management and growth advisor. "
            "Answer the user's question using ONLY the grounded transcript context provided below. "
            "Structure your answer with clear headers, bullet points, and cite the guests (e.g. Shreyas Doshi, Elena Verna) "
            "when referencing their concepts. If the context does not fully cover an aspect, explicitly acknowledge the limitation."
        )

        user_prompt_with_context = f"Question: {user_prompt}\n\nGrounded Transcript Context:\n{grounded_context}"
        answer_text = await provider_router.generate(prompt=user_prompt_with_context, system_prompt=system_prompt)

        # Save User Message
        user_msg = MessageModel(session_id=session_id, role="user", content=user_prompt)
        db.add(user_msg)
        db.flush()

        # Save Assistant Message
        asst_msg = MessageModel(
            session_id=session_id,
            role="assistant",
            content=answer_text,
            citations=citations
        )
        db.add(asst_msg)
        db.flush()

        # Step 4: Artifact Generation (if requested or forced)
        generated_artifacts = []
        prompt_lower = user_prompt.lower()
        
        should_gen_essay = force_artifact == "essay" or "essay" in prompt_lower or "ship 30" in prompt_lower
        should_gen_html = force_artifact == "html" or "html" in prompt_lower or "visual" in prompt_lower or "card" in prompt_lower or "framework card" in prompt_lower

        if should_gen_essay:
            essay_content = await generate_ship30_essay_tool(topic=user_prompt, grounded_context=grounded_context)
            essay_art = ArtifactModel(
                session_id=session_id,
                message_id=asst_msg.id,
                title=f"Ship 30 Essay: {user_prompt[:40]}",
                artifact_type="essay",
                content=essay_content,
                metadata_json={"guest": citations[0]["guest_name"] if citations else "Lenny's Podcast"}
            )
            db.add(essay_art)
            db.flush()
            generated_artifacts.append(essay_art)

        if should_gen_html:
            html_content = await generate_ui_artifact_tool(
                title=f"{citations[0]['guest_name']} Framework",
                topic=user_prompt,
                grounded_context=grounded_context
            )
            html_art = ArtifactModel(
                session_id=session_id,
                message_id=asst_msg.id,
                title=f"Visual Card: {user_prompt[:40]}",
                artifact_type="html",
                content=html_content,
                metadata_json={"guest": citations[0]["guest_name"] if citations else "Lenny's Podcast"}
            )
            db.add(html_art)
            db.flush()
            generated_artifacts.append(html_art)

        db.commit()

        return {
            "message": asst_msg,
            "citations": citations,
            "artifacts": generated_artifacts
        }

agent_orchestrator = AgentOrchestrator()
