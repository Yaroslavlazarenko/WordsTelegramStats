"""Unit tests for NLP tokenization and lemmatization module."""

import unittest

from src.nlp.lemmatizer import (
    detect_lang,
    is_stop_word,
    lemmatize_word,
    pos_of,
    raw_tokenize,
)


class TestNlpLemmatizer(unittest.TestCase):
    """Scenario: Verify morphological analysis and tokenization."""

    def test_should_tokenize_raw_text_into_lowercase_words(self) -> None:
        """Test raw tokenization strips punctuation and lowers case."""
        tokens = raw_tokenize("Привіт, Світ! Hello 2026.")
        self.assertIn("привіт", tokens)
        self.assertIn("світ", tokens)
        self.assertIn("hello", tokens)

    def test_should_lemmatize_inflected_words_to_normal_form(self) -> None:
        """Test lemmatization converts inflected forms to base dictionary lemma."""
        lemma_ru = lemmatize_word("делами")
        self.assertEqual(lemma_ru, "дело")

        lemma_uk = lemmatize_word("робимо")
        self.assertEqual(lemma_uk, "робити")

    def test_should_identify_stop_words_accurately(self) -> None:
        """Test functional and grammatical particles/prepositions are flagged as stop words."""
        self.assertTrue(is_stop_word("и"))
        self.assertTrue(is_stop_word("в"))
        self.assertTrue(is_stop_word("на"))
        self.assertTrue(is_stop_word("он"))
        self.assertTrue(is_stop_word("це"))
        self.assertFalse(is_stop_word("програмування"))

    def test_should_detect_languages_correctly(self) -> None:
        """Test language detection for English, Ukrainian, and Russian."""
        self.assertEqual(detect_lang("developer"), "en")
        self.assertEqual(detect_lang("їжак"), "uk")
        self.assertEqual(detect_lang("привет"), "ru")

    def test_should_return_pos_category_for_known_words(self) -> None:
        """Test part-of-speech generalization for dictionary words."""
        self.assertEqual(pos_of("бежать"), "глаголы")
        self.assertEqual(pos_of("книга"), "существительные")
        self.assertEqual(pos_of("красивый"), "прилагательные")
