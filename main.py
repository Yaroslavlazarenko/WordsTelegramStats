#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordsTelegramStats — Universal CLI and Application Entry Point.

Usage:
  python main.py                  # Launch Web UI (default)
  python main.py web              # Launch Web UI
  python main.py fetch            # Download new Telegram messages
  python main.py analyze          # Run NLP text & frequency analysis
  python main.py infographics     # Generate all infographics and charts
  python main.py pipeline         # Run full end-to-end analytics pipeline
"""

import argparse
import asyncio
import sys
import uvicorn

from src.core.config import DATA_DIR, INFOGRAPHICS_DIR, REPORT_FILE
from src.data.loader import load_chats
from src.pipeline.runner import run_text_analysis, run_full_pipeline
from src.visualization.basic import generate_basic_charts
from src.visualization.behavioral import generate_behavioral_charts
from src.visualization.linguistic import generate_linguistic_charts
from src.visualization.social import generate_social_charts
from src.telegram.client import get_telegram_client
from src.telegram.fetcher import fetch_messages_incremental
from src.telegram.auth import get_auth_state


def cmd_web(args):
    """Launch FastAPI web dashboard."""
    print(f"🚀 Запуск WordsTelegramStats Web UI на http://{args.host}:{args.port}")
    uvicorn.run("src.web.app:app", host=args.host, port=args.port, reload=args.reload)


def cmd_fetch(args):
    """Fetch new messages from Telegram dialogs."""
    async def _fetch():
        client = get_telegram_client()
        await client.connect()
        auth = await get_auth_state(client)
        if not auth["is_authorized"]:
            print("[!] Клієнт не авторизований. Авторизуйтесь через QR-код у терміналі або відкрийте веб-інтерфейс.")
            qr = await client.qr_login()
            print(f"\nURL для входу: {qr.url}\n")
            try:
                await qr.wait(timeout=180)
                print("[✔] Вхід успішний!")
            except Exception as e:
                print(f"[❌] Помилка авторизації: {e}")
                return
        await fetch_messages_incremental(client)

    asyncio.run(_fetch())


def cmd_analyze(args):
    """Run textual and language frequency analysis."""
    run_text_analysis()


def cmd_infographics(args):
    """Generate all infographics charts."""
    print("Завантаження даних...")
    chats, _ = load_chats()
    if not chats:
        print("[❌] Даних не знайдено.")
        return

    generate_basic_charts(chats)
    generate_behavioral_charts(chats)
    generate_linguistic_charts(chats)
    generate_social_charts(chats)
    print(f"\n[✔] Усі графіки успішно згенеровано у: '{INFOGRAPHICS_DIR}/'")


def cmd_pipeline(args):
    """Execute complete analytics and infographics pipeline."""
    run_full_pipeline()


def main():
    parser = argparse.ArgumentParser(
        description="WordsTelegramStats — глибокий стилометричний аналіз та інфографіка листування в Telegram."
    )
    subparsers = parser.add_subparsers(dest="command", help="Команда для виконання")

    # Command: web
    p_web = subparsers.add_parser("web", help="Запустити інтерактивний веб-дашборд")
    p_web.add_argument("--host", default="0.0.0.0", help="Хост сервера (default: 0.0.0.0)")
    p_web.add_argument("--port", type=int, default=8000, help="Порт сервера (default: 8000)")
    p_web.add_argument("--reload", action="store_true", help="Автоперезавантаження коду")
    p_web.set_defaults(func=cmd_web)

    # Command: fetch
    p_fetch = subparsers.add_parser("fetch", help="Синхронізувати повідомлення з Telegram")
    p_fetch.set_defaults(func=cmd_fetch)

    # Command: analyze
    p_analyze = subparsers.add_parser("analyze", help="Виконати текстовий та частотний аналіз")
    p_analyze.set_defaults(func=cmd_analyze)

    # Command: infographics
    p_info = subparsers.add_parser("infographics", help="Згенерувати всі блоки інфографіки")
    p_info.set_defaults(func=cmd_infographics)

    # Command: pipeline / all
    p_pipe = subparsers.add_parser("pipeline", help="Запустити повний цикл (аналіз + інфографіка)")
    p_pipe.set_defaults(func=cmd_pipeline)

    p_all = subparsers.add_parser("all", help="Аліас для pipeline")
    p_all.set_defaults(func=cmd_pipeline)

    args = parser.parse_args()

    if not args.command:
        # Default behavior: run web dashboard
        args.host = "0.0.0.0"
        args.port = 8000
        args.reload = False
        cmd_web(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
