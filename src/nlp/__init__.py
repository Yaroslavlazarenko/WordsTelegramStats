# -*- coding: utf-8 -*-
"""Natural Language Processing and Linguistics package."""

from .lemmatizer import (
    lemmatize_word,
    tokenize,
    raw_tokenize,
    word_known,
    is_stop_word,
    detect_lang,
    pos_of,
    WORD_RE,
    LATIN_RE,
    UK_LETTERS_RE,
)
from .reference import build_ru_lemma_reference
from .detectors import (
    is_mat,
    MAT_ROOTS,
    LAUGH_RE,
    laugh_family,
    is_ty,
    is_vy,
    categorize_vocab_word,
)

__all__ = [
    "lemmatize_word",
    "tokenize",
    "raw_tokenize",
    "word_known",
    "is_stop_word",
    "detect_lang",
    "pos_of",
    "WORD_RE",
    "LATIN_RE",
    "UK_LETTERS_RE",
    "build_ru_lemma_reference",
    "is_mat",
    "MAT_ROOTS",
    "LAUGH_RE",
    "laugh_family",
    "is_ty",
    "is_vy",
    "categorize_vocab_word",
]
