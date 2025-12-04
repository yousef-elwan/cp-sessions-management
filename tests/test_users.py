"""User Management Tests

Tests for user operations:
1. Get Profile (Me)
2. List Users (Admin only)
3. Update Profile
"""
import pytest
import httpx
from app.core.config import settings

BASE_URL = "http://localhost:8000"

async def get_admin_token():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        return response.json()["access_token"]

@pytest.mark.asyncio
async def test_get_me():
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == settings.SUPER_ADMIN_EMAIL
        assert data["role"] == "super_admin"

@pytest.mark.asyncio
async def test_list_users_admin():
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.get("/users/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
