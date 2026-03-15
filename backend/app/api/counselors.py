"""Counselor list and admin CRUD API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import Counselor

router = APIRouter(prefix="/counselors", tags=["counselors"])


def _counselor_to_dict(c: Counselor) -> dict:
    return {
        "id": c.id,
        "employee_id": c.employee_id,
        "name": c.name,
        "email": c.email,
        "is_active": c.is_active,
    }


@router.get("")
async def list_counselors(
    all: bool = Query(False, description="Include inactive (for admin)"),
    session: AsyncSession = Depends(get_db),
):
    """Return counselors. Default: active only. Use ?all=true for admin."""
    q = select(Counselor).order_by(Counselor.employee_id)
    if not all:
        q = q.where(Counselor.is_active == True)
    result = await session.execute(q)
    rows = result.scalars().all()
    return [_counselor_to_dict(c) for c in rows]


@router.get("/{counselor_id:int}")
async def get_counselor(counselor_id: int, session: AsyncSession = Depends(get_db)):
    """Get one counselor by id."""
    result = await session.execute(select(Counselor).where(Counselor.id == counselor_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Counselor not found")
    return _counselor_to_dict(c)


class CounselorCreate(BaseModel):
    employee_id: str
    name: str
    email: str
    is_active: bool = True


class CounselorUpdate(BaseModel):
    employee_id: str | None = None
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None


@router.post("")
async def create_counselor(body: CounselorCreate, session: AsyncSession = Depends(get_db)):
    """Create a counselor (admin)."""
    body.employee_id = body.employee_id.strip()
    body.name = body.name.strip()
    body.email = body.email.strip()
    if not body.employee_id or not body.name or not body.email:
        raise HTTPException(status_code=400, detail="employee_id, name, email are required")
    result = await session.execute(select(Counselor).where(Counselor.employee_id == body.employee_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="工号已存在")
    c = Counselor(
        employee_id=body.employee_id,
        name=body.name,
        email=body.email,
        is_active=body.is_active,
    )
    session.add(c)
    await session.flush()
    await session.refresh(c)
    return _counselor_to_dict(c)


@router.put("/{counselor_id:int}")
async def update_counselor(
    counselor_id: int, body: CounselorUpdate, session: AsyncSession = Depends(get_db)
):
    """Update a counselor (admin)."""
    result = await session.execute(select(Counselor).where(Counselor.id == counselor_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Counselor not found")
    if body.employee_id is not None:
        c.employee_id = body.employee_id.strip()
    if body.name is not None:
        c.name = body.name.strip()
    if body.email is not None:
        c.email = body.email.strip()
    if body.is_active is not None:
        c.is_active = body.is_active
    await session.flush()
    await session.refresh(c)
    return _counselor_to_dict(c)


@router.delete("/{counselor_id:int}")
async def delete_counselor(counselor_id: int, session: AsyncSession = Depends(get_db)):
    """Soft-delete: set is_active=False (admin)."""
    result = await session.execute(select(Counselor).where(Counselor.id == counselor_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Counselor not found")
    c.is_active = False
    await session.flush()
    await session.refresh(c)
    return {"ok": True}
