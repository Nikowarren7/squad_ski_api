# === Squad Ski API Test ===
# Basic desktop test for write/read to your live Render FastAPI
# Run this on your laptop (not Pico)
# Niko Warren 2025

import requests
import time

API_BASE = "https://squad-ski-api.onrender.com"
TEST_NAME = "Niko_Test"

def register_user():
    print("📡 Registering user...")
    r = requests.post(f"{API_BASE}/register", json={"name": TEST_NAME})
    print("Status:", r.status_code)
    print("Response:", r.json())
    return r.json().get("user_id")

def update_user(user_id, active=True):
    print("🔁 Updating active status...")
    r = requests.post(f"{API_BASE}/update", json={"user_id": user_id, "active": active})
    print("Status:", r.status_code)
    print("Response:", r.json())

def get_active_users():
    print("🧠 Fetching active riders...")
    r = requests.get(f"{API_BASE}/active")
    print("Status:", r.status_code)
    print("Response:", r.json())

def main():
    user_id = register_user()
    time.sleep(2)
    update_user(user_id, True)
    time.sleep(2)
    get_active_users()

if __name__ == "__main__":
    main()
