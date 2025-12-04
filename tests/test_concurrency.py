"""Concurrency Tests

Tests for concurrent operations to ensure thread-safety and prevent race conditions.
Critical for production deployment.
"""
import pytest
import httpx
import asyncio
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
async def test_concurrent_bookings_last_seat():
    """
    Test multiple students trying to book the last seat simultaneously.
    Only one should succeed, others should get 400 (session full).
    """
    # Setup: Create session with capacity of 1
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Concurrency Topic {uuid.uuid4().hex[:4]}",
            "description": "Test concurrent bookings"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        # Get trainer ID
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Create session with capacity of 1 (only one seat)
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Last Seat Test",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 1
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
    
    # Create 5 students
    student_tokens = []
    for i in range(5):
        email = f"concurrent_student_{i}_{uuid.uuid4().hex[:4]}@test.com"
        token = await create_student(email)
        student_tokens.append(token)
    
    # All 5 students try to book the same session simultaneously
    async def book_session(token):
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            try:
                response = await client.post("/bookings/", json={
                    "session_id": session_id
                }, headers={"Authorization": f"Bearer {token}"})
                return response.status_code
            except Exception as e:
                return None
    
    # Execute all bookings concurrently
    results = await asyncio.gather(*[book_session(token) for token in student_tokens])
    
    # Verify results: exactly 1 success (201), rest should fail (400)
    success_count = sum(1 for r in results if r == 201)
    failed_count = sum(1 for r in results if r == 400)
    
    assert success_count == 1, f"Expected exactly 1 success, got {success_count}"
    assert failed_count == 4, f"Expected 4 failures, got {failed_count}"


@pytest.mark.asyncio
async def test_concurrent_bookings_multiple_seats():
    """
    Test concurrent bookings with multiple available seats.
    Should handle all bookings correctly up to capacity.
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Multi Seat Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Create session with capacity of 3
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Multi Seat Test",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 3
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
    
    # Create 5 students (more than capacity)
    student_tokens = []
    for i in range(5):
        email = f"multi_seat_student_{i}_{uuid.uuid4().hex[:4]}@test.com"
        token = await create_student(email)
        student_tokens.append(token)
    
    async def book_session(token):
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            try:
                response = await client.post("/bookings/", json={
                    "session_id": session_id
                }, headers={"Authorization": f"Bearer {token}"})
                return response.status_code
            except Exception:
                return None
    
    # Execute all bookings concurrently
    results = await asyncio.gather(*[book_session(token) for token in student_tokens])
    
    # Verify: exactly 3 successes, 2 failures
    success_count = sum(1 for r in results if r == 201)
    failed_count = sum(1 for r in results if r == 400)
    
    assert success_count == 3, f"Expected exactly 3 successes, got {success_count}"
    assert failed_count == 2, f"Expected 2 failures, got {failed_count}"


@pytest.mark.asyncio
async def test_concurrent_session_updates():
    """
    Test concurrent updates to the same session.
    Should handle all updates without data corruption.
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create session
        topic_resp = await client.post("/topics/", json={
            "name": f"Update Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Original Title",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
    
    # Multiple concurrent updates
    async def update_session(title_suffix):
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            try:
                response = await client.patch(f"/sessions/{session_id}", json={
                    "title": f"Updated Title {title_suffix}"
                }, headers=admin_headers)
                return response.status_code
            except Exception:
                return None
    
    # Execute 5 concurrent updates
    results = await asyncio.gather(*[update_session(i) for i in range(5)])
    
    # All updates should succeed (200)
    success_count = sum(1 for r in results if r == 200)
    assert success_count >= 4, f"Expected at least 4 successful updates, got {success_count}"
    
    # Verify session still exists and is valid
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        final_resp = await client.get(f"/sessions/{session_id}", headers=admin_headers)
        assert final_resp.status_code == 200
        final_data = final_resp.json()
        assert "Updated Title" in final_data["title"]


@pytest.mark.asyncio
async def test_no_double_booking():
    """
    Ensure a student cannot book the same session twice,
    even with concurrent requests.
    """
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create session
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        topic_resp = await client.post("/topics/", json={
            "name": f"Double Book Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "No Double Book Test",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
    
    # Create one student
    student_email = f"double_book_student_{uuid.uuid4().hex[:6]}@test.com"
    student_token = await create_student(student_email)
    
    # Same student tries to book 3 times concurrently
    async def book_session():
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            try:
                response = await client.post("/bookings/", json={
                    "session_id": session_id
                }, headers={"Authorization": f"Bearer {student_token}"})
                return response.status_code
            except Exception:
                return None
    
    # Execute 3 concurrent booking attempts
    results = await asyncio.gather(*[book_session() for _ in range(3)])
    
    # Only 1 should succeed, rest should fail
    success_count = sum(1 for r in results if r == 201)
    failed_count = sum(1 for r in results if r == 400)
    
    assert success_count == 1, f"Expected exactly 1 success, got {success_count}"
    assert failed_count == 2, f"Expected 2 failures (already booked), got {failed_count}"
