"""Unit tests for availability service."""
import pytest
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db import Base
from app.models import Counselor, SlotTemplate, Appointment
from app.services.availability import get_availability

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
    )
    async with async_session() as session:
        c = Counselor(employee_id="T1", name="Test", email="t@t.com", is_active=True)
        session.add(c)
        await session.flush()
        for p, h in [("morning", 8), ("morning", 9), ("afternoon", 14)]:
            session.add(SlotTemplate(period=p, hour=h))
        await session.commit()
        await session.refresh(c)
        yield session, c.id
    await engine.dispose()


@pytest.mark.asyncio
async def test_availability_no_appointments(session):
    sess, counselor_id = session
    start = date.today()
    end = start + timedelta(days=2)
    slots = await get_availability(sess, counselor_id, start, end)
    assert len(slots) == 3 * 3  # 3 days * 3 slot templates
    dates = {s["date"] for s in slots}
    assert start.isoformat() in dates
    assert end.isoformat() in dates


@pytest.mark.asyncio
async def test_availability_excludes_booked(session):
    sess, counselor_id = session
    start = date.today()
    end = start + timedelta(days=1)
    # Book one slot
    apt = Appointment(
        counselor_id=counselor_id,
        appointment_date=start,
        period="morning",
        hour=8,
        content="x",
        contact_name="y",
        contact_phone="1",
        status="confirmed",
    )
    sess.add(apt)
    await sess.commit()
    slots = await get_availability(sess, counselor_id, start, end)
    booked = [s for s in slots if s["date"] == start.isoformat() and s["period"] == "morning" and s["hour"] == 8]
    assert len(booked) == 0
