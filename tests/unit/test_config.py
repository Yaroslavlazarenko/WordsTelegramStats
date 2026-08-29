"""Unit tests for configuration and environment settings."""

import unittest
from pathlib import Path

from src.core.config import AppSettings


class TestAppSettings(unittest.TestCase):
    """Scenario: Verify application configuration behaves correctly."""

    def test_should_initialize_default_paths_correctly(self) -> None:
        """Test default filesystem paths are resolved to absolute directories."""
        settings = AppSettings()
        self.assertTrue(settings.dir_base.is_absolute())
        self.assertEqual(settings.dir_data.name, "chats_data")
        self.assertEqual(settings.dir_infographics.name, "infographics")
        self.assertEqual(settings.tz_offset_hours, 3)

    def test_should_create_directories_when_ensure_called(self) -> None:
        """Test ensure_directories successfully creates all missing target folders."""
        import shutil
        import tempfile

        temp_root = Path(tempfile.mkdtemp())
        try:
            settings_custom = AppSettings(
                dir_base=temp_root,
                dir_data=temp_root / "data_test",
                dir_infographics=temp_root / "infographics_test",
                dir_words_lists=temp_root / "words_test",
                dir_cache=temp_root / "cache_test",
                dir_session=temp_root / "session_test",
                file_report=temp_root / "report.txt",
            )
            settings_custom.ensure_directories()

            self.assertTrue(settings_custom.dir_data.is_dir())
            self.assertTrue(settings_custom.dir_infographics.is_dir())
            self.assertTrue(settings_custom.dir_words_lists.is_dir())
            self.assertTrue(settings_custom.dir_cache.is_dir())
            self.assertTrue(settings_custom.dir_session.is_dir())
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)
