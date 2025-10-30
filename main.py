# === SmartSki HUD Shared API (FastAPI + SQLite3) ===
# Author: Niko Warren 2025

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3, time

app = FastAPI(title="SmartSki HUD API")

DB = "ski_hud.db"

# ---------- DB SETUP ----------
def db_connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_users (
            username TEXT PRIMARY KEY,
            lat REAL,
            lon REAL,
            speed REAL,
            max_speed REAL,
            g_force REAL,
            max_g REAL,
            updated REAL
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database ready!")

init_db()


# ---------- ROUTES ----------
@app.get("/")
def index():
    return {"status": "🏔️ SmartSki HUD API online", "routes": ["/update", "/get_all", "/records"]}


@app.post("/update")
async def update(request: Request):
    data = await request.json()
    user = data.get("user", "anon").lower()
    lat, lon = data.get("lat", 0.0), data.get("lon", 0.0)
    speed, g = float(data.get("speed", 0.0)), float(data.get("g", 0.0))

    conn = db_connect()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM active_users WHERE username=?", (user,)).fetchone()

    if row:
        max_speed = max(row["max_speed"], speed)
        max_g = max(row["max_g"], g)
        cur.execute("""
            UPDATE active_users
            SET lat=?, lon=?, speed=?, g_force=?, max_speed=?, max_g=?, updated=?
            WHERE username=?
        """, (lat, lon, speed, g, max_speed, max_g, time.time(), user))
    else:
        cur.execute("""
            INSERT INTO active_users(username, lat, lon, speed, max_speed, g_force, max_g, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user, lat, lon, speed, speed, g, g, time.time()))

    conn.commit()
    conn.close()
    return JSONResponse({"status": "ok", "user": user})


@app.get("/get_all")
def get_all():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM active_users WHERE updated > ?", (time.time() - 60,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/records")
def records():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT username, max_speed, max_g
        FROM active_users
        ORDER BY max_speed DESC
        LIMIT 5
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/reset")
def reset():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM active_users")
    conn.commit()
    conn.close()
    return {"status": "database cleared"}
