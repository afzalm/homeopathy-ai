"""
Remedy Routes
=============
GET /api/v1/remedies/          — list all remedies
GET /api/v1/remedies/{id}      — get remedy detail
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from database.models import Remedy
from models.schemas import RemedyResponse

router = APIRouter()


@router.get("/", response_model=list[RemedyResponse])
async def list_remedies(
    skip:  int = 0,
    limit: int = 100,
    db:    AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Remedy).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{remedy_id}", response_model=RemedyResponse)
async def get_remedy(
    remedy_id: int,
    db:        AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Remedy).where(Remedy.id == remedy_id)
    )
    remedy = result.scalar_one_or_none()
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")
    return remedy
