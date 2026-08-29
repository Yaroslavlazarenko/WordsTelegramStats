"""
Telegram QR login and 2FA authentication handlers.
"""

import base64
import io
from typing import Any

import qrcode
from telethon import TelegramClient

from src.telegram.client import get_telegram_client


async def get_auth_state(client: TelegramClient | None = None) -> dict[str, Any]:
    """Checks current authorization state and user info."""
    c = client or get_telegram_client()
    if not c.is_connected():
        try:
            await c.connect()
        except Exception as e:
            return {"is_authorized": False, "status": "error", "error": str(e), "user": None}

    try:
        is_auth = await c.is_user_authorized()
        if is_auth:
            me = await c.get_me()
            return {
                "is_authorized": True,
                "status": "authorized",
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone": me.phone,
                },
            }
        return {"is_authorized": False, "status": "unauthorized", "user": None}
    except Exception as e:
        return {"is_authorized": False, "status": "error", "error": str(e), "user": None}


def generate_qr_base64(url: str) -> str:
    """Generates PNG Base64 data URL for a Telegram login URL."""
    qr = qrcode.QRCode(border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
