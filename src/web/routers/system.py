"""System status and log streaming endpoints."""

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.core.config import settings
from src.data.db import get_dataset_summary
from src.telegram.client import get_telegram_client
from src.web.state import state_manager

router_system = APIRouter(prefix="/api", tags=["system"])


@router_system.get("/status")
async def api_status() -> dict[str, Any]:
    """Return runtime application state, user auth, and DB summary."""
    client_tg = get_telegram_client()
    user_authorized = False

    if not client_tg.is_connected():
        try:
            await client_tg.connect()
        except Exception:
            pass

    if client_tg.is_connected():
        try:
            user_authorized = await client_tg.is_user_authorized()
            if user_authorized and (state_manager.user_info is None):
                user_entity = await client_tg.get_me()
                state_manager.user_info = {
                    "id": user_entity.id,
                    "first_name": user_entity.first_name,
                    "last_name": user_entity.last_name,
                    "username": user_entity.username,
                    "phone": user_entity.phone,
                }
                state_manager.auth_status = "authorized"
        except Exception:
            pass

    summary_data = get_dataset_summary()
    count_infographics = len(list(settings.dir_infographics.glob("*.png")))

    return {
        "is_authorized": user_authorized,
        "auth_status": state_manager.auth_status,
        "user_info": state_manager.user_info,
        "total_chats": summary_data["total_chats"],
        "total_messages": summary_data["total_messages"],
        "min_date": summary_data["min_date"],
        "max_date": summary_data["max_date"],
        "infographics_count": count_infographics,
        "task_running": state_manager.task_running,
        "task_type": state_manager.task_type,
        "progress": state_manager.task_progress,
    }


@router_system.get("/logs/stream")
async def logs_stream() -> StreamingResponse:
    """Stream live log events and heartbeats via Server-Sent Events (SSE)."""
    async def generate_events() -> AsyncGenerator[str, None]:
        queue_subscriber = state_manager.subscribe_logs()
        # Yield initial batch of recent logs
        for log_line in state_manager.get_recent_logs():
            payload = {
                "log": log_line,
                "running": state_manager.task_running,
                "type": state_manager.task_type,
            }
            yield f"data: {json.dumps(payload)}\n\n"

        try:
            while True:
                try:
                    log_item = await asyncio.wait_for(queue_subscriber.get(), timeout=1.0)
                    payload = {
                        "log": log_item,
                        "running": state_manager.task_running,
                        "type": state_manager.task_type,
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                except TimeoutError:
                    # Heartbeat ping
                    payload = {
                        "ping": True,
                        "running": state_manager.task_running,
                        "type": state_manager.task_type,
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
        finally:
            state_manager.unsubscribe_logs(queue_subscriber)

    return StreamingResponse(generate_events(), media_type="text/event-stream")
