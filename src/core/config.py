"""Central configuration for WordsTelegramStats.

Manages application paths, Telegram API credentials, NLP caching,
timezones, and visual themes using Pydantic Settings.
"""

import shutil
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application configuration and runtime environment settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Base filesystem paths
    dir_base: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    dir_data: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "chats_data")
    dir_infographics: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "infographics")
    dir_words_lists: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "words_lists")
    dir_cache: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / ".cache")
    dir_session: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "session")
    file_report: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "advanced_report.txt")

    # Telegram API credentials
    tg_api_id: int = Field(default=2040, alias="TG_API_ID")
    tg_api_hash: str = Field(default="b18441a1ff607e10a989891a5462e627", alias="TG_API_HASH")

    # Timezone settings (default to UTC+3 Kyiv/EET with DST)
    tz_offset_hours: int = Field(default=3, alias="TZ_OFFSET_HOURS")

    # Visual theme settings for Matplotlib and WordCloud
    color_bg: str = "#0f1117"
    color_fg: str = "#e6e6e6"
    color_accent: str = "#4cc9f0"
    color_accent2: str = "#f72585"
    color_accent3: str = "#80ed99"
    color_grid: str = "#2a2d36"

    palette: list[str] = [
        "#4cc9f0", "#f72585", "#80ed99", "#ffd166", "#b794f6",
        "#ff8fab", "#06d6a0", "#ef476f", "#118ab2", "#fb8500",
    ]

    months_uk: list[str] = [
        "", "Січ", "Лют", "Бер", "Кві", "Тра", "Чер",
        "Лип", "Сер", "Вер", "Жов", "Лис", "Гру",
    ]

    days_uk: list[str] = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

    def ensure_directories(self) -> None:
        """Create necessary runtime directories if they do not exist."""
        for directory in [
            self.dir_data,
            self.dir_infographics,
            self.dir_words_lists,
            self.dir_cache,
            self.dir_session,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Migrate legacy session file if present in root
        session_legacy = self.dir_base / "telegram_words_stats.session"
        session_current = self.dir_session / "telegram_words_stats.session"
        if session_legacy.is_file() and not session_current.exists():
            try:
                shutil.copy2(session_legacy, session_current)
            except OSError:
                pass


# Global settings singleton
settings = AppSettings()
settings.ensure_directories()

# Backward-compatible aliases
BASE_DIR = settings.dir_base
DATA_DIR = settings.dir_data
INFOGRAPHICS_DIR = settings.dir_infographics
WORDS_LISTS_DIR = settings.dir_words_lists
CACHE_DIR = settings.dir_cache
SESSION_DIR = settings.dir_session
REPORT_FILE = settings.file_report

API_ID = settings.tg_api_id
API_HASH = settings.tg_api_hash
SESSION_NAME = str(settings.dir_session / "telegram_words_stats")
TZ_OFFSET_HOURS = settings.tz_offset_hours

REF_RU_PATH = settings.dir_cache / "lemma_ref_ru.pkl"

BG_COLOR = settings.color_bg
FG_COLOR = settings.color_fg
ACCENT_COLOR = settings.color_accent
ACCENT2_COLOR = settings.color_accent2
ACCENT3_COLOR = settings.color_accent3
GRID_COLOR = settings.color_grid
PALETTE = settings.palette
MONTHS_UK = settings.months_uk
DAYS_UK = settings.days_uk
