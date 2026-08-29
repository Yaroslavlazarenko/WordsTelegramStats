"""
Validation and quality audit of vocabulary.
Distinguishes genuine dictionary words from typos, chat laughter, and slang,
and computes hapax legomena distributions.
"""

from collections import Counter
from typing import Any

from src.nlp.detectors import categorize_vocab_word
from src.nlp.lemmatizer import tokenize


def validate_vocabulary(chats: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyzes vocabulary authenticity across all chats.
    Returns:
      {
        'total_types': int,
        'total_tokens': int,
        'by_cat_types': Counter,
        'by_cat_tokens': Counter,
        'hapax_by_cat': Counter,
        'categories_order': list
      }
    """
    counter = Counter()
    for ch in chats:
        for _, t in ch["messages"]:
            counter.update(tokenize(t))

    total_types = len(counter)
    total_tokens = sum(counter.values())

    by_cat_types = Counter()
    by_cat_tokens = Counter()
    hapax_by_cat = Counter()

    for w, c in counter.items():
        cat = categorize_vocab_word(w)
        by_cat_types[cat] += 1
        by_cat_tokens[cat] += c
        if c == 1:
            hapax_by_cat[cat] += 1

    categories_order = [
        "словникове (uk/ru)",
        "латиниця (англ/жаргон)",
        "сміх (хпхвх/хах)",
        "несловникове (одруківки/сленг/імена)",
    ]

    return {
        "total_types": total_types,
        "total_tokens": total_tokens,
        "by_cat_types": by_cat_types,
        "by_cat_tokens": by_cat_tokens,
        "hapax_by_cat": hapax_by_cat,
        "categories_order": categories_order,
    }
