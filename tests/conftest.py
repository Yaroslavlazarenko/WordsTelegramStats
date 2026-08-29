"""Shared test fixtures and environment configuration."""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.core.config import AppSettings


@pytest.fixture
def temp_workspace():
    """Create and tear down an isolated temporary workspace directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="tg_stats_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_settings(temp_workspace):
    """Provide an isolated AppSettings instance configured with temporary paths."""
    settings_test = AppSettings(
        dir_base=temp_workspace,
        dir_data=temp_workspace / "chats_data",
        dir_infographics=temp_workspace / "infographics",
        dir_words_lists=temp_workspace / "words_lists",
        dir_cache=temp_workspace / ".cache",
        dir_session=temp_workspace / "session",
        file_report=temp_workspace / "advanced_report.txt",
    )
    settings_test.ensure_directories()
    return settings_test
