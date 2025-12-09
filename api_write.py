# === SmartSki HUD Skill: API Write ===
# Posts ONLY lat, lon, alt to Squad Ski API
# Niko Warren 2025

import urequests
import time

API_BASE = "https://squad-ski-api.onrender.com"
USER_NAME = "Niko"
USER_ID = None


def register_user():
    global USER_ID
    try:
        print("📡 Registering...")
        res = urequests.post(f"{API_BASE}/register", json={"name": USER_NAME})
        if res.status_code == 200:
            data = res.json()
            USER_ID = data.get("user_id")
            print(f"✅ Registered as {USER_NAME} ({USER_ID[:6]})")
        else:
            print("❌ Register failed:", res.status_code)
    except Exception as e:
        print("⚠️ Register error:", e)


def update_position(lat, lon, alt, active=True):
    global USER_ID

    if not USER_ID:
        print("⚠️ No user ID → registering...")
        register_user()
        return

    payload = {
        "user_id": USER_ID,
        "lat": float(lat),
        "lon": float(lon),
        "alt": float(alt),
        "active": active
    }

    try:
        res = urequests.post(f"{API_BASE}/update", json=payload)
        if res.status_code == 200:
            print("📡 Position updated:", res.json())
        else:
            print("❌ API update error:", res.status_code)
    except Exception as e:
        print("⚠️ Update exception:", e)
