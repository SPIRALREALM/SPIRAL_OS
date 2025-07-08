"""SQLite helpers to store voice interactions."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path(__file__).resolve().parent / "interactions.db"


def init_db(db_path: Path = DB_PATH) -> None:
    """Create the interactions table if it does not exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                transcript TEXT NOT NULL,
                emotion TEXT NOT NULL,
                response_path TEXT NOT NULL
            )
            """
        )
    conn.close()


def save_interaction(
    transcript: str,
    emotion: str,
    response_path: str,
    *,
    db_path: Path = DB_PATH,
) -> None:
    """Record a conversation entry in the database."""
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO interactions(timestamp, transcript, emotion, response_path) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), transcript, emotion, response_path),
        )
    conn.close()


def fetch_interactions(limit: Optional[int] = None, db_path: Path = DB_PATH) -> List[Dict[str, str]]:
    """Return saved interactions ordered from newest to oldest."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = "SELECT timestamp, transcript, emotion, response_path FROM interactions ORDER BY id DESC"
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "timestamp": row[0],
            "transcript": row[1],
            "emotion": row[2],
            "response_path": row[3],
        }
        for row in rows
    ]


def last_interaction(db_path: Path = DB_PATH) -> Optional[Dict[str, str]]:
    """Return the most recent interaction or ``None`` if database is empty."""
    rows = fetch_interactions(limit=1, db_path=db_path)
    return rows[0] if rows else None


__all__ = [
    "init_db",
    "save_interaction",
    "fetch_interactions",
    "last_interaction",
]
