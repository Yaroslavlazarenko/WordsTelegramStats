# -*- coding: utf-8 -*-
"""Telegram integration package."""

from .client import get_telegram_client
from .fetcher import fetch_messages_incremental
from .auth import get_auth_state, generate_qr_base64

__all__ = [
    "get_telegram_client",
    "fetch_messages_incremental",
    "get_auth_state",
    "generate_qr_base64",
]
