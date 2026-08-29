"""Morphological analysis and lemmatization module using pymorphy3.

Provides automated POS tagging, stop word detection, and dictionary validation
without requiring hardcoded word lists.
"""

import re
from functools import lru_cache

import pymorphy3

PATTERN_WORD = re.compile(r"[a-zA-Zа-яА-ЯёЁіїєґІЇЄҐ]+")
PATTERN_LATIN = re.compile(r"[a-z]")
PATTERN_UK_LETTERS = re.compile(r"[іїєґ]")

# Backward-compatible aliases
WORD_RE = PATTERN_WORD
LATIN_RE = PATTERN_LATIN
UK_LETTERS_RE = PATTERN_UK_LETTERS

_morph_analyzer_ru: pymorphy3.MorphAnalyzer | None = None
_morph_analyzer_uk: pymorphy3.MorphAnalyzer | bool | None = None


def get_morph_analyzer_ru() -> pymorphy3.MorphAnalyzer:
    """Return singleton MorphAnalyzer instance for Russian language."""
    global _morph_analyzer_ru
    if _morph_analyzer_ru is None:
        _morph_analyzer_ru = pymorphy3.MorphAnalyzer(lang="ru")
    return _morph_analyzer_ru


def get_morph_analyzer_uk() -> pymorphy3.MorphAnalyzer | None:
    """Return singleton MorphAnalyzer instance for Ukrainian language."""
    global _morph_analyzer_uk
    if _morph_analyzer_uk is None:
        try:
            _morph_analyzer_uk = pymorphy3.MorphAnalyzer(lang="uk")
        except Exception:
            _morph_analyzer_uk = False
    return _morph_analyzer_uk if isinstance(_morph_analyzer_uk, pymorphy3.MorphAnalyzer) else None


@lru_cache(maxsize=65536)
def lemmatize_word(word: str) -> str:
    """Normalize input word into standard dictionary lemma form.

    :param word: Single token string.
    :return: Normalized lemma or original string if unrecognized.
    """
    if PATTERN_LATIN.search(word):
        return word

    if PATTERN_UK_LETTERS.search(word):
        morph_uk = get_morph_analyzer_uk()
        if morph_uk and morph_uk.word_is_known(word):
            return morph_uk.parse(word)[0].normal_form

    morph_ru = get_morph_analyzer_ru()
    if morph_ru.word_is_known(word):
        return morph_ru.parse(word)[0].normal_form

    # Fallback to Ukrainian analyzer if unknown in Russian
    morph_uk = get_morph_analyzer_uk()
    if morph_uk and morph_uk.word_is_known(word):
        return morph_uk.parse(word)[0].normal_form

    return word


def tokenize(text: str) -> list[str]:
    """Convert raw text string into a list of normalized lemmas.

    :param text: Input text document.
    :return: List of lemmatized lowercase tokens.
    """
    return [lemmatize_word(token) for token in PATTERN_WORD.findall(text.lower())]


def raw_tokenize(text: str) -> list[str]:
    """Extract lowercase tokens from text without applying lemmatization.

    :param text: Input text document.
    :return: List of raw lowercase tokens.
    """
    return PATTERN_WORD.findall(text.lower())


@lru_cache(maxsize=65536)
def word_known(word: str) -> bool:
    """Check if word exists in morphological dictionaries (Russian/Ukrainian) or Latin.

    :param word: Single token string.
    :return: True if known, False otherwise.
    """
    if PATTERN_LATIN.search(word):
        return True

    if PATTERN_UK_LETTERS.search(word):
        morph_uk = get_morph_analyzer_uk()
        if morph_uk and morph_uk.word_is_known(word):
            return True

    return get_morph_analyzer_ru().word_is_known(word)


@lru_cache(maxsize=65536)
def is_stop_word(word: str) -> bool:
    """Identify functional and grammatical service words using POS tags.

    :param word: Single token string.
    :return: True if stop word, False otherwise.
    """
    if len(word) <= 1:
        return True
    if PATTERN_LATIN.search(word):
        return len(word) <= 2

    service_pos_tags = {"PREP", "CONJ", "PRCL", "NPRO"}

    morph_ru = get_morph_analyzer_ru()
    if morph_ru.word_is_known(word):
        parse_result = morph_ru.parse(word)[0]
        if parse_result.tag.POS in service_pos_tags or "Apro" in parse_result.tag.grammemes:
            return True

    morph_uk = get_morph_analyzer_uk()
    if morph_uk and morph_uk.word_is_known(word):
        parse_result = morph_uk.parse(word)[0]
        if parse_result.tag.POS in service_pos_tags or "Apro" in parse_result.tag.grammemes:
            return True

    return False


@lru_cache(maxsize=65536)
def detect_lang(word: str) -> str:
    """Detect language of a word using alphabet heuristics and dictionary lookup.

    :param word: Single token string.
    :return: ISO language code ('en', 'uk', 'ru').
    """
    if PATTERN_LATIN.search(word):
        return "en"
    if PATTERN_UK_LETTERS.search(word):
        return "uk"

    morph_uk = get_morph_analyzer_uk()
    if morph_uk and morph_uk.word_is_known(word) and not get_morph_analyzer_ru().word_is_known(word):
        return "uk"

    return "ru"


@lru_cache(maxsize=65536)
def pos_of(word: str) -> str | None:
    """Return generalized Russian part of speech classification for dictionary words.

    :param word: Single token string.
    :return: Friendly category name or None.
    """
    if PATTERN_LATIN.search(word) or not get_morph_analyzer_ru().word_is_known(word):
        return None

    tag_pos = get_morph_analyzer_ru().parse(word)[0].tag.POS
    if tag_pos in ("VERB", "INFN", "GRND", "PRTF", "PRTS"):
        return "глаголы"
    if tag_pos == "NOUN":
        return "существительные"
    if tag_pos in ("ADJF", "ADJS", "COMP"):
        return "прилагательные"
    if tag_pos == "ADVB":
        return "наречия"
    if tag_pos == "NPRO":
        return "местоимения"
    if tag_pos is None:
        return None
    return "служебные/прочие"
