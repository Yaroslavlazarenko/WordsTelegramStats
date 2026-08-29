"""Telegram integration package."""

from .auth import generate_qr_base64, get_auth_state
from .client import get_telegram_client
from .fetcher import fetch_messages_incremental

__all__ = [
    "get_telegram_client",
    "fetch_messages_incremental",
    "get_auth_state",
    "generate_qr_base64",
]
