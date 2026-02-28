"""
Debate persistence: SQLite storage and file export.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from autodebater.dialogue import DialogueHistory, DialogueMessage

_DEFAULT_DB = "debates.db"


class DebateStore:
    """SQLite-backed store for debates and their messages."""

    def __init__(self, db_path: str = _DEFAULT_DB):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS debates (
                    debate_id TEXT PRIMARY KEY,
                    motion TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debate_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    stance TEXT,
                    judgement REAL,
                    message TEXT NOT NULL
                )
                """
            )

    def save(self, history: DialogueHistory, motion: str):
        """Upsert the debate row and insert all messages."""
        if not history.messages:
            return
        debate_id = history.messages[0].debate_id
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO debates (debate_id, motion, created_at) VALUES (?, ?, ?)",
                (debate_id, motion, datetime.now().isoformat()),
            )
            conn.execute("DELETE FROM messages WHERE debate_id = ?", (debate_id,))
            for msg in history.messages:
                conn.execute(
                    "INSERT INTO messages (debate_id, timestamp, name, role, stance, judgement, message) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        msg.debate_id,
                        msg.timestamp.isoformat(),
                        msg.name,
                        msg.role,
                        msg.stance,
                        msg.judgement,
                        msg.message,
                    ),
                )

    def load(self, debate_id: str) -> list:
        """Load all messages for a debate."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT timestamp, name, role, stance, judgement, message, debate_id "
                "FROM messages WHERE debate_id = ? ORDER BY id",
                (debate_id,),
            ).fetchall()
        messages = []
        for row in rows:
            ts, name, role, stance, judgement, message, did = row
            msg = DialogueMessage(
                name=name,
                role=role,
                message=message,
                debate_id=did,
                stance=stance or "neutral",
                judgement=judgement,
                timestamp=datetime.fromisoformat(ts),
            )
            messages.append(msg)
        return messages

    def list_debates(self) -> list:
        """Return a summary list of all stored debates."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT debate_id, motion, created_at FROM debates ORDER BY created_at DESC"
            ).fetchall()
        return [{"debate_id": r[0], "motion": r[1], "created_at": r[2]} for r in rows]


class DebateExporter:
    """Static export helpers for debate histories."""

    @staticmethod
    def to_json(history: DialogueHistory) -> str:
        return json.dumps([m.to_dict() for m in history.messages], indent=2)

    @staticmethod
    def to_markdown(history: DialogueHistory) -> str:
        lines = ["# Debate Transcript\n"]
        for msg in history.messages:
            stance_tag = f" ({msg.stance})" if msg.stance and msg.stance != "neutral" else ""
            score_tag = f" [score: {msg.judgement}]" if msg.judgement is not None else ""
            lines.append(f"## {msg.name} — {msg.role}{stance_tag}{score_tag}\n")
            lines.append(f"{msg.message}\n")
        return "\n".join(lines)

    @staticmethod
    def export_file(history: DialogueHistory, path: str, fmt: str = "json"):
        content = (
            DebateExporter.to_markdown(history)
            if fmt == "md"
            else DebateExporter.to_json(history)
        )
        Path(path).write_text(content, encoding="utf-8")
