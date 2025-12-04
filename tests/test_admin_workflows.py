"""Admin Workflow Tests

Comprehensive tests for admin user operations:
- Admin user creation
- Managing topics, sessions, and users
- Viewing system-wide data
"""
import pytest
import httpx
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def get_super_admin_token():
    """Get super admin token for admin operations"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return response.json()["access_token"]


@pytest.mark.asyncio
async def test_admin_create_topic():
    """Test admin can create topics"""
    token = await get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        topic_name = f"Admin Topic {uuid.uuid4().hex[:6]}"
        response = await client.post("/topics/", json={
            "name": topic_name,
            "description": "Created by admin"
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == topic_name


@pytest.mark.asyncio
async def test_admin_update_topic():
    """Test admin can update topics"""
    token = await get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic first
        topic_resp = await client.post("/topics/", json={
            "name": f"Update Test {uuid.uuid4().hex[:4]}",
            "description": "Original"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        # Update topic
        response = await client.patch(f"/topics/{topic_id}", json={
            "description": "Updated by admin"
        }, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["description"] == "Updated by admin"


@pytest.mark.asyncio
async def test_admin_delete_topic():
    """Test admin can delete topics (soft delete)"""
    token = await get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Delete Test {uuid.uuid4().hex[:4]}",
            "description": "Will be deleted"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        # Delete topic
        response = await client.delete(f"/topics/{topic_id}", headers=headers)
        assert response.status_code == 200
        
        # Verify deleted (shouldn't appear in list)
        list_resp = await client.get("/topics/", headers=headers)
        topic_ids = [t["id"] for t in list_resp.json()]
        assert topic_id not in topic_ids


@pytest.mark.asyncio
async def test_admin_create_session_for_trainer():
    """Test admin can create sessions and assign trainers"""
    token = await get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Get admin ID (will act as trainer)
        me_resp = await client.get("/auth/me", headers=headers)
        admin_id = me_resp.json()["id"]
        
        # Create topic
        topic_resp = await client.post("/topics/", json={
            "name": f"Session Topic {uuid.uuid4().hex[:4]}",
            "description": "For session"
        }, headers=headers)
        topic_id = topic_resp.json()["id"]
        
        # Create session
        start_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        response = await client.post("/sessions/", json={
            "title": "Admin Created Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": admin_id,
            "capacity": 15
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Admin Created Session"
        assert data["capacity"] == 15


@pytest.mark.asyncio
async def test_admin_view_all_users():
    """Test admin can view all users"""
    token = await get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/users/", headers=headers)
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0  # At least super admin exists


@pytest.mark.asyncio
async def test_admin_view_user_profile():
    """Test admin can view any user's profile"""
    token = await get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Get own profile first
        me_resp = await client.get("/auth/me", headers=headers)
        user_id = me_resp.json()["id"]
        
        # View profile
        response = await client.get(f"/users/{user_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_admin_view_all_sessions():
    """Test admin can view all sessions"""
    token = await get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/sessions/", headers=headers)
        
        assert response.status_code == 200
        sessions = response.json()
        assert isinstance(sessions, list)
