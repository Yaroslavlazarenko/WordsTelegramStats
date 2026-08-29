"""
Core text statistics engine.
Computes token frequencies, TTR (type-token ratio), chat rankings, yearly trends,
Zipf distribution slopes, and language reference comparisons.
"""

import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from wordfreq import zipf_frequency

from src.nlp.detectors import LAUGH_RE
from src.nlp.lemmatizer import WORD_RE, detect_lang, is_stop_word, tokenize
from src.nlp.reference import build_ru_lemma_reference


def compute_message_stats(messages: list[tuple[str, str]]) -> dict[str, Any]:
    """
    Computes linguistic metrics for a list of (date_str, text_str) tuples.
    """
    total_words = 0
    total_chars = 0
    counter = Counter()

    for _, text in messages:
        words = tokenize(text)
        total_words += len(words)
        total_chars += len(text)
        counter.update(words)

    n_msg = len(messages)
    unique = len(counter)
    ttr = (unique / total_words) if total_words > 0 else 0.0
    avg_words = (total_words / n_msg) if n_msg > 0 else 0.0
    avg_chars = (total_chars / n_msg) if n_msg > 0 else 0.0

    return {
        "n_msg": n_msg,
        "total_words": total_words,
        "total_chars": total_chars,
        "unique": unique,
        "ttr": ttr,
        "avg_words": avg_words,
        "avg_chars": avg_chars,
        "counter": counter,
    }


def top_meaningful(counter: Counter, n: int = 15) -> list[tuple[str, int]]:
    """Returns top N meaningful words (excluding stop words and short particles)."""
    return [
        (w, c)
        for w, c in counter.most_common()
        if not is_stop_word(w) and len(w) > 2
    ][:n]


def safe_filename(name: str) -> str:
    """Sanitizes chat title for text file outputs."""
    s = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁіІїЇєЄґҐ_\-]", "", name.replace(" ", "_"))
    return s[:40] or "unknown"


def write_frequency_file(file_path: str | Path, title: str, counter: Counter) -> None:
    """Exports raw word frequencies into a readable text format."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# ПОВНИЙ ЧАСТОТНИЙ СЛОВНИК: {title}\n")
        f.write(f"# Унікальних слів: {len(counter)} | Всього слів: {sum(counter.values())}\n")
        f.write("# Формат:  слово : кількість разів\n")
        f.write("-" * 50 + "\n")
        for w, c in counter.most_common():
            f.write(f"{w} : {c}\n")


def analyze_vocabulary_shifts(
    year_stats: dict[str, dict[str, Any]],
    years: list[str]
) -> tuple[list[tuple[str, float, float, float]], list[tuple[str, float, float, float]]]:
    """
    Identifies words rising in popularity and fading out between earliest and latest years.
    Returns: (rose, fell) where each item is (word, freq_first_ppm, freq_last_ppm, delta_ppm)
    """
    if len(years) < 2:
        return [], []

    first, last = years[0], years[-1]
    c1, c2 = year_stats[first]["counter"], year_stats[last]["counter"]
    t1, t2 = year_stats[first]["total_words"], year_stats[last]["total_words"]
    if not t1 or not t2:
        return [], []

    candidates = {w for w, c in c2.items() if c >= 15} | {w for w, c in c1.items() if c >= 15}
    rose, fell = [], []

    for w in candidates:
        if is_stop_word(w) or len(w) <= 2:
            continue
        f1 = c1.get(w, 0) / t1 * 1e6
        f2 = c2.get(w, 0) / t2 * 1e6
        delta = f2 - f1
        if c2.get(w, 0) >= 15 and delta > 0:
            rose.append((w, f1, f2, delta))
        elif c1.get(w, 0) >= 15 and delta < 0:
            fell.append((w, f1, f2, delta))

    rose.sort(key=lambda r: r[3], reverse=True)
    fell.sort(key=lambda r: r[3])
    return rose, fell


def compute_zipf_comparison(
    counter: Counter,
    min_count: int = 25
) -> dict[str, Any]:
    """
    Compares user frequencies against standard language corpus (wordfreq).
    """
    ru_ref = build_ru_lemma_reference()

    totals = defaultdict(int)
    for w, c in counter.items():
        totals[detect_lang(w)] += c

    records = []
    personal = []
    for w, c in counter.items():
        if c < min_count or len(w) < 2:
            continue
        lang = detect_lang(w)
        if totals[lang] == 0:
            continue
        my_zipf = math.log10(c / totals[lang] * 1e9)
        ref_zipf = ru_ref.get(w, 0) if lang == "ru" else zipf_frequency(w, lang)
        if ref_zipf == 0:
            if not LAUGH_RE.match(w):
                personal.append((w, lang, c, my_zipf))
        else:
            records.append((w, lang, c, my_zipf, ref_zipf, my_zipf - ref_zipf))

    # Top lemmas from reference missing in speech
    top_lemmas = sorted(ru_ref.items(), key=lambda x: x[1], reverse=True)
    missing = []
    seen = 0
    for w, _ in top_lemmas:
        if not WORD_RE.fullmatch(w) or len(w) < 2:
            continue
        seen += 1
        if seen > 300:
            break
        c = counter.get(w, 0)
        if c < min_count // 2:
            missing.append((w, c))

    # Zipf Law regression slope
    items = counter.most_common(1000)
    slope = 0.0
    if len(items) >= 50:
        xs = [math.log10(rank) for rank in range(1, len(items) + 1)]
        ys = [math.log10(c) for _, c in items]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=False))
        den = sum((x - mx) ** 2 for x in xs)
        slope = num / den if den else 0.0

    return {
        "records": records,
        "personal": personal,
        "missing_common": missing,
        "zipf_slope": slope,
    }
