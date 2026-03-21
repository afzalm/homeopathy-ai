"""
Chat Routes
===========
POST /api/v1/chat/{session_id}/message  — send a message, get AI response
POST /api/v1/chat/{session_id}/analyse  — trigger full remedy analysis
GET  /api/v1/chat/{session_id}/history  — get conversation history
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from core.database import get_db
from services.session_manager import SessionManager
from services.symptom_extractor import SymptomExtractor
from services.repertory_engine import RepertoryEngine
from services.rag_service import MateriaMedicaRAG
from services.remedy_ranker import RemedyRanker
from llm.case_agent import CaseAgent
from database.models import MessageRole, SessionStage
from models.schemas import (
    ChatRequest, ChatResponse, AnalysisResponse,
    MessageResponse, RemedyScore, MateriaMedicaExcerpt
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{session_id}/message", response_model=ChatResponse)
async def send_message(
    session_id: str,
    body:       ChatRequest,
    db:         AsyncSession = Depends(get_db),
):
    """
    Main conversation endpoint.

    Flow:
    1. Store user message
    2. Extract symptoms
    3. Update session state
    4. Check if analysis ready
    5. Plan next question
    6. Generate LLM response
    7. Store assistant message
    8. Return response
    """
    manager   = SessionManager(db)
    extractor = SymptomExtractor()
    agent     = CaseAgent()

    # Verify session exists
    session = await manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    current_stage = session.stage

    # 1. Store user message
    user_msg = await manager.store_message(
        session_id, MessageRole.user, body.message
    )

    # 2. Extract symptoms from user message
    extracted = await extractor.extract(body.message)
    logger.info(f"Extracted {len(extracted)} symptoms from session {session_id}")

    # 3. Update session state with extracted symptoms
    await manager.update_symptoms(session_id, extracted, user_msg.id)

    # Advance stage on first message
    if session.stage == SessionStage.initial:
        current_stage = await manager.advance_stage(session_id)

    # 4. Check if enough rubrics collected for analysis
    analysis_ready = await manager.is_analysis_ready(session_id)

    # 5. Plan next question (or None if ready)
    next_question = None if analysis_ready else await manager.plan_next_question(session_id)

    # 6. Get conversation history for LLM context
    history = await manager.get_conversation_history(session_id)
    conversation = [
        {"role": msg.role.value, "content": msg.content}
        for msg in history
        if msg.id != user_msg.id  # exclude message we just added
    ]

    # 7. Generate LLM response
    try:
        reply = await agent.generate_response(
            conversation_history=conversation,
            session_state=await manager.build_state_summary(session_id),
            next_question=next_question,
        )
    except NotImplementedError:
        # LLM not yet configured — return rule-based response
        if analysis_ready:
            reply = "Thank you. I have collected enough information to analyse your symptoms. Please request the analysis."
        elif next_question:
            reply = next_question
        else:
            reply = "Thank you for sharing that. Could you tell me more?"

    # 8. Store assistant response
    assistant_msg = await manager.store_message(
        session_id, MessageRole.assistant, reply
    )

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        stage=current_stage,
        symptoms_extracted=extracted,
        analysis_ready=analysis_ready,
        message_id=assistant_msg.id,
    )


@router.post("/{session_id}/analyse", response_model=AnalysisResponse)
async def analyse_case(
    session_id: str,
    db:         AsyncSession = Depends(get_db),
):
    """
    Trigger full remedy analysis for a session.

    Flow:
    1. Load session rubrics
    2. Score remedies via repertory graph
    3. Retrieve Materia Medica via RAG
    4. Apply weighted ranking
    5. Generate explanation
    6. Return structured analysis
    """
    manager  = SessionManager(db)
    engine   = RepertoryEngine()
    rag      = MateriaMedicaRAG()
    ranker   = RemedyRanker()
    agent    = CaseAgent()

    session = await manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. Load rubrics
    rubric_paths = await manager.get_session_rubric_paths(session_id)
    if not rubric_paths:
        raise HTTPException(
            status_code=422,
            detail="No rubrics collected yet. Continue the consultation first."
        )

    state_summary = await manager.build_state_summary(session_id)

    # 2. Score remedies from repertory graph
    candidates = await engine.score_remedies(rubric_paths)
    top_remedy_names = [c.name for c in candidates[:5]]

    # 3. Collect symptom text for RAG query
    all_symptoms = (
        state_summary["symptoms"]["location"] +
        state_summary["symptoms"]["sensations"] +
        state_summary["symptoms"]["modalities"]
    )

    # 4. Retrieve Materia Medica
    mm_chunks = await rag.retrieve_top_remedies(top_remedy_names, all_symptoms)

    # 5. Rank remedies
    ranked = ranker.rank(candidates, mm_chunks)

    # 6. Generate explanation
    mm_texts = [f"{c.remedy} ({c.source}): {c.text}" for c in mm_chunks]
    remedy_scores_for_prompt = [
        {"remedy": r.remedy, "final_score": r.final_score}
        for r in ranked
    ]

    try:
        explanation = await agent.generate_explanation(
            symptom_summary=", ".join(all_symptoms),
            rubric_list=rubric_paths,
            remedy_scores=remedy_scores_for_prompt,
            materia_medica_excerpts=mm_texts,
        )
    except NotImplementedError:
        explanation = (
            f"Top remedy: {ranked[0].remedy} (score: {ranked[0].final_score:.2f}). "
            f"Matched rubrics: {', '.join(ranked[0].matching_rubrics[:3])}. "
            f"Configure LLM provider for full explanation."
        )

    # Advance to analysis stage
    if session.stage not in (SessionStage.analysis, SessionStage.completed):
        await manager.advance_stage(session_id)

    return AnalysisResponse(
        session_id=session_id,
        top_remedies=[
            RemedyScore(
                remedy=r.remedy,
                repertory_score=r.repertory_score,
                rag_score=r.rag_score,
                outcome_prior=r.outcome_prior,
                final_score=r.final_score,
                matching_rubrics=r.matching_rubrics,
            )
            for r in ranked
        ],
        materia_medica=[
            MateriaMedicaExcerpt(
                remedy=c.remedy,
                text=c.text,
                source=c.source,
                confidence=c.confidence,
            )
            for c in mm_chunks
        ],
        explanation=explanation,
        rubrics_used=rubric_paths,
        generated_at=datetime.utcnow(),
    )


@router.get("/{session_id}/history", response_model=list[MessageResponse])
async def get_history(
    session_id: str,
    db:         AsyncSession = Depends(get_db),
):
    """Return full conversation history for a session."""
    manager = SessionManager(db)
    session = await manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await manager.get_conversation_history(session_id)
    return messages
