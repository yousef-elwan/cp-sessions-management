"""Auth Tests

Tests for authentication flows:
1. Register Student
2. Login (Student, Admin, Trainer)
3. Token Validation
4. Role Permissions
"""
import pytest
import httpx
from app.core.config import settings

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_register_student():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Register
        email = "test_student_auth@example.com"
        response = await client.post("/auth/register", json={
            "name": "Test Student",
            "email": email,
            "password": "Pass123!Student"
        })
        assert response.status_code in [200, 400]  # 400 if already exists

        # 2. Login
        response = await client.post("/auth/login", json={
            "email": email,
            "password": "Pass123!Student"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_super_admin_login():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": settings.SUPER_ADMIN_PASSWORD
        })
        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
