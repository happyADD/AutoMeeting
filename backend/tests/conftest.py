"""Pytest fixtures: test DB, client, seed data."""
import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db
from app.models import Counselor, SlotTemplate, Appointment


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def seeded_session(test_engine):
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
    )
    async with async_session() as session:
        for emp_id, name, email in [
            ("T001", "张老师", "zhang@test.com"),
            ("T002", "李老师", "li@test.com"),
        ]:
            session.add(Counselor(employee_id=emp_id, name=name, email=email, is_active=True))
        for period, hour in [
            ("morning", 8), ("morning", 9), ("afternoon", 14), ("afternoon", 15),
        ]:
            session.add(SlotTemplate(period=period, hour=hour))
        await session.commit()
    yield async_session


@pytest.fixture
async def client(test_engine, seeded_session):
    async def override_get_db():
        async with seeded_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
