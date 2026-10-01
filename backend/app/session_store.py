"""Small SQLite repository for non-sensitive demo session metadata."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sakhi_sessions.db"

def initialize() -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, language TEXT NOT NULL, demo_mode INTEGER NOT NULL, scheme_id TEXT NOT NULL)")

def save(session: dict) -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT INTO sessions (session_id, language, demo_mode, scheme_id) VALUES (?, ?, ?, ?)", (session["session_id"], session["language"], int(session["demo_mode"]), session["scheme_id"]))

def get(session_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT session_id, language, demo_mode, scheme_id FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    return {"session_id": row[0], "language": row[1], "demo_mode": bool(row[2]), "scheme_id": row[3]} if row else None
