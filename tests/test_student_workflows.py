"""Student Workflow Tests

Comprehensive tests for student user operations:
- Registration and login
- Browsing topics and sessions
- Booking sessions
- Viewing own bookings
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def create_test_student():
    """Helper to create and login a test student"""
    email = f"student_{uuid.uuid4().hex[:8]}@test.com"
    password = "Student123!"
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Register
        await client.post("/auth/register", json={
            "name": "Test Student",
            "email": email,
            "password": password
        })
        
        # Login
        login_resp = await client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        return login_resp.json()["access_token"]


async def get_admin_token():
    """Get admin token for setup"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return response.json()["access_token"]


@pytest.mark.asyncio
async def test_student_registration():
    """Test student can register successfully"""
    email = f"new_student_{uuid.uuid4().hex[:6]}@test.com"
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/register", json={
            "name": "New Student",
            "email": email,
            "password": "Pass123!New"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "email" in data


@pytest.mark.asyncio
async def test_student_login():
    """Test student can login after registration"""
    email = f"login_student_{uuid.uuid4().hex[:6]}@test.com"
    password = "LoginPass123!"
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Register first
        await client.post("/auth/register", json={
            "name": "Login Student",
            "email": email,
            "password": password
        })
        
        # Login
        response = await client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_student_view_own_profile():
    """Test student can view their own profile"""
    token = await create_test_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "student"
        assert "email" in data


@pytest.mark.asyncio
async def test_student_browse_topics():
    """Test student can browse available topics"""
    token = await create_test_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/topics/", headers=headers)
        
        assert response.status_code == 200
        topics = response.json()
        assert isinstance(topics, list)


@pytest.mark.asyncio
async def test_student_browse_sessions():
    """Test student can browse available sessions"""
    token = await create_test_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/sessions/", headers=headers)
        
        assert response.status_code == 200
        sessions = response.json()
        assert isinstance(sessions, list)


@pytest.mark.asyncio
async def test_student_book_session():
    """Test student can book an available session"""
    # Setup: Create session as admin
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Book Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        # Get admin ID
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Create session
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Bookable Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
        
        # Student books session
        student_token = await create_test_student()
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        response = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_student_view_own_bookings():
    """Test student can view their own bookings"""
    token = await create_test_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/sessions/my-bookings", headers=headers)
        
        assert response.status_code == 200
        bookings = response.json()
        assert isinstance(bookings, list)


@pytest.mark.asyncio
async def test_student_cannot_book_twice():
    """Test student cannot book the same session twice"""
    # Setup session
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic and session
        topic_resp = await client.post("/topics/", json={
            "name": f"Double Book Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Double Book Test",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
        
        # Student books once
        student_token = await create_test_student()
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        first_booking = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student_headers)
        assert first_booking.status_code == 201
        
        # Try to book again
        second_booking = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student_headers)
        assert second_booking.status_code == 400
        assert "already booked" in second_booking.json()["detail"].lower()
