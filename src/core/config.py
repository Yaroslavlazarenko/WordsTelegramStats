# -*- coding: utf-8 -*-
"""
Central configuration for WordsTelegramStats.
Manages paths, Telegram API credentials, NLP caching, timezones, and visual themes.
"""

import os
import shutil
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "chats_data"
INFOGRAPHICS_DIR = BASE_DIR / "infographics"
WORDS_LISTS_DIR = BASE_DIR / "words_lists"
CACHE_DIR = BASE_DIR / ".cache"
SESSION_DIR = BASE_DIR / "session"
REPORT_FILE = BASE_DIR / "advanced_report.txt"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
INFOGRAPHICS_DIR.mkdir(parents=True, exist_ok=True)
WORDS_LISTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Backward compatibility: migrate old root session file to session directory if exists
old_session = BASE_DIR / "telegram_words_stats.session"
new_session = SESSION_DIR / "telegram_words_stats.session"
if old_session.is_file() and not new_session.exists():
    try:
        shutil.copy2(old_session, new_session)
    except Exception:
        pass

# Telegram API credentials (default official App ID or overridden by env)
API_ID = int(os.getenv("TG_API_ID", "2040"))
API_HASH = os.getenv("TG_API_HASH", "b18441a1ff607e10a989891a5462e627")
SESSION_NAME = str(SESSION_DIR / "telegram_words_stats")

# Timezone settings (default to UTC+3 Kyiv/EET with DST)
TZ_OFFSET_HOURS = int(os.getenv("TZ_OFFSET_HOURS", "3"))

# Cache files
REF_RU_PATH = CACHE_DIR / "lemma_ref_ru.pkl"

# Visual theme settings for Matplotlib and WordCloud
BG_COLOR = "#0f1117"
FG_COLOR = "#e6e6e6"
ACCENT_COLOR = "#4cc9f0"
ACCENT2_COLOR = "#f72585"
ACCENT3_COLOR = "#80ed99"
GRID_COLOR = "#2a2d36"

PALETTE = [
    "#4cc9f0", "#f72585", "#80ed99", "#ffd166", "#b794f6",
    "#ff8fab", "#06d6a0", "#ef476f", "#118ab2", "#fb8500"
]

MONTHS_UK = [
    "", "Січ", "Лют", "Бер", "Кві", "Тра", "Чер",
    "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"
]

DAYS_UK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
