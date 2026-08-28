#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate all infographics (Basic, Behavioral, Linguistic, and Social).
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.config import INFOGRAPHICS_DIR
from src.data.loader import load_chats
from src.visualization.basic import generate_basic_charts
from src.visualization.behavioral import generate_behavioral_charts
from src.visualization.linguistic import generate_linguistic_charts
from src.visualization.social import generate_social_charts


def main():
    print("Завантаження даних...")
    chats, _ = load_chats()
    if not chats:
        print("[❌] Даних не знайдено.")
        return

    generate_basic_charts(chats)
    generate_behavioral_charts(chats)
    generate_linguistic_charts(chats)
    generate_social_charts(chats)

    print(f"\n[✔] Усі графіки успішно збережено у: '{INFOGRAPHICS_DIR}/'")


if __name__ == "__main__":
    main()
