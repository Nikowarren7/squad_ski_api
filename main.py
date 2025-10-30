# === Squad Ski API v1 ===
# Minimal FastAPI backend with user_id, name, and active status
# Author: Niko Warren 2025

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3, time, uuid

app = FastAPI(title="Squad Ski API v1")

DB = "squad_ski.db"

# ---------- DB SETUP ----------
def db_connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            active INTEGER,
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
    return {"status": "✅ Squad Ski API online", "routes": ["/register", "/update", "/active"]}


@app.post("/register")
async def register(request: Request):
    """
    Registers a new user. Auto-generates a UUID if not provided.
    Example:
    {"name": "Niko"} → returns {"user_id": "...", "name": "Niko"}
    """
    data = await request.json()
    name = data.get("name", "anon")
    user_id = str(uuid.uuid4())

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, name, active, updated) VALUES (?, ?, ?, ?)",
                (user_id, name, 1, time.time()))
    conn.commit()
    conn.close()

    return {"user_id": user_id, "name": name, "active": True}


@app.post("/update")
async def update(request: Request):
    """
    Update a user's active status.
    Example: {"user_id": "...", "active": false}
    """
    data = await request.json()
    user_id = data.get("user_id")
    active = bool(data.get("active", True))

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET active=?, updated=? WHERE user_id=?",
                (1 if active else 0, time.time(), user_id))
    conn.commit()
    conn.close()

    return {"status": "updated", "user_id": user_id, "active": active}


@app.get("/active")
def get_active():
    """
    Returns all users currently active in the last 60 seconds.
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE active=1 AND updated > ?", (time.time() - 60,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/all")
def get_all():
    """
    Returns all users regardless of active status.
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/reset")
def reset():
    """
    Deletes all users (for dev use only)
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    return {"status": "database cleared"}
