# -*- coding: utf-8 -*-
"""
Telegram client singleton manager.
"""

from typing import Optional
from pathlib import Path
from telethon import TelegramClient

from src.core.config import API_ID, API_HASH, SESSION_NAME

_client_instance: Optional[TelegramClient] = None


def get_telegram_client() -> TelegramClient:
    """Returns or creates the singleton TelegramClient instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = TelegramClient(
            SESSION_NAME,
            API_ID,
            API_HASH,
            device_model="Desktop UI",
            system_version="Linux",
            app_version="1.0.0",
        )
    return _client_instance


async def reset_telegram_client() -> None:
    """Logs out and resets the Telegram client instance, removing session files."""
    global _client_instance
    if _client_instance is not None:
        try:
            if _client_instance.is_connected():
                if await _client_instance.is_user_authorized():
                    await _client_instance.log_out()
                await _client_instance.disconnect()
        except Exception:
            pass
        _client_instance = None

    # Clean up session file on disk
    session_file = Path(SESSION_NAME + ".session")
    session_journal = Path(SESSION_NAME + ".session-journal")
    if session_file.exists():
        session_file.unlink(missing_ok=True)
    if session_journal.exists():
        session_journal.unlink(missing_ok=True)
