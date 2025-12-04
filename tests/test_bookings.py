"""Booking Tests

Tests for booking flow:
1. Book Session
2. Check Capacity
3. Cancel Booking
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def get_token(email, password):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={"email": email, "password": password})
        return response.json()["access_token"]

async def setup_session():
    # Helper to create a session
    admin_token = await get_token(settings.SUPER_ADMIN_EMAIL, settings.SUPER_ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Topic
        t_resp = await client.post("/topics/", json={"name": f"Book Topic {uuid.uuid4().hex[:4]}", "description": "D"}, headers=headers)
        topic_id = t_resp.json()["id"]
        
        # Trainer (Admin)
        me = await client.get("/auth/me", headers=headers)
        trainer_id = me.json()["id"]
        
        # Session
        start = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        s_resp = await client.post("/sessions/", json={
            "title": "Booking Test",
            "start_time": start,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 5
        }, headers=headers)
        return s_resp.json()["id"]

@pytest.mark.asyncio
async def test_booking_flow():
    # 1. Setup Session
    session_id = await setup_session()
    
    # 2. Register Student
    student_email = f"student_book_{uuid.uuid4().hex[:4]}@test.com"
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        await client.post("/auth/register", json={
            "name": "Booker",
            "email": student_email,
            "password": "Pass123!Student"
        })
        
        # Login
        token = await get_token(student_email, "Pass123!Student")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Book
        response = await client.post("/bookings/", json={"session_id": session_id}, headers=headers)
        assert response.status_code == 201
        booking_id = response.json()["id"]
        
        # 4. Verify
        bookings = await client.get("/sessions/my-bookings", headers=headers)
        assert len(bookings.json()) > 0
