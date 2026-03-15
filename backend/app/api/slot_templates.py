"""Slot template CRUD API (admin): 可预约时段配置."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import SlotTemplate

router = APIRouter(prefix="/slot-templates", tags=["slot-templates"])


def _slot_to_dict(s: SlotTemplate) -> dict:
    return {"id": s.id, "period": s.period, "hour": s.hour}


@router.get("")
async def list_slot_templates(session: AsyncSession = Depends(get_db)):
    """List all slot templates (admin)."""
    result = await session.execute(
        select(SlotTemplate).order_by(SlotTemplate.period, SlotTemplate.hour)
    )
    return [_slot_to_dict(s) for s in result.scalars().all()]


@router.get("/{template_id:int}")
async def get_slot_template(template_id: int, session: AsyncSession = Depends(get_db)):
    """Get one slot template."""
    result = await session.execute(select(SlotTemplate).where(SlotTemplate.id == template_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Slot template not found")
    return _slot_to_dict(s)


class SlotTemplateCreate(BaseModel):
    period: str  # "morning" | "afternoon"
    hour: int


class SlotTemplateUpdate(BaseModel):
    period: str | None = None
    hour: int | None = None


@router.post("")
async def create_slot_template(body: SlotTemplateCreate, session: AsyncSession = Depends(get_db)):
    """Create a slot template (admin)."""
    if body.period not in ("morning", "afternoon"):
        raise HTTPException(status_code=400, detail="period must be 'morning' or 'afternoon'")
    if body.hour < 0 or body.hour > 23:
        raise HTTPException(status_code=400, detail="hour must be 0-23")
    result = await session.execute(
        select(SlotTemplate).where(
            SlotTemplate.period == body.period, SlotTemplate.hour == body.hour
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该时段已存在")
    s = SlotTemplate(period=body.period, hour=body.hour)
    session.add(s)
    await session.flush()
    await session.refresh(s)
    return _slot_to_dict(s)


@router.put("/{template_id:int}")
async def update_slot_template(
    template_id: int, body: SlotTemplateUpdate, session: AsyncSession = Depends(get_db)
):
    """Update a slot template (admin)."""
    result = await session.execute(select(SlotTemplate).where(SlotTemplate.id == template_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Slot template not found")
    if body.period is not None:
        if body.period not in ("morning", "afternoon"):
            raise HTTPException(status_code=400, detail="period must be 'morning' or 'afternoon'")
        s.period = body.period
    if body.hour is not None:
        if body.hour < 0 or body.hour > 23:
            raise HTTPException(status_code=400, detail="hour must be 0-23")
        s.hour = body.hour
    await session.flush()
    await session.refresh(s)
    return _slot_to_dict(s)


@router.delete("/{template_id:int}")
async def delete_slot_template(template_id: int, session: AsyncSession = Depends(get_db)):
    """Delete a slot template (admin)."""
    result = await session.execute(select(SlotTemplate).where(SlotTemplate.id == template_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Slot template not found")
    await session.delete(s)
    await session.flush()
    return {"ok": True}
