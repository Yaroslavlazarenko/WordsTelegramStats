# -*- coding: utf-8 -*-
"""
Telegram message fetcher.
Downloads user's sent messages from 1-on-1 dialogs incrementally and saves them into SQLite databases.
Provides real-time detailed progress logging, download speed calculation, and remaining ETA.
"""

import asyncio
import math
import os
import time
from typing import Callable, Optional, Dict, Any, List
from telethon import TelegramClient

from src.core.config import DATA_DIR
from src.data.db import get_safe_filename, init_chat_db, get_last_msg_id, save_messages_batch, get_dataset_summary


def format_eta(seconds: float) -> str:
    """Formats seconds into human-readable ETA string (UA)."""
    if seconds <= 0 or math.isnan(seconds) or math.isinf(seconds):
        return "розрахунок..."
    sec = int(seconds)
    if sec < 60:
        return f"{sec} с"
    minutes = sec // 60
    rem_sec = sec % 60
    if minutes < 60:
        return f"{minutes} хв {rem_sec:02d} с"
    hours = minutes // 60
    rem_min = minutes % 60
    return f"{hours} год {rem_min:02d} хв"


async def fetch_messages_incremental(
    client: TelegramClient,
    log_callback: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Incrementally fetches sent messages for all active 1-on-1 personal dialogs.
    Computes real-time download speed (msg/s), overall progress %, and ETA.
    """
    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    def report_progress(data: Dict[str, Any]) -> None:
        if progress_callback:
            progress_callback(data)

    if not client.is_connected():
        await client.connect()

    if not await client.is_user_authorized():
        log("[❌] Клієнт Telegram не авторизований.")
        return {"status": "unauthorized"}

    me = await client.get_me()
    log(f"Вхід виконано як: {me.first_name} {me.last_name or ''} (@{me.username or 'немає_юзернейму'})")
    log("Отримання списку діалогів...")

    dialogs = await client.get_dialogs()
    personal_dialogs = []

    for dialog in dialogs:
        is_bot = getattr(dialog.entity, "bot", False) if hasattr(dialog, "entity") else False
        is_self = getattr(dialog.entity, "is_self", False) if hasattr(dialog, "entity") else False
        if dialog.is_user and not is_bot and not is_self:
            personal_dialogs.append(dialog)

    total_dialogs = len(personal_dialogs)
    log(f"Знайдено {total_dialogs} особистих чатів із реальними користувачами.")
    log("Оцінка загального обсягу нових повідомлень по всіх діалогах...")

    # Fast pre-scan of total messages in batches of 15
    dialog_meta: Dict[int, Dict[str, Any]] = {}
    total_expected_all = 0

    async def pre_check_dialog(d):
        chat_id = d.id
        chat_title = d.title or "Unknown Title"
        db_filename = get_safe_filename(chat_id, chat_title)
        db_path = DATA_DIR / db_filename
        init_chat_db(db_path)
        last_id = get_last_msg_id(db_path)
        cnt = 0
        try:
            res = await client.get_messages(d, from_user="me", min_id=last_id, limit=0)
            if res is not None:
                cnt = res.total or 0
        except Exception:
            cnt = 0
        return chat_id, cnt, last_id, db_path

    chunk_size = 15
    for i in range(0, total_dialogs, chunk_size):
        chunk = personal_dialogs[i:i + chunk_size]
        results = await asyncio.gather(*[pre_check_dialog(d) for d in chunk])
        for chat_id, cnt, last_id, db_path in results:
            dialog_meta[chat_id] = {
                "expected": cnt,
                "last_id": last_id,
                "db_path": db_path
            }
            total_expected_all += cnt

    log(f"Загальний обсяг до синхронізації: ~{total_expected_all:,} повідомлень.")
    log("ℹ️ Збираються виключно ваші вихідні повідомлення (from_user='me'), без повідомлень співрозмовників — для точного персонального аналізу лише вашого мовлення.")
    log(f"Початок збору повідомлень у '{DATA_DIR}'...\n")

    total_new_saved = 0
    total_scanned_chats = 0
    sync_start_time = time.time()

    # Initial progress report
    report_progress({
        "current": 0,
        "total": total_expected_all,
        "pct": 0.0,
        "speed": 0.0,
        "eta": "розрахунок...",
        "current_chat": "Підготовка...",
        "chat_idx": 0,
        "total_chats": total_dialogs
    })

    for idx, dialog in enumerate(personal_dialogs, 1):
        chat_id = dialog.id
        chat_title = dialog.title or "Unknown Title"
        chat_type = "User"

        meta = dialog_meta.get(chat_id, {})
        expected_chat = meta.get("expected", 0)
        last_msg_id = meta.get("last_id", 0)
        db_path = meta.get("db_path", DATA_DIR / get_safe_filename(chat_id, chat_title))

        if expected_chat == 0:
            elapsed = time.time() - sync_start_time
            speed = total_new_saved / elapsed if elapsed > 0.5 else 0.0
            pct = (total_new_saved / total_expected_all * 100) if total_expected_all > 0 else (idx / total_dialogs * 100)
            remaining_msgs = max(0, total_expected_all - total_new_saved)
            eta_sec = remaining_msgs / speed if speed > 0 else 0
            eta_str = format_eta(eta_sec)

            log(f"[{idx:>3}/{total_dialogs}] [{pct:>5.1f}%] {chat_title[:22]:<22} | [✔] Актуально (нових немає)")
            total_scanned_chats += 1

            report_progress({
                "current": total_new_saved,
                "total": total_expected_all,
                "pct": round(pct, 1),
                "speed": round(speed, 1),
                "eta": eta_str,
                "current_chat": chat_title,
                "chat_idx": idx,
                "total_chats": total_dialogs
            })
            continue

        log(f"[{idx:>3}/{total_dialogs}] Чат «{chat_title}» (~{expected_chat:,} пов. до завантаження)...")

        chat_messages_batch: List[tuple] = []
        chat_count = 0

        try:
            async for msg in client.iter_messages(dialog, from_user="me", min_id=last_msg_id):
                text = msg.message or msg.text
                if not text:
                    continue

                is_forwarded = 1 if msg.fwd_from is not None else 0
                reply_to = msg.reply_to_msg_id if msg.reply_to else None

                char_count = len(text)
                word_count = len(text.split())

                db_id = f"{chat_id}_{msg.id}"
                msg_date = msg.date.isoformat() if msg.date else ""

                chat_messages_batch.append((
                    db_id,
                    msg.id,
                    chat_id,
                    chat_title,
                    chat_type,
                    msg_date,
                    text,
                    is_forwarded,
                    reply_to,
                    char_count,
                    word_count,
                ))

                chat_count += 1

                if len(chat_messages_batch) >= 100:
                    save_messages_batch(db_path, chat_messages_batch)
                    chat_messages_batch = []

                    # Calculate live speed & ETA
                    current_total = total_new_saved + chat_count
                    elapsed = time.time() - sync_start_time
                    speed = current_total / elapsed if elapsed > 0.5 else 0.0
                    pct = (current_total / total_expected_all * 100) if total_expected_all > 0 else (idx / total_dialogs * 100)
                    remaining_msgs = max(0, total_expected_all - current_total)
                    eta_sec = remaining_msgs / speed if speed > 0 else 0
                    eta_str = format_eta(eta_sec)

                    log(f"   ⏳ [{pct:>5.1f}%] {chat_title[:18]} ({chat_count}/{expected_chat}) | {speed:,.0f} пов/с | Залишилось: ~{eta_str}")

                    report_progress({
                        "current": current_total,
                        "total": total_expected_all,
                        "pct": round(pct, 1),
                        "speed": round(speed, 1),
                        "eta": eta_str,
                        "current_chat": chat_title,
                        "chat_idx": idx,
                        "total_chats": total_dialogs
                    })

            if chat_messages_batch:
                save_messages_batch(db_path, chat_messages_batch)

            total_new_saved += chat_count
            elapsed = time.time() - sync_start_time
            speed = total_new_saved / elapsed if elapsed > 0.5 else 0.0
            pct = (total_new_saved / total_expected_all * 100) if total_expected_all > 0 else (idx / total_dialogs * 100)
            remaining_msgs = max(0, total_expected_all - total_new_saved)
            eta_sec = remaining_msgs / speed if speed > 0 else 0
            eta_str = format_eta(eta_sec)

            if chat_count > 0:
                log(f"[{idx:>3}/{total_dialogs}] [{pct:>5.1f}%] {chat_title[:22]:<22} | [✔] +{chat_count} пов. (Всього: {total_new_saved:,} | ~{eta_str} зал.)\n")
            else:
                log(f"[{idx:>3}/{total_dialogs}] [{pct:>5.1f}%] {chat_title[:22]:<22} | [✔] Актуально\n")

            total_scanned_chats += 1

            report_progress({
                "current": total_new_saved,
                "total": total_expected_all,
                "pct": round(pct, 1),
                "speed": round(speed, 1),
                "eta": eta_str,
                "current_chat": chat_title,
                "chat_idx": idx,
                "total_chats": total_dialogs
            })

        except Exception as e:
            log(f"[{idx:>3}/{total_dialogs}] {chat_title[:22]:<22} | [❌] Помилка: {str(e)[:40]}\n")

    summary = get_dataset_summary()
    total_time = time.time() - sync_start_time
    avg_speed = total_new_saved / total_time if total_time > 0.5 else 0.0

    log("=" * 60)
    log(" ПІДСУМОК СИНХРОНІЗАЦІЇ")
    log("=" * 60)
    log(f"Перевірено чатів:        {total_scanned_chats}")
    log(f"Нових повідомлень додано:{total_new_saved:,}")
    log(f"Час синхронізації:       {total_time:.1f} сек")
    log(f"Середня швидкість:       {avg_speed:,.1f} повідомлень/сек")
    log(f"Всього повідомлень у БД: {summary['total_messages']:,}")
    log(f"Всього чатів у базі:     {summary['total_chats']}")
    log("=" * 60 + "\n")

    report_progress({
        "current": total_new_saved,
        "total": total_expected_all,
        "pct": 100.0,
        "speed": round(avg_speed, 1),
        "eta": "0 с",
        "current_chat": "Завершено",
        "chat_idx": total_dialogs,
        "total_chats": total_dialogs
    })

    return {
        "scanned_chats": total_scanned_chats,
        "new_saved": total_new_saved,
        "total_messages": summary["total_messages"],
        "total_chats": summary["total_chats"],
        "total_time_seconds": total_time,
        "average_speed": avg_speed,
    }
