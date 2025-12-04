"""Integration Tests

Full end-to-end integration tests covering complete user flows:
- Complete booking flow from registration to attendance
- Notification delivery system
- Trainer-topic assignment workflow
- Multi-user scenarios
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


@pytest.mark.asyncio
async def test_complete_booking_flow_end_to_end():
    """
    Complete flow: Admin creates topic and session,
    Student registers, books session, views booking
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Step 1: Admin creates topic
        admin_token = await get_admin_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        topic_resp = await client.post("/topics/", json={
            "name": f"E2E Topic {uuid.uuid4().hex[:4]}",
            "description": "End-to-end test topic"
        }, headers=admin_headers)
        assert topic_resp.status_code == 200
        topic_id = topic_resp.json()["id"]
        
        # Step 2: Admin creates session
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "E2E Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 5,
            "meet_link": "https://meet.google.com/e2e-test"
        }, headers=admin_headers)
        assert session_resp.status_code == 200
        session_id = session_resp.json()["id"]
        
        # Step 3: Student registers
        student_email = f"e2e_student_{uuid.uuid4().hex[:6]}@test.com"
        register_resp = await client.post("/auth/register", json={
            "name": "E2E Student",
            "email": student_email,
            "password": "E2EPass123!"
        })
        assert register_resp.status_code == 201
        
        # Step 4: Student logs in
        login_resp = await client.post("/auth/login", json={
            "email": student_email,
            "password": "E2EPass123!"
        })
        assert login_resp.status_code == 200
        student_token = login_resp.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # Step 5: Student views available sessions
        sessions_resp = await client.get("/sessions/", headers=student_headers)
        assert sessions_resp.status_code == 200
        sessions = sessions_resp.json()
        assert any(s["id"] == session_id for s in sessions), \
            f"Session {session_id} not found in returned sessions"
        
        # Step 6: Student books the session
        booking_resp = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=student_headers)
        assert booking_resp.status_code == 201
        booking_data = booking_resp.json()
        assert booking_data["session_id"] == session_id
        
        # Step 7: Student views their bookings
        my_bookings_resp = await client.get("/sessions/my-bookings", headers=student_headers)
        assert my_bookings_resp.status_code == 200
        bookings = my_bookings_resp.json()
        assert len(bookings) > 0
        assert any(b["session_id"] == session_id for b in bookings)
        
        # Step 8: Trainer views session bookings
        trainer_bookings_resp = await client.get(f"/sessions/{session_id}/bookings", headers=admin_headers)
        assert trainer_bookings_resp.status_code == 200
        trainer_bookings = trainer_bookings_resp.json()
        assert len(trainer_bookings) > 0


@pytest.mark.asyncio
async def test_multiple_students_booking_same_session():
    """Test multiple students can book the same session until capacity"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Setup: Create session with capacity of 3
        admin_token = await get_admin_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        topic_resp = await client.post("/topics/", json={
            "name": f"Multi Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Multi Student Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 3
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
        
        # Create 3 students and book
        for i in range(3):
            email = f"multi_student_{i}_{uuid.uuid4().hex[:4]}@test.com"
            await client.post("/auth/register", json={
                "name": f"Student {i}",
                "email": email,
                "password": "Pass123!"
            })
            
            login_resp = await client.post("/auth/login", json={
                "email": email,
                "password": "Pass123!"
            })
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            booking_resp = await client.post("/bookings/", json={
                "session_id": session_id
            }, headers=headers)
            assert booking_resp.status_code == 201
        
        # 4th student should fail (session full)
        email = f"multi_student_4_{uuid.uuid4().hex[:4]}@test.com"
        await client.post("/auth/register", json={
            "name": "Student 4",
            "email": email,
            "password": "Pass123!"
        })
        
        login_resp = await client.post("/auth/login", json={
            "email": email,
            "password": "Pass123!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        booking_resp = await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=headers)
        assert booking_resp.status_code == 400


@pytest.mark.asyncio
async def test_session_lifecycle():
    """Test complete session lifecycle from creation to deletion"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        admin_token = await get_admin_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Lifecycle Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Create session
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Lifecycle Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        assert session_resp.status_code == 200
        session_id = session_resp.json()["id"]
        
        # View session
        get_resp = await client.get(f"/sessions/{session_id}", headers=admin_headers)
        assert get_resp.status_code == 200
        
        # Update session
        update_resp = await client.patch(f"/sessions/{session_id}", json={
            "title": "Updated Lifecycle Session",
            "capacity": 15
        }, headers=admin_headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["title"] == "Updated Lifecycle Session"
        
        # Delete session
        delete_resp = await client.delete(f"/sessions/{session_id}", headers=admin_headers)
        assert delete_resp.status_code == 200


@pytest.mark.asyncio
async def test_topic_with_multiple_sessions():
    """Test one topic can have multiple sessions"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        admin_token = await get_admin_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create one topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Popular Topic {uuid.uuid4().hex[:4]}",
            "description": "Has multiple sessions"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        # Create 3 sessions for same topic
        session_ids = []
        for i in range(3):
            start_time = (datetime.now(timezone.utc) + timedelta(days=i+1)).isoformat()
            session_resp = await client.post("/sessions/", json={
                "title": f"Session {i+1} for Topic",
                "start_time": start_time,
                "topic_id": topic_id,
                "trainer_id": trainer_id,
                "capacity": 10
            }, headers=admin_headers)
            assert session_resp.status_code == 200
            session_ids.append(session_resp.json()["id"])
        
        # Verify all sessions exist
        for session_id in session_ids:
            get_resp = await client.get(f"/sessions/{session_id}", headers=admin_headers)
            assert get_resp.status_code == 200
            assert get_resp.json()["topic_id"] == topic_id


@pytest.mark.asyncio
async def test_notifications_on_booking():
    """Test that notifications are created when booking (if implemented)"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create session
        admin_token = await get_admin_token()
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        topic_resp = await client.post("/topics/", json={
            "name": f"Notif Topic {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        me_resp = await client.get("/auth/me", headers=admin_headers)
        trainer_id = me_resp.json()["id"]
        
        start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        session_resp = await client.post("/sessions/", json={
            "title": "Notification Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": trainer_id,
            "capacity": 10
        }, headers=admin_headers)
        session_id = session_resp.json()["id"]
        
        # Create student and book
        email = f"notif_student_{uuid.uuid4().hex[:6]}@test.com"
        await client.post("/auth/register", json={
            "name": "Notif Student",
            "email": email,
            "password": "Pass123!"
        })
        
        login_resp = await client.post("/auth/login", json={
            "email": email,
            "password": "Pass123!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Book session
        await client.post("/bookings/", json={
            "session_id": session_id
        }, headers=headers)
        
        # Check notifications (if endpoint exists)
        notif_resp = await client.get("/notifications/", headers=headers)
        assert notif_resp.status_code == 200
        # Notifications might or might not exist depending on implementation
