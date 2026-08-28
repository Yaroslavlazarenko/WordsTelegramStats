# -*- coding: utf-8 -*-
"""
Telegram client singleton manager.
"""

from typing import Optional
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
