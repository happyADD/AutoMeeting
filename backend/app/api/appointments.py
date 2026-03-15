"""Appointment create and list API."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db import get_db
from app.models import Counselor, Appointment
from app.services.availability import get_availability
from app.services.email import send_appointment_email

router = APIRouter(prefix="/appointments", tags=["appointments"])


class CreateAppointmentBody(BaseModel):
    counselor_id: int
    date: date
    period: str  # "morning" | "afternoon"
    hour: int
    content: str
    contact_name: str
    contact_phone: str | None = None
    contact_email: str | None = None


@router.post("")
async def create_appointment(body: CreateAppointmentBody, session: AsyncSession = Depends(get_db)):
    """Create appointment, then send email to counselor. Returns 409 if slot taken."""
    if body.period not in ("morning", "afternoon"):
        raise HTTPException(status_code=400, detail="period must be 'morning' or 'afternoon'")
    if not body.content or not body.contact_name.strip():
        raise HTTPException(status_code=400, detail="content and contact_name are required")
    if not body.contact_phone and not body.contact_email:
        raise HTTPException(status_code=400, detail="At least one of contact_phone or contact_email is required")

    # Check counselor exists
    result = await session.execute(select(Counselor).where(Counselor.id == body.counselor_id))
    counselor = result.scalar_one_or_none()
    if not counselor:
        raise HTTPException(status_code=404, detail="Counselor not found")
    if not counselor.is_active:
        raise HTTPException(status_code=400, detail="Counselor is not active")

    # Conflict check: already booked?
    result = await session.execute(
        select(Appointment).where(
            and_(
                Appointment.counselor_id == body.counselor_id,
                Appointment.appointment_date == body.date,
                Appointment.period == body.period,
                Appointment.hour == body.hour,
                Appointment.status == "confirmed",
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="This slot is already booked")

    appointment = Appointment(
        counselor_id=body.counselor_id,
        appointment_date=body.date,
        period=body.period,
        hour=body.hour,
        content=body.content.strip(),
        contact_name=body.contact_name.strip(),
        contact_phone=body.contact_phone.strip() if body.contact_phone else None,
        contact_email=body.contact_email.strip() if body.contact_email else None,
        status="confirmed",
    )
    session.add(appointment)
    await session.flush()
    await session.refresh(appointment)

    # Send email (don't rollback appointment on failure)
    try:
        send_appointment_email(
            to_email=counselor.email,
            counselor_name=counselor.name,
            appointment_date=body.date.isoformat(),
            period=body.period,
            hour=body.hour,
            content=appointment.content,
            contact_name=appointment.contact_name,
            contact_phone=appointment.contact_phone,
            contact_email=appointment.contact_email,
        )
    except Exception:
        # Log and continue; appointment is already stored
        pass

    return {
        "id": appointment.id,
        "counselor_id": appointment.counselor_id,
        "date": appointment.appointment_date.isoformat(),
        "period": appointment.period,
        "hour": appointment.hour,
        "content": appointment.content,
        "contact_name": appointment.contact_name,
        "status": appointment.status,
    }


@router.get("")
async def list_appointments(
    counselor_id: int | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    """List appointments with optional filters."""
    q = select(Appointment).order_by(Appointment.appointment_date.desc(), Appointment.id.desc())
    if counselor_id is not None:
        q = q.where(Appointment.counselor_id == counselor_id)
    if start_date is not None:
        q = q.where(Appointment.appointment_date >= start_date)
    if end_date is not None:
        q = q.where(Appointment.appointment_date <= end_date)
    result = await session.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": a.id,
            "counselor_id": a.counselor_id,
            "date": a.appointment_date.isoformat(),
            "period": a.period,
            "hour": a.hour,
            "content": a.content,
            "contact_name": a.contact_name,
            "contact_phone": a.contact_phone,
            "contact_email": a.contact_email,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in rows
    ]


@router.delete("/{appointment_id:int}")
async def delete_appointment(
    appointment_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Cancel/delete an appointment (admin). Sets status to cancelled."""
    result = await session.execute(select(Appointment).where(Appointment.id == appointment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    a.status = "cancelled"
    await session.flush()
    await session.refresh(a)
    return {"ok": True}
