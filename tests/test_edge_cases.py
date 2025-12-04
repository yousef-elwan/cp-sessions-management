"""Edge Cases and Error Handling Tests

Tests for edge cases, error handling, and boundary conditions:
- Duplicate operations
- Invalid inputs
- Capacity limits
- Booking conflicts
- Prerequisites violations
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def get_admin_token():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        resp = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return resp.json()["access_token"]


async def create_student():
    email = f"edge_student_{uuid.uuid4().hex[:6]}@test.com"
    password = "Pass123!"
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Register
        await client.post("/auth/register", json={
            "name": "Edge Student",
            "email": email,
            "password": password
        })
        # Login to get token
        login_resp = await client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        return login_resp.json()["access_token"]


@pytest.mark.asyncio
async def test_duplicate_email_registration():
    """Test duplicate email registration is rejected"""
    email = f"duplicate_{uuid.uuid4().hex[:6]}@test.com"
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # First registration
        resp1 = await client.post("/auth/register", json={
            "name": "First User",
            "email": email,
            "password": "Pass123!"
        })
        assert resp1.status_code == 201
        
        # Try to register again with same email
        resp2 = await client.post("/auth/register", json={
            "name": "Second User",
            "email": email,
            "password": "DifferentPass123!"
        })
        assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_invalid_email_format():
    """Test invalid email format is rejected"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/register", json={
            "name": "Invalid Email",
            "email": "not-an-email",
            "password": "Pass123!"
        })
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_weak_password_rejected():
    """Test weak passwords are rejected"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/register", json={
            "name": "Weak Pass",
            "email": f"weak_{uuid.uuid4().hex[:4]}@test.com",
            "password": "123"  # Too short
        })
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_session_capacity_limit():
    """Test booking fails when session is full"""
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Capacity Test {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        # Get trainer ID
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Create session with capacity of 1
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Full Session Test",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 1  # Only 1 seat
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
        
        # First student books (should succeed)
        student1_token = await create_student()
        student1_headers = {"Authorization": f"Bearer {student1_token}"}
        
        booking1 = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student1_headers)
        assert booking1.status_code == 201
        
        # Second student tries to book (should fail - session full)
        student2_token = await create_student()
        student2_headers = {"Authorization": f"Bearer {student2_token}"}
        
        booking2 = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student2_headers)
        assert booking2.status_code == 400
        assert "full" in booking2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_invalid_session_id():
    """Test booking with invalid session ID"""
    token = await create_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/bookings/", json={
            "session_id": "00000000-0000-0000-0000-000000000000"
        }, headers=headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_past_session_cannot_be_booked():
    """Test cannot book sessions in the past"""
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Past Session {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Create session with past time (1 hour ago)
        # Note: This might be rejected at creation, so we test that
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Past Session",
            "start_time": past_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        
        # If session creation is allowed, try to book it
        if session_resp.status_code == 200:
            session_id = session_resp.json()["id"]
            
            student_token = await create_student()
            student_headers = {"Authorization": f"Bearer {student_token}"}
            
            booking = await client.post("/bookings/", json={
                "session_id": session_id
            }, headers=student_headers)
            assert booking.status_code == 400


@pytest.mark.asyncio
async def test_create_topic_with_empty_name():
    """Test creating topic with empty name fails"""
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/topics/", json={
            "name": "",  # Empty name
            "description": "Test"
        }, headers=headers)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_session_with_zero_capacity():
    """Test creating session with zero capacity fails"""
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Get topic
        topics_resp = await client.get("/topics/", headers=headers)
        topics = topics_resp.json()
        
        if topics:
            topic_id = topics[0]["id"]
            me_resp = await client.get("/auth/me", headers=headers)
            trainer_id = me_resp.json()["id"]
            
            start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            response = await client.post("/sessions/", json={
                "title": "Zero Capacity",
                "start_time": start_time,
                "topic_id": topic_id,
                "trainer_id": trainer_id,
                "capacity": 0  # Invalid
            }, headers=headers)
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_session_with_negative_duration():
    """Test creating session with negative duration fails"""
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        topics_resp = await client.get("/topics/", headers=headers)
        topics = topics_resp.json()
        
        if topics:
            topic_id = topics[0]["id"]
            me_resp = await client.get("/auth/me", headers=headers)
            trainer_id = me_resp.json()["id"]
            
            start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            response = await client.post("/sessions/", json={
                "title": "Negative Duration",
                "start_time": start_time,
                "topic_id": topic_id,
                "trainer_id": trainer_id,
                "capacity": 10,
                "duration_minutes": -30  # Invalid
            }, headers=headers)
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_with_wrong_password():
    """Test login fails with wrong password"""
    email = f"wrong_pass_{uuid.uuid4().hex[:6]}@test.com"
    correct_password = "CorrectPass123!"
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Register
        await client.post("/auth/register", json={
            "name": "User",
            "email": email,
            "password": correct_password
        })
        
        # Try to login with wrong password
        response = await client.post("/auth/login", json={
            "email": email,
            "password": "WrongPass123!"
        })
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_nonexistent_email():
    """Test login fails with non-existent email"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={
            "email": "doesnotexist@test.com",
            "password": "SomePass123!"
        })
        assert response.status_code == 401
