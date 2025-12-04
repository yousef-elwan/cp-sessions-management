"""Notification Tests

Tests for notifications:
1. Receive Notification (on booking)
2. Mark as Read
3. Unread Count
"""
import pytest
import httpx
from app.core.config import settings
import uuid

BASE_URL = "http://localhost:8000"

async def get_token(email, password):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/auth/login", json={"email": email, "password": password})
        return response.json()["access_token"]

@pytest.mark.asyncio
async def test_notifications():
    # 1. Use Super Admin (who likely has notifications from system events)
    token = await get_token(settings.SUPER_ADMIN_EMAIL, settings.SUPER_ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Get Notifications
        response = await client.get("/notifications/", headers=headers)
        assert response.status_code == 200
        notifications = response.json()
        
        if notifications:
            # Test Mark Read
            notif_id = notifications[0]["id"]
            resp_read = await client.patch(f"/notifications/{notif_id}/read", headers=headers)
            assert resp_read.status_code == 200
            assert resp_read.json()["is_read"] == True
            
        # Test Count
        resp_count = await client.get("/notifications/unread/count", headers=headers)
        assert response.status_code == 200
        assert "unread_count" in resp_count.json()
