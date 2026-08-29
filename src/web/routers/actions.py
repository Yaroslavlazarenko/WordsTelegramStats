"""Asynchronous task triggering endpoints for message synchronization and analysis."""

import asyncio
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.pipeline.runner import run_full_pipeline
from src.telegram.client import get_telegram_client
from src.telegram.fetcher import fetch_messages_incremental
from src.web.state import state_manager

router_actions = APIRouter(prefix="/api/actions", tags=["actions"])


@router_actions.post("/fetch")
async def action_fetch(background_tasks: BackgroundTasks, lang: str = "uk") -> dict[str, Any]:
    """Trigger background Telegram message synchronization."""
    if state_manager.task_running:
        message_error = (
            "Task is already in progress"
            if lang == "en"
            else "Завдання вже виконується"
        )
        raise HTTPException(status_code=400, detail=message_error)

    state_manager.set_task_started("fetch")
    message_start = (
        "=== Starting Telegram message synchronization ==="
        if lang == "en"
        else "=== Запуск синхронізації повідомлень із Telegram ==="
    )
    state_manager.log_event(message_start)

    def callback_progress(progress_data: dict[str, Any]) -> None:
        state_manager.task_progress = progress_data

    async def execute_fetch() -> None:
        try:
            client_tg = get_telegram_client()
            await fetch_messages_incremental(
                client_tg,
                log_callback=state_manager.log_event,
                progress_callback=callback_progress,
                lang=lang,
            )
        except Exception as error:
            message_failure = (
                f"[❌] Synchronization error: {error}"
                if lang == "en"
                else f"[❌] Помилка під час синхронізації: {error}"
            )
            state_manager.log_event(message_failure)
        finally:
            state_manager.set_task_finished()
            message_end = (
                "=== Message synchronization completed ==="
                if lang == "en"
                else "=== Синхронізацію повідомлень завершено ==="
            )
            state_manager.log_event(message_end)

    background_tasks.add_task(execute_fetch)
    return {"status": "started"}


@router_actions.post("/analyze")
async def action_analyze(background_tasks: BackgroundTasks, lang: str = "uk") -> dict[str, Any]:
    """Trigger full linguistic analytics and visualization pipeline."""
    if state_manager.task_running:
        message_error = (
            "Task is already in progress"
            if lang == "en"
            else "Завдання вже виконується"
        )
        raise HTTPException(status_code=400, detail=message_error)

    state_manager.set_task_started("analyze")
    message_start = (
        "=== Starting full analytics and infographics generation ==="
        if lang == "en"
        else "=== Запуск повного аналізу та генерації інфографіки ==="
    )
    state_manager.log_event(message_start)

    def execute_analyze_sync() -> None:
        try:
            run_full_pipeline(log_callback=state_manager.log_event, lang=lang)
        except Exception as error:
            message_failure = (
                f"[❌] Pipeline error: {error}"
                if lang == "en"
                else f"[❌] Помилка під час аналізу: {error}"
            )
            state_manager.log_event(message_failure)
        finally:
            state_manager.set_task_finished()
            message_end = (
                "=== Analysis and charts generation completed ==="
                if lang == "en"
                else "=== Аналіз та генерацію графіків завершено ==="
            )
            state_manager.log_event(message_end)

    background_tasks.add_task(asyncio.to_thread, execute_analyze_sync)
    return {"status": "started"}
