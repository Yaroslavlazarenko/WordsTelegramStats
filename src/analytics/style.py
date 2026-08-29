"""
Linguistic style analysis: n-grams (collocations), POS evolution, and messaging rhythm.
"""

from collections import Counter
from typing import Any

import numpy as np

from src.data.loader import parse_local_dt
from src.nlp.lemmatizer import pos_of, raw_tokenize, tokenize


def compute_ngrams(
    chats: list[dict[str, Any]],
    top_n: int = 18
) -> tuple[list[tuple[tuple[str, str], int]], list[tuple[tuple[str, str, str], int]]]:
    """
    Computes most frequent bigrams and trigrams from raw unlemmatized tokens.
    """
    bi, tri = Counter(), Counter()
    for ch in chats:
        for _, t in ch["messages"]:
            toks = raw_tokenize(t)
            for i in range(len(toks) - 1):
                bi[(toks[i], toks[i + 1])] += 1
            for i in range(len(toks) - 2):
                tri[(toks[i], toks[i + 1], toks[i + 2])] += 1
    return bi.most_common(top_n), tri.most_common(top_n)


def compute_pos_evolution(chats: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Tracks proportion of parts of speech (nouns, verbs, adjectives, etc.) across years.
    """
    cats = [
        "дієслова", "іменники", "прикметники", "прислівники",
        "займенники", "службові/інші"
    ]
    pos_map = {
        "глаголы": "дієслова",
        "существительные": "іменники",
        "прилагательные": "прикметники",
        "наречия": "прислівники",
        "местоимения": "займенники",
        "служебные/прочие": "службові/інші",
    }
    data = {c: Counter() for c in cats}
    tot = Counter()

    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            for w in tokenize(t):
                p = pos_of(w)
                if p:
                    uk_p = pos_map.get(p, p)
                    if uk_p in data:
                        data[uk_p][dt.year] += 1
                        tot[dt.year] += 1

    years = sorted(tot)
    stacks = [[data[c][y] / tot[y] * 100 if tot[y] > 0 else 0 for y in years] for c in cats]

    return {
        "years": years,
        "categories": cats,
        "stacks": stacks,
        "totals": dict(tot),
    }


def compute_message_rhythm(chats: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyzes inter-message burst intervals and burstiness index.
    """
    gaps_sec = []
    for ch in chats:
        dts = []
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                dts.append(dt)
        dts.sort()
        for a, b in zip(dts, dts[1:], strict=False):
            s = (b - a).total_seconds()
            if 0 < s <= 3600 * 24:
                gaps_sec.append(s)

    return {
        "gaps_sec": np.array(gaps_sec) if gaps_sec else np.empty(0),
    }
