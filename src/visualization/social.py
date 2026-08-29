"""
Social, interpersonal, and dialog dynamics visualization:
  - Chat linguistic fingerprints TF-IDF (chat_fingerprint.png)
  - Formality / Ty-Vy balance (ty_vy.png)
  - Profanity rate per chat (mat_per_chat.png)
  - Interlocutor streamgraph (streamgraph_chats.png)
  - Social breadth & concentration (social_breadth.png)
  - Relationships lifecycle heatmap (relationships_timeline.png)
  - Vocabulary similarity dendrogram & clustering (speech_clustering.png)
"""

import math
from collections import Counter, defaultdict
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

from src.core.config import (
    ACCENT2_COLOR,
    ACCENT_COLOR,
    BG_COLOR,
    FG_COLOR,
    GRID_COLOR,
    PALETTE,
)
from src.data.loader import parse_local_dt
from src.nlp.detectors import LAUGH_RE, is_mat, is_ty, is_vy
from src.nlp.lemmatizer import is_stop_word, tokenize
from src.nlp.reference import build_ru_lemma_reference
from src.visualization.theme import (
    apply_style,
    create_figure,
    save_figure,
    setup_legend,
)


def _chat_counters(chats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ru_ref = build_ru_lemma_reference()
    out = []
    for ch in chats:
        c = Counter()
        for _, t in ch["messages"]:
            for w in tokenize(t):
                if (
                    len(w) > 2
                    and not is_stop_word(w)
                    and not LAUGH_RE.match(w)
                    and ru_ref.get(w, 0) < 5.2
                ):
                    c[w] += 1
        out.append({"title": ch["title"], "n": len(ch["messages"]), "counter": c})
    return out


def chart_chat_fingerprint(chats: list[dict[str, Any]], top_chats: int = 9, per: int = 7) -> None:
    cc = _chat_counters(chats)
    df = Counter()
    for d in cc:
        for w in d["counter"]:
            df[w] += 1
    N = len(cc)
    chosen = sorted(cc, key=lambda d: d["n"], reverse=True)[:top_chats]
    if not chosen:
        return

    fig = plt.figure(figsize=(15, 11), facecolor=BG_COLOR)
    fig.suptitle(
        "Лінгвістичний «відбиток» спілкування з різними людьми (TF-IDF)",
        color=FG_COLOR,
        fontsize=17,
        fontweight="bold",
        y=0.98,
    )
    for i, d in enumerate(chosen, 1):
        tot = sum(d["counter"].values()) or 1
        scored = []
        for w, c in d["counter"].items():
            if c < 8:
                continue
            tfidf = (c / tot) * math.log(N / (1 + df[w]))
            scored.append((w, tfidf))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:per][::-1]
        ax = fig.add_subplot(3, 3, i)
        if top:
            ax.barh(
                [w for w, _ in top],
                [s for _, s in top],
                color=PALETTE[(i - 1) % len(PALETTE)],
                edgecolor=BG_COLOR,
            )
        apply_style(ax, d["title"][:22])
        ax.tick_params(labelsize=9)
        ax.set_xticks([])
        ax.grid(axis="x", color=GRID_COLOR, alpha=0.2)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, "chat_fingerprint.png")


def chart_ty_vy(chats: list[dict[str, Any]], top_chats: int = 15) -> None:
    rows = []
    for ch in sorted(chats, key=lambda c: len(c["messages"]), reverse=True)[:top_chats]:
        ty = vy = 0
        for _, t in ch["messages"]:
            for w in tokenize(t):
                if is_ty(w):
                    ty += 1
                elif is_vy(w):
                    vy += 1
        if ty + vy >= 20:
            rows.append((ch["title"][:20], vy / (ty + vy) * 100, ty + vy))
    if not rows:
        return
    rows.sort(key=lambda r: r[1])
    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    fig = create_figure(11, 7)
    ax = fig.add_subplot(111)
    colors = [ACCENT_COLOR if v < 50 else ACCENT2_COLOR for v in vals]
    ax.barh(labels, vals, color=colors, edgecolor=BG_COLOR)
    ax.axvline(50, color=FG_COLOR, ls=":", lw=1, alpha=0.5)
    apply_style(ax, "Формальність спілкування: частка «ви» проти «ти»")
    ax.set_xlabel("% звертань на «ви»  (0 = завжди «ти», 100 = завжди «ви»)")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "ty_vy.png")


def chart_mat_per_chat(chats: list[dict[str, Any]], top_chats: int = 15) -> None:
    rows = []
    for ch in sorted(chats, key=lambda c: len(c["messages"]), reverse=True)[:top_chats]:
        mat = tot = 0
        for _, t in ch["messages"]:
            for w in tokenize(t):
                tot += 1
                if is_mat(w):
                    mat += 1
        if tot > 500:
            rows.append((ch["title"][:20], mat / tot * 1000))
    if not rows:
        return
    rows.sort(key=lambda r: r[1])
    fig = create_figure(11, 7)
    ax = fig.add_subplot(111)
    ax.barh([r[0] for r in rows], [r[1] for r in rows], color=ACCENT2_COLOR, edgecolor=BG_COLOR)
    apply_style(ax, "Кому я пишу більше ненормативної лексики (слів на 1000 слів)")
    ax.set_xlabel("ненормативних слів на 1000 слів")
    ax.grid(axis="x", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "mat_per_chat.png")


def chart_streamgraph(chats: list[dict[str, Any]], top_chats: int = 8) -> None:
    top = sorted(chats, key=lambda c: len(c["messages"]), reverse=True)[:top_chats]
    if not top:
        return
    by_year_chat = {ch["title"]: Counter() for ch in top}
    years_set = set()
    for ch in top:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                by_year_chat[ch["title"]][dt.year] += 1
                years_set.add(dt.year)
    years = sorted(years_set)
    if not years:
        return
    ys = [str(y) for y in years]
    stacks = [[by_year_chat[ch["title"]][y] for y in years] for ch in top]
    fig = create_figure(13, 6.5)
    ax = fig.add_subplot(111)
    ax.stackplot(
        ys, *stacks,
        labels=[ch["title"][:18] for ch in top],
        colors=PALETTE[:len(top)],
        baseline="wiggle",
        alpha=0.9,
    )
    apply_style(ax, "Як змінювався склад мого топ-спілкування за роками")
    ax.set_ylabel("повідомлень (потік)")
    setup_legend(ax)
    save_figure(fig, "streamgraph_chats.png")


def chart_social_breadth(chats: list[dict[str, Any]]) -> None:
    by_month = defaultdict(set)
    year_chat = defaultdict(Counter)
    for ch in chats:
        cid = ch["title"]
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                by_month[(dt.year, dt.month)].add(cid)
                year_chat[dt.year][cid] += 1
    months = sorted(by_month)
    if not months:
        return

    fig = plt.figure(figsize=(13, 8), facecolor=BG_COLOR)
    gs = fig.add_gridspec(2, 1, hspace=0.35)

    ax1 = fig.add_subplot(gs[0])
    xs = range(len(months))
    ys = [len(by_month[m]) for m in months]
    ax1.fill_between(xs, ys, color=ACCENT_COLOR, alpha=0.2)
    ax1.plot(xs, ys, color=ACCENT_COLOR, lw=2)
    ticks = [i for i, (y, m) in enumerate(months) if m == 1]
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([str(months[i][0]) for i in ticks])
    apply_style(ax1, "Скільки різних людей на місяць я писав (широта спілкування)")
    ax1.set_ylabel("різних чатів / місяць")
    ax1.grid(color=GRID_COLOR, alpha=0.3)

    ax2 = fig.add_subplot(gs[1])
    years = sorted(year_chat)
    top3 = []
    for y in years:
        c = year_chat[y]
        tot = sum(c.values())
        t3 = sum(v for _, v in c.most_common(3))
        top3.append(t3 / tot * 100 if tot else 0)
    ax2.plot([str(y) for y in years], top3, "o-", color=ACCENT2_COLOR, lw=2.5)
    apply_style(ax2, "Концентрація спілкування: частка повідомлень у топ-3 чати")
    ax2.set_ylabel("% повідомлень у топ-3")
    ax2.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "social_breadth.png")


def chart_relationships_timeline(chats: list[dict[str, Any]], top_n: int = 25) -> None:
    top = sorted(chats, key=lambda c: len(c["messages"]), reverse=True)[:top_n]
    allm = []
    for ch in top:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                allm.append((dt.year, dt.month))
    if not allm:
        return
    y0, m0 = min(allm)
    y1, m1 = max(allm)
    months = []
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        months.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    midx = {ym: i for i, ym in enumerate(months)}

    def first_month(ch):
        ms = [parse_local_dt(d) for d, _ in ch["messages"] if parse_local_dt(d)]
        dt = min(ms) if ms else None
        return (dt.year, dt.month) if dt else (9999, 99)

    top.sort(key=first_month)

    grid = np.zeros((len(top), len(months)))
    for r, ch in enumerate(top):
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                grid[r, midx[(dt.year, dt.month)]] += 1
    grid[grid == 0] = np.nan

    fig = plt.figure(figsize=(14, 9), facecolor=BG_COLOR)
    ax = fig.add_subplot(111)
    im = ax.imshow(
        grid,
        aspect="auto",
        cmap="magma",
        norm=LogNorm(vmin=1, vmax=np.nanmax(grid) if not np.isnan(np.nanmax(grid)) else 1),
    )
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([ch["title"][:22] for ch in top], fontsize=9)
    ticks = [i for i, (yy, mm) in enumerate(months) if mm == 1]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(months[i][0]) for i in ticks])
    apply_style(ax, "Життя кожного чату за місяцями (коли спалахувало і згасало спілкування)")
    ax.tick_params(colors=FG_COLOR)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025)
    cbar.ax.tick_params(colors=FG_COLOR)
    cbar.set_label("повідомлень / місяць (лог)", color=FG_COLOR)
    save_figure(fig, "relationships_timeline.png")


def _compute_speech_similarity_data(
    chats: list[dict[str, Any]],
    top_n: int = 20,
) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray] | None:
    """Computes similarity matrix and hierarchical linkage for top chats."""
    top = sorted(chats, key=lambda c: len(c["messages"]), reverse=True)[:top_n]
    if len(top) < 3:
        return None
    ru_ref = build_ru_lemma_reference()

    vecs = []
    for ch in top:
        c = Counter()
        for _, t in ch["messages"]:
            for w in tokenize(t):
                if (
                    len(w) > 2
                    and not is_stop_word(w)
                    and not LAUGH_RE.match(w)
                    and ru_ref.get(w, 0) < 5.5
                ):
                    c[w] += 1
        vecs.append(c)

    vocab = sorted({w for c in vecs for w, n in c.items() if n >= 5})
    if not vocab:
        return None
    vidx = {w: i for i, w in enumerate(vocab)}
    M = np.zeros((len(top), len(vocab)))
    for r, c in enumerate(vecs):
        for w, n in c.items():
            if w in vidx:
                M[r, vidx[w]] = n

    norm = np.linalg.norm(M, axis=1, keepdims=True)
    norm[norm == 0] = 1
    Mn = M / norm
    S = Mn @ Mn.T
    np.clip(S, 0, 1, out=S)
    D = 1 - S
    np.fill_diagonal(D, 0)
    D = (D + D.T) / 2

    try:
        Z = linkage(squareform(D, checks=False), method="average")
    except Exception:
        return None

    titles = [ch["title"][:22] for ch in top]
    return titles, S, D, Z


def chart_speech_clustering(chats: list[dict[str, Any]], top_n: int = 20) -> None:
    """Generates standalone hierarchical clustering dendrogram tree (speech_clustering.png)."""
    data = _compute_speech_similarity_data(chats, top_n)
    if data is None:
        return
    titles, _, _, Z = data

    fig = create_figure(14, 8)
    ax = fig.add_subplot(111)

    dendrogram(
        Z,
        labels=titles,
        orientation="top",
        leaf_rotation=35,
        leaf_font_size=9,
        color_threshold=0.7 * max(Z[:, 2]),
        ax=ax,
    )

    apply_style(ax, "Кластеризація співрозмовників за подібністю вашого словника")
    ax.set_ylabel("Лінгвістична дистанція (Косинусна відстань)")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    ax.tick_params(axis="x", colors=FG_COLOR, labelsize=9)
    ax.tick_params(axis="y", colors=FG_COLOR, labelsize=9)
    plt.setp(ax.get_xticklabels(), ha="right", rotation_mode="anchor")

    fig.tight_layout()
    save_figure(fig, "speech_clustering.png")


def chart_speech_similarity_matrix(chats: list[dict[str, Any]], top_n: int = 20) -> None:
    """Generates standalone cosine similarity heatmap matrix (speech_similarity_matrix.png)."""
    data = _compute_speech_similarity_data(chats, top_n)
    if data is None:
        return
    titles, S, _, Z = data

    # Order by dendrogram leaves so clustered chats are grouped together
    dn = dendrogram(Z, no_plot=True)
    order = dn["leaves"]
    ordered_titles = [titles[i] for i in order]
    ordered_S = S[np.ix_(order, order)]

    fig = create_figure(12, 10)
    ax = fig.add_subplot(111)

    im = ax.imshow(ordered_S, cmap="viridis", vmin=0, vmax=1)
    apply_style(ax, "Матриця схожості лексичного стилю (косинус)")

    ax.set_xticks(range(len(ordered_titles)))
    ax.set_xticklabels(ordered_titles, rotation=45, ha="right", fontsize=8, color=FG_COLOR)
    ax.set_yticks(range(len(ordered_titles)))
    ax.set_yticklabels(ordered_titles, fontsize=8, color=FG_COLOR)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=FG_COLOR)
    cbar.set_label("Косинусна схожість", color=FG_COLOR, fontsize=10)

    fig.tight_layout()
    save_figure(fig, "speech_similarity_matrix.png")


def generate_social_charts(chats: list[dict[str, Any]]) -> None:
    """Generates all interpersonal and dialog dynamics infographics."""
    print("  [•] Генерація інфографіки стосунків та діалогів...")
    chart_chat_fingerprint(chats)
    chart_ty_vy(chats)
    chart_mat_per_chat(chats)
    chart_streamgraph(chats)
    chart_social_breadth(chats)
    chart_relationships_timeline(chats)
    chart_speech_clustering(chats)
    chart_speech_similarity_matrix(chats)
