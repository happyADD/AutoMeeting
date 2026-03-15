"""API integration tests: counselors, availability, appointments."""
import pytest
from unittest.mock import patch
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_list_counselors(client):
    r = await client.get("/api/workers")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 2
    assert any(c["employee_id"] == "T001" and c["name"] == "张老师" for c in data)


@pytest.mark.asyncio
async def test_availability_empty(client):
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=7)).isoformat()
    r = await client.get(f"/api/availability?counselor_id=1&start_date={start}&end_date={end}")
    assert r.status_code == 200
    slots = r.json()
    assert isinstance(slots, list)
    # Should have slots for each day in range
    assert len(slots) >= 4 * 8  # 8 days * 4 slots per day


@pytest.mark.asyncio
async def test_create_appointment_success(client):
    start = date.today() + timedelta(days=1)
    with patch("app.api.appointments.send_appointment_email"):
        r = await client.post(
            "/api/appointments",
            json={
                "counselor_id": 1,
                "date": start.isoformat(),
                "period": "morning",
                "hour": 8,
                "content": "学业咨询",
                "contact_name": "小明",
                "contact_phone": "13800138000",
                "contact_email": "xiaoming@test.com",
            },
        )
    assert r.status_code == 200
    data = r.json()
    assert data["counselor_id"] == 1
    assert data["date"] == start.isoformat()
    assert data["period"] == "morning"
    assert data["hour"] == 8
    assert data["contact_name"] == "小明"


@pytest.mark.asyncio
async def test_create_appointment_conflict(client):
    start = date.today() + timedelta(days=2)
    payload = {
        "counselor_id": 1,
        "date": start.isoformat(),
        "period": "morning",
        "hour": 9,
        "content": "第一次",
        "contact_name": "用户A",
        "contact_phone": "13900000001",
    }
    with patch("app.api.appointments.send_appointment_email"):
        r1 = await client.post("/api/appointments", json=payload)
    assert r1.status_code == 200
    r2 = await client.post("/api/appointments", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_create_appointment_validation(client):
    start = (date.today() + timedelta(days=1)).isoformat()
    r = await client.post(
        "/api/appointments",
        json={
            "counselor_id": 1,
            "date": start,
            "period": "morning",
            "hour": 8,
            "content": "",
            "contact_name": "Test",
            "contact_phone": None,
            "contact_email": None,
        },
    )
    assert r.status_code == 422 or r.status_code == 400  # Pydantic or our validation
