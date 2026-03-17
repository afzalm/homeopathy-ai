"""
Session Manager Service
=======================
Core orchestration layer. Handles:
- Session lifecycle (create, load, advance stage)
- Message storage
- Symptom state tracking
- Question planning
- Repertory trigger logic
"""

import logging
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database.models import (
    Session, Message, SessionState, SessionSymptom,
    SessionRubric, AskedQuestion,
    SessionStage, SessionStatus, MessageRole
)
from models.schemas import SymptomExtracted
from core.config import settings

logger = logging.getLogger(__name__)

# Question dimension priority (classical hierarchy)
DIMENSION_PRIORITY = [
    "mental",
    "generals",
    "location",
    "sensation",
    "modality",
]

QUESTION_TEMPLATES = {
    "location":  "Where exactly do you feel this symptom?",
    "sensation": "How does it feel — can you describe the sensation?",
    "modality":  "What makes it worse or better?",
    "mental":    "How are you feeling emotionally during this problem?",
    "generals":  "How is your energy, sleep, and appetite generally?",
}


class SessionManager:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Session Lifecycle ─────────────────────────────────

    async def create_session(self, user_id: UUID | None = None) -> Session:
        session = Session(
            user_id=user_id,
            status=SessionStatus.active,
            stage=SessionStage.initial,
        )
        self.db.add(session)

        # Create empty state row
        state = SessionState(
            session_id=session.id,
            location=[],
            sensations=[],
            modalities=[],
            mental_symptoms=[],
            generals=[],
        )
        self.db.add(state)
        await self.db.flush()

        logger.info(f"Created session {session.id}")
        return session

    async def get_session(self, session_id: UUID) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_session_state(self, session_id: UUID) -> SessionState | None:
        result = await self.db.execute(
            select(SessionState).where(SessionState.session_id == session_id)
        )
        return result.scalar_one_or_none()

    # ── Message Storage ───────────────────────────────────

    async def store_message(
        self,
        session_id: UUID,
        role: MessageRole,
        content: str
    ) -> Message:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def get_conversation_history(self, session_id: UUID) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    # ── Symptom State Updates ─────────────────────────────

    async def update_symptoms(
        self,
        session_id: UUID,
        extracted: list[SymptomExtracted],
        source_message_id: UUID
    ):
        """Add newly extracted symptoms to session state."""
        state = await self.get_session_state(session_id)
        if not state:
            logger.warning(f"No state found for session {session_id}")
            return

        for symptom in extracted:
            # Skip low-confidence extractions
            if symptom.confidence < 0.6:
                logger.debug(f"Skipping low-confidence symptom: {symptom.text} ({symptom.confidence})")
                continue

            # Store structured symptom
            session_symptom = SessionSymptom(
                session_id=session_id,
                symptom_text=symptom.text,
                rubric_id=symptom.rubric_id,
                rubric_path=symptom.rubric_path,
                confidence=symptom.confidence,
                source_message_id=source_message_id,
                is_active=True,
            )
            self.db.add(session_symptom)

            # Store rubric if mapped
            if symptom.rubric_id and symptom.rubric_path:
                rubric = SessionRubric(
                    session_id=session_id,
                    rubric_id=symptom.rubric_id,
                    rubric_path=symptom.rubric_path,
                    confidence=symptom.confidence,
                )
                self.db.add(rubric)

            # Update dimension arrays on state
            text_lower = symptom.text.lower()
            if any(w in text_lower for w in ["head", "stomach", "back", "chest", "throat"]):
                if text_lower not in (state.location or []):
                    state.location = (state.location or []) + [symptom.text]

            elif any(w in text_lower for w in ["fear", "anxiety", "sad", "angry", "irritable", "weeping"]):
                if symptom.text not in (state.mental_symptoms or []):
                    state.mental_symptoms = (state.mental_symptoms or []) + [symptom.text]

            elif any(w in text_lower for w in ["worse", "better", "aggravat", "ameliorat"]):
                if symptom.text not in (state.modalities or []):
                    state.modalities = (state.modalities or []) + [symptom.text]

            else:
                if symptom.text not in (state.sensations or []):
                    state.sensations = (state.sensations or []) + [symptom.text]

        state.last_updated = datetime.utcnow()
        await self.db.flush()

    # ── Question Planning ─────────────────────────────────

    async def get_missing_dimensions(self, session_id: UUID) -> list[str]:
        """Returns dimensions not yet collected, in priority order."""
        state = await self.get_session_state(session_id)
        if not state:
            return DIMENSION_PRIORITY[:]

        missing = []
        if not state.location:        missing.append("location")
        if not state.sensations:      missing.append("sensation")
        if not state.modalities:      missing.append("modality")
        if not state.mental_symptoms: missing.append("mental")
        if not state.generals:        missing.append("generals")

        # Sort by priority
        return [d for d in DIMENSION_PRIORITY if d in missing]

    async def plan_next_question(self, session_id: UUID) -> str | None:
        """
        Returns the next question to ask, or None if analysis is ready.
        Uses rule-based question planner — no LLM improvisation.
        """
        missing    = await self.get_missing_dimensions(session_id)
        asked_types = await self._get_asked_question_types(session_id)

        for dimension in missing:
            if dimension not in asked_types:
                question = QUESTION_TEMPLATES.get(dimension)
                if question:
                    await self._record_question(session_id, dimension, question)
                    return question

        return None  # All dimensions covered — ready for analysis

    async def _get_asked_question_types(self, session_id: UUID) -> set[str]:
        result = await self.db.execute(
            select(AskedQuestion.question_type)
            .where(AskedQuestion.session_id == session_id)
        )
        return {row[0] for row in result.fetchall()}

    async def _record_question(
        self,
        session_id: UUID,
        question_type: str,
        question_text: str
    ):
        q = AskedQuestion(
            session_id=session_id,
            question_type=question_type,
            question_text=question_text,
        )
        self.db.add(q)
        await self.db.flush()

    # ── Stage Management ──────────────────────────────────

    async def advance_stage(self, session_id: UUID) -> SessionStage:
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        transitions = {
            SessionStage.initial:            SessionStage.symptom_collection,
            SessionStage.symptom_collection: SessionStage.modalities,
            SessionStage.modalities:         SessionStage.mental_symptoms,
            SessionStage.mental_symptoms:    SessionStage.analysis,
            SessionStage.analysis:           SessionStage.completed,
        }

        next_stage = transitions.get(session.stage, session.stage)
        await self.db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(stage=next_stage, updated_at=datetime.utcnow())
        )
        await self.db.flush()
        logger.info(f"Session {session_id} advanced: {session.stage} → {next_stage}")
        return next_stage

    # ── Repertory Trigger ─────────────────────────────────

    async def is_analysis_ready(self, session_id: UUID) -> bool:
        """
        Checks if enough rubrics have been collected to trigger analysis.
        Threshold: settings.MIN_RUBRICS_FOR_ANALYSIS (default: 4)
        """
        result = await self.db.execute(
            select(SessionRubric)
            .where(
                SessionRubric.session_id == session_id,
            )
        )
        rubrics = result.scalars().all()
        active_rubrics = [r for r in rubrics if r.confidence >= 0.7]
        return len(active_rubrics) >= settings.MIN_RUBRICS_FOR_ANALYSIS

    async def get_session_rubric_paths(self, session_id: UUID) -> list[str]:
        result = await self.db.execute(
            select(SessionRubric.rubric_path)
            .where(SessionRubric.session_id == session_id)
        )
        return [row[0] for row in result.fetchall()]

    # ── Session State Summary ─────────────────────────────

    async def build_state_summary(self, session_id: UUID) -> dict:
        """Builds the full state object passed to the LLM."""
        session = await self.get_session(session_id)
        state   = await self.get_session_state(session_id)
        rubrics = await self.get_session_rubric_paths(session_id)
        missing = await self.get_missing_dimensions(session_id)

        return {
            "session_id":        str(session_id),
            "stage":             session.stage.value if session else "unknown",
            "symptoms": {
                "location":        state.location        or [],
                "sensations":      state.sensations      or [],
                "modalities":      state.modalities      or [],
                "mental":          state.mental_symptoms or [],
                "generals":        state.generals        or [],
            },
            "rubrics":           rubrics,
            "missing_dimensions": missing,
        }
