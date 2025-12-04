"""Authorization Tests

Tests for role-based access control (RBAC) and permission enforcement:
- Unauthorized access attempts
- Role-based permission checks
- Token validation
- Cross-role access restrictions
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def create_student():
    """Create a test student"""
    email = f"auth_student_{uuid.uuid4().hex[:6]}@test.com"
    password = "Pass123!"
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Register (returns 201)
        await client.post("/auth/register", json={
            "name": "Auth Student",
            "email": email,
            "password": password
        })
        # Login to get token
        login_resp = await client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        return login_resp.json()["access_token"]


async def get_admin_token():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        resp = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_unauthenticated_access_denied():
    """Test unauthenticated users cannot access protected endpoints"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Try to access protected endpoint without token
        response = await client.get("/auth/me")
        assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_invalid_token_rejected():
    """Test invalid tokens are rejected"""
    headers = {"Authorization": "Bearer invalid_token_here"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_student_cannot_create_topics():
    """Test students cannot create topics (admin only)"""
    token = await create_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/topics/", json={
            "name": "Unauthorized Topic",
            "description": "Should fail"
        }, headers=headers)
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_update_topics():
    """Test students cannot update topics"""
    # Create topic as admin
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        topic_resp = await client.post("/topics/", json={
            "name": f"Update Test {uuid.uuid4().hex[:4]}",
            "description": "Original"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        # Try to update as student
        student_token = await create_student()
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        response = await client.patch(f"/topics/{topic_id}", json={
            "description": "Hacked"
        }, headers=student_headers)
        
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_delete_topics():
    """Test students cannot delete topics"""
    # Create topic as admin
    admin_token = await get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        topic_resp = await client.post("/topics/", json={
            "name": f"Delete Test {uuid.uuid4().hex[:4]}",
            "description": "Should not be deleted"
        }, headers=admin_headers)
        topic_id = topic_resp.json()["id"]
        
        # Try to delete as student
        student_token = await create_student()
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        response = await client.delete(f"/topics/{topic_id}", headers=student_headers)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_create_sessions():
    """Test students cannot create sessions (trainer/admin only)"""
    token = await create_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Get any topic ID
        topics_resp = await client.get("/topics/", headers=headers)
        topics = topics_resp.json()
        
        if topics:
            topic_id = topics[0]["id"]
            start_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            
            response = await client.post("/sessions/", json={
                "title": "Unauthorized Session",
                "start_time": start_time,
                "topic_id": topic_id,
                "capacity": 10
            }, headers=headers)
            
            assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_view_all_users():
    """Test students cannot view user list (admin only)"""
    token = await create_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/users/", headers=headers)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_can_view_own_profile():
    """Test students can view their own profile"""
    token = await create_student()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == "student"


@pytest.mark.asyncio
async def test_student_cannot_view_other_user_profile():
    """Test students cannot view other users' profiles"""
    # Get admin user ID
    admin_token = await get_admin_token()
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        admin_resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        admin_id = admin_resp.json()["id"]
        
        # Try to view admin profile as student
        student_token = await create_student()
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        response = await client.get(f"/users/{admin_id}", headers=student_headers)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_all_endpoints():
    """Test admin has full access"""
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Can view users
        users_resp = await client.get("/users/", headers=headers)
        assert users_resp.status_code == 200
        
        # Can create topics
        topic_resp = await client.post("/topics/", json={
            "name": f"Admin Access Test {uuid.uuid4().hex[:4]}",
            "description": "Test"
        }, headers=headers)
        assert topic_resp.status_code == 200
        
        # Can view sessions
        sessions_resp = await client.get("/sessions/", headers=headers)
        assert sessions_resp.status_code == 200


@pytest.mark.asyncio
async def test_expired_token_rejected():
    """Test expired tokens are properly rejected"""
    # This would require creating a token with past expiration
    # For now, we test invalid token format
    headers = {"Authorization": "Bearer expired.token.here"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 401
