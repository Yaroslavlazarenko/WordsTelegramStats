# -*- coding: utf-8 -*-
"""
FastAPI Web Application backend for WordsTelegramStats.
Provides dashboard metrics, live SSE logging, QR auth, and infographics gallery.
"""

import asyncio
import glob
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from telethon import errors

from src.core.config import (
    DATA_DIR,
    INFOGRAPHICS_DIR,
    WORDS_LISTS_DIR,
    REPORT_FILE,
)
from src.data.db import get_dataset_summary
from src.telegram.client import get_telegram_client, reset_telegram_client
from src.telegram.auth import get_auth_state, generate_qr_base64
from src.telegram.fetcher import fetch_messages_incremental
from src.pipeline.runner import run_full_pipeline

WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"

# Shared server state
state: Dict[str, Any] = {
    "auth_status": "unknown",
    "qr_img_base64": None,
    "user_info": None,
    "qr_login_obj": None,
    "task_running": False,
    "task_type": None,
    "task_progress": None,
    "logs": [],
}


def log_event(msg: str) -> None:
    """Appends an event to the circular in-memory log buffer."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    state["logs"].append(formatted)
    if len(state["logs"]) > 2500:
        state["logs"].pop(0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes Telegram client connection on server startup."""
    auth_data = await get_auth_state()
    state["auth_status"] = auth_data["status"]
    state["user_info"] = auth_data.get("user")
    yield


app = FastAPI(title="WordsTelegramStats UI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static mounts
app.mount("/static/infographics", StaticFiles(directory=str(INFOGRAPHICS_DIR)), name="infographics")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the main web dashboard."""
    index_path = STATIC_DIR / "index.html"
    return FileResponse(index_path)


@app.get("/api/status")
async def api_status():
    """Returns runtime application state, user auth, and DB summary."""
    client = get_telegram_client()
    is_auth = False
    if client.is_connected():
        try:
            is_auth = await client.is_user_authorized()
            if is_auth and not state["user_info"]:
                me = await client.get_me()
                state["user_info"] = {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone": me.phone,
                }
                state["auth_status"] = "authorized"
        except Exception:
            pass

    summary = get_dataset_summary()
    png_count = len(list(INFOGRAPHICS_DIR.glob("*.png")))

    return {
        "is_authorized": is_auth,
        "auth_status": state["auth_status"],
        "user_info": state["user_info"],
        "total_chats": summary["total_chats"],
        "total_messages": summary["total_messages"],
        "min_date": summary["min_date"],
        "max_date": summary["max_date"],
        "infographics_count": png_count,
        "task_running": state["task_running"],
        "task_type": state["task_type"],
        "progress": state["task_progress"],
    }


@app.post("/api/auth/start-qr")
async def start_qr():
    """Starts Telegram QR login flow and returns QR Base64 image."""
    client = get_telegram_client()
    if not client.is_connected():
        await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        state["auth_status"] = "authorized"
        state["user_info"] = {
            "id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "phone": me.phone,
        }
        return {"status": "already_authorized", "user": state["user_info"]}

    state["auth_status"] = "need_qr"
    state["qr_login_obj"] = await client.qr_login()
    state["qr_img_base64"] = generate_qr_base64(state["qr_login_obj"].url)

    async def wait_qr():
        try:
            await state["qr_login_obj"].wait(timeout=180)
            me = await client.get_me()
            state["auth_status"] = "authorized"
            state["user_info"] = {
                "id": me.id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "phone": me.phone,
            }
            state["qr_img_base64"] = None
            log_event("Успішна авторизація в Telegram за QR-кодом!")
        except errors.SessionPasswordNeededError:
            state["auth_status"] = "need_2fa"
            log_event("Потрібне введення 2FA-паролю.")
        except Exception as e:
            state["auth_status"] = "unauthorized"
            state["qr_img_base64"] = None
            log_event(f"Вичерпано час очікування або помилка QR: {e}")

    asyncio.create_task(wait_qr())

    return {
        "status": "need_qr",
        "qr_image": f"data:image/png;base64,{state['qr_img_base64']}",
        "url": state["qr_login_obj"].url,
    }


@app.post("/api/auth/2fa")
async def submit_2fa(request: Request):
    """Submits Telegram 2FA password."""
    data = await request.json()
    password = data.get("password")
    client = get_telegram_client()
    try:
        await client.sign_in(password=password)
        me = await client.get_me()
        state["auth_status"] = "authorized"
        state["user_info"] = {
            "id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "phone": me.phone,
        }
        state["qr_img_base64"] = None
        log_event("Успішний вхід із 2FA-паролем!")
        return {"status": "authorized", "user": state["user_info"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/auth/logout")
async def logout():
    """Logs out from Telegram, disconnects client and clears session file."""
    await reset_telegram_client()
    state["auth_status"] = "unauthorized"
    state["user_info"] = None
    state["qr_img_base64"] = None
    state["qr_login_obj"] = None
    log_event("Вихід з облікового запису Telegram успішно виконано.")
    return {"status": "unauthorized"}


@app.get("/api/infographics")
def list_infographics():
    """Returns available infographics grouped by analytical categories."""
    categories = {
        "dashboard": {
            "title": "Головне та базова інфографіка",
            "items": [
                {"file": "wordcloud.png", "title": "Хмара слів", "desc": "Візуалізація найчастіших змістовних слів за весь час"},
                {"file": "top_words.png", "title": "Топ-25 змістовних слів", "desc": "Рейтинг найбільш вживаних лексичних одиниць"},
                {"file": "years_volume.png", "title": "Обсяг за роками", "desc": "Динаміка кількості повідомлень та слів"},
                {"file": "ttr_evolution.png", "title": "Багатство мови (TTR)", "desc": "Словникове різноманіття та середня довжина реплік"},
                {"file": "zipf_distribution.png", "title": "Закон Ціпфа", "desc": "Рангочастотний розподіл слів vs ідеальний закон"},
                {"file": "word_length_distribution.png", "title": "Довжина слів", "desc": "Розподіл слів за кількістю літер"},
            ]
        },
        "time": {
            "title": "Часові патерни, ритм та режим сну",
            "items": [
                {"file": "timeline_monthly.png", "title": "Щомісячний таймлайн", "desc": "Обсяг повідомлень місяць за місяцем за всі роки"},
                {"file": "activity_by_hour.png", "title": "Активність за годинами", "desc": "Добовий розподіл відправки повідомлень"},
                {"file": "activity_by_weekday.png", "title": "Активність за днями тижня", "desc": "Порівняння робочих днів та вихідних"},
                {"file": "seasonality.png", "title": "Сезонність", "desc": "У які місяці року інтенсивність спілкування найвища"},
                {"file": "night_trend.png", "title": "Нічні повідомлення", "desc": "Частка повідомлень після півночі (00:00–06:00)"},
                {"file": "active_days.png", "title": "Активні дні та серії", "desc": "Кількість активних днів на рік та рекорди поспіль"},
                {"file": "sleep_evolution.png", "title": "Еволюція режиму сну", "desc": "Реконструкція часу засинання, пробудження та тривалості сну"},
                {"file": "message_rhythm.png", "title": "Ритм та паузи", "desc": "Розподіл пауз між репліками та частка повідомлень-черг"},
                {"file": "msg_length_dist.png", "title": "Розподіл довжини реплік", "desc": "Гістограма довжини повідомлень у словах"},
            ]
        },
        "style": {
            "title": "Стиль мовлення, словник та лінгвістика",
            "items": [
                {"file": "core_vocabulary.png", "title": "Кістяк мовлення", "desc": "Слова, що стабільно вживаються з року в рік (heatmap)"},
                {"file": "vocab_timeline.png", "title": "Чесний ріст словника", "desc": "Крива накопичення перевірених та словникових лем"},
                {"file": "vocab_growth.png", "title": "Закон Хіпса", "desc": "Зростання словникового запасу від обсягу тексту"},
                {"file": "vocab_validation.png", "title": "Склад словника", "desc": "Словникові слова vs латиниця vs сленг/одруківки"},
                {"file": "ngrams.png", "title": "Коронні фрази", "desc": "Топ стійких біграм та триграм"},
                {"file": "pos_evolution.png", "title": "Частини мови", "desc": "Співвідношення дієслів, іменників, прикметників"},
                {"file": "informality.png", "title": "Неформальність", "desc": "Частка несловникових слів та сленгу за роками"},
                {"file": "laughter_evolution.png", "title": "Еволюція сміху", "desc": "Динаміка написання сміху (ха-ха, хпхвх, хехе)"},
                {"file": "questions_exclamations.png", "title": "Питання та знаки оклику", "desc": "Емоційність та частка повідомлень із ? та !"},
                {"file": "profanity_trend.png", "title": "Частота мату", "desc": "Ненормативна лексика на 1000 слів за роками"},
                {"file": "language_mix.png", "title": "Мовний мікс", "desc": "Співвідношення мов (українська / російська / англійська)"},
            ]
        },
        "social": {
            "title": "Стосунки, чати та кластеризація",
            "items": [
                {"file": "top_chats.png", "title": "Топ діалогів", "desc": "Найбільш активні чати за кількістю повідомлень"},
                {"file": "streamgraph_chats.png", "title": "Потік спілкування (Streamgraph)", "desc": "Як з роками перерозподілялась увага між чатами"},
                {"file": "social_breadth.png", "title": "Широта спілкування", "desc": "Кількість співрозмовників на місяць та частка топ-3"},
                {"file": "relationships_timeline.png", "title": "Таймлайн життя чатів", "desc": "Коли починалось, спалахувало та згасало спілкування"},
                {"file": "chat_fingerprint.png", "title": "Лінгвістичні відбитки чатів", "desc": "Характерні слова для кожного контакту (TF-IDF)"},
                {"file": "ty_vy.png", "title": "Ти / Ви", "desc": "Рівень формальності та пропорція звертань"},
                {"file": "mat_per_chat.png", "title": "Мат за чатами", "desc": "Розподіл ненормативної лексики по конкретних діалогах"},
                {"file": "speech_clustering.png", "title": "Кластеризація мовлення", "desc": "Дендрограма схожості лексичного стилю з різними людьми"},
            ]
        },
    }

    # Filter out files that do not exist yet on disk
    for cat in categories.values():
        cat["items"] = [
            it for it in cat["items"]
            if (INFOGRAPHICS_DIR / it["file"]).exists()
        ]

    return categories


@app.get("/api/report")
def get_report():
    """Returns generated textual report content."""
    if REPORT_FILE.exists():
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            return {"exists": True, "content": f.read()}
    return {"exists": False, "content": None}


@app.get("/api/logs/stream")
async def logs_stream():
    """Streams live log messages via Server-Sent Events."""
    async def event_generator():
        last_idx = 0
        while True:
            if last_idx < len(state["logs"]):
                new_logs = state["logs"][last_idx:]
                last_idx = len(state["logs"])
                for l in new_logs:
                    yield f"data: {json.dumps({'log': l, 'running': state['task_running'], 'type': state['task_type']})}\n\n"
            else:
                yield f"data: {json.dumps({'ping': True, 'running': state['task_running'], 'type': state['task_type']})}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/actions/fetch")
async def action_fetch(background_tasks: BackgroundTasks, lang: str = "uk"):
    """Triggers Telegram message synchronization."""
    if state["task_running"]:
        err_msg = "Task is already in progress" if lang == "en" else "Завдання вже виконується"
        return JSONResponse({"status": "error", "message": err_msg}, status_code=400)

    state["task_running"] = True
    state["task_type"] = "fetch"
    state["task_progress"] = None
    start_msg = "=== Starting Telegram message synchronization ===" if lang == "en" else "=== Запуск синхронізації повідомлень із Telegram ==="
    log_event(start_msg)

    def update_progress(p_data: Dict[str, Any]):
        state["task_progress"] = p_data

    async def run_fetch():
        try:
            client = get_telegram_client()
            await fetch_messages_incremental(
                client,
                log_callback=log_event,
                progress_callback=update_progress,
                lang=lang
            )
        except Exception as e:
            err_msg = f"[❌] Synchronization error: {e}" if lang == "en" else f"[❌] Помилка під час синхронізації: {e}"
            log_event(err_msg)
        finally:
            state["task_running"] = False
            state["task_type"] = None
            state["task_progress"] = None
            end_msg = "=== Message synchronization completed ===" if lang == "en" else "=== Синхронізацію повідомлень завершено ==="
            log_event(end_msg)

    background_tasks.add_task(run_fetch)
    return {"status": "started"}


@app.post("/api/actions/analyze")
async def action_analyze(background_tasks: BackgroundTasks, lang: str = "uk"):
    """Triggers full analytics and visualization pipeline."""
    if state["task_running"]:
        err_msg = "Task is already in progress" if lang == "en" else "Завдання вже виконується"
        return JSONResponse({"status": "error", "message": err_msg}, status_code=400)

    state["task_running"] = True
    state["task_type"] = "analyze"
    start_msg = "=== Starting full analytics and infographics generation ===" if lang == "en" else "=== Запуск повного аналізу та генерації інфографіки ==="
    log_event(start_msg)

    def run_analyze_sync():
        try:
            run_full_pipeline(log_callback=log_event, lang=lang)
        except Exception as e:
            err_msg = f"[❌] Pipeline error: {e}" if lang == "en" else f"[❌] Помилка під час аналізу: {e}"
            log_event(err_msg)
        finally:
            state["task_running"] = False
            state["task_type"] = None
            end_msg = "=== Analysis and charts generation completed ===" if lang == "en" else "=== Аналіз та генерацію графіків завершено ==="
            log_event(end_msg)

    background_tasks.add_task(asyncio.to_thread, run_analyze_sync)
    return {"status": "started"}
