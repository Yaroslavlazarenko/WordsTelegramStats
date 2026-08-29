"""Authentication endpoints for Telegram QR code and 2FA login."""

import asyncio
from typing import Any

from fastapi import APIRouter, Request
from telethon import errors

from src.telegram.auth import generate_qr_base64
from src.telegram.client import get_telegram_client, reset_telegram_client
from src.web.state import state_manager

router_auth = APIRouter(prefix="/api/auth", tags=["auth"])


@router_auth.post("/start-qr")
async def start_qr() -> dict[str, Any]:
    """Start Telegram QR login flow and return base64 encoded QR image."""
    client_tg = get_telegram_client()
    if not client_tg.is_connected():
        await client_tg.connect()

    if await client_tg.is_user_authorized():
        user_entity = await client_tg.get_me()
        state_manager.auth_status = "authorized"
        state_manager.user_info = {
            "id": user_entity.id,
            "first_name": user_entity.first_name,
            "last_name": user_entity.last_name,
            "username": user_entity.username,
            "phone": user_entity.phone,
        }
        return {"status": "already_authorized", "user": state_manager.user_info}

    state_manager.auth_status = "need_qr"
    state_manager.qr_login_obj = await client_tg.qr_login()
    state_manager.qr_img_base64 = generate_qr_base64(state_manager.qr_login_obj.url)

    async def wait_qr_completion() -> None:
        try:
            await state_manager.qr_login_obj.wait(timeout=180)
            user_entity = await client_tg.get_me()
            state_manager.auth_status = "authorized"
            state_manager.user_info = {
                "id": user_entity.id,
                "first_name": user_entity.first_name,
                "last_name": user_entity.last_name,
                "username": user_entity.username,
                "phone": user_entity.phone,
            }
            state_manager.qr_img_base64 = None
            state_manager.log_event("Успішна авторизація в Telegram за QR-кодом!")
        except errors.SessionPasswordNeededError:
            state_manager.auth_status = "need_2fa"
            state_manager.log_event("Потрібне введення 2FA-паролю.")
        except Exception as error:
            state_manager.auth_status = "unauthorized"
            state_manager.qr_img_base64 = None
            state_manager.log_event(f"Вичерпано час очікування або помилка QR: {error}")

    asyncio.create_task(wait_qr_completion())

    return {
        "status": "need_qr",
        "qr_image": f"data:image/png;base64,{state_manager.qr_img_base64}",
        "url": state_manager.qr_login_obj.url,
    }


@router_auth.post("/2fa")
async def submit_2fa(request: Request) -> dict[str, Any]:
    """Submit 2FA password to complete Telegram authentication."""
    body = await request.json()
    password_input = body.get("password")
    client_tg = get_telegram_client()

    try:
        await client_tg.sign_in(password=password_input)
        user_entity = await client_tg.get_me()
        state_manager.auth_status = "authorized"
        state_manager.user_info = {
            "id": user_entity.id,
            "first_name": user_entity.first_name,
            "last_name": user_entity.last_name,
            "username": user_entity.username,
            "phone": user_entity.phone,
        }
        state_manager.qr_img_base64 = None
        state_manager.log_event("Успішний вхід із 2FA-паролем!")
        return {"status": "authorized", "user": state_manager.user_info}
    except Exception as error:
        return {"status": "error", "message": str(error)}


@router_auth.post("/logout")
async def logout() -> dict[str, str]:
    """Log out from Telegram session and clear local credentials."""
    await reset_telegram_client()
    state_manager.reset_auth()
    state_manager.log_event("Вихід з облікового запису Telegram успішно виконано.")
    return {"status": "unauthorized"}
