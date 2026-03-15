"""Availability (calendar) API."""
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.availability import get_availability

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("")
async def availability(
    counselor_id: int = Query(..., description="辅导员 ID"),
    start_date: date = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: date = Query(..., description="结束日期 YYYY-MM-DD"),
    session: AsyncSession = Depends(get_db),
):
    """Return available slots for the counselor in [start_date, end_date]."""
    if start_date > end_date:
        return []
    return await get_availability(session, counselor_id, start_date, end_date)
