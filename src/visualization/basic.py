"""
Basic infographics suite:
  1. Wordcloud
  2. Hourly message activity
  3. Weekday message activity
  4. Top words bar chart
  5. Yearly messages & words evolution
  6. Vocabulary diversity (TTR) evolution
  7. Top active chats
  8. Zipf law distribution
  9. Word length distribution
"""

from collections import Counter, defaultdict
from typing import Any

import numpy as np
from wordcloud import WordCloud

from src.analytics.text_stats import compute_message_stats, top_meaningful
from src.core.config import (
    ACCENT2_COLOR,
    ACCENT3_COLOR,
    ACCENT_COLOR,
    BG_COLOR,
    DAYS_UK,
    FG_COLOR,
    GRID_COLOR,
)
from src.data.loader import parse_local_dt
from src.nlp.lemmatizer import is_stop_word, tokenize
from src.visualization.theme import (
    FONT_PATH,
    apply_style,
    create_figure,
    save_figure,
)


def chart_wordcloud(all_counter: Counter) -> None:
    meaningful = {
        w: c
        for w, c in all_counter.items()
        if not is_stop_word(w)
        and len(w) > 2
        and not w.startswith(("хпх", "хах", "пхв", "ахв"))
    }
    wc = WordCloud(
        width=1600,
        height=900,
        background_color=BG_COLOR,
        font_path=FONT_PATH,
        colormap="cool",
        max_words=200,
        prefer_horizontal=0.95,
        collocations=False,
        relative_scaling=0.5,
    ).generate_from_frequencies(meaningful)

    fig = create_figure(13, 7.3)
    ax = fig.add_subplot(111)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Хмара моїх слів (за весь час)", color=FG_COLOR, fontsize=18, fontweight="bold", pad=14)
    save_figure(fig, "wordcloud.png")


def chart_hours(chats: list[dict[str, Any]]) -> None:
    hours = Counter()
    for ch in chats:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                hours[dt.hour] += 1

    xs = list(range(24))
    ys = [hours[h] for h in xs]

    fig = create_figure(11, 5.5)
    ax = fig.add_subplot(111)
    bars = ax.bar(xs, ys, color=ACCENT_COLOR, edgecolor=BG_COLOR, width=0.8)

    max_idx = int(np.argmax(ys)) if ys else 0
    if ys:
        bars[max_idx].set_color(ACCENT2_COLOR)

    ax.set_xticks(xs)
    ax.set_xticklabels([f"{h:02d}:00" for h in xs], rotation=45, ha="right", fontsize=9)
    ax.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
    apply_style(ax, "Активність за годинами доби (місцевий час)")
    save_figure(fig, "activity_by_hour.png")


def chart_weekdays(chats: list[dict[str, Any]]) -> None:
    days = Counter()
    for ch in chats:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                days[dt.weekday()] += 1

    xs = list(range(7))
    ys = [days[i] for i in xs]

    fig = create_figure(9, 5)
    ax = fig.add_subplot(111)
    colors = [ACCENT3_COLOR if i >= 5 else ACCENT_COLOR for i in xs]
    ax.bar(xs, ys, color=colors, edgecolor=BG_COLOR, width=0.65)
    ax.set_xticks(xs)
    ax.set_xticklabels(DAYS_UK, fontsize=11)
    ax.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
    apply_style(ax, "Активність за днями тижня (вихідні виділено)")
    save_figure(fig, "activity_by_weekday.png")


def chart_top_words(all_counter: Counter) -> None:
    meaningful = top_meaningful(all_counter, 25)
    words = [w for w, _ in reversed(meaningful)]
    counts = [c for _, c in reversed(meaningful)]

    fig = create_figure(10, 9)
    ax = fig.add_subplot(111)
    ax.barh(words, counts, color=ACCENT_COLOR, edgecolor=BG_COLOR)
    for i, c in enumerate(counts):
        ax.text(c + max(counts) * 0.01, i, f"{c:,}".replace(",", " "), va="center", color=FG_COLOR, fontsize=9)
    ax.set_xlim(0, max(counts) * 1.15 if counts else 1)
    ax.grid(axis="x", color=GRID_COLOR, linestyle="--", alpha=0.7)
    apply_style(ax, "Топ-25 найчастіших змістовних слів (без службових)")
    save_figure(fig, "top_words.png")


def chart_years_evolution(chats: list[dict[str, Any]]) -> None:
    by_year_msgs = Counter()
    by_year_words = Counter()
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                by_year_msgs[dt.year] += 1
                by_year_words[dt.year] += len(tokenize(t))

    years = sorted(by_year_msgs.keys())
    if not years:
        return

    xs = np.arange(len(years))
    width = 0.38

    fig = create_figure(11, 5.5)
    ax = fig.add_subplot(111)
    ax.bar(xs - width / 2, [by_year_msgs[y] for y in years], width=width, label="Повідомлень", color=ACCENT_COLOR)
    ax.bar(xs + width / 2, [by_year_words[y] for y in years], width=width, label="Слів", color=ACCENT2_COLOR)

    ax.set_xticks(xs)
    ax.set_xticklabels([str(y) for y in years], fontsize=11)
    ax.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
    ax.legend(facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=FG_COLOR)
    apply_style(ax, "Обсяг спілкування за роками")
    save_figure(fig, "years_volume.png")


def chart_ttr_evolution(chats: list[dict[str, Any]]) -> None:
    by_year = defaultdict(list)
    for ch in chats:
        for d, t in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                by_year[dt.year].append((d, t))

    years = sorted(by_year.keys())
    ttrs = []
    avg_lens = []
    for y in years:
        st = compute_message_stats(by_year[y])
        ttrs.append(st["ttr"] * 100)
        avg_lens.append(st["avg_words"])

    if not years:
        return

    fig = create_figure(11, 5.5)
    ax1 = fig.add_subplot(111)
    color1 = ACCENT3_COLOR
    color2 = ACCENT2_COLOR

    ax1.plot(years, ttrs, color=color1, marker="o", linewidth=2.5, label="Різноманіття TTR (%)")
    ax1.set_ylabel("TTR (унікальних / всіх слів, %)", color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)

    ax2 = ax1.twinx()
    ax2.plot(years, avg_lens, color=color2, marker="s", linestyle="--", linewidth=2, label="Слів / повідомлення")
    ax2.set_ylabel("Сер. довжина повідомлення (слів)", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.spines["right"].set_color(GRID_COLOR)

    apply_style(ax1, "Еволюція мовного багатства та довжини реплік")
    ax1.grid(color=GRID_COLOR, linestyle="--", alpha=0.7)
    save_figure(fig, "ttr_evolution.png")


def chart_top_chats(chats: list[dict[str, Any]], top_n: int = 12) -> None:
    active = sorted(chats, key=lambda c: len(c["messages"]), reverse=True)[:top_n]
    titles = [c["title"][:22] for c in reversed(active)]
    counts = [len(c["messages"]) for c in reversed(active)]

    fig = create_figure(10, 7)
    ax = fig.add_subplot(111)
    ax.barh(titles, counts, color=ACCENT_COLOR, edgecolor=BG_COLOR)
    for i, c in enumerate(counts):
        ax.text(c + max(counts) * 0.01, i, f"{c:,}".replace(",", " "), va="center", color=FG_COLOR, fontsize=9)
    ax.set_xlim(0, max(counts) * 1.15 if counts else 1)
    ax.grid(axis="x", color=GRID_COLOR, linestyle="--", alpha=0.7)
    apply_style(ax, f"Топ-{top_n} найактивніших чатів за кількістю моїх повідомлень")
    save_figure(fig, "top_chats.png")


def chart_zipf(all_counter: Counter) -> None:
    items = all_counter.most_common(1000)
    if len(items) < 10:
        return

    ranks = np.arange(1, len(items) + 1)
    freqs = np.array([c for _, c in items])

    fig = create_figure(10, 6)
    ax = fig.add_subplot(111)
    ax.loglog(ranks, freqs, color=ACCENT_COLOR, linewidth=2, label="Мої частоти")

    c_max = freqs[0]
    ideal = c_max / ranks
    ax.loglog(ranks, ideal, color=ACCENT2_COLOR, linestyle="--", linewidth=1.5, label="Ідеальний закон Ціпфа (1/r)")

    ax.set_xlabel("Ранг слова (log)", color=FG_COLOR)
    ax.set_ylabel("Частота (log)", color=FG_COLOR)
    ax.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.6)
    ax.legend(facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=FG_COLOR)
    apply_style(ax, "Розподіл слів за законом Ціпфа")
    save_figure(fig, "zipf_distribution.png")


def chart_word_length(all_counter: Counter) -> None:
    lens = Counter()
    for w, c in all_counter.items():
        lens[len(w)] += c

    xs = [k for k in sorted(lens.keys()) if 1 <= k <= 18]
    ys = [lens[k] for k in xs]

    fig = create_figure(10, 5.5)
    ax = fig.add_subplot(111)
    ax.bar(xs, ys, color=ACCENT_COLOR, edgecolor=BG_COLOR)
    ax.set_xticks(xs)
    ax.set_xlabel("Довжина слова (букв)", color=FG_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
    apply_style(ax, "Розподіл слів за довжиною")
    save_figure(fig, "word_length_distribution.png")


def generate_basic_charts(chats: list[dict[str, Any]]) -> None:
    """Generates all 9 basic infographics charts."""
    print("  [•] Генерація базової інфографіки (9 графіків)...")
    all_counter = Counter()
    for ch in chats:
        for _, t in ch["messages"]:
            all_counter.update(tokenize(t))

    chart_wordcloud(all_counter)
    chart_hours(chats)
    chart_weekdays(chats)
    chart_top_words(all_counter)
    chart_years_evolution(chats)
    chart_ttr_evolution(chats)
    chart_top_chats(chats)
    chart_zipf(all_counter)
    chart_word_length(all_counter)
