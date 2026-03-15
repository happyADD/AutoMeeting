"""Seed counselors and slot_templates. Run from backend dir: python -m scripts.seed_db."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.db import engine, AsyncSessionLocal, Base
from app.models import Counselor, SlotTemplate


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        r = await session.execute(select(Counselor).limit(1))
        if r.scalar_one_or_none():
            print("DB already has counselors, skip seed.")
            return

        for emp_id, name, email in [
            ("T001", "张老师", "zhang@example.com"),
            ("T002", "李老师", "li@example.com"),
            ("T003", "王老师", "wang@example.com"),
        ]:
            session.add(Counselor(employee_id=emp_id, name=name, email=email, is_active=True))

        r = await session.execute(select(SlotTemplate).limit(1))
        if not r.scalar_one_or_none():
            for period, hour in [
                ("morning", 8), ("morning", 9), ("morning", 10), ("morning", 11),
                ("afternoon", 14), ("afternoon", 15), ("afternoon", 16), ("afternoon", 17),
            ]:
                session.add(SlotTemplate(period=period, hour=hour))
        await session.commit()
    print("Seed done.")


if __name__ == "__main__":
    asyncio.run(seed())
