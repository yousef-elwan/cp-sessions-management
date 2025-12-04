"""Prerequisites Tests

Tests for topic prerequisites validation and tracking.
Ensures students cannot book sessions without completing prerequisites.
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid


BASE_URL = "http://localhost:8000"


async def get_admin_token():
    """Get admin access token"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        resp = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return resp.json()["access_token"]


async def create_student(email: str, password: str = "Pass123!"):
    """Helper to create and login a student"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Register
        await client.post("/auth/register", json={
            "name": f"Student {email}",
            "email": email,
            "password": password
        })
        
        # Login
        login_resp = await client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        return login_resp.json()["access_token"]


@pytest.mark.asyncio
async def test_booking_blocked_by_missing_prerequisite():
    """
    Test that a student cannot book a session if they haven't
    completed the prerequisite topic.
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create prerequisite topic (Python Basics)
        prereq_topic_resp = await client.post("/topics/", json={
            "name": f"Python Basics {uuid.uuid4().hex[:4]}",
            "description": "Prerequisite topic"
        }, headers=admin_headers)
        prereq_topic_id = prereq_topic_resp.json()["id"]
        
        # Create advanced topic (Advanced Python) that requires prerequisite
        advanced_topic_resp = await client.post("/topics/", json={
            "name": f"Advanced Python {uuid.uuid4().hex[:4]}",
            "description": "Requires Python Basics"
        }, headers=admin_headers)
        advanced_topic_id = advanced_topic_resp.json()["id"]
        
        # Add prerequisite relationship
        resp = await client.post("/topic-prerequisites/", json={
            "topic_id": advanced_topic_id,
            "prerequisite_topic_id": prereq_topic_id
        }, headers=admin_headers)
        assert resp.status_code == 200

        # Create session for advanced topic
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Advanced Python Session",
            "start_time": start_time,
            "topic_id": advanced_topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
    
    # Create student who hasn't completed prerequisite
    student_email = f"prereq_student_{uuid.uuid4().hex[:6]}@test.com"
    student_token = await create_student(student_email)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Try to book the advanced session (should fail)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        booking_resp = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student_headers)
        
        # Should be rejected due to missing prerequisite
        assert booking_resp.status_code == 400
        assert "prerequisite" in booking_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_booking_allowed_with_completed_prerequisite():
    """
    Test that a student CAN book a session after completing
    the prerequisite topic.
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create prerequisite topic
        prereq_topic_resp = await client.post("/topics/", json={
            "name": f"Intro Topic {uuid.uuid4().hex[:4]}",
            "description": "Prerequisite"
        }, headers=admin_headers)
        prereq_topic_id = prereq_topic_resp.json()["id"]
        
        # Create advanced topic
        advanced_topic_resp = await client.post("/topics/", json={
            "name": f"Advanced Topic {uuid.uuid4().hex[:4]}",
            "description": "Requires Intro"
        }, headers=admin_headers)
        advanced_topic_id = advanced_topic_resp.json()["id"]
        
        # Add prerequisite
        resp = await client.post("/topic-prerequisites/", json={
            "topic_id": advanced_topic_id,
            "prerequisite_topic_id": prereq_topic_id
        }, headers=admin_headers)
        assert resp.status_code == 200
        
        # Create sessions for both topics
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Prerequisite session
        prereq_start = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        prereq_session_resp = await client.post("/sessions/", json={
            "title": "Intro Session",
            "start_time": prereq_start,
            "topic_id": prereq_topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        prereq_session_id = prereq_session_resp.json()["id"]
        
        # Advanced session
        adv_start = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        adv_session_resp = await client.post("/sessions/", json={
            "title": "Advanced Session",
            "start_time": adv_start,
            "topic_id": advanced_topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        adv_session_id = adv_session_resp.json()["id"]
    
    # Create student
    student_email = f"completed_prereq_student_{uuid.uuid4().hex[:6]}@test.com"
    student_token = await create_student(student_email)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Get student ID
        me_resp = await client.get("/auth/me", headers=student_headers)
        student_id = me_resp.json()["id"]

        # Mark prerequisite topic as completed using admin token
        # POST /students/{student_id}/subjects
        complete_resp = await client.post(
            f"/students/{student_id}/subjects",
            json={"topic_id": prereq_topic_id},
            headers=admin_headers
        )
        assert complete_resp.status_code == 200
        
        # Try to book advanced session (should succeed now)
        adv_booking = await client.post("/bookings/", json={
            "session_id": adv_session_id
        }, headers=student_headers)
        
        # Should succeed since prerequisite is completed
        assert adv_booking.status_code == 201


@pytest.mark.asyncio
async def test_prerequisite_chain():
    """
    Test prerequisite chains: Topic C requires B, B requires A.
    Student must complete A, then B, then can access C.
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create three topics: A (basic), B (intermediate), C (advanced)
        topic_a_resp = await client.post("/topics/", json={
            "name": f"Topic A {uuid.uuid4().hex[:4]}",
            "description": "Basic"
        }, headers=admin_headers)
        topic_a_id = topic_a_resp.json()["id"]
        
        topic_b_resp = await client.post("/topics/", json={
            "name": f"Topic B {uuid.uuid4().hex[:4]}",
            "description": "Intermediate"
        }, headers=admin_headers)
        topic_b_id = topic_b_resp.json()["id"]
        
        topic_c_resp = await client.post("/topics/", json={
            "name": f"Topic C {uuid.uuid4().hex[:4]}",
            "description": "Advanced"
        }, headers=admin_headers)
        topic_c_id = topic_c_resp.json()["id"]
        
        # Setup chain: C requires B, B requires A
        resp1 = await client.post("/topic-prerequisites/", json={
            "topic_id": topic_b_id,
            "prerequisite_topic_id": topic_a_id
        }, headers=admin_headers)
        assert resp1.status_code == 200
        
        resp2 = await client.post("/topic-prerequisites/", json={
            "topic_id": topic_c_id,
            "prerequisite_topic_id": topic_b_id
        }, headers=admin_headers)
        assert resp2.status_code == 200
        
        # Create sessions for each
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        session_a_resp = await client.post("/sessions/", json={
            "title": "Session A",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "topic_id": topic_a_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_a_id = session_a_resp.json()["id"]
        
        session_c_resp = await client.post("/sessions/", json={
            "title": "Session C",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "topic_id": topic_c_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_c_id = session_c_resp.json()["id"]
    
    # Create student
    student_email = f"chain_student_{uuid.uuid4().hex[:6]}@test.com"
    student_token = await create_student(student_email)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Try to book C directly (should fail - needs B)
        booking_c_resp = await client.post("/bookings/", json={
            "session_id": session_c_id
        }, headers=student_headers)
        
        # Should fail due to missing prerequisite B (which also requires A)
        assert booking_c_resp.status_code == 400


@pytest.mark.asyncio
async def test_circular_prerequisite_prevention():
    """
    Test that the system prevents circular prerequisites.
    Example: A requires B, B requires C, C requires A (circular!)
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create three topics
        topic_a_resp = await client.post("/topics/", json={
            "name": f"Circular A {uuid.uuid4().hex[:4]}",
            "description": "Test circular"
        }, headers=admin_headers)
        topic_a_id = topic_a_resp.json()["id"]
        
        topic_b_resp = await client.post("/topics/", json={
            "name": f"Circular B {uuid.uuid4().hex[:4]}",
            "description": "Test circular"
        }, headers=admin_headers)
        topic_b_id = topic_b_resp.json()["id"]
        
        topic_c_resp = await client.post("/topics/", json={
            "name": f"Circular C {uuid.uuid4().hex[:4]}",
            "description": "Test circular"
        }, headers=admin_headers)
        topic_c_id = topic_c_resp.json()["id"]
        
        # Add A requires B
        resp1 = await client.post("/topic-prerequisites/", json={
            "topic_id": topic_a_id,
            "prerequisite_topic_id": topic_b_id
        }, headers=admin_headers)
        assert resp1.status_code == 200
        
        # Add B requires C
        resp2 = await client.post("/topic-prerequisites/", json={
            "topic_id": topic_b_id,
            "prerequisite_topic_id": topic_c_id
        }, headers=admin_headers)
        assert resp2.status_code == 200
        
        # Try to add C requires A (creates circular dependency)
        resp3 = await client.post("/topic-prerequisites/", json={
            "topic_id": topic_c_id,
            "prerequisite_topic_id": topic_a_id
        }, headers=admin_headers)
        
        # Should be rejected due to circular dependency
        assert resp3.status_code == 400
        assert "circular" in resp3.json()["detail"].lower()


@pytest.mark.asyncio
async def test_multiple_prerequisites():
    """
    Test a topic that has multiple prerequisites (AND condition).
    Student must complete ALL prerequisites before accessing the topic.
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create prerequisite topics: Python and SQL
        prereq_python_resp = await client.post("/topics/", json={
            "name": f"Python Basics {uuid.uuid4().hex[:4]}",
            "description": "Python prerequisite"
        }, headers=admin_headers)
        prereq_python_id = prereq_python_resp.json()["id"]
        
        prereq_sql_resp = await client.post("/topics/", json={
            "name": f"SQL Basics {uuid.uuid4().hex[:4]}",
            "description": "SQL prerequisite"
        }, headers=admin_headers)
        prereq_sql_id = prereq_sql_resp.json()["id"]
        
        # Create advanced topic that requires BOTH
        advanced_topic_resp = await client.post("/topics/", json={
            "name": f"Data Science {uuid.uuid4().hex[:4]}",
            "description": "Requires Python AND SQL"
        }, headers=admin_headers)
        advanced_topic_id = advanced_topic_resp.json()["id"]
        
        # Add both prerequisites
        resp1 = await client.post("/topic-prerequisites/", json={
            "topic_id": advanced_topic_id,
            "prerequisite_topic_id": prereq_python_id
        }, headers=admin_headers)
        assert resp1.status_code == 200
        
        resp2 = await client.post("/topic-prerequisites/", json={
            "topic_id": advanced_topic_id,
            "prerequisite_topic_id": prereq_sql_id
        }, headers=admin_headers)
        assert resp2.status_code == 200
        
        # Create session for advanced topic
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        advanced_session_resp = await client.post("/sessions/", json={
            "title": "Data Science Session",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "topic_id": advanced_topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        advanced_session_id = advanced_session_resp.json()["id"]
    
    # Create student
    student_email = f"multi_prereq_student_{uuid.uuid4().hex[:6]}@test.com"
    student_token = await create_student(student_email)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Try to book without completing any prerequisite
        booking_resp = await client.post("/bookings/", json={
            "session_id": advanced_session_id
        }, headers=student_headers)
        
        # Should fail - needs both Python AND SQL
        assert booking_resp.status_code == 400
        assert "prerequisite" in booking_resp.json()["detail"].lower()
