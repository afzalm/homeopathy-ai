"""
SQLAlchemy ORM models — maps to PostgreSQL schema.
"""

import uuid
import json
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    ForeignKey, DateTime, Text, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
import enum


# ── Enums ─────────────────────────────────────────────────

class SessionStage(str, enum.Enum):
    initial            = "initial"
    symptom_collection = "symptom_collection"
    modalities         = "modalities"
    mental_symptoms    = "mental_symptoms"
    analysis           = "analysis"
    completed          = "completed"


class SessionStatus(str, enum.Enum):
    active    = "active"
    completed = "completed"
    abandoned = "abandoned"


class MessageRole(str, enum.Enum):
    user      = "user"
    assistant = "assistant"
    system    = "system"


class OutcomeResult(str, enum.Enum):
    improved  = "improved"
    no_change = "no_change"
    worsened  = "worsened"
    unknown   = "unknown"


# ── Session ───────────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id             = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id        = Column(String(36), nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status         = Column(Enum(SessionStatus), default=SessionStatus.active)
    stage          = Column(Enum(SessionStage),  default=SessionStage.initial)

    # Relationships
    messages         = relationship("Message",         back_populates="session", cascade="all, delete-orphan")
    session_state    = relationship("SessionState",    back_populates="session", uselist=False, cascade="all, delete-orphan")
    session_symptoms = relationship("SessionSymptom",  back_populates="session", cascade="all, delete-orphan")
    session_rubrics  = relationship("SessionRubric",   back_populates="session", cascade="all, delete-orphan")
    asked_questions  = relationship("AskedQuestion",   back_populates="session", cascade="all, delete-orphan")


# ── Messages ──────────────────────────────────────────────

class Message(Base):
    __tablename__ = "messages"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    role       = Column(Enum(MessageRole),  nullable=False)
    content    = Column(Text,               nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


# ── Session State ─────────────────────────────────────────

class SessionState(Base):
    __tablename__ = "session_state"

    session_id      = Column(String(36), ForeignKey("sessions.id"), primary_key=True)
    location        = Column(JSON, default=list)
    sensations      = Column(JSON, default=list)
    modalities      = Column(JSON, default=list)
    mental_symptoms = Column(JSON, default=list)
    generals        = Column(JSON, default=list)
    last_updated    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("Session", back_populates="session_state")


# ── Session Symptoms ──────────────────────────────────────

class SessionSymptom(Base):
    __tablename__ = "session_symptoms"

    id                = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id        = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    symptom_text      = Column(Text,    nullable=False)
    rubric_id         = Column(Integer, nullable=True)
    rubric_path       = Column(Text,    nullable=True)
    confidence        = Column(Float,   default=1.0)
    is_active         = Column(Boolean, default=True)
    source_message_id = Column(String(36), ForeignKey("messages.id"), nullable=True)
    superseded_by     = Column(String(36), ForeignKey("session_symptoms.id"), nullable=True)
    created_at        = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="session_symptoms")


# ── Session Rubrics ───────────────────────────────────────

class SessionRubric(Base):
    __tablename__ = "session_rubrics"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    rubric_id  = Column(Integer, nullable=False)
    rubric_path= Column(Text,    nullable=False)
    confidence = Column(Float,   default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="session_rubrics")


# ── Asked Questions ───────────────────────────────────────

class AskedQuestion(Base):
    __tablename__ = "asked_questions"

    id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id    = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    question_type = Column(String, nullable=False)   # location / sensation / modality / mental / general
    question_text = Column(Text,   nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="asked_questions")


# ── Remedies ──────────────────────────────────────────────

class Remedy(Base):
    __tablename__ = "remedies"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String,  nullable=False, unique=True)
    latin_name  = Column(String,  nullable=True)
    abbreviation= Column(String,  nullable=True)
    kingdom     = Column(String,  nullable=True)
    description = Column(Text,    nullable=True)


# ── Rubrics ───────────────────────────────────────────────

class Rubric(Base):
    __tablename__ = "rubrics"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    name      = Column(String,  nullable=False)
    parent_id = Column(Integer, ForeignKey("rubrics.id"), nullable=True)
    category  = Column(String,  nullable=True)
    path      = Column(Text,    nullable=True)   # e.g. "Head > Pain > Throbbing"
    level     = Column(Integer, default=0)


# ── Rubric–Remedy ─────────────────────────────────────────

class RubricRemedy(Base):
    __tablename__ = "rubric_remedy"

    rubric_id  = Column(Integer, ForeignKey("rubrics.id"),  primary_key=True)
    remedy_id  = Column(Integer, ForeignKey("remedies.id"), primary_key=True)
    grade      = Column(Integer, nullable=False)   # 1 / 2 / 3


# ── Clinical Cases ────────────────────────────────────────

class Case(Base):
    __tablename__ = "cases"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id  = Column(String(36), ForeignKey("sessions.id"), nullable=True)
    patient_age = Column(Integer, nullable=True)
    gender      = Column(String,  nullable=True)
    date        = Column(DateTime, default=datetime.utcnow)
    notes       = Column(Text,    nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    symptoms = relationship("CaseSymptom", back_populates="case", cascade="all, delete-orphan")
    remedies = relationship("CaseRemedy",  back_populates="case", cascade="all, delete-orphan")


class CaseSymptom(Base):
    __tablename__ = "case_symptoms"

    id        = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id   = Column(String(36), ForeignKey("cases.id"), nullable=False)
    rubric_id = Column(Integer, ForeignKey("rubrics.id"), nullable=False)

    case = relationship("Case", back_populates="symptoms")


class CaseRemedy(Base):
    __tablename__ = "case_remedies"

    id        = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id   = Column(String(36), ForeignKey("cases.id"), nullable=False)
    remedy_id = Column(Integer, ForeignKey("remedies.id"), nullable=False)
    potency   = Column(String,  nullable=True)
    outcome   = Column(Enum(OutcomeResult), default=OutcomeResult.unknown)

    case = relationship("Case", back_populates="remedies")
