"""
Behavioral and time analytics visualization:
  - Monthly activity timeline (timeline_monthly.png)
  - Seasonality by month (seasonality.png)
  - Night owl messaging trend (night_trend.png)
  - Active days & consecutive streak (active_days.png)
  - Message length distribution (msg_length_dist.png)
  - Sleep schedule evolution (sleep_evolution.png)
  - Inter-message gaps and burstiness (message_rhythm.png)
"""

from collections import Counter, defaultdict
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from src.analytics.sleep import compute_sleep_schedule, decimal_hour_to_str
from src.core.config import (
    ACCENT2_COLOR,
    ACCENT3_COLOR,
    ACCENT_COLOR,
    BG_COLOR,
    FG_COLOR,
    GRID_COLOR,
    MONTHS_UK,
)
from src.data.loader import parse_local_dt
from src.nlp.lemmatizer import tokenize
from src.visualization.theme import (
    apply_style,
    create_figure,
    save_figure,
    setup_legend,
)


def chart_timeline_monthly(chats: list[dict[str, Any]]) -> None:
    by_month = Counter()
    for ch in chats:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                by_month[(dt.year, dt.month)] += 1
    if not by_month:
        return
    keys = sorted(by_month)
    labels = [f"{y}-{m:02d}" for y, m in keys]
    vals = [by_month[k] for k in keys]
    x = range(len(keys))
    fig = create_figure(14, 5)
    ax = fig.add_subplot(111)
    ax.fill_between(x, vals, color=ACCENT_COLOR, alpha=0.25)
    ax.plot(x, vals, color=ACCENT_COLOR, lw=1.6)
    step = max(1, len(keys) // 16)
    ax.set_xticks(list(x)[::step])
    ax.set_xticklabels(labels[::step], rotation=45, ha="right", fontsize=8)
    apply_style(ax, "Повідомлення за місяцями за всю історію")
    ax.set_ylabel("повідомлень / місяць")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "timeline_monthly.png")


def chart_seasonality(chats: list[dict[str, Any]]) -> None:
    by_m = Counter()
    for ch in chats:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                by_m[dt.month] += 1
    vals = [by_m.get(m, 0) for m in range(1, 13)]
    fig = create_figure(11, 5)
    ax = fig.add_subplot(111)
    bars = ax.bar([MONTHS_UK[m] for m in range(1, 13)], vals, color=ACCENT3_COLOR, edgecolor=BG_COLOR)
    mx = max(vals) if vals else 0
    for b, v in zip(bars, vals, strict=False):
        if v == mx:
            b.set_color(ACCENT2_COLOR)
    apply_style(ax, "Сезонність: у які місяці я спілкуюся більше")
    ax.set_ylabel("повідомлень за всі роки")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "seasonality.png")


def chart_night_trend(chats: list[dict[str, Any]]) -> None:
    total = Counter()
    night = Counter()
    for ch in chats:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if not dt:
                continue
            total[dt.year] += 1
            if 0 <= dt.hour < 6:
                night[dt.year] += 1
    years = sorted(total)
    if not years:
        return
    pct = [night[y] / total[y] * 100 for y in years]
    fig = create_figure()
    ax = fig.add_subplot(111)
    ax.plot([str(y) for y in years], pct, "o-", color=ACCENT2_COLOR, lw=2.5)
    ax.fill_between([str(y) for y in years], pct, color=ACCENT2_COLOR, alpha=0.15)
    apply_style(ax, "Частка «нічних» повідомлень (00:00–06:00) за роками")
    ax.set_ylabel("% повідомлень уночі")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "night_trend.png")


def chart_active_days(chats: list[dict[str, Any]]) -> None:
    days_by_year = defaultdict(set)
    all_days = set()
    for ch in chats:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                dd = dt.date()
                days_by_year[dt.year].add(dd)
                all_days.add(dd)
    years = sorted(days_by_year)
    if not years:
        return
    counts = [len(days_by_year[y]) for y in years]
    streak = best = 0
    prev = None
    for dd in sorted(all_days):
        if prev and (dd - prev).days == 1:
            streak += 1
        else:
            streak = 1
        best = max(best, streak)
        prev = dd

    fig = create_figure()
    ax = fig.add_subplot(111)
    bars = ax.bar([str(y) for y in years], counts, color=ACCENT_COLOR, edgecolor=BG_COLOR)
    for b, v in zip(bars, counts, strict=False):
        ax.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom", color=FG_COLOR, fontsize=9)
    apply_style(ax, f"Активних днів у році  (всього: {len(all_days)} дн., макс. серія: {best} дн.)")
    ax.set_ylabel("днів із повідомленнями")
    ax.axhline(365, color=ACCENT3_COLOR, ls="--", lw=1, alpha=0.6)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "active_days.png")


def chart_msg_length_dist(chats: list[dict[str, Any]]) -> None:
    lengths = []
    for ch in chats:
        for _, t in ch["messages"]:
            n = len(tokenize(t))
            if n > 0:
                lengths.append(min(n, 30))
    if not lengths:
        return
    fig = create_figure()
    ax = fig.add_subplot(111)
    ax.hist(lengths, bins=range(1, 32), color=ACCENT_COLOR, edgecolor=BG_COLOR, align="left")
    med = int(np.median(lengths))
    ax.axvline(med, color=ACCENT2_COLOR, ls="--", lw=2, label=f"медіана = {med} сл.")
    apply_style(ax, "Розподіл довжини повідомлень (слів, обмежено на 30)")
    ax.set_xlabel("слів у повідомленні")
    ax.set_ylabel("повідомлень")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    setup_legend(ax)
    save_figure(fig, "msg_length_dist.png")


def chart_message_rhythm(chats: list[dict[str, Any]]) -> None:
    gaps = []
    rapid_by_year = Counter()
    pairs_by_year = Counter()
    for ch in chats:
        dts = sorted(parse_local_dt(d) for d, _ in ch["messages"] if parse_local_dt(d))
        for a, b in zip(dts, dts[1:], strict=False):
            sec = (b - a).total_seconds()
            if sec < 0:
                continue
            gaps.append(sec)
            pairs_by_year[b.year] += 1
            if sec <= 60:
                rapid_by_year[b.year] += 1

    gaps = np.array([g for g in gaps if g > 0])
    if len(gaps) == 0:
        return

    fig = plt.figure(figsize=(13, 5.2), facecolor=BG_COLOR)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 1], wspace=0.28)

    ax1 = fig.add_subplot(gs[0])
    bins = np.logspace(0, 6, 40)
    ax1.hist(gaps, bins=bins, color=ACCENT_COLOR, edgecolor=BG_COLOR)
    ax1.set_xscale("log")
    med = np.median(gaps)
    ax1.axvline(med, color=ACCENT2_COLOR, ls="--", lw=2, label=f"медіана {med:.0f} c")
    rapid_share = (gaps <= 60).mean() * 100
    apply_style(ax1, "Паузи між моїми повідомленнями поспіль")
    ax1.set_xlabel("пауза, секунд (лог)")
    ax1.set_ylabel("пар повідомлень")
    ax1.text(
        0.02, 0.92,
        f"протягом хвилини: {rapid_share:.0f}%\n(повідомлення-«черги»)",
        transform=ax1.transAxes,
        color=FG_COLOR,
        fontsize=10,
        bbox={"facecolor": BG_COLOR, "edgecolor": GRID_COLOR},
    )
    setup_legend(ax1)

    ax2 = fig.add_subplot(gs[1])
    years = sorted(pairs_by_year)
    share = [rapid_by_year[y] / pairs_by_year[y] * 100 for y in years]
    ax2.bar([str(y) for y in years], share, color=ACCENT3_COLOR, edgecolor=BG_COLOR)
    apply_style(ax2, "Частка «черг» повідомлень за роками")
    ax2.set_ylabel("% надісланих протягом хвилини")
    ax2.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_figure(fig, "message_rhythm.png")


def chart_sleep_evolution(chats: list[dict[str, Any]]) -> None:
    res = compute_sleep_schedule(chats)
    years = res["years"]
    norm = res["normalized_grid"]
    stats = res["stats"]

    if not years:
        return

    fig = plt.figure(figsize=(14, 11), facecolor=BG_COLOR)
    gs = fig.add_gridspec(3, 1, height_ratios=[1.8, 1, 1], hspace=0.45)

    ax1 = fig.add_subplot(gs[0])
    im = ax1.imshow(norm, aspect="auto", cmap="magma", origin="upper")
    ax1.set_yticks(range(len(years)))
    ax1.set_yticklabels([str(y) for y in years], fontsize=10)
    ax1.set_xticks(range(24))
    ax1.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=9)
    apply_style(ax1, "Розподіл повідомлень за годинами доби у кожному році (темне = сон)")
    ax1.tick_params(colors=FG_COLOR)
    cbar = fig.colorbar(im, ax=ax1, fraction=0.02, pad=0.02)
    cbar.ax.tick_params(colors=FG_COLOR)
    cbar.set_label("відносна активність", color=FG_COLOR)

    valid_years = [y for y in years if y in stats]
    ys = [str(y) for y in valid_years]
    bed_med = [stats[y]["bed_median"] for y in valid_years]
    wake_med = [stats[y]["wake_median"] for y in valid_years]
    dur_med = [stats[y]["dur_median"] for y in valid_years]

    ax2 = fig.add_subplot(gs[1])
    ax2.plot(ys, bed_med, "o-", color=ACCENT2_COLOR, lw=2.5, label="Відбій (медіана)")
    ax2.plot(ys, wake_med, "s-", color=ACCENT_COLOR, lw=2.5, label="Підйом (медіана)")
    for i, _y in enumerate(valid_years):
        ax2.text(i, bed_med[i] + 0.35, decimal_hour_to_str(bed_med[i]), color=ACCENT2_COLOR, ha="center", fontsize=9)
        ax2.text(i, wake_med[i] - 0.55, decimal_hour_to_str(wake_med[i]), color=ACCENT_COLOR, ha="center", fontsize=9)
    apply_style(ax2, "Оцінка часу засинання та пробудження (найдовша нічна пауза)")
    ax2.set_ylabel("година доби")
    ax2.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    setup_legend(ax2)

    ax3 = fig.add_subplot(gs[2])
    bars = ax3.bar(ys, dur_med, color=ACCENT3_COLOR, edgecolor=BG_COLOR, width=0.55)
    for b, v in zip(bars, dur_med, strict=False):
        ax3.text(b.get_x() + b.get_width() / 2, v + 0.1, f"{v:.1f} год", ha="center", color=FG_COLOR, fontsize=9)
    apply_style(ax3, "Медіанна тривалість нічної паузи (оцінка сну)")
    ax3.set_ylabel("годин")
    ax3.set_ylim(0, max(dur_med, default=10) + 1.5)
    ax3.grid(axis="y", color=GRID_COLOR, alpha=0.3)

    save_figure(fig, "sleep_evolution.png")


def generate_behavioral_charts(chats: list[dict[str, Any]]) -> None:
    """Generates all behavioral and temporal infographics."""
    print("  [•] Генерація інфографіки поведінки та часу...")
    chart_timeline_monthly(chats)
    chart_seasonality(chats)
    chart_night_trend(chats)
    chart_active_days(chats)
    chart_msg_length_dist(chats)
    chart_message_rhythm(chats)
    chart_sleep_evolution(chats)
