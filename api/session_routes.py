"""
Session Routes
==============
POST /api/v1/sessions/         — create session
GET  /api/v1/sessions/{id}     — get session
GET  /api/v1/sessions/{id}/state — get full state
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.database import get_db
from services.session_manager import SessionManager
from models.schemas import SessionCreate, SessionResponse, SessionStateResponse
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    body: SessionCreate,
    db:   AsyncSession = Depends(get_db),
):
    """Start a new consultation session."""
    manager = SessionManager(db)
    session = await manager.create_session(user_id=body.user_id)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db:         AsyncSession = Depends(get_db),
):
    manager = SessionManager(db)
    session = await manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/state", response_model=SessionStateResponse)
async def get_session_state(
    session_id: UUID,
    db:         AsyncSession = Depends(get_db),
):
    """Return full structured state of the session."""
    manager = SessionManager(db)
    session = await manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    state   = await manager.get_session_state(session_id)
    rubrics = await manager.get_session_rubric_paths(session_id)
    missing = await manager.get_missing_dimensions(session_id)

    return SessionStateResponse(
        session_id=session_id,
        stage=session.stage,
        location=state.location        or [],
        sensations=state.sensations    or [],
        modalities=state.modalities    or [],
        mental_symptoms=state.mental_symptoms or [],
        generals=state.generals        or [],
        rubrics=rubrics,
        missing_dimensions=missing,
        last_updated=state.last_updated or datetime.utcnow(),
    )
