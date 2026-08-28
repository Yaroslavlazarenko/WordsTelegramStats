# -*- coding: utf-8 -*-
"""
Builds and caches lemma-level frequency distribution from wordfreq.
Used to calculate Zipf deviations, distinctive words, and vocabulary gaps.
"""

import math
import pickle
from collections import defaultdict
from typing import Dict

from src.core.config import REF_RU_PATH, CACHE_DIR
from src.nlp.lemmatizer import lemmatize_word


def build_ru_lemma_reference(verbose: bool = True) -> Dict[str, float]:
    """
    Builds and caches lemma-level frequency distribution from wordfreq for Russian.
    Returns a dict {lemma: zipf_score}.
    """
    if REF_RU_PATH.exists():
        with open(REF_RU_PATH, "rb") as f:
            return pickle.load(f)

    from wordfreq import get_frequency_dict

    if verbose:
        print("  [i] Побудова еталона мови на рівні лем (один раз, ~45 c)...", flush=True)

    freq = get_frequency_dict("ru")
    agg = defaultdict(float)
    for w, f in freq.items():
        agg[lemmatize_word(w)] += f

    ref = {lemma: math.log10(s) + 9 for lemma, s in agg.items() if s > 0}

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(REF_RU_PATH, "wb") as f:
        pickle.dump(ref, f)

    return ref
