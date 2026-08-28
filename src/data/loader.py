# -*- coding: utf-8 -*-
"""
Data loading and filtering pipeline for Telegram chat databases.
Filters out forwarded messages, copypastas, links, and noise.
"""

import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

from src.core.config import DATA_DIR, TZ_OFFSET_HOURS
from src.data.db import list_chat_db_files

LINK_RE = re.compile(r"https?://\S+|www\.\S+|tg://\S+")


def parse_local_dt(date_str: str, tz_offset: int = TZ_OFFSET_HOURS) -> Optional[datetime]:
    """
    Parses an ISO format date string and converts it to local timezone datetime.
    """
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt + timedelta(hours=tz_offset)


def is_noise(text: str, max_chars: int = 600, max_words: int = 100) -> bool:
    """
    Detects if a message is copypasta, a long quote, or contains links.
    Used to keep only the user's authentic speech.
    """
    if not text:
        return True
    if len(text) > max_chars:
        return True
    if len(text.split()) > max_words:
        return True
    if LINK_RE.search(text):
        return True
    return False


def load_chats(
    data_dir: str | Path = DATA_DIR,
    tz_offset: int = TZ_OFFSET_HOURS
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Loads all dialogs from SQLite database files.
    Returns:
      (chats, filter_stats)
      chats: list of dicts:
        {
          'title': str,
          'file': str,
          'messages': list of (date_str, text_str)
        }
      filter_stats: {
          'total': int,
          'forwarded': int,
          'noise': int,
          'clean': int
      }
    """
    data_path = Path(data_dir)
    if not data_path.is_dir():
        print(f"[❌] Directory '{data_path}' not found.")
        return [], {"total": 0, "forwarded": 0, "noise": 0, "clean": 0}

    chats = []
    filt = {"total": 0, "forwarded": 0, "noise": 0, "clean": 0}

    db_files = sorted(data_path.glob("*.db"))

    for db_file in db_files:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT chat_title, date, text, is_forwarded FROM messages"
            ).fetchall()
        except sqlite3.OperationalError:
            conn.close()
            continue
        conn.close()

        if not rows:
            continue

        chat_title = rows[0]["chat_title"] or db_file.stem
        clean_msgs = []

        for r in rows:
            filt["total"] += 1
            if r["is_forwarded"]:
                filt["forwarded"] += 1
                continue
            txt = r["text"] or ""
            if not txt.strip() or is_noise(txt):
                filt["noise"] += 1
                continue
            filt["clean"] += 1
            clean_msgs.append((r["date"], txt))

        if clean_msgs:
            chats.append({
                "title": chat_title,
                "file": db_file.name,
                "messages": clean_msgs
            })

    return chats, filt
