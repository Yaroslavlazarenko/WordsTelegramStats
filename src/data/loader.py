"""Data loading and filtering pipeline for Telegram chat databases.

Filters out forwarded messages, copypastas, links, and noise to isolate authentic user speech.
"""

import re
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from src.core.config import settings
from src.data.db import list_chat_db_files

PATTERN_LINK = re.compile(r"https?://\S+|www\.\S+|tg://\S+")


def parse_local_datetime(
    date_str: str | None,
    tz_offset_hours: int = settings.tz_offset_hours,
) -> datetime | None:
    """Parse an ISO format date string and convert to local timezone datetime.

    :param date_str: ISO formatted timestamp string.
    :param tz_offset_hours: Timezone offset in hours from UTC.
    :return: Offset datetime object or None if parsing fails.
    """
    if not date_str:
        return None
    try:
        dt_parsed = datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None

    if dt_parsed.tzinfo:
        dt_parsed = dt_parsed.astimezone(UTC).replace(tzinfo=None)
    return dt_parsed + timedelta(hours=tz_offset_hours)


# Backward-compatible alias
parse_local_dt = parse_local_datetime


def is_noise(text: str | None, max_chars: int = 600, max_words: int = 100) -> bool:
    """Detect if a message is noise, copypasta, link, or forwarded quote.

    :param text: Raw message content.
    :param max_chars: Maximum acceptable character length.
    :param max_words: Maximum acceptable word count.
    :return: True if message should be filtered out, False otherwise.
    """
    if not text:
        return True
    text_stripped = text.strip()
    if not text_stripped:
        return True
    if len(text_stripped) > max_chars:
        return True
    if len(text_stripped.split()) > max_words:
        return True
    if PATTERN_LINK.search(text_stripped):
        return True
    return False


def load_chats(
    directory_data: Path | str | None = None,
    tz_offset_hours: int = settings.tz_offset_hours,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Load all dialogs from SQLite database files and apply authenticity filters.

    :param directory_data: Directory containing chat database files.
    :param tz_offset_hours: Timezone offset in hours.
    :return: Tuple of (chats_loaded, stats_filter).
    """
    path_data = Path(directory_data) if directory_data else settings.dir_data
    if not path_data.is_dir():
        return [], {"total": 0, "forwarded": 0, "noise": 0, "clean": 0}

    stats_filter = {"total": 0, "forwarded": 0, "noise": 0, "clean": 0}
    chats_loaded: list[dict[str, Any]] = []
    files_db = list_chat_db_files(path_data)

    for file_db in files_db:
        try:
            with sqlite3.connect(file_db) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                rows = cursor.execute(
                    "SELECT chat_title, date, text, is_forwarded FROM messages"
                ).fetchall()
        except sqlite3.OperationalError:
            continue

        if not rows:
            continue

        title_chat = rows[0]["chat_title"] or file_db.stem
        messages_clean: list[tuple[str, str]] = []

        for row in rows:
            stats_filter["total"] += 1
            if row["is_forwarded"]:
                stats_filter["forwarded"] += 1
                continue

            text_raw = row["text"] or ""
            if is_noise(text_raw):
                stats_filter["noise"] += 1
                continue

            stats_filter["clean"] += 1
            messages_clean.append((row["date"], text_raw))

        if messages_clean:
            chats_loaded.append({
                "title": title_chat,
                "file": file_db.name,
                "messages": messages_clean,
            })

    return chats_loaded, stats_filter
