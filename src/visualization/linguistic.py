"""
Linguistic style and vocabulary evolution visualization:
  - Profanity trend (profanity_trend.png)
  - Laughter styles evolution (laughter_evolution.png)
  - Questions and exclamations (questions_exclamations.png)
  - Language mix (language_mix.png)
  - Heaps' law vocabulary growth (vocab_growth.png)
  - Honest vocabulary timeline (vocab_timeline.png)
  - Core vocabulary heatmap (core_vocabulary.png)
  - Vocabulary authenticity breakdown (vocab_validation.png)
  - Top n-grams (ngrams.png)
  - Parts of speech evolution (pos_evolution.png)
  - Informality & non-dictionary words (informality.png)
"""

from collections import Counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

from src.analytics.core_vocab import compute_core_vocabulary
from src.analytics.style import compute_ngrams
from src.analytics.vocab_validator import validate_vocabulary
from src.core.config import (
    ACCENT2_COLOR,
    ACCENT3_COLOR,
    ACCENT_COLOR,
    BG_COLOR,
    FG_COLOR,
    GRID_COLOR,
    PALETTE,
)
from src.data.loader import parse_local_dt
from src.nlp.detectors import (
    LAUGH_RE,
    is_mat,
    laugh_family,
)
from src.nlp.lemmatizer import (
    LATIN_RE,
    detect_lang,
    pos_of,
    raw_tokenize,
    tokenize,
    word_known,
)
from src.visualization.theme import (
    apply_style,
    create_figure,
    save_figure,
    setup_legend,
)


def _is_dict_word(w: str) -> bool:
    if LATIN_RE.search(w) or LAUGH_RE.match(w):
        return False
    return word_known(w)


def chart_profanity_trend(chats: list[dict[str, Any]]) -> None:
    mat = Counter()
    words = Counter()
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            for w in tokenize(t):
                words[dt.year] += 1
                if is_mat(w):
                    mat[dt.year] += 1
    years = sorted(words)
    if not years:
        return
    rate = [mat[y] / words[y] * 1000 for y in years]
    fig = create_figure()
    ax = fig.add_subplot(111)
    bars = ax.bar([str(y) for y in years], rate, color=ACCENT2_COLOR, edgecolor=BG_COLOR)
    for b, v in zip(bars, rate, strict=False):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}", ha="center", va="bottom", color=FG_COLOR, fontsize=9)
    apply_style(ax, "Частота мату за роками")
    ax.set_ylabel("ненормативних слів на 1000 слів")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "profanity_trend.png")


def chart_laughter_evolution(chats: list[dict[str, Any]]) -> None:
    fams = ["класичний (ха-ха)", "клавіатурний (хпхвх/пхвх)", "хехе / хіхі", "хмх", "інший"]
    data = {f: Counter() for f in fams}
    msgs_year = Counter()
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            msgs_year[dt.year] += 1
            for w in tokenize(t):
                if LAUGH_RE.match(w):
                    data[laugh_family(w)][dt.year] += 1
    years = sorted(msgs_year)
    if not years:
        return
    ys = [str(y) for y in years]
    stacks = [[data[f][y] / msgs_year[y] * 100 for y in years] for f in fams]
    fig = create_figure(11, 6)
    ax = fig.add_subplot(111)
    ax.stackplot(ys, *stacks, labels=fams, colors=PALETTE[:len(fams)], alpha=0.9)
    apply_style(ax, "Еволюція «сміху»: скільки токенів сміху на 100 повідомлень")
    ax.set_ylabel("токенів сміху на 100 повідомлень")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.25)
    setup_legend(ax)
    save_figure(fig, "laughter_evolution.png")


def chart_questions_exclamations(chats: list[dict[str, Any]]) -> None:
    q = Counter()
    e = Counter()
    tot = Counter()
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            tot[dt.year] += 1
            if "?" in t:
                q[dt.year] += 1
            if "!" in t:
                e[dt.year] += 1
    years = sorted(tot)
    if not years:
        return
    ys = [str(y) for y in years]
    qp = [q[y] / tot[y] * 100 for y in years]
    ep = [e[y] / tot[y] * 100 for y in years]
    fig = create_figure()
    ax = fig.add_subplot(111)
    ax.plot(ys, qp, "o-", color=ACCENT_COLOR, lw=2.5, label="з питанням «?»")
    ax.plot(ys, ep, "s-", color=ACCENT2_COLOR, lw=2.5, label="зі знаком оклику «!»")
    apply_style(ax, "Частка питань та знаків оклику за роками")
    ax.set_ylabel("% повідомлень")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    setup_legend(ax)
    save_figure(fig, "questions_exclamations.png")


def chart_language_mix(chats: list[dict[str, Any]]) -> None:
    langs = ["ru", "uk", "en"]
    names = {"ru": "російська", "uk": "українська", "en": "англійська"}
    data = {lang_code: Counter() for lang_code in langs}
    tot = Counter()
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            for w in tokenize(t):
                lg = detect_lang(w)
                data[lg][dt.year] += 1
                tot[dt.year] += 1
    years = sorted(tot)
    if not years:
        return
    ys = [str(y) for y in years]
    stacks = [[data[lang_code][y] / tot[y] * 100 for y in years] for lang_code in langs]
    fig = create_figure(11, 6)
    ax = fig.add_subplot(111)
    ax.stackplot(ys, *stacks, labels=[names[lang_code] for lang_code in langs], colors=[ACCENT_COLOR, ACCENT3_COLOR, ACCENT2_COLOR], alpha=0.9)
    apply_style(ax, "Мовний мікс за роками (частка слів)")
    ax.set_ylabel("% слів")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.25)
    setup_legend(ax)
    ax.text(
        0.01, -0.16,
        "українська — за унікальними літерами (і/ї/є/ґ) та характерними словами;",
        transform=ax.transAxes,
        color="#8a8f98",
        fontsize=8,
    )
    save_figure(fig, "language_mix.png")


def chart_vocab_growth(chats: list[dict[str, Any]]) -> None:
    msgs = []
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                msgs.append((dt, t))
    msgs.sort(key=lambda x: x[0])

    counts = Counter()
    confirmed = 0
    seen_dict = set()
    xs, conf_y, dict_y = [], [], []
    total = 0
    step = 3000
    nxt = step
    for _, t in msgs:
        for w in tokenize(t):
            total += 1
            counts[w] += 1
            if counts[w] == 2:
                confirmed += 1
            if w not in seen_dict and _is_dict_word(w):
                seen_dict.add(w)
        if total >= nxt:
            xs.append(total)
            conf_y.append(confirmed)
            dict_y.append(len(seen_dict))
            nxt += step
    xs.append(total)
    conf_y.append(confirmed)
    dict_y.append(len(seen_dict))

    fig = create_figure()
    ax = fig.add_subplot(111)
    xm = np.array(xs) / 1e6
    ax.plot(xm, conf_y, color=ACCENT_COLOR, lw=2.5, label="перевірені (≥2 разів)")
    ax.plot(xm, dict_y, color=ACCENT2_COLOR, lw=2.5, label="словникові (uk/ru)")
    apply_style(ax, "Зростання словникового запасу від обсягу тексту (закон Хіпса)")
    ax.set_xlabel("всього слів написано, млн")
    ax.set_ylabel("унікальних лем")
    ax.grid(color=GRID_COLOR, alpha=0.3)
    if len(xs) > 10 and dict_y[-1] > 0:
        valid_indices = [i for i, v in enumerate(dict_y) if v > 0 and xs[i] > 0]
        if len(valid_indices) > 5:
            b, _a = np.polyfit(np.log10([xs[i] for i in valid_indices]), np.log10([dict_y[i] for i in valid_indices]), 1)
            ax.text(
                0.05, 0.86,
                f"показник Хіпса β ≈ {b:.2f} (за словниковими)\nчим вище — тим активніше поповнюється словник",
                transform=ax.transAxes,
                color=FG_COLOR,
                fontsize=9,
                bbox={"facecolor": BG_COLOR, "edgecolor": GRID_COLOR},
            )
    setup_legend(ax)
    save_figure(fig, "vocab_growth.png")


def chart_vocab_timeline(chats: list[dict[str, Any]]) -> None:
    msgs = []
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                msgs.append((dt, t))
    msgs.sort(key=lambda x: x[0])

    counts = Counter()
    confirmed = 0
    seen_dict = set()
    new_conf = Counter()
    new_dict = Counter()
    monthly = []
    cur = None
    for dt, t in msgs:
        ym = (dt.year, dt.month)
        if cur is not None and ym != cur:
            monthly.append((cur, confirmed, len(seen_dict)))
        cur = ym
        for w in tokenize(t):
            counts[w] += 1
            if counts[w] == 2:
                confirmed += 1
                new_conf[dt.year] += 1
            if w not in seen_dict and _is_dict_word(w):
                seen_dict.add(w)
                new_dict[dt.year] += 1
    if cur is not None:
        monthly.append((cur, confirmed, len(seen_dict)))

    years = sorted({y for (y, _m), _c, _d in monthly})
    fig = plt.figure(figsize=(13, 9), facecolor=BG_COLOR)
    gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.4)

    ax1 = fig.add_subplot(gs[0])
    xs = list(range(len(monthly)))
    conf_y = [c for _, c, _ in monthly]
    dict_y = [d for _, _, d in monthly]
    ax1.fill_between(xs, conf_y, color=ACCENT_COLOR, alpha=0.18)
    ax1.plot(xs, conf_y, color=ACCENT_COLOR, lw=2.3, label="перевірений (зустрілося ≥2 разів)")
    ax1.plot(xs, dict_y, color=ACCENT2_COLOR, lw=2.3, label="тільки словникові (uk/ru)")
    ticks = [i for i, ((y, m), _c, _d) in enumerate(monthly) if m == 1]
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([str(monthly[i][0][0]) for i in ticks])
    if conf_y:
        ax1.annotate(
            f"{conf_y[-1]:,}".replace(",", " "), xy=(xs[-1], conf_y[-1]),
            xytext=(-6, 4), textcoords="offset points", color=ACCENT_COLOR,
            fontsize=11, fontweight="bold", ha="right"
        )
        ax1.annotate(
            f"{dict_y[-1]:,}".replace(",", " "), xy=(xs[-1], dict_y[-1]),
            xytext=(-6, -14), textcoords="offset points", color=ACCENT2_COLOR,
            fontsize=11, fontweight="bold", ha="right"
        )
    apply_style(ax1, "Чесне зростання словникового запасу у часі")
    ax1.set_ylabel("накопичених лем")
    ax1.grid(color=GRID_COLOR, alpha=0.3)
    setup_legend(ax1)

    ax2 = fig.add_subplot(gs[1])
    x = np.arange(len(years))
    w = 0.4
    ax2.bar(x - w / 2, [new_conf[y] for y in years], w, color=ACCENT_COLOR, edgecolor=BG_COLOR, label="нових перевірених (≥2 разів)")
    ax2.bar(x + w / 2, [new_dict[y] for y in years], w, color=ACCENT2_COLOR, edgecolor=BG_COLOR, label="нових словникових (uk/ru)")
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(y) for y in years])
    apply_style(ax2, "Нових слів додано за рік (чесні метрики)")
    ax2.set_ylabel("нових лем")
    ax2.grid(axis="y", color=GRID_COLOR, alpha=0.25)
    setup_legend(ax2)
    ax2.text(
        0.0, -0.3,
        "«Сирий» лічильник усіх унікальних лем виключено: ~46% із них — несловникові та одноразові одруківки.",
        transform=ax2.transAxes,
        color="#8a8f98",
        fontsize=8,
    )
    save_figure(fig, "vocab_timeline.png")


def chart_core_vocabulary(chats: list[dict[str, Any]]) -> None:
    res = compute_core_vocabulary(chats)
    reliable = res["reliable_years"]
    core = res["core_words"]
    matrix = res["matrix"]

    if not core or len(reliable) == 0:
        return

    fig = plt.figure(figsize=(12, 11), facecolor=BG_COLOR)
    ax = fig.add_subplot(111)
    im = ax.imshow(
        matrix, aspect="auto", cmap="viridis",
        norm=LogNorm(vmin=max(0.1, matrix.min()), vmax=matrix.max())
    )
    ax.set_xticks(range(len(reliable)))
    ax.set_xticklabels([str(y) for y in reliable])
    ax.set_yticks(range(len(core)))
    ax.set_yticklabels(core, fontsize=10)
    for i in range(len(core)):
        for j in range(len(reliable)):
            ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center", color="white", fontsize=7)
    apply_style(ax, "Кістяк мого мовлення: слова, стабільні з року в рік (на 1000 слів)")
    ax.tick_params(colors=FG_COLOR)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025)
    cbar.ax.tick_params(colors=FG_COLOR)
    cbar.set_label("частота на 1000 слів (лог)", color=FG_COLOR)
    ax.text(
        0.0, -0.06,
        "Слова відсортовані за частотою у найгірший рік → зверху найбільш стабільні.",
        transform=ax.transAxes,
        color="#8a8f98",
        fontsize=8,
    )
    save_figure(fig, "core_vocabulary.png")


def chart_vocab_validation(chats: list[dict[str, Any]]) -> None:
    res = validate_vocabulary(chats)
    total_types = res["total_types"]
    total_tokens = res["total_tokens"]
    by_cat_types = res["by_cat_types"]
    by_cat_tokens = res["by_cat_tokens"]
    order = res["categories_order"]

    fig = plt.figure(figsize=(13, 6), facecolor=BG_COLOR)
    gs = fig.add_gridspec(1, 2, wspace=0.25)

    colors = [ACCENT3_COLOR, ACCENT_COLOR, ACCENT2_COLOR, "#ffd166"]

    # Types pie
    ax1 = fig.add_subplot(gs[0])
    type_counts = [by_cat_types[c] for c in order]
    wedges1, _, autotexts1 = ax1.pie(
        type_counts, labels=None, autopct="%1.1f%%", colors=colors, startangle=140,
        pctdistance=0.75, textprops={"color": BG_COLOR, "fontweight": "bold"}
    )
    ax1.set_title(f"Склад словника за ТИПАМИ слів\n(всього {total_types:,} унікальних лем)".replace(",", " "), color=FG_COLOR, fontsize=13, fontweight="bold")

    # Tokens pie
    ax2 = fig.add_subplot(gs[1])
    token_counts = [by_cat_tokens[c] for c in order]
    wedges2, _, autotexts2 = ax2.pie(
        token_counts, labels=None, autopct="%1.1f%%", colors=colors, startangle=140,
        pctdistance=0.75, textprops={"color": BG_COLOR, "fontweight": "bold"}
    )
    ax2.set_title(f"Склад мовлення за ТОКЕНАМИ (вживаннями)\n(всього {total_tokens:,} слів написав)".replace(",", " "), color=FG_COLOR, fontsize=13, fontweight="bold")

    fig.legend(wedges1, order, loc="lower center", ncol=2, facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=FG_COLOR, fontsize=9)
    save_figure(fig, "vocab_validation.png")


def chart_ngrams(chats: list[dict[str, Any]], top: int = 18) -> None:
    bi, tri = compute_ngrams(chats, top)

    fig = plt.figure(figsize=(15, 8), facecolor=BG_COLOR)
    fig.suptitle(
        "Мої коронні фрази (найчастіші стійкі словосполучення)",
        color=FG_COLOR,
        fontsize=18,
        fontweight="bold",
        y=0.97,
    )
    for idx, (items, title, color) in enumerate([
        (bi[::-1], "Біграми (2 слова)", ACCENT_COLOR),
        (tri[::-1], "Триграми (3 слова)", ACCENT2_COLOR),
    ]):
        ax = fig.add_subplot(1, 2, idx + 1)
        labels = [" ".join(g) for g, _ in items]
        vals = [c for _, c in items]
        ax.barh(labels, vals, color=color, edgecolor=BG_COLOR)
        for y, v in enumerate(vals):
            ax.text(v, y, f" {v}", va="center", color=FG_COLOR, fontsize=8)
        apply_style(ax, title)
        ax.grid(axis="x", color=GRID_COLOR, alpha=0.3)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, "ngrams.png")


def chart_pos_evolution(chats: list[dict[str, Any]]) -> None:
    cats = ["дієслова", "іменники", "прикметники", "прислівники", "займенники", "службові/інші"]
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
    if not years:
        return
    ys = [str(y) for y in years]
    stacks = [[data[c][y] / tot[y] * 100 for y in years] for c in cats]

    fig = create_figure(12, 6.5)
    ax = fig.add_subplot(111)
    ax.stackplot(ys, *stacks, labels=cats, colors=PALETTE[:len(cats)], alpha=0.9)
    apply_style(ax, "Профіль частин мови за роками (частка серед словникових слів)")
    ax.set_ylabel("% слів")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.25)
    setup_legend(ax)
    save_figure(fig, "pos_evolution.png")


def chart_informality(chats: list[dict[str, Any]]) -> None:
    unknown = Counter()
    tot = Counter()
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            for w in raw_tokenize(t):
                if LAUGH_RE.match(w):
                    continue
                tot[dt.year] += 1
                if not word_known(w):
                    unknown[dt.year] += 1
    years = sorted(tot)
    if not years:
        return
    rate = [unknown[y] / tot[y] * 100 for y in years]
    fig = create_figure()
    ax = fig.add_subplot(111)
    ax.plot([str(y) for y in years], rate, "o-", color=ACCENT3_COLOR, lw=2.5)
    ax.fill_between([str(y) for y in years], rate, color=ACCENT3_COLOR, alpha=0.15)
    apply_style(ax, "Частка несловникових слів за роками (сленг / одруківки / скорочення / імена)")
    ax.set_ylabel("% слів поза словником")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "informality.png")


def generate_linguistic_charts(chats: list[dict[str, Any]]) -> None:
    """Generates all linguistic and vocabulary infographics."""
    print("  [•] Генерація лінгвістичної інфографіки...")
    chart_profanity_trend(chats)
    chart_laughter_evolution(chats)
    chart_questions_exclamations(chats)
    chart_language_mix(chats)
    chart_vocab_growth(chats)
    chart_vocab_timeline(chats)
    chart_core_vocabulary(chats)
    chart_vocab_validation(chats)
    chart_ngrams(chats)
    chart_pos_evolution(chats)
    chart_informality(chats)
