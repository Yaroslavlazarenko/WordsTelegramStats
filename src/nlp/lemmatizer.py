# -*- coding: utf-8 -*-
"""
Morphological analysis and lemmatization module using pymorphy3.
Provides automated POS tagging, stop word detection, and dictionary validation
without requiring hardcoded word lists.
"""

import re
from functools import lru_cache
from typing import List, Optional

import pymorphy3

WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁіїєґІЇЄҐ]+")
LATIN_RE = re.compile(r"[a-z]")
UK_LETTERS_RE = re.compile(r"[іїєґ]")

_ru = None
_uk = None


def _ru_morph():
    global _ru
    if _ru is None:
        _ru = pymorphy3.MorphAnalyzer(lang="ru")
    return _ru


def _uk_morph():
    global _uk
    if _uk is None:
        try:
            _uk = pymorphy3.MorphAnalyzer(lang="uk")
        except Exception:
            _uk = False
    return _uk


@lru_cache(maxsize=None)
def lemmatize_word(word: str) -> str:
    """Returns normalized lemma; unrecognized words/slang are preserved as is."""
    if LATIN_RE.search(word):
        return word
    if UK_LETTERS_RE.search(word):
        uk = _uk_morph()
        if uk and uk.word_is_known(word):
            return uk.parse(word)[0].normal_form
    ru = _ru_morph()
    if ru.word_is_known(word):
        return ru.parse(word)[0].normal_form
    return word


def tokenize(text: str) -> List[str]:
    """Converts raw text into a list of normalized lemmas."""
    return [lemmatize_word(w) for w in WORD_RE.findall(text.lower())]


def raw_tokenize(text: str) -> List[str]:
    """Converts raw text into a list of lowercase tokens without lemmatization."""
    return WORD_RE.findall(text.lower())


@lru_cache(maxsize=None)
def word_known(word: str) -> bool:
    """Checks if a word exists in morphological dictionaries (ru/uk) or is latin."""
    if LATIN_RE.search(word):
        return True
    if UK_LETTERS_RE.search(word):
        uk = _uk_morph()
        if uk and uk.word_is_known(word):
            return True
    return _ru_morph().word_is_known(word)


@lru_cache(maxsize=None)
def is_stop_word(word: str) -> bool:
    """
    Dynamically identifies functional and grammatical service words (prepositions,
    conjunctions, pronouns, particles, pronominal adjectives) purely via morphological POS tags.
    """
    if len(word) <= 1:
        return True
    if LATIN_RE.search(word):
        return len(word) <= 2

    # Check grammatical POS tag & grammemes via pymorphy3
    SERVICE_POS = {"PREP", "CONJ", "PRCL", "NPRO"}
    ru = _ru_morph()
    if ru.word_is_known(word):
        p = ru.parse(word)[0]
        if p.tag.POS in SERVICE_POS or "Apro" in p.tag.grammemes:
            return True

    uk = _uk_morph()
    if uk and uk.word_is_known(word):
        p = uk.parse(word)[0]
        if p.tag.POS in SERVICE_POS or "Apro" in p.tag.grammemes:
            return True

    return False


@lru_cache(maxsize=None)
def detect_lang(word: str) -> str:
    """Detects word language dynamically using alphabet and dictionary lookup."""
    if LATIN_RE.search(word):
        return "en"
    if UK_LETTERS_RE.search(word):
        return "uk"
    uk = _uk_morph()
    if uk and uk.word_is_known(word) and not _ru_morph().word_is_known(word):
        return "uk"
    return "ru"


@lru_cache(maxsize=None)
def pos_of(word: str) -> Optional[str]:
    """Returns generalized part of speech for dictionary words."""
    if LATIN_RE.search(word) or not _ru_morph().word_is_known(word):
        return None
    tag = _ru_morph().parse(word)[0].tag.POS
    if tag in ("VERB", "INFN", "GRND", "PRTF", "PRTS"):
        return "глаголы"
    if tag == "NOUN":
        return "существительные"
    if tag in ("ADJF", "ADJS", "COMP"):
        return "прилагательные"
    if tag == "ADVB":
        return "наречия"
    if tag == "NPRO":
        return "местоимения"
    if tag is None:
        return None
    return "служебные/прочие"
