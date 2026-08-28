#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to validate vocabulary authenticity and generate vocab_validation.png.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.config import INFOGRAPHICS_DIR
from src.data.loader import load_chats
from src.analytics.vocab_validator import validate_vocabulary
from src.visualization.linguistic import chart_vocab_validation


def main():
    print("Завантаження даних...")
    chats, _ = load_chats()
    if not chats:
        print("[❌] Даних не знайдено.")
        return

    res = validate_vocabulary(chats)
    print("\n" + "=" * 78)
    print(" З ЧОГО СКЛАДАЄТЬСЯ «СЛОВНИКОВИЙ ЗАПАС»")
    print("=" * 78)
    print(f"Всього унікальних лем (типів): {res['total_types']:,}".replace(",", " "))
    print(f"Всього вживань (токенів):      {res['total_tokens']:,}".replace(",", " "))
    print(f"\n{'категорія':<38}{'унік.':>9}{'% унік.':>9}{'токенів':>11}{'% токенів':>11}")
    print("-" * 78)

    for cat in res["categories_order"]:
        t = res["by_cat_types"][cat]
        tok = res["by_cat_tokens"][cat]
        pct_t = t / res["total_types"] * 100 if res["total_types"] else 0
        pct_tok = tok / res["total_tokens"] * 100 if res["total_tokens"] else 0
        print(f"{cat:<38}{t:>9}{pct_t:>8.1f}%{tok:>11}{pct_tok:>10.1f}%")

    chart_vocab_validation(chats)
    print(f"\n[✔] Графік збережено у: '{INFOGRAPHICS_DIR}/vocab_validation.png'")


if __name__ == "__main__":
    main()
