# === SmartSki HUD Skill: API Read ===
# Pulls list of active users + positions from Squad Ski API

import urequests

API_BASE = "https://squad-ski-api.onrender.com"


def get_active_users():
    """Fetch list of active riders + their positions."""
    try:
        res = urequests.get(f"{API_BASE}/active")
        if res.status_code == 200:
            data = res.json()
            print("Active riders:")
            if not data:
                print("   (none online yet)")
            else:
                for u in data:
                    lat = u.get("lat")
                    lon = u.get("lon")
                    alt = u.get("alt")
                    trail = u.get("trail") or ""

                    lat_s = f"{lat:.6f}" if lat is not None else "n/a"
                    lon_s = f"{lon:.6f}" if lon is not None else "n/a"
                    alt_s = f"{alt:.1f}" if alt is not None else "n/a"

                    print(
                        f"   {u.get('name', 'anon')} ({u['user_id'][:6]})  "
                        f"lat={lat_s}, lon={lon_s}, alt={alt_s}, trail={trail!r}"
                    )

            return data
        else:
            print("Fetch failed:", res.status_code)
            return []
    except Exception as e:
        print("Read error:", e)
        return []
