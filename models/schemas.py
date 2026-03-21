"""
Pydantic schemas — request bodies and response models.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from database.models import SessionStage, SessionStatus, MessageRole, OutcomeResult


# ── Session ───────────────────────────────────────────────

class SessionCreate(BaseModel):
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    id:         str
    user_id:    Optional[str]
    status:     SessionStatus
    stage:      SessionStage
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Messages ──────────────────────────────────────────────

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id:         str
    session_id: str
    role:       MessageRole
    content:    str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Chat ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000,
                         description="Patient or practitioner message")


class SymptomExtracted(BaseModel):
    text:        str
    dimension:   Optional[str] = None
    normalized:  Optional[str] = None
    rubric_path: Optional[str]
    rubric_id:   Optional[int]
    confidence:  float


class ChatResponse(BaseModel):
    session_id:          str
    reply:               str
    stage:               SessionStage
    symptoms_extracted:  list[SymptomExtracted]
    analysis_ready:      bool
    message_id:          str


# ── Symptom State ─────────────────────────────────────────

class SessionStateResponse(BaseModel):
    session_id:      str
    stage:           SessionStage
    location:        list[str]
    sensations:      list[str]
    modalities:      list[str]
    mental_symptoms: list[str]
    generals:        list[str]
    rubrics:         list[str]
    missing_dimensions: list[str]
    last_updated:    datetime

    class Config:
        from_attributes = True


# ── Analysis / Remedy Ranking ─────────────────────────────

class RubricMatch(BaseModel):
    rubric_path:  str
    rubric_id:    int
    grade:        int
    remedy_name:  str


class RemedyScore(BaseModel):
    remedy:           str
    repertory_score:  float
    rag_score:        float
    outcome_prior:    float
    final_score:      float
    matching_rubrics: list[str]


class MateriaMedicaExcerpt(BaseModel):
    remedy:     str
    text:       str
    source:     str
    confidence: float


class AnalysisResponse(BaseModel):
    session_id:       str
    top_remedies:     list[RemedyScore]
    materia_medica:   list[MateriaMedicaExcerpt]
    explanation:      str
    rubrics_used:     list[str]
    generated_at:     datetime


# ── Cases ─────────────────────────────────────────────────

class CaseCreate(BaseModel):
    session_id:  Optional[str]  = None
    patient_age: Optional[int]   = None
    gender:      Optional[str]   = None
    notes:       Optional[str]   = None


class CaseRemedyCreate(BaseModel):
    remedy_id: int
    potency:   Optional[str] = None
    outcome:   OutcomeResult = OutcomeResult.unknown


class CaseResponse(BaseModel):
    id:         str
    session_id: Optional[str]
    date:       datetime
    notes:      Optional[str]

    class Config:
        from_attributes = True


# ── Remedies ──────────────────────────────────────────────

class RemedyResponse(BaseModel):
    id:          int
    name:        str
    latin_name:  Optional[str]
    abbreviation:Optional[str]
    kingdom:     Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True
