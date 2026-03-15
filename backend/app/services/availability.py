"""Compute available slots for a counselor in a date range."""
from datetime import date, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SlotTemplate, Appointment


async def get_availability(
    session: AsyncSession,
    counselor_id: int,
    start_date: date,
    end_date: date,
) -> list[dict]:
    """
    Return list of available slots: each item is
    { "date": "YYYY-MM-DD", "period": "morning"|"afternoon", "hour": int }.
    """
    # Load slot templates (which hours are bookable)
    result = await session.execute(select(SlotTemplate).order_by(SlotTemplate.period, SlotTemplate.hour))
    templates = result.scalars().all()
    if not templates:
        # Default: morning 8-11, afternoon 14-17
        default_hours = [
            ("morning", 8), ("morning", 9), ("morning", 10), ("morning", 11),
            ("afternoon", 14), ("afternoon", 15), ("afternoon", 16), ("afternoon", 17),
        ]
        slot_keys = [{"period": p, "hour": h} for p, h in default_hours]
    else:
        slot_keys = [{"period": t.period, "hour": t.hour} for t in templates]

    # Load existing appointments for this counselor in range
    result = await session.execute(
        select(Appointment.appointment_date, Appointment.period, Appointment.hour).where(
            and_(
                Appointment.counselor_id == counselor_id,
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date,
                Appointment.status == "confirmed",
            )
        )
    )
    occupied = set((row[0], row[1], row[2]) for row in result.all())

    out = []
    d = start_date
    while d <= end_date:
        for sk in slot_keys:
            if (d, sk["period"], sk["hour"]) not in occupied:
                out.append({
                    "date": d.isoformat(),
                    "period": sk["period"],
                    "hour": sk["hour"],
                })
        d += timedelta(days=1)
    return out
