#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to download Telegram message history from 1-on-1 personal dialogs.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from src.telegram.client import get_telegram_client
from src.telegram.fetcher import fetch_messages_incremental
from src.telegram.auth import get_auth_state


async def main():
    client = get_telegram_client()
    await client.connect()

    auth = await get_auth_state(client)
    if not auth["is_authorized"]:
        print("[!] Клієнт не авторизований. Авторизуйтесь через QR-код у терміналі або відкрийте веб-інтерфейс.")
        qr_login = await client.qr_login()
        print(f"\nURL для входу: {qr_login.url}\n")
        try:
            await qr_login.wait(timeout=180)
            print("[✔] Вхід успішний!")
        except Exception as e:
            print(f"[❌] Помилка авторизації: {e}")
            return

    await fetch_messages_incremental(client)


if __name__ == "__main__":
    asyncio.run(main())
