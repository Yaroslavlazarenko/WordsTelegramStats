# -*- coding: utf-8 -*-
"""
Analysis of core vocabulary ("кістяк мовлення") — words consistently used across years.
"""

from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import numpy as np

from src.data.loader import parse_local_dt
from src.nlp.lemmatizer import tokenize, is_stop_word
from src.nlp.detectors import LAUGH_RE

MIN_YEAR_TOKENS = 20000
MIN_PER_YEAR = 5
DEFAULT_TOP = 30


def compute_core_vocabulary(
    chats: List[Dict[str, Any]],
    min_year_tokens: int = MIN_YEAR_TOKENS,
    min_per_year: int = MIN_PER_YEAR,
    top_n: int = DEFAULT_TOP
) -> Dict[str, Any]:
    """
    Computes the stable vocabulary backbone across years.
    Returns:
      {
        'reliable_years': [int],
        'dropped_years': [(int, token_count)],
        'core_words': [str],
        'relative_freqs': {word: [freq_per_1000_in_year_i]},
        'core_scores': {word: min_freq},
        'matrix': 2D np.array [word_idx, year_idx]
      }
    """
    total_by_year = Counter()
    cnt_by_year = defaultdict(Counter)

    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            for w in tokenize(t):
                total_by_year[dt.year] += 1
                if len(w) > 2 and not is_stop_word(w) and not LAUGH_RE.match(w):
                    cnt_by_year[dt.year][w] += 1

    reliable = sorted(y for y, n in total_by_year.items() if n >= min_year_tokens)
    dropped = sorted([(y, total_by_year[y]) for y, n in total_by_year.items() if n < min_year_tokens])

    if not reliable:
        return {
            "reliable_years": [],
            "dropped_years": dropped,
            "core_words": [],
            "relative_freqs": {},
            "core_scores": {},
            "matrix": np.empty((0, 0)),
        }

    candidates = set(cnt_by_year[reliable[0]])
    for y in reliable[1:]:
        candidates &= set(cnt_by_year[y])

    rel = {}
    core_score = {}
    for w in candidates:
        per_year = [cnt_by_year[y][w] / total_by_year[y] * 1000 for y in reliable]
        raw_min = min(cnt_by_year[y][w] for y in reliable)
        if raw_min < min_per_year:
            continue
        rel[w] = per_year
        core_score[w] = min(per_year)

    core = sorted(rel, key=lambda w: core_score[w], reverse=True)[:top_n]
    matrix = np.array([rel[w] for w in core]) if core else np.empty((0, len(reliable)))

    return {
        "reliable_years": reliable,
        "dropped_years": dropped,
        "core_words": core,
        "relative_freqs": rel,
        "core_scores": core_score,
        "matrix": matrix,
        "total_by_year": dict(total_by_year),
    }
