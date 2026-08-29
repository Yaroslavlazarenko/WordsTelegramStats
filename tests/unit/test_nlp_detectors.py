from collections import Counter

from src.analytics.text_stats import compute_zipf_comparison
from src.nlp.detectors import (
    is_mat,
    is_ty,
    is_vy,
    laugh_family,
)


def test_is_mat_detects_profanities():
    profanities = [
        "хуй",
        "пиздец",
        "блядь",
        "наебать",
        "сука",
        "ебать",
        "охуеть",
        "долбоеб",
        "fuck",
        "fucking",
        "shit",
        "bitch",
    ]
    for word in profanities:
        assert is_mat(word) is True, f"Expected '{word}' to be identified as profanity"


def test_is_mat_ignores_clean_words():
    clean_words = [
        "привет",
        "дякую",
        "спасибо",
        "дом",
        "программа",
        "мир",
        "hello",
        "world",
        "телефон",
    ]
    for word in clean_words:
        assert is_mat(word) is False, f"Expected '{word}' not to be identified as profanity"


def test_pronouns_detection():
    assert is_ty("ты") is True
    assert is_ty("ти") is True
    assert is_ty("вы") is False

    assert is_vy("вы") is True
    assert is_vy("ви") is True
    assert is_vy("ты") is False


def test_laugh_family():
    assert laugh_family("хпхвх") == "клавіатурний (хпхвх/пхвх)"
    assert laugh_family("хехе") == "хехе / хіхі"
    assert laugh_family("хаха") == "класичний (ха-ха)"


def test_zipf_comparison_excludes_laugh_from_personal():
    counter = Counter({
        "хпхвх": 100,
        "хахвх": 80,
        "кста": 60,
        "нормас": 50,
        "привет": 100,
    })
    res = compute_zipf_comparison(counter, min_count=20)
    personal_words = [w for w, _, _, _ in res["personal"]]
    assert "хпхвх" not in personal_words
    assert "хахвх" not in personal_words
    assert "кста" in personal_words or "нормас" in personal_words

