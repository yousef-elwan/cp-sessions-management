"""Session Tests

Tests for session management:
1. Create Session
2. List Sessions
3. Session Capacity Logic
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def get_admin_token():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return response.json()["access_token"]

async def create_test_topic(headers):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        resp = await client.post("/topics/", json={
            "name": f"Session Topic {uuid.uuid4().hex[:4]}",
            "description": "Desc"
        }, headers=headers)
        return resp.json()["id"]

@pytest.mark.asyncio
async def test_create_session():
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Need a topic and trainer first
    topic_id = await create_test_topic(headers)
    
    # Get admin ID as trainer (since admin can be trainer)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        me = await client.get("/auth/me", headers=headers)
        trainer_id = me.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        response = await client.post("/sessions/", json={
            "title": "Test Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10,
            "duration_minutes": 60
        }, headers=headers)
        
        if response.status_code != 200:
            print(f"Session creation failed: {response.text}")
        
        assert response.status_code == 200
        assert response.json()["title"] == "Test Session"
