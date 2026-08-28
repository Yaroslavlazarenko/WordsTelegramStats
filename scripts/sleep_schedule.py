#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to reconstruct sleep schedule evolution and generate sleep_evolution.png.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.config import INFOGRAPHICS_DIR
from src.data.loader import load_chats
from src.visualization.behavioral import chart_sleep_evolution


def main():
    print("Завантаження даних...")
    chats, _ = load_chats()
    if not chats:
        print("[❌] Даних не знайдено.")
        return
    chart_sleep_evolution(chats)
    print(f"\n[✔] Графік збережено у: '{INFOGRAPHICS_DIR}/sleep_evolution.png'")


if __name__ == "__main__":
    main()
