# === SmartSki HUD Skill: API Read ===
# Pulls list of active users + positions from Squad Ski API
# Niko Warren 2025

import urequests

API_BASE = "https://squad-ski-api.onrender.com"

def get_active_users():
    """Fetch list of active riders + their positions."""
    try:
        res = urequests.get(f"{API_BASE}/active")
        if res.status_code == 200:
            data = res.json()
            print("🏂 Active riders:")
            if not data:
                print("   (none online yet)")
            else:
                for u in data:
                    lat = u.get("lat", 0.0)
                    lon = u.get("lon", 0.0)
                    alt = u.get("alt", 0.0)

                    print(
                        f"   {u.get('name','anon')} ({u['user_id'][:6]})  "
                        f"lat={lat:.6f}, lon={lon:.6f}, alt={alt:.1f}"
                    )

            return data
        else:
            print("❌ Fetch failed:", res.status_code)
            return []
    except Exception as e:
        print("⚠️ Read error:", e)
        return []
