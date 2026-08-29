"""Unit tests for noise filtering and datetime parsing logic."""

import unittest

from src.data.loader import is_noise, parse_local_datetime


class TestNoiseFilter(unittest.TestCase):
    """Scenario: Verify text noise classification and date parsing."""

    def test_should_filter_out_empty_or_whitespace_strings(self) -> None:
        """Test empty string and whitespace are classified as noise."""
        self.assertTrue(is_noise(""))
        self.assertTrue(is_noise("   "))
        self.assertTrue(is_noise(None))

    def test_should_filter_out_links(self) -> None:
        """Test messages containing URLs are classified as noise."""
        self.assertTrue(is_noise("Check this out https://example.com/item"))
        self.assertTrue(is_noise("visit http://google.com for info"))
        self.assertTrue(is_noise("join tg://resolve?domain=test"))

    def test_should_filter_out_excessively_long_messages(self) -> None:
        """Test long quotes and copypastas exceeding character limit are filtered."""
        long_message = "слово " * 120
        self.assertTrue(is_noise(long_message, max_words=100))

    def test_should_accept_normal_conversational_messages(self) -> None:
        """Test typical human conversational speech passes the noise filter."""
        self.assertFalse(is_noise("Привіт! Як твої справи?"))
        self.assertFalse(is_noise("Давай зустрінемось завтра о 15:00"))
        self.assertFalse(is_noise("Дякую за допомогу, все чудово працює."))

    def test_should_parse_iso_datetime_with_timezone_offset(self) -> None:
        """Test parsing ISO string and applying UTC offset."""
        parsed_dt = parse_local_datetime("2026-05-10T12:00:00", tz_offset_hours=3)
        self.assertIsNotNone(parsed_dt)
        self.assertEqual(parsed_dt.year, 2026)
        self.assertEqual(parsed_dt.month, 5)
        self.assertEqual(parsed_dt.day, 10)
        self.assertEqual(parsed_dt.hour, 15)

    def test_should_return_none_on_invalid_datetime_string(self) -> None:
        """Test invalid date format returns None gracefully."""
        self.assertIsNone(parse_local_datetime("invalid-date-string"))
        self.assertIsNone(parse_local_datetime(None))
