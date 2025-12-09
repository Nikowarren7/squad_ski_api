# === Squad Ski API v2 ===
# FastAPI backend with user_id, name, active status,
# plus optional GPS (lat/lon), altitude, and trail name.
# Author: Niko Warren 2025, extended for SmartSki HUD.

from fastapi import FastAPI, Request
import sqlite3
import time
import uuid

app = FastAPI(title="Squad Ski API v2")

# Bump the DB filename so we get a clean schema without touching the old file.
DB = "squad_ski_v2.db"


# ---------- DB SETUP ----------
def db_connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the users table with extended fields if it doesn't exist.
    Columns:
      user_id TEXT PRIMARY KEY
      name    TEXT
      active  INTEGER
      updated REAL (unix timestamp)
      lat     REAL (latitude)
      lon     REAL (longitude)
      alt     REAL (altitude, meters)
      trail   TEXT (up to 16 characters, enforced in code)
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name    TEXT,
            active  INTEGER,
            updated REAL,
            lat     REAL,
            lon     REAL,
            alt     REAL,
            trail   TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    print("✅ Database ready!")


init_db()


# ---------- ROUTES ----------


@app.get("/")
def index():
    return {
        "status": "✅ Squad Ski API online",
        "routes": ["/register", "/update", "/active", "/all", "/reset"],
    }


@app.post("/register")
async def register(request: Request):
    """
    Registers a new user. Auto-generates a UUID if not provided.
    Example:
      {"name": "Niko"}
      → returns {"user_id": "...", "name": "Niko", "active": true}
    """
    data = await request.json()
    name = data.get("name", "anon")
    user_id = str(uuid.uuid4())

    now = time.time()

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (user_id, name, active, updated, lat, lon, alt, trail)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, 1, now, None, None, None, ""),
    )
    conn.commit()
    conn.close()

    return {"user_id": user_id, "name": name, "active": True}


@app.post("/update")
async def update(request: Request):
    """
    Update a user's status and/or telemetry.

    Old style (still supported):
      {"user_id": "...", "active": false}

    New style with GPS/alt/trail:
      {
        "user_id": "...",
        "active": true,
        "lat": 39.123456,
        "lon": -106.123456,
        "alt": 2900.5,
        "trail": "GreenRun01"
      }

    Any field you omit is left unchanged.
    'updated' is always refreshed to "now".
    """
    data = await request.json()
    user_id = data.get("user_id")
    if not user_id:
        return {"error": "user_id required"}

    fields = ["updated=?"]
    values = [time.time()]

    # Optional fields — only update if present in JSON
    if "active" in data:
        active = bool(data.get("active", True))
        fields.append("active=?")
        values.append(1 if active else 0)
    else:
        active = None  # for response only

    if "lat" in data:
        fields.append("lat=?")
        values.append(float(data["lat"]))

    if "lon" in data:
        fields.append("lon=?")
        values.append(float(data["lon"]))

    if "alt" in data:
        fields.append("alt=?")
        values.append(float(data["alt"]))

    if "trail" in data:
        # Enforce max 16 chars on trail name
        trail = str(data["trail"] or "")[:16]
        fields.append("trail=?")
        values.append(trail)
    else:
        trail = None  # for response only

    # Build and run UPDATE
    set_clause = ", ".join(fields)
    sql = f"UPDATE users SET {set_clause} WHERE user_id=?"
    values.append(user_id)

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()

    # Fetch updated row to return full state
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error": "user_id not found", "user_id": user_id}

    row_dict = dict(row)
    # Normalize active back to bool in response
    row_dict["active"] = bool(row_dict.get("active", 0))

    return {"status": "updated", **row_dict}


@app.get("/active")
def get_active():
    """
    Returns all users currently active in the last 60 seconds,
    including lat/lon/alt/trail if present.
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE active=1 AND updated > ?",
        (time.time() - 60,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Normalize active to bool for nicer JSON
    for r in rows:
        r["active"] = bool(r.get("active", 0))
    return rows


@app.get("/all")
def get_all():
    """
    Returns all users regardless of active status,
    including lat/lon/alt/trail if present.
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for r in rows:
        r["active"] = bool(r.get("active", 0))
    return rows


@app.get("/reset")
def reset():
    """
    Deletes all users (for dev use only).
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    return {"status": "database cleared"}
