"""
Case Routes
===========
POST /api/v1/cases/                        — create case record
GET  /api/v1/cases/{id}                    — get case
POST /api/v1/cases/{id}/remedies           — record remedy prescribed
PATCH /api/v1/cases/{id}/remedies/{rid}    — update outcome
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from core.database import get_db
from database.models import Case, CaseRemedy, CaseSymptom
from models.schemas import CaseCreate, CaseRemedyCreate, CaseResponse

router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_case(
    body: CaseCreate,
    db:   AsyncSession = Depends(get_db),
):
    case = Case(
        session_id=body.session_id,
        patient_age=body.patient_age,
        gender=body.gender,
        notes=body.notes,
    )
    db.add(case)
    await db.flush()
    return case


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    db:      AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case   = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/remedies", status_code=201)
async def add_case_remedy(
    case_id: UUID,
    body:    CaseRemedyCreate,
    db:      AsyncSession = Depends(get_db),
):
    """Record a remedy prescribed for a case."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case   = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    remedy = CaseRemedy(
        case_id=case_id,
        remedy_id=body.remedy_id,
        potency=body.potency,
        outcome=body.outcome,
    )
    db.add(remedy)
    await db.flush()
    return {"status": "recorded", "case_id": str(case_id), "remedy_id": body.remedy_id}


@router.patch("/{case_id}/remedies/{remedy_id}")
async def update_outcome(
    case_id:   UUID,
    remedy_id: int,
    outcome:   str,
    db:        AsyncSession = Depends(get_db),
):
    """Update the treatment outcome — feeds back into outcome_priors."""
    result = await db.execute(
        select(CaseRemedy).where(
            CaseRemedy.case_id   == case_id,
            CaseRemedy.remedy_id == remedy_id,
        )
    )
    case_remedy = result.scalar_one_or_none()
    if not case_remedy:
        raise HTTPException(status_code=404, detail="Case remedy not found")

    case_remedy.outcome = outcome
    await db.flush()
    return {"status": "updated", "outcome": outcome}
