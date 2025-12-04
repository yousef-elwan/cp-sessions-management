"""Topic Tests

Tests for topic management:
1. Create Topic (Admin)
2. List Topics
3. Update/Delete Topic
"""
import pytest
import httpx
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

@pytest.mark.asyncio
async def test_create_topic():
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    topic_name = f"Test Topic {uuid.uuid4().hex[:6]}"
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/topics/", json={
            "name": topic_name,
            "description": "Test Description"
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == topic_name
        return data["id"]

@pytest.mark.asyncio
async def test_list_topics():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/topics/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
