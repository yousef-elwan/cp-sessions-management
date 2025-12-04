"""Trainer Workflow Tests

Comprehensive tests for trainer user operations:
- Trainer registration/assignment
- Creating and managing sessions
- Viewing session bookings
- Managing own sessions only
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def get_admin_token():
    """Get admin token for setup"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return response.json()["access_token"]


async def create_trainer():
    """Create a trainer user (currently trainers are created as regular users with trainer role)"""
    # Note: In current implementation, we use super_admin as trainer
    # In a real scenario, you'd have a separate endpoint to create trainers
    return await get_admin_token()


@pytest.mark.asyncio
async def test_trainer_create_session():
    """Test trainer can create sessions"""
    token = await create_trainer()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic first
        topic_resp = await client.post("/topics/", json={
            "name": f"Trainer Topic {uuid.uuid4().hex[:4]}",
            "description": "For trainer session"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        # Get trainer ID
        me_resp = await client.get("/auth/me", headers=headers)
        trainer_id = me_resp.json()["id"]
        
        # Create session
        start_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        response = await client.post("/sessions/", json={
            "title": "Trainer Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 20,
            "duration_minutes": 90
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Trainer Session"
        assert data["trainer_id"] == trainer_id


@pytest.mark.asyncio
async def test_trainer_view_own_sessions():
    """Test trainer can view their own sessions"""
    token = await create_trainer()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create a session first
        topic_resp = await client.post("/topics/", json={
            "name": f"View Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        await client.post("/sessions/", json={
            "title": "My Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=headers)
        
        # View all sessions
        response = await client.get("/sessions/", headers=headers)
        assert response.status_code == 200
        sessions = response.json()
        assert isinstance(sessions, list)


@pytest.mark.asyncio
async def test_trainer_update_own_session():
    """Test trainer can update their own session"""
    token = await create_trainer()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create session
        topic_resp = await client.post("/topics/", json={
            "name": f"Update Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Original Title",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=headers)
        session_id = session_resp.json()["id"]
        
        # Update session
        response = await client.patch(f"/sessions/{session_id}", json={
            "title": "Updated Title",
            "capacity": 15
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["capacity"] == 15


@pytest.mark.asyncio
async def test_trainer_view_session_bookings():
    """Test trainer can view bookings for their sessions"""
    trainer_token = await create_trainer()
    trainer_headers = {"Authorization": f"Bearer {trainer_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create session
        topic_resp = await client.post("/topics/", json={
            "name": f"Booking Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=trainer_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=trainer_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Bookings Test",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=trainer_headers)
        session_id = session_resp.json()["id"]
        
        # Create a student and book
        student_email = f"booking_student_{uuid.uuid4().hex[:6]}@test.com"
        await client.post("/auth/register", json={
            "name": "Booking Student",
            "email": student_email,
            "password": "Pass123!"
        })
        
        login_resp = await client.post("/auth/login", json={
            "email": student_email,
            "password": "Pass123!"
        })
        student_token = login_resp.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student_headers)
        
        # Trainer views bookings
        response = await client.get(f"/sessions/{session_id}/bookings", headers=trainer_headers)
        assert response.status_code == 200
        bookings = response.json()
        assert isinstance(bookings, list)
        assert len(bookings) > 0


@pytest.mark.asyncio
async def test_trainer_delete_own_session():
    """Test trainer can delete their own session"""
    token = await create_trainer()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create session
        topic_resp = await client.post("/topics/", json={
            "name": f"Delete Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "To Delete",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=headers)
        session_id = session_resp.json()["id"]
        
        # Delete session
        response = await client.delete(f"/sessions/{session_id}", headers=headers)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_trainer_create_session_with_custom_duration():
    """Test trainer can create sessions with custom duration"""
    token = await create_trainer()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        topic_resp = await client.post("/topics/", json={
            "name": f"Duration Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        response = await client.post("/sessions/", json={
            "title": "Long Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10,
            "duration_minutes": 120  # 2 hours
        }, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["duration_minutes"] == 120


@pytest.mark.asyncio
async def test_trainer_create_session_with_meet_link():
    """Test trainer can add meeting link to session"""
    token = await create_trainer()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        topic_resp = await client.post("/topics/", json={
            "name": f"Meet Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        response = await client.post("/sessions/", json={
            "title": "Online Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10,
            "meet_link": "https://meet.google.com/abc-defg-hij"
        }, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["meet_link"] == "https://meet.google.com/abc-defg-hij"
