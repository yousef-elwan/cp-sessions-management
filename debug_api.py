import asyncio
import httpx
from app.core.config import settings
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

async def debug_api():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("1. Logging in as Super Admin...")
        try:
            resp = await client.post("/auth/login", json={
                "email": settings.SUPER_ADMIN_EMAIL,
                "password": settings.SUPER_ADMIN_PASSWORD
            })
            if resp.status_code != 200:
                print(f"Login failed: {resp.text}")
                return
            token = resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("Login successful.")
        except Exception as e:
            print(f"Could not connect to server: {e}")
            print("Make sure the server is running: uvicorn app.main:app --reload")
            return

        print("2. Getting User ID...")
        resp = await client.get("/auth/me", headers=headers)
        user_id = resp.json()["id"]
        print(f"User ID: {user_id}")

        print("3. Getting a Topic...")
        resp = await client.get("/topics/", headers=headers)
        topics = resp.json()
        if not topics:
            print("No topics found. Creating one...")
            resp = await client.post("/topics/", json={"name": "Debug Topic", "description": "Debug"}, headers=headers)
            topic_id = resp.json()["id"]
        else:
            topic_id = topics[0]["id"]
        print(f"Topic ID: {topic_id}")

        print("4. Creating Session...")
        start_time = (datetime.now(datetime.UTC) + timedelta(days=1)).isoformat()
        payload = {
            "title": "API Debug Session",
            "start_time": start_time,
            "topic_id": topic_id,
            "trainer_id": user_id,
            "capacity": 10,
            "duration_minutes": 60
        }
        print(f"Payload: {payload}")
        
        resp = await client.post("/sessions/", json=payload, headers=headers)
        print(f"Status Code: {resp.status_code}")
        print(f"Response Body: {resp.text}")

if __name__ == "__main__":
    asyncio.run(debug_api())
