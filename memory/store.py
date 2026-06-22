import sqlite3
from datetime import datetime
from config import DB_PATH


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            role      TEXT    NOT NULL,
            content   TEXT    NOT NULL,
            agent     TEXT,
            timestamp TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_message(role: str, content: str, agent: str | None = None) -> None:
    conn = _conn()
    conn.execute(
        "INSERT INTO conversations (role, content, agent, timestamp) VALUES (?, ?, ?, ?)",
        (role, content, agent, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def load_recent(limit: int = 20) -> list[dict]:
    conn = _conn()
    rows = conn.execute(
        "SELECT role, content, agent, timestamp FROM conversations "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {"role": r[0], "content": r[1], "agent": r[2], "timestamp": r[3]}
        for r in reversed(rows)
    ]


def clear_history() -> None:
    conn = _conn()
    conn.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()
