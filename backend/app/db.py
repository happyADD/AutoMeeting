"""Database connection and session."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import get_settings

settings = get_settings()

# Check if using SQLite (doesn't support connection pooling)
is_sqlite = settings.database_url.startswith("sqlite")

if is_sqlite:
    # SQLite doesn't support connection pooling
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        poolclass=NullPool,
    )
else:
    # PostgreSQL/MySQL with connection pooling
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create tables. Call on startup."""
    from app.models import Counselor, SlotTemplate, Appointment  # noqa: F401 - register models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_db():
    """Seed initial counselors and slot templates if the database is empty."""
    from sqlalchemy import select
    from app.models import Counselor, SlotTemplate

    async with AsyncSessionLocal() as session:
        counselor_result = await session.execute(select(Counselor).limit(1))
        if not counselor_result.scalar_one_or_none():
            for emp_id, name, email in [
                ("T001", "张老师", "zhang@example.com"),
                ("T002", "李老师", "li@example.com"),
                ("T003", "王老师", "wang@example.com"),
            ]:
                session.add(Counselor(employee_id=emp_id, name=name, email=email, is_active=True))

        slot_result = await session.execute(select(SlotTemplate).limit(1))
        if not slot_result.scalar_one_or_none():
            for period, hour in [
                ("morning", 8), ("morning", 9), ("morning", 10), ("morning", 11),
                ("afternoon", 14), ("afternoon", 15), ("afternoon", 16), ("afternoon", 17),
            ]:
                session.add(SlotTemplate(period=period, hour=hour))

        await session.commit()
