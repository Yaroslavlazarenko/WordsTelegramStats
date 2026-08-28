# -*- coding: utf-8 -*-
"""
Telegram message fetcher.
Downloads user's sent messages from 1-on-1 dialogs incrementally and saves them into SQLite databases.
"""

import os
from typing import Callable, Optional, Dict, Any, List
from telethon import TelegramClient

from src.core.config import DATA_DIR
from src.data.db import get_safe_filename, init_chat_db, get_last_msg_id, save_messages_batch, get_dataset_summary


async def fetch_messages_incremental(
    client: TelegramClient,
    log_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """
    Incrementally fetches sent messages for all active 1-on-1 personal dialogs.
    """
    def log(msg: str) -> None:
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

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

    log(f"Знайдено {len(personal_dialogs)} особистих чатів із реальними користувачами.")
    log(f"Початок збору ваших надісланих повідомлень у '{DATA_DIR}'...")

    total_new_saved = 0
    total_scanned_chats = 0

    for idx, dialog in enumerate(personal_dialogs, 1):
        chat_id = dialog.id
        chat_title = dialog.title or "Unknown Title"
        chat_type = "User"

        db_filename = get_safe_filename(chat_id, chat_title)
        db_path = DATA_DIR / db_filename

        init_chat_db(db_path)
        last_msg_id = get_last_msg_id(db_path)

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

            if chat_messages_batch:
                save_messages_batch(db_path, chat_messages_batch)

            if chat_count > 0:
                log(f"  [{idx}/{len(personal_dialogs)}] {chat_title[:22]:<22} | [✔] +{chat_count} нових повідомлень")
                total_new_saved += chat_count
            else:
                log(f"  [{idx}/{len(personal_dialogs)}] {chat_title[:22]:<22} | [✔] Актуально (нових немає)")

            total_scanned_chats += 1

        except Exception as e:
            log(f"  [{idx}/{len(personal_dialogs)}] {chat_title[:22]:<22} | [❌] Помилка: {str(e)[:40]}")

    summary = get_dataset_summary()
    log("\n" + "=" * 60)
    log(" ПІДСУМОК СИНХРОНІЗАЦІЇ")
    log("=" * 60)
    log(f"Перевірено чатів:        {total_scanned_chats}")
    log(f"Нових повідомлень додано:{total_new_saved}")
    log(f"Всього повідомлень у БД: {summary['total_messages']}")
    log(f"Всього чатів у базі:     {summary['total_chats']}")
    log("=" * 60 + "\n")

    return {
        "scanned_chats": total_scanned_chats,
        "new_saved": total_new_saved,
        "total_messages": summary["total_messages"],
        "total_chats": summary["total_chats"],
    }
