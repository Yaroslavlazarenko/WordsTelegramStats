# -*- coding: utf-8 -*-
"""
Database operations for storing and reading Telegram messages.
Handles SQLite schema, message batch saving, and chat database metadata.
"""

import os
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.core.config import DATA_DIR


def get_safe_filename(chat_id: int, title: str) -> str:
    """Generates a filesystem-safe database filename for a chat."""
    clean_title = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁіІїЇєЄґҐ_\-]", "", title.replace(" ", "_"))
    clean_title = clean_title[:30]
    return f"{chat_id}_{clean_title}.db"


def init_chat_db(db_path: str | Path) -> None:
    """Initializes the messages table and indices in the chat SQLite DB."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            msg_id INTEGER,
            chat_id INTEGER,
            chat_title TEXT,
            chat_type TEXT,
            date TEXT,
            text TEXT,
            is_forwarded INTEGER,
            reply_to_msg_id INTEGER,
            char_count INTEGER,
            word_count INTEGER
        )
    """
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date)")
    conn.commit()
    conn.close()


def get_last_msg_id(db_path: str | Path) -> int:
    """Returns the highest message ID saved in the chat DB, or 0 if empty/nonexistent."""
    if not os.path.exists(db_path):
        return 0
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(msg_id) FROM messages")
        row = cursor.fetchone()
        last_id = row[0] if row and row[0] is not None else 0
    except sqlite3.OperationalError:
        last_id = 0
    conn.close()
    return last_id


def save_messages_batch(db_path: str | Path, batch: List[tuple]) -> None:
    """Saves a batch of messages to the chat database."""
    if not batch:
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO messages (
            id, msg_id, chat_id, chat_title, chat_type, date, text,
            is_forwarded, reply_to_msg_id, char_count, word_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        batch,
    )
    conn.commit()
    conn.close()


def list_chat_db_files() -> List[Path]:
    """Returns sorted list of all chat database paths in the data directory."""
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.glob("*.db"))


def get_dataset_summary() -> Dict[str, Any]:
    """Returns high-level statistics across all chat database files."""
    db_files = list_chat_db_files()
    total_messages = 0
    min_date = None
    max_date = None

    for f in db_files:
        try:
            conn = sqlite3.connect(f)
            r = conn.cursor().execute(
                "SELECT MIN(date), MAX(date), COUNT(*) FROM messages"
            ).fetchone()
            if r and r[0] and r[1]:
                if min_date is None or r[0] < min_date:
                    min_date = r[0]
                if max_date is None or r[1] > max_date:
                    max_date = r[1]
                total_messages += r[2]
            conn.close()
        except Exception:
            pass

    return {
        "total_chats": len(db_files),
        "total_messages": total_messages,
        "min_date": min_date,
        "max_date": max_date,
    }
