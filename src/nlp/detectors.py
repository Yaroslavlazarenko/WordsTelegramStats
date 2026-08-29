"""
Linguistic pattern detectors: profanity, laughter styles, address forms (ty/vy), and vocabulary categories.
"""

import json
import re
from pathlib import Path

from src.nlp.lemmatizer import LATIN_RE, word_known

# Load profanity dictionary sourced from Valve Steam Text Filter repository
_DATA_PATH = Path(__file__).resolve().parent / "data" / "steam_profanity.json"

_STEAM_WORDS: set[str] = set()
_STEAM_PATTERN: re.Pattern | None = None

if _DATA_PATH.exists():
    with open(_DATA_PATH, encoding="utf-8") as _f:
        _data = json.load(_f)
        _STEAM_WORDS = set(_data.get("words", []))
        _raw_patterns = _data.get("patterns", [])
        if _raw_patterns:
            _STEAM_PATTERN = re.compile(
                "|".join(f"(?:{p})" for p in _raw_patterns),
                re.IGNORECASE,
            )


def is_mat(word: str) -> bool:
    """Checks if a word matches known profanities from the Steam filter repository."""
    w = word.lower()
    if w in _STEAM_WORDS:
        return True
    if _STEAM_PATTERN and _STEAM_PATTERN.search(w):
        return True
    return False


# Regex for chat laughter variants (e.g., 'хаха', 'хпхвх', 'ахах', etc.)
LAUGH_RE = re.compile(r"^(?=.*х)[хпваеимдоьъ]{3,}$")


def laugh_family(w: str) -> str:
    """Classifies laughter token into stylistic families."""
    if "хп" in w or "пх" in w:
        return "клавіатурний (хпхвх/пхвх)"
    if "хе" in w or "хи" in w:
        return "хехе / хіхі"
    if "хм" in w:
        return "хмх"
    if "ха" in w or "ах" in w or set(w) <= {"х", "а"}:
        return "класичний (ха-ха)"
    return "інший"


# Informal (ty) vs formal/plural (vy) address pronouns
TY_PRONOUNS = {"ты", "ти", "твой", "твій", "тебе", "тебя", "тобі"}
VY_PRONOUNS = {"вы", "ви", "ваш", "вас", "вам", "вами"}


def is_ty(word: str) -> bool:
    """Checks if word is an informal 2nd person singular pronoun."""
    return word in TY_PRONOUNS


def is_vy(word: str) -> bool:
    """Checks if word is a formal/plural 2nd person pronoun."""
    return word in VY_PRONOUNS


def categorize_vocab_word(w: str) -> str:
    """
    Categorizes a word into:
      - 'сміх (хпхвх/хах)'
      - 'латиниця (англ/жаргон)'
      - 'словникове (uk/ru)'
      - 'несловникове (одруківки/сленг/імена)'
    """
    if LAUGH_RE.match(w):
        return "сміх (хпхвх/хах)"
    if LATIN_RE.search(w):
        return "латиниця (англ/жаргон)"
    if word_known(w):
        return "словникове (uk/ru)"
    return "несловникове (одруківки/сленг/імена)"
