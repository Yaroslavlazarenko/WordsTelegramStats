"""Unit tests for SQLite database repository and message storage operations."""

import shutil
import tempfile
import unittest
from pathlib import Path

from src.data.db import (
    get_dataset_summary,
    get_last_msg_id,
    get_safe_filename,
    init_chat_db,
    save_messages_batch,
)


class TestDataRepository(unittest.TestCase):
    """Scenario: Verify SQLite database initialization, storage, and queries."""

    def setUp(self) -> None:
        """Create isolated temporary directory for test databases."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_should_generate_safe_filename_without_illegal_characters(self) -> None:
        """Test sanitization of chat titles into safe filenames."""
        filename_safe = get_safe_filename(12345, "My Chat / Special: *? Name")
        self.assertEqual(filename_safe, "12345_My_Chat__Special__Name.db")

    def test_should_initialize_database_and_return_zero_last_id_when_empty(self) -> None:
        """Test empty initialized database yields a last message ID of 0."""
        db_path = self.temp_dir / "chat_test.db"
        init_chat_db(db_path)
        self.assertTrue(db_path.exists())

        last_id = get_last_msg_id(db_path)
        self.assertEqual(last_id, 0)

    def test_should_save_batch_and_retrieve_max_msg_id(self) -> None:
        """Test batch insertion correctly stores records and updates max message ID."""
        db_path = self.temp_dir / "chat_test.db"
        init_chat_db(db_path)

        messages_batch = [
            ("msg_1", 1, 100, "Test Chat", "user", "2026-01-01T12:00:00", "Hello", 0, None, 5, 1),
            ("msg_2", 5, 100, "Test Chat", "user", "2026-01-01T12:05:00", "World", 0, None, 5, 1),
            ("msg_3", 12, 100, "Test Chat", "user", "2026-01-01T12:10:00", "Test message", 0, None, 12, 2),
        ]
        save_messages_batch(db_path, messages_batch)

        last_id = get_last_msg_id(db_path)
        self.assertEqual(last_id, 12)

    def test_should_compute_dataset_summary_across_multiple_databases(self) -> None:
        """Test summary aggregates total chats and total message count correctly."""
        db1_path = self.temp_dir / "chat1.db"
        db2_path = self.temp_dir / "chat2.db"
        init_chat_db(db1_path)
        init_chat_db(db2_path)

        batch_db1 = [
            ("msg_1", 1, 1, "Chat 1", "user", "2026-01-01T10:00:00", "A", 0, None, 1, 1),
            ("msg_2", 2, 1, "Chat 1", "user", "2026-01-02T10:00:00", "B", 0, None, 1, 1),
        ]
        batch_db2 = [
            ("msg_3", 3, 2, "Chat 2", "user", "2026-02-01T10:00:00", "C", 0, None, 1, 1),
        ]
        save_messages_batch(db1_path, batch_db1)
        save_messages_batch(db2_path, batch_db2)

        summary = get_dataset_summary(self.temp_dir)
        self.assertEqual(summary["total_chats"], 2)
        self.assertEqual(summary["total_messages"], 3)
        self.assertEqual(summary["min_date"], "2026-01-01T10:00:00")
        self.assertEqual(summary["max_date"], "2026-02-01T10:00:00")
