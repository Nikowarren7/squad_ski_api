# === Squad Ski API Test ===
# Basic desktop test for write/read to your live Render FastAPI

import requests
import time
import random

API_BASE = "https://squad-ski-api.onrender.com"
TEST_NAME = "Marshall_Test"


def register_user():
    print("📡 Registering user...")
    r = requests.post(f"{API_BASE}/register", json={"name": TEST_NAME})
    print("Status:", r.status_code)
    print("Response:", r.json())
    return r.json().get("user_id")


def update_user(user_id, active=True, lat=None, lon=None, alt=None, trail=None):
    print("🔁 Updating user...")
    payload = {"user_id": user_id, "active": active}
    if lat is not None:
        payload["lat"] = lat
    if lon is not None:
        payload["lon"] = lon
    if alt is not None:
        payload["alt"] = alt
    if trail is not None:
        payload["trail"] = trail

    r = requests.post(f"{API_BASE}/update", json=payload)
    print("Status:", r.status_code)
    print("Response:", r.json())


def get_active_users():
    print("🧠 Fetching active riders...")
    r = requests.get(f"{API_BASE}/active")
    print("Status:", r.status_code)
    print("Response:", r.json())


def main():
    user_id = register_user()
    time.sleep(1)

    # Send some fake GPS data
    update_user(
        user_id,
        active=True,
        lat=39.123456,
        lon=-106.654321,
        alt=2925.5,
        trail="GreenGlades01",
    )

    time.sleep(1)
    get_active_users()


if __name__ == "__main__":
    main()
