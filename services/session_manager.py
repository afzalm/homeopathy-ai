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
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from database.models import (
    AskedQuestion,
    Message,
    MessageRole,
    Session,
    SessionRubric,
    SessionStage,
    SessionState,
    SessionStatus,
    SessionSymptom,
)
from models.schemas import SymptomExtracted

logger = logging.getLogger(__name__)

DIMENSION_PRIORITY = [
    "mental",
    "generals",
    "location",
    "sensation",
    "modality",
]

QUESTION_TEMPLATES = {
    "location": "Where exactly do you feel this symptom?",
    "sensation": "How does it feel - can you describe the sensation?",
    "modality": "What makes it worse or better?",
    "mental": "How are you feeling emotionally during this problem?",
    "generals": "How is your energy, sleep, and appetite generally?",
}

REFINEMENT_PRIORITY = [
    "mental",
    "generals",
    "modality",
    "sensation",
    "location",
]

REFINEMENT_QUESTION_TEMPLATES = {
    "location": "Does the symptom stay in one exact spot, or does it spread anywhere else?",
    "sensation": "Can you describe the sensation more precisely, such as throbbing, bursting, burning, stitching, or pressure?",
    "modality": "Are there any other clear things that make it worse or better, such as noise, motion, touch, heat, cold, or time of day?",
    "mental": "Along with the complaint, are there any marked emotional changes such as fear, anxiety, irritability, or restlessness?",
    "generals": "Apart from the main complaint, have you noticed any clear changes in sleep, thirst, appetite, temperature, or energy?",
}

CHARACTERISTIC_QUESTION = (
    "What feels most unusual or characteristic about this problem compared with your usual state?"
)


class SessionManager:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: str | None = None) -> Session:
        session_id = str(uuid.uuid4())

        session = Session(
            id=session_id,
            user_id=user_id,
            status=SessionStatus.active,
            stage=SessionStage.initial,
        )
        self.db.add(session)

        state = SessionState(
            session_id=session_id,
            location=[],
            sensations=[],
            modalities=[],
            mental_symptoms=[],
            generals=[],
        )
        self.db.add(state)
        await self.db.flush()

        logger.info("Created session %s", session_id)
        return session

    async def get_session(self, session_id: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_session_state(self, session_id: str) -> SessionState | None:
        result = await self.db.execute(
            select(SessionState).where(SessionState.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def store_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
    ) -> Message:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def get_conversation_history(self, session_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    async def update_symptoms(
        self,
        session_id: str,
        extracted: list[SymptomExtracted],
        source_message_id: str,
    ) -> None:
        state = await self.get_session_state(session_id)
        if not state:
            logger.warning("No state found for session %s", session_id)
            return

        existing_symptom_texts = {
            row[0].strip().lower()
            for row in (
                await self.db.execute(
                    select(SessionSymptom.symptom_text)
                    .where(
                        SessionSymptom.session_id == session_id,
                        SessionSymptom.is_active.is_(True),
                    )
                )
            ).fetchall()
            if row[0]
        }
        existing_rubric_paths = {
            row[0]
            for row in (
                await self.db.execute(
                    select(SessionRubric.rubric_path)
                    .where(SessionRubric.session_id == session_id)
                )
            ).fetchall()
            if row[0]
        }

        for symptom in extracted:
            if symptom.confidence < 0.6:
                logger.debug(
                    "Skipping low-confidence symptom: %s (%s)",
                    symptom.text,
                    symptom.confidence,
                )
                continue

            symptom_text = (symptom.normalized or symptom.text).strip()
            symptom_key = symptom_text.lower()

            if symptom_key and symptom_key not in existing_symptom_texts:
                session_symptom = SessionSymptom(
                    session_id=session_id,
                    symptom_text=symptom_text,
                    rubric_id=symptom.rubric_id,
                    rubric_path=symptom.rubric_path,
                    confidence=symptom.confidence,
                    source_message_id=source_message_id,
                    is_active=True,
                )
                self.db.add(session_symptom)
                existing_symptom_texts.add(symptom_key)

            if (
                symptom.rubric_id
                and symptom.rubric_path
                and symptom.rubric_path not in existing_rubric_paths
            ):
                rubric = SessionRubric(
                    session_id=session_id,
                    rubric_id=symptom.rubric_id,
                    rubric_path=symptom.rubric_path,
                    confidence=symptom.confidence,
                )
                self.db.add(rubric)
                existing_rubric_paths.add(symptom.rubric_path)

            self._update_state_dimension(state, symptom)

        state.last_updated = datetime.utcnow()
        await self.db.flush()

    async def get_missing_dimensions(self, session_id: str) -> list[str]:
        state = await self.get_session_state(session_id)
        if not state:
            return DIMENSION_PRIORITY[:]

        missing = []
        if not state.location:
            missing.append("location")
        if not state.sensations:
            missing.append("sensation")
        if not state.modalities:
            missing.append("modality")
        if not state.mental_symptoms:
            missing.append("mental")
        if not state.generals:
            missing.append("generals")

        return [dimension for dimension in DIMENSION_PRIORITY if dimension in missing]

    async def plan_next_question(self, session_id: str) -> str | None:
        if await self.is_analysis_ready(session_id):
            return None

        missing = await self.get_missing_dimensions(session_id)
        asked_types = await self._get_asked_question_types(session_id)

        for dimension in missing:
            if dimension not in asked_types:
                question = QUESTION_TEMPLATES.get(dimension)
                if question:
                    await self._record_question(session_id, dimension, question)
                    return question

        refinement = await self._plan_refinement_question(session_id, asked_types)
        if refinement:
            question_type, question_text = refinement
            await self._record_question(session_id, question_type, question_text)
            return question_text

        if "characteristic_detail" not in asked_types:
            await self._record_question(session_id, "characteristic_detail", CHARACTERISTIC_QUESTION)
            return CHARACTERISTIC_QUESTION

        return None

    async def _get_asked_question_types(self, session_id: str) -> set[str]:
        result = await self.db.execute(
            select(AskedQuestion.question_type)
            .where(AskedQuestion.session_id == session_id)
        )
        return {row[0] for row in result.fetchall()}

    async def _record_question(
        self,
        session_id: str,
        question_type: str,
        question_text: str,
    ) -> None:
        question = AskedQuestion(
            session_id=session_id,
            question_type=question_type,
            question_text=question_text,
        )
        self.db.add(question)
        await self.db.flush()

    async def _plan_refinement_question(
        self,
        session_id: str,
        asked_types: set[str],
    ) -> tuple[str, str] | None:
        state = await self.get_session_state(session_id)
        if not state:
            return None

        evidence_counts = await self._get_rubric_backed_dimension_counts(session_id)

        for dimension in REFINEMENT_PRIORITY:
            if not self._dimension_has_data(state, dimension):
                continue
            if evidence_counts.get(dimension, 0) > 0:
                continue

            question_type = f"refine_{dimension}"
            question_text = REFINEMENT_QUESTION_TEMPLATES.get(dimension)
            if question_text and question_type not in asked_types:
                return question_type, question_text

        weakest_dimensions = sorted(
            (
                dimension
                for dimension in REFINEMENT_PRIORITY
                if self._dimension_has_data(state, dimension)
            ),
            key=lambda dimension: (
                evidence_counts.get(dimension, 0),
                REFINEMENT_PRIORITY.index(dimension),
            ),
        )

        for dimension in weakest_dimensions:
            question_type = f"refine_{dimension}"
            question_text = REFINEMENT_QUESTION_TEMPLATES.get(dimension)
            if question_text and question_type not in asked_types:
                return question_type, question_text

        return None

    async def _get_rubric_backed_dimension_counts(self, session_id: str) -> dict[str, int]:
        state = await self.get_session_state(session_id)
        if not state:
            return {}

        dimension_lookup = {
            **{value: "location" for value in (state.location or [])},
            **{value: "sensation" for value in (state.sensations or [])},
            **{value: "modality" for value in (state.modalities or [])},
            **{value: "mental" for value in (state.mental_symptoms or [])},
            **{value: "generals" for value in (state.generals or [])},
        }

        result = await self.db.execute(
            select(SessionSymptom.symptom_text)
            .where(
                SessionSymptom.session_id == session_id,
                SessionSymptom.is_active.is_(True),
                SessionSymptom.rubric_id.is_not(None),
                SessionSymptom.rubric_path.is_not(None),
            )
        )

        counts: dict[str, int] = {}
        for (symptom_text,) in result.fetchall():
            if not symptom_text:
                continue
            dimension = dimension_lookup.get(symptom_text)
            if not dimension:
                dimension = self._normalize_dimension_name(self._infer_dimension(symptom_text))
            counts[dimension] = counts.get(dimension, 0) + 1

        return counts

    async def advance_stage(self, session_id: str) -> SessionStage:
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        transitions = {
            SessionStage.initial: SessionStage.symptom_collection,
            SessionStage.symptom_collection: SessionStage.modalities,
            SessionStage.modalities: SessionStage.mental_symptoms,
            SessionStage.mental_symptoms: SessionStage.analysis,
            SessionStage.analysis: SessionStage.completed,
        }

        next_stage = transitions.get(session.stage, session.stage)
        await self.db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(stage=next_stage, updated_at=datetime.utcnow())
        )
        await self.db.flush()
        logger.info("Session %s advanced: %s -> %s", session_id, session.stage, next_stage)
        return next_stage

    async def is_analysis_ready(self, session_id: str) -> bool:
        result = await self.db.execute(
            select(SessionRubric)
            .where(SessionRubric.session_id == session_id)
        )
        rubrics = result.scalars().all()
        active_rubrics = {
            rubric.rubric_path
            for rubric in rubrics
            if rubric.confidence >= 0.7 and rubric.rubric_path
        }
        return len(active_rubrics) >= settings.MIN_RUBRICS_FOR_ANALYSIS

    async def get_session_rubric_paths(self, session_id: str) -> list[str]:
        result = await self.db.execute(
            select(SessionRubric.rubric_path)
            .where(SessionRubric.session_id == session_id)
        )
        rubric_paths = [row[0] for row in result.fetchall() if row[0]]
        return list(dict.fromkeys(rubric_paths))

    async def build_state_summary(self, session_id: str) -> dict:
        session = await self.get_session(session_id)
        state = await self.get_session_state(session_id)
        rubrics = await self.get_session_rubric_paths(session_id)
        missing = await self.get_missing_dimensions(session_id)

        return {
            "session_id": str(session_id),
            "stage": session.stage.value if session else "unknown",
            "symptoms": {
                "location": state.location or [],
                "sensations": state.sensations or [],
                "modalities": state.modalities or [],
                "mental": state.mental_symptoms or [],
                "generals": state.generals or [],
            },
            "rubrics": rubrics,
            "missing_dimensions": missing,
        }

    def _update_state_dimension(self, state: SessionState, symptom: SymptomExtracted) -> None:
        value = (symptom.normalized or symptom.text).strip()
        if not value:
            return

        dimension = (symptom.dimension or self._infer_dimension(symptom.text)).lower()
        if dimension == "location":
            state.location = self._append_unique(state.location, value)
            return

        if dimension in {"mental", "mental_symptom"}:
            state.mental_symptoms = self._append_unique(state.mental_symptoms, value)
            return

        if dimension in {"modality", "modality_aggravation", "modality_amelioration", "time"}:
            state.modalities = self._append_unique(state.modalities, value)
            return

        if dimension in {"general", "generals"}:
            if symptom.rubric_id and symptom.rubric_path:
                state.generals = self._append_unique(state.generals, value)
            return

        state.sensations = self._append_unique(state.sensations, value)

    @staticmethod
    def _dimension_has_data(state: SessionState, dimension: str) -> bool:
        if dimension == "location":
            return bool(state.location)
        if dimension == "sensation":
            return bool(state.sensations)
        if dimension == "modality":
            return bool(state.modalities)
        if dimension == "mental":
            return bool(state.mental_symptoms)
        if dimension == "generals":
            return bool(state.generals)
        return False

    @staticmethod
    def _append_unique(values: list[str] | None, value: str) -> list[str]:
        values = values or []
        if value not in values:
            return values + [value]
        return values

    @staticmethod
    def _infer_dimension(text: str) -> str:
        text_lower = text.lower()
        if any(word in text_lower for word in ["head", "stomach", "back", "chest", "throat"]):
            return "location"
        if any(word in text_lower for word in ["fear", "anxiety", "sad", "angry", "irritable", "weeping"]):
            return "mental"
        if any(word in text_lower for word in ["worse", "better", "aggravat", "ameliorat"]):
            return "modality"
        if any(word in text_lower for word in ["energy", "sleep", "appetite", "restless", "thirst", "tired"]):
            return "general"
        return "sensation"

    @staticmethod
    def _normalize_dimension_name(dimension: str) -> str:
        if dimension == "general":
            return "generals"
        return dimension
