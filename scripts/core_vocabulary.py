#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to compute core vocabulary across years and generate core_vocabulary.png.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.config import INFOGRAPHICS_DIR
from src.data.loader import load_chats
from src.visualization.linguistic import chart_core_vocabulary


def main():
    print("Завантаження даних...")
    chats, _ = load_chats()
    if not chats:
        print("[❌] Даних не знайдено.")
        return
    chart_core_vocabulary(chats)
    print(f"\n[✔] Графік збережено у: '{INFOGRAPHICS_DIR}/core_vocabulary.png'")


if __name__ == "__main__":
    main()
