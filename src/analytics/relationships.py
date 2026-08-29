"""
Social and relational analytics: chat fingerprints, Ty/Vy balance, profanity by chat,
and vocabulary clustering across dialogs.
"""

from collections import Counter
from typing import Any

import numpy as np

from src.nlp.detectors import LAUGH_RE, is_mat, is_ty, is_vy
from src.nlp.lemmatizer import is_stop_word, tokenize


def compute_ty_vy_balance(chats: list[dict[str, Any]], min_msgs: int = 50) -> list[dict[str, Any]]:
    """
    Calculates proportion of informal (ty) vs formal/group (vy) pronouns per chat.
    """
    results = []
    for ch in chats:
        if len(ch["messages"]) < min_msgs:
            continue
        c_ty, c_vy = 0, 0
        for _, t in ch["messages"]:
            for w in tokenize(t):
                if is_ty(w):
                    c_ty += 1
                elif is_vy(w):
                    c_vy += 1
        total = c_ty + c_vy
        if total >= 5:
            results.append({
                "title": ch["title"],
                "n_msgs": len(ch["messages"]),
                "ty": c_ty,
                "vy": c_vy,
                "total": total,
                "ty_ratio": c_ty / total,
            })
    return sorted(results, key=lambda x: x["total"], reverse=True)


def compute_profanity_per_chat(chats: list[dict[str, Any]], min_words: int = 1000) -> list[dict[str, Any]]:
    """
    Calculates profanity frequency per 1000 words across active chats.
    """
    results = []
    for ch in chats:
        mat_cnt = 0
        word_cnt = 0
        for _, t in ch["messages"]:
            words = tokenize(t)
            word_cnt += len(words)
            for w in words:
                if is_mat(w):
                    mat_cnt += 1
        if word_cnt >= min_words:
            rate = (mat_cnt / word_cnt) * 1000
            results.append({
                "title": ch["title"],
                "word_cnt": word_cnt,
                "mat_cnt": mat_cnt,
                "rate_per_1000": rate,
            })
    return sorted(results, key=lambda x: x["rate_per_1000"], reverse=True)


def compute_chat_clustering_data(
    chats: list[dict[str, Any]],
    top_chats: int = 20,
    top_features: int = 500
) -> dict[str, Any]:
    """
    Computes TF-IDF / cosine similarity matrix for top dialogs based on vocabulary distribution.
    """
    active_chats = sorted(chats, key=lambda c: len(c["messages"]), reverse=True)[:top_chats]
    if len(active_chats) < 3:
        return {"titles": [], "matrix": np.empty((0, 0))}

    doc_freqs = Counter()
    chat_counters = []
    chat_totals = []

    for ch in active_chats:
        cnt = Counter()
        for _, t in ch["messages"]:
            for w in tokenize(t):
                if len(w) > 2 and not is_stop_word(w) and not LAUGH_RE.match(w):
                    cnt[w] += 1
        chat_counters.append(cnt)
        chat_totals.append(sum(cnt.values()) or 1)
        for w in set(cnt):
            doc_freqs[w] += 1

    common_vocab = [w for w, _ in doc_freqs.most_common(top_features) if doc_freqs[w] >= 2]
    if not common_vocab:
        return {"titles": [c["title"] for c in active_chats], "matrix": np.empty((0, 0))}

    w_to_idx = {w: i for i, w in enumerate(common_vocab)}
    vectors = np.zeros((len(active_chats), len(common_vocab)))

    for i, (cnt, total) in enumerate(zip(chat_counters, chat_totals, strict=False)):
        for w, c in cnt.items():
            if w in w_to_idx:
                tf = c / total
                idf = np.log((len(active_chats) + 1) / (doc_freqs[w] + 1))
                vectors[i, w_to_idx[w]] = tf * idf

    # Normalize vectors
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_vectors = vectors / norms

    sim_matrix = norm_vectors @ norm_vectors.T

    return {
        "titles": [c["title"][:22] for c in active_chats],
        "similarity_matrix": sim_matrix,
    }
