# -*- coding: utf-8 -*-
"""
Telegram message fetcher.
Downloads user's sent messages from 1-on-1 dialogs incrementally and saves them into SQLite databases.
Provides real-time detailed progress logging, download speed calculation, and remaining ETA in multiple languages.
"""

import asyncio
import math
import os
import time
from typing import Callable, Optional, Dict, Any, List
from telethon import TelegramClient

from src.core.config import DATA_DIR
from src.data.db import get_safe_filename, init_chat_db, get_last_msg_id, save_messages_batch, get_dataset_summary


def format_eta(seconds: float, lang: str = "uk") -> str:
    """Formats seconds into human-readable ETA string."""
    is_en = lang == "en"
    if seconds <= 0 or math.isnan(seconds) or math.isinf(seconds):
        return "calculating..." if is_en else "розрахунок..."
    sec = int(seconds)
    if sec < 60:
        return f"{sec}s" if is_en else f"{sec} с"
    minutes = sec // 60
    rem_sec = sec % 60
    if minutes < 60:
        return f"{minutes}m {rem_sec:02d}s" if is_en else f"{minutes} хв {rem_sec:02d} с"
    hours = minutes // 60
    rem_min = minutes % 60
    return f"{hours}h {rem_min:02d}m" if is_en else f"{hours} год {rem_min:02d} хв"


async def fetch_messages_incremental(
    client: TelegramClient,
    log_callback: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    lang: str = "uk"
) -> Dict[str, Any]:
    """
    Incrementally fetches sent messages for all active 1-on-1 personal dialogs.
    Computes real-time download speed (msg/s), overall progress %, and ETA.
    """
    is_en = lang == "en"

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
        log("[❌] Telegram client is not authorized." if is_en else "[❌] Клієнт Telegram не авторизований.")
        return {"status": "unauthorized"}

    me = await client.get_me()
    no_user = "no_username" if is_en else "немає_юзернейму"
    logged_in_text = f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or no_user})" if is_en else f"Вхід виконано як: {me.first_name} {me.last_name or ''} (@{me.username or no_user})"
    log(logged_in_text)
    log("Fetching dialogs list..." if is_en else "Отримання списку діалогів...")

    dialogs = await client.get_dialogs()
    personal_dialogs = []

    for dialog in dialogs:
        is_bot = getattr(dialog.entity, "bot", False) if hasattr(dialog, "entity") else False
        is_self = getattr(dialog.entity, "is_self", False) if hasattr(dialog, "entity") else False
        if dialog.is_user and not is_bot and not is_self:
            personal_dialogs.append(dialog)

    total_dialogs = len(personal_dialogs)
    log(f"Found {total_dialogs} private chats with real users." if is_en else f"Знайдено {total_dialogs} особистих чатів із реальними користувачами.")
    log("Estimating total new messages volume across all chats..." if is_en else "Оцінка загального обсягу нових повідомлень по всіх діалогах...")

    # Fast pre-scan of total messages in batches of 10 with live feedback
    dialog_meta: Dict[int, Dict[str, Any]] = {}
    total_expected_all = 0

    async def pre_check_dialog(d):
        chat_id = d.id
        chat_title = d.title or ("Unknown Title" if is_en else "Без назви")
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
        return chat_id, cnt, last_id, db_path, chat_title

    chunk_size = 10
    processed_prep = 0
    for i in range(0, total_dialogs, chunk_size):
        chunk = personal_dialogs[i:i + chunk_size]
        results = await asyncio.gather(*[pre_check_dialog(d) for d in chunk])
        for chat_id, cnt, last_id, db_path, title in results:
            dialog_meta[chat_id] = {
                "expected": cnt,
                "last_id": last_id,
                "db_path": db_path
            }
            total_expected_all += cnt

        processed_prep = min(i + chunk_size, total_dialogs)
        pct_prep = round((processed_prep / total_dialogs) * 100, 1)
        last_title = results[-1][4] if results else ("Chat" if is_en else "Чат")

        prep_word = "Preparing" if is_en else "Підготовка"
        checked_word = "checked" if is_en else "перевірено"
        found_word = "found" if is_en else "знайдено"
        msgs_word = "msgs" if is_en else "пов."
        log(f"  🔍 {prep_word} [{processed_prep:>3}/{total_dialogs}] ({pct_prep:>5.1f}%): {checked_word} «{last_title[:20]}» | {found_word}: ~{total_expected_all:,} {msgs_word}")

        report_progress({
            "phase": "precheck",
            "current": total_expected_all,
            "total": None,
            "pct": pct_prep,
            "speed": 0.0,
            "eta": "queue estimation" if is_en else "оцінка черги...",
            "current_chat": last_title[:18],
            "chat_idx": processed_prep,
            "total_chats": total_dialogs
        })

    total_vol_msg = f"\nTotal volume to synchronize: ~{total_expected_all:,} messages." if is_en else f"\nЗагальний обсяг до синхронізації: ~{total_expected_all:,} повідомлень."
    disclaimer_msg = (
        "ℹ️ Exclusively your outgoing messages (from_user='me') are collected, without interlocutor messages — for accurate personal speech stylometry."
        if is_en else
        "ℹ️ Збираються виключно ваші вихідні повідомлення (from_user='me'), без повідомлень співрозмовників — для точного персонального аналізу лише вашого мовлення."
    )
    start_collect_msg = f"Starting message collection into '{DATA_DIR}'...\n" if is_en else f"Початок збору повідомлень у '{DATA_DIR}'...\n"

    log(total_vol_msg)
    log(disclaimer_msg)
    log(start_collect_msg)

    total_new_saved = 0
    total_scanned_chats = 0
    sync_start_time = time.time()

    # Initial progress report
    report_progress({
        "current": 0,
        "total": total_expected_all,
        "pct": 0.0,
        "speed": 0.0,
        "eta": "calculating..." if is_en else "розрахунок...",
        "current_chat": "",
        "chat_idx": 0,
        "total_chats": total_dialogs
    })

    for idx, dialog in enumerate(personal_dialogs, 1):
        chat_id = dialog.id
        chat_title = dialog.title or ("Unknown Title" if is_en else "Без назви")
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
            eta_str = format_eta(eta_sec, lang=lang)

            up_to_date_str = "[✔] Up to date (no new messages)" if is_en else "[✔] Актуально (нових немає)"
            log(f"[{idx:>3}/{total_dialogs}] [{pct:>5.1f}%] {chat_title[:22]:<22} | {up_to_date_str}")
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

        chat_label = f"Chat \"{chat_title}\" (~{expected_chat:,} msgs to fetch)..." if is_en else f"Чат «{chat_title}» (~{expected_chat:,} пов. до завантаження)..."
        log(f"[{idx:>3}/{total_dialogs}] {chat_label}")

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
                    eta_str = format_eta(eta_sec, lang=lang)

                    speed_unit = "msg/s" if is_en else "пов/с"
                    rem_label = "Remaining" if is_en else "Залишилось"
                    log(f"   ⏳ [{pct:>5.1f}%] {chat_title[:18]} ({chat_count}/{expected_chat}) | {speed:,.0f} {speed_unit} | {rem_label}: ~{eta_str}")

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
            eta_str = format_eta(eta_sec, lang=lang)

            if chat_count > 0:
                tot_lbl = "Total" if is_en else "Всього"
                rem_lbl = "rem." if is_en else "зал."
                msgs_lbl = "msgs" if is_en else "пов."
                log(f"[{idx:>3}/{total_dialogs}] [{pct:>5.1f}%] {chat_title[:22]:<22} | [✔] +{chat_count} {msgs_lbl} ({tot_lbl}: {total_new_saved:,} | ~{eta_str} {rem_lbl})\n")
            else:
                up_to_date_str = "[✔] Up to date" if is_en else "[✔] Актуально"
                log(f"[{idx:>3}/{total_dialogs}] [{pct:>5.1f}%] {chat_title[:22]:<22} | {up_to_date_str}\n")

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
            err_lbl = "Error" if is_en else "Помилка"
            log(f"[{idx:>3}/{total_dialogs}] {chat_title[:22]:<22} | [❌] {err_lbl}: {str(e)[:40]}\n")

    summary = get_dataset_summary()
    total_time = time.time() - sync_start_time
    avg_speed = total_new_saved / total_time if total_time > 0.5 else 0.0

    header_summary = "SYNCHRONIZATION SUMMARY" if is_en else "ПІДСУМОК СИНХРОНІЗАЦІЇ"
    log("=" * 60)
    log(f" {header_summary}")
    log("=" * 60)
    if is_en:
        log(f"Chats inspected:         {total_scanned_chats}")
        log(f"New messages added:      {total_new_saved:,}")
        log(f"Sync time:               {total_time:.1f} sec")
        log(f"Average speed:           {avg_speed:,.1f} messages/sec")
        log(f"Total messages in DB:    {summary['total_messages']:,}")
        log(f"Total chats in database: {summary['total_chats']}")
    else:
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
        "eta": "0s" if is_en else "0 с",
        "current_chat": "Completed" if is_en else "Завершено",
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
