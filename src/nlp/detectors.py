"""
Linguistic pattern detectors: profanity, laughter styles, address forms (ty/vy), and vocabulary categories.
"""

import re

from src.nlp.lemmatizer import LATIN_RE, word_known

# Profanity roots (Russian / Ukrainian)
MAT_ROOTS = (
    "хуй", "хуё", "хуе", "хуя", "хуи", "хую", "хует",
    "пизд", "еба", "ебал", "ебан", "ебл", "ебу", "ёба", "ёбн", "єба", "єбл", "єбу",
    "наеб", "уеб", "выеб", "въеб", "заеб", "доеб", "подъеб", "отъеб", "съеб", "проеб",
    "наєб", "заєб", "доєб", "підєб", "відєб", "проєб",
    "бля", "блят", "блядь", "сука", "суки", "сукин", "суча",
    "ахуе", "ахуи", "охуе", "охуи", "нахуй", "похуй", "нихуя", "дохуя", "ахуё", "охуё",
    "ахує", "охує", "ніхуя",
    "мудак", "мудил", "мудоз", "говн", "гавн", "долбоеб", "долбоёб", "довбойоб",
    "залуп", "пидор", "пидар", "гондон", "гандон", "пизж", "спизд", "распизд",
)


def is_mat(word: str) -> bool:
    """Checks if a word starts with any known profanity root."""
    return any(word.startswith(r) for r in MAT_ROOTS)


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
