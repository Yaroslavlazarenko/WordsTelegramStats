"""Database operations and repository for storing and querying Telegram messages.

Handles SQLite schema creation, message batch operations, and chat statistics.
"""

import re
import sqlite3
from pathlib import Path
from typing import Any

from src.core.config import settings


def get_safe_filename(chat_id: int, title: str) -> str:
    """Generate a filesystem-safe database filename for a Telegram chat.

    :param chat_id: Unique integer identifier of the chat.
    :param title: Display title of the chat.
    :return: Sanitized filename ending in .db.
    """
    title_clean = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁіІїЇєЄґҐ_\-]", "", title.replace(" ", "_"))
    title_truncated = title_clean[:30]
    return f"{chat_id}_{title_truncated}.db"


def init_chat_db(path_db: str | Path) -> None:
    """Initialize the messages table and performance indices in SQLite.

    :param path_db: Filepath to the SQLite database.
    """
    path_resolved = Path(path_db).resolve()
    path_resolved.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path_resolved) as connection:
        cursor = connection.cursor()
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
        connection.commit()


def get_last_msg_id(path_db: str | Path) -> int:
    """Return the highest message ID saved in the chat database.

    :param path_db: Filepath to the SQLite database.
    :return: Highest integer message ID, or 0 if database is empty or nonexistent.
    """
    path_resolved = Path(path_db)
    if not path_resolved.exists():
        return 0

    with sqlite3.connect(path_resolved) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT MAX(msg_id) FROM messages")
            row = cursor.fetchone()
            return row[0] if (row and row[0] is not None) else 0
        except sqlite3.OperationalError:
            return 0


def save_messages_batch(path_db: str | Path, messages_batch: list[tuple[Any, ...]]) -> None:
    """Save a batch of parsed message records into the database.

    :param path_db: Filepath to the SQLite database.
    :param messages_batch: List of message tuples matching table schema.
    """
    if not messages_batch:
        return

    path_resolved = Path(path_db)
    with sqlite3.connect(path_resolved) as connection:
        cursor = connection.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO messages (
                id, msg_id, chat_id, chat_title, chat_type, date, text,
                is_forwarded, reply_to_msg_id, char_count, word_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            messages_batch,
        )
        connection.commit()


def list_chat_db_files(directory_data: Path | None = None) -> list[Path]:
    """Return sorted list of all chat database files.

    :param directory_data: Directory containing chat database files (defaults to settings.dir_data).
    :return: List of sorted Path objects for .db files.
    """
    target_dir = directory_data or settings.dir_data
    if not target_dir.exists():
        return []
    return sorted(target_dir.glob("*.db"))


def get_dataset_summary(directory_data: Path | None = None) -> dict[str, Any]:
    """Calculate and return aggregate statistics across all chat databases.

    :param directory_data: Directory containing chat database files.
    :return: Dictionary containing total_chats, total_messages, min_date, max_date.
    """
    files_db = list_chat_db_files(directory_data)
    messages_total = 0
    date_min: str | None = None
    date_max: str | None = None

    for file_db in files_db:
        try:
            with sqlite3.connect(file_db) as connection:
                cursor = connection.cursor()
                result = cursor.execute(
                    "SELECT MIN(date), MAX(date), COUNT(*) FROM messages"
                ).fetchone()
                if result and result[0] and result[1]:
                    if date_min is None or result[0] < date_min:
                        date_min = result[0]
                    if date_max is None or result[1] > date_max:
                        date_max = result[1]
                    messages_total += result[2]
        except sqlite3.Error:
            continue

    return {
        "total_chats": len(files_db),
        "total_messages": messages_total,
        "min_date": date_min,
        "max_date": date_max,
    }
