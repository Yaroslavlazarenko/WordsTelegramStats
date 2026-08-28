# -*- coding: utf-8 -*-
"""
Script to generate plausible, anonymous, synthetic charts for the README showcase.
Outputs high-resolution dark-themed PNG images to docs/images/.
"""

import os
import sys
import random
import math
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
from wordcloud import WordCloud

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_IMG_DIR = BASE_DIR / "docs" / "images"
DOCS_IMG_DIR.mkdir(parents=True, exist_ok=True)

# Visual styling
BG_COLOR = "#0f1117"
FG_COLOR = "#e6e6e6"
ACCENT_COLOR = "#4cc9f0"
ACCENT2_COLOR = "#f72585"
ACCENT3_COLOR = "#80ed99"
ACCENT4_COLOR = "#ffd166"
GRID_COLOR = "#2a2d36"

PALETTE = [
    "#4cc9f0", "#f72585", "#80ed99", "#ffd166", "#b794f6",
    "#ff8fab", "#06d6a0", "#ef476f", "#118ab2", "#fb8500"
]

FONT_PATH = os.path.join(
    os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"
)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False


def apply_style(ax, title=None):
    ax.set_facecolor(BG_COLOR)
    for s in ax.spines.values():
        s.set_color(GRID_COLOR)
    ax.tick_params(colors=FG_COLOR)
    ax.yaxis.label.set_color(FG_COLOR)
    ax.xaxis.label.set_color(FG_COLOR)
    if title:
        ax.set_title(title, color=FG_COLOR, fontsize=14, fontweight="bold", pad=12)


def create_figure(w=11, h=6):
    return plt.figure(figsize=(w, h), facecolor=BG_COLOR)


def setup_legend(ax, **kwargs):
    default_kwargs = {
        "facecolor": BG_COLOR,
        "edgecolor": GRID_COLOR,
        "labelcolor": FG_COLOR,
        "fontsize": 9,
    }
    default_kwargs.update(kwargs)
    return ax.legend(**default_kwargs)


def save_chart(fig, filename, dpi=140):
    out_path = DOCS_IMG_DIR / filename
    fig.savefig(out_path, dpi=dpi, facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✔] Generated demo chart: {out_path}")
    return out_path


# ==============================================================================
# 1. Wordcloud & Core Vocabulary
# ==============================================================================
def generate_wordcloud():
    frequencies = {
        "проект": 4820, "робота": 4350, "зробити": 3980, "думати": 3810, "треба": 3720,
        "завтра": 3410, "код": 3120, "баг": 2980, "реліз": 2840, "сервер": 2710,
        "зустріч": 2650, "супер": 2580, "дякую": 2490, "чудово": 2340, "питання": 2290,
        "ідея": 2210, "план": 2180, "результат": 2100, "тест": 2040, "дизайн": 1980,
        "api": 1950, "update": 1870, "сьогодні": 1820, "тиждень": 1780, "задача": 1740,
        "кава": 1690, "ноут": 1620, "комміт": 1580, "деплой": 1540, "модель": 1490,
        "архітектура": 1420, "дані": 1390, "база": 1360, "фіча": 1310, "ревʼю": 1280,
        "час": 1250, "документ": 1210, "оптимізація": 1180, "вечір": 1150, "вихідні": 1120,
        "сервіс": 1090, "клієнт": 1060, "docker": 1030, "контейнер": 990, "пайплайн": 960,
        "фреймворк": 930, "дебаг": 910, "конфіг": 880, "метрика": 860, "швидкість": 840,
        "настрій": 820, "калібрування": 790, "логіка": 770, "модуль": 750, "статус": 730
    }

    wc = WordCloud(
        width=1600,
        height=900,
        background_color=BG_COLOR,
        font_path=FONT_PATH,
        colormap="cool",
        max_words=120,
        prefer_horizontal=0.92,
        collocations=False,
        relative_scaling=0.45,
    ).generate_from_frequencies(frequencies)

    fig = create_figure(12, 6.8)
    ax = fig.add_subplot(111)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Хмара слів (Лемматизований корпус мовлення)", color=FG_COLOR, fontsize=16, fontweight="bold", pad=14)
    save_chart(fig, "wordcloud.png")


# ==============================================================================
# 2. Activity Heatmap (Hour x Day of Week)
# ==============================================================================
def generate_activity_heatmap():
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    hours = list(range(24))

    # Generate realistic activity matrix (peaks in afternoon/evening and night shifts)
    np.random.seed(42)
    matrix = np.zeros((7, 24))
    for d in range(7):
        for h in range(24):
            base = 5.0
            if 10 <= h <= 13:
                base += 35.0
            elif 14 <= h <= 18:
                base += 50.0
            elif 19 <= h <= 23:
                base += 70.0
            elif 0 <= h <= 2:
                base += 40.0
            elif 3 <= h <= 8:
                base += 2.0

            # Weekend adjustments
            if d >= 5:
                if 1 <= h <= 3:
                    base += 25.0
                if 8 <= h <= 12:
                    base *= 0.6
                if 15 <= h <= 23:
                    base *= 1.2

            matrix[d, h] = base * np.random.uniform(0.85, 1.15)

    fig = create_figure(12, 5.5)
    ax = fig.add_subplot(111)
    cax = ax.imshow(matrix, cmap="viridis", aspect="auto", interpolation="nearest")

    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}" for h in hours], fontsize=9)
    ax.set_yticks(range(7))
    ax.set_yticklabels(days, fontsize=10, fontweight="bold")

    cbar = fig.colorbar(cax, ax=ax, orientation="vertical", pad=0.02)
    cbar.ax.tick_params(colors=FG_COLOR)
    cbar.set_label("Інтенсивність повідомлень", color=FG_COLOR, fontsize=10)

    apply_style(ax, "Теплова карта активності: Години доби × Дні тижня")
    ax.set_xlabel("Година доби (місцевий час)")
    ax.set_ylabel("День тижня")
    save_chart(fig, "activity_heatmap.png")


# ==============================================================================
# 3. Monthly Timeline & Activity
# ==============================================================================
def generate_timeline_monthly():
    months = []
    vals = []
    base_date = datetime(2019, 1, 1)

    # 2019 to 2026 (92 months)
    for i in range(92):
        dt = base_date + timedelta(days=i * 30.4)
        m_str = dt.strftime("%Y-%m")
        months.append(m_str)
        # S-curve growth + oscillations
        growth = 1200 + 4500 * (1 / (1 + math.exp(- (i - 45) / 14)))
        season = 600 * math.sin(i * math.pi / 6)
        noise = random.uniform(-300, 300)
        val = max(300, int(growth + season + noise))
        vals.append(val)

    x = range(len(months))
    fig = create_figure(13, 4.8)
    ax = fig.add_subplot(111)
    ax.fill_between(x, vals, color=ACCENT_COLOR, alpha=0.25)
    ax.plot(x, vals, color=ACCENT_COLOR, lw=2.0, label="Обсяг повідомлень / міс.")

    step = 8
    ax.set_xticks(list(x)[::step])
    ax.set_xticklabels(months[::step], rotation=35, ha="right", fontsize=9)
    apply_style(ax, "Щомісячна динаміка вихідних повідомлень (2019–2026)")
    ax.set_ylabel("Кількість повідомлень")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    setup_legend(ax)
    save_chart(fig, "timeline_monthly.png")


# ==============================================================================
# 4. Sleep Evolution
# ==============================================================================
def generate_sleep_evolution():
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    # Bedtime shifting later
    bedtimes = [23.4, 23.8, 0.4, 1.6, 2.2, 2.5, 2.9, 3.1]  # 23:24 -> 03:06
    # Waketimes
    waketimes = [8.5, 8.7, 9.2, 9.8, 10.1, 10.4, 10.8, 11.0]
    # Sleep duration
    durations = [(w - (b if b < 12 else b - 24)) for b, w in zip(bedtimes, waketimes)]

    fig = create_figure(12, 5.5)
    ax1 = fig.add_subplot(111)

    ys = [str(y) for y in years]
    ax1.plot(ys, bedtimes, "o-", color=ACCENT2_COLOR, lw=2.5, label="Час відбою (засинання)")
    ax1.plot(ys, waketimes, "s-", color=ACCENT_COLOR, lw=2.5, label="Час підйому (пробудження)")

    # Format Y axis for clock
    ax1.set_yticks([0, 2, 4, 6, 8, 10, 12, 23, 24])
    ax1.set_yticklabels(["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "23:00", "24:00"], fontsize=9)

    apply_style(ax1, "Реконструкція біоритмів: Еволюція часу сну за роками")
    ax1.set_ylabel("Година доби (HH:MM)")
    ax1.grid(color=GRID_COLOR, alpha=0.3)
    setup_legend(ax1, loc="upper left")

    # Secondary axis for duration
    ax2 = ax1.twinx()
    ax2.plot(ys, durations, "^--", color=ACCENT3_COLOR, lw=2, label="Тривалість сну (год)")
    ax2.set_ylabel("Середня тривалість (годин)", color=ACCENT3_COLOR, fontsize=10)
    ax2.tick_params(colors=ACCENT3_COLOR)
    ax2.set_ylim(6.0, 11.0)
    setup_legend(ax2, loc="lower right")

    save_chart(fig, "sleep_evolution.png")


# ==============================================================================
# 5. Vocabulary Timeline (Honest vs Verified)
# ==============================================================================
def generate_vocab_timeline():
    tokens = [25000, 75000, 150000, 240000, 320000, 410000, 500000]
    total_raw = [4200, 10500, 18200, 27100, 35400, 44200, 52000]
    verified_2plus = [2100, 5800, 10400, 14900, 18800, 22400, 25800]
    dictionary_ru_uk = [1800, 4900, 8900, 12800, 16100, 19200, 22100]

    fig = create_figure(12, 5.5)
    ax = fig.add_subplot(111)

    x_k = [t / 1000 for t in tokens]
    ax.plot(x_k, total_raw, "--", color="#6c757d", lw=1.8, label="Сирий облік лем (включає одруківки та одноразовий сленг)")
    ax.plot(x_k, verified_2plus, "o-", color=ACCENT_COLOR, lw=2.4, label="Підтверджений активний словник (вжито ≥2 разів)")
    ax.plot(x_k, dictionary_ru_uk, "s-", color=ACCENT3_COLOR, lw=2.4, label="Словниковий запас (нормативні слова UA/EN)")

    apply_style(ax, "Зростання активного словникового запасу (Закон Гіпса)")
    ax.set_xlabel("Загальна кількість набраних слів (тис. токенів)")
    ax.set_ylabel("Кількість унікальних лем")
    ax.grid(color=GRID_COLOR, alpha=0.3)
    setup_legend(ax, loc="upper left")
    save_chart(fig, "vocab_timeline.png")


# ==============================================================================
# 6. Laughter Styles Evolution
# ==============================================================================
def generate_laughter_evolution():
    years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]

    classic = [55, 48, 32, 20, 14, 9, 6, 4]      # хаха
    keyboard = [12, 18, 35, 52, 60, 68, 73, 76]  # хпхвх / пхвх
    hehe = [22, 21, 19, 16, 14, 12, 11, 10]      # хехе / хіхі
    short_hm = [8, 9, 10, 8, 7, 6, 6, 6]        # хмх
    other = [3, 4, 4, 4, 5, 5, 4, 4]

    fig = create_figure(12, 5.5)
    ax = fig.add_subplot(111)

    ax.stackplot(
        years, classic, keyboard, hehe, short_hm, other,
        labels=["Класичний (ха-ха / ахах)", "Клавіатурний (хпхвх / пхвх)", "Хехе / Хіхі", "Короткий (хмх)", "Інші форми"],
        colors=[ACCENT_COLOR, ACCENT2_COLOR, ACCENT3_COLOR, ACCENT4_COLOR, "#b794f6"],
        alpha=0.85
    )

    apply_style(ax, "Еволюція вираження сміху в листуванні (% частоти)")
    ax.set_ylabel("Частка у відсотках (%)")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    setup_legend(ax, loc="upper left")
    save_chart(fig, "laughter_evolution.png")


# ==============================================================================
# 7. Streamgraph: Attention to Contacts Across Years
# ==============================================================================
def generate_streamgraph_chats():
    years = np.array([2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026])
    contacts = [
        "Олександр (Tech Lead)",
        "Марія (Design)",
        "Dev Team Chat",
        "Дмитро",
        "Катерина",
        "Gaming Squad",
        "Андрій",
        "Інші (50+ чатів)"
    ]

    # Synthetic stacked proportions
    v1 = np.array([5, 12, 25, 30, 28, 22, 18, 15])
    v2 = np.array([0, 0, 10, 18, 24, 26, 25, 22])
    v3 = np.array([0, 5, 15, 22, 25, 28, 30, 32])
    v4 = np.array([30, 28, 20, 12, 8, 5, 4, 3])
    v5 = np.array([25, 22, 15, 8, 4, 3, 2, 2])
    v6 = np.array([10, 12, 8, 6, 5, 7, 9, 12])
    v7 = np.array([15, 10, 4, 2, 2, 3, 4, 5])
    v8 = np.array([15, 11, 3, 2, 4, 6, 8, 9])

    data = np.vstack([v1, v2, v3, v4, v5, v6, v7, v8])

    fig = create_figure(12, 5.8)
    ax = fig.add_subplot(111)

    ax.stackplot(
        [str(y) for y in years], data,
        labels=contacts,
        colors=PALETTE[:len(contacts)],
        alpha=0.88
    )

    apply_style(ax, "Стрімграф: Перерозподіл соціальної уваги за роками (% обсягу)")
    ax.set_ylabel("Частка повідомлень (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    setup_legend(ax, loc="upper right", bbox_to_anchor=(1.28, 1.0))
    save_chart(fig, "streamgraph_chats.png")


# ==============================================================================
# 8. Chat Fingerprints (TF-IDF distinctive words)
# ==============================================================================
def generate_chat_fingerprints():
    chats = [
        ("Олександр (Tech Lead)", ["архітектура", "деплой", "пайплайн", "модель", "реліз", "тести"]),
        ("Марія (Design Sync)", ["палітра", "макет", "шрифт", "ui/ux", "анімація", "компоненти"]),
        ("Dev Team Chat", ["мердж", "ревʼю", "комміт", "багфікс", "стейджинг", "дока"]),
        ("Gaming Squad", ["діскорд", "катка", "войс", "стім", "рейд", "тіммейт"]),
        ("Family & Home", ["завтра", "приїду", "вечеря", "потяг", "купити", "вітання"]),
        ("Дмитро", ["зустріч", "кава", "проект", "обговорити", "дзвінок", "ідея"])
    ]

    fig = create_figure(12, 6.5)

    for i, (name, words) in enumerate(chats):
        ax = fig.add_subplot(2, 3, i + 1)
        weights = [random.uniform(0.4, 0.95) for _ in words]
        weights.sort(reverse=True)

        y_pos = range(len(words))
        bars = ax.barh(y_pos, weights, color=PALETTE[i % len(PALETTE)], alpha=0.85, edgecolor=BG_COLOR)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(words, fontsize=9, fontweight="bold", color=FG_COLOR)
        ax.invert_yaxis()
        apply_style(ax, name)
        ax.set_xticks([])
        ax.set_facecolor("#151821")

    fig.suptitle("Лінґвістичні відбитки чатів (Унікальні TF-IDF леми діалогів)", color=FG_COLOR, fontsize=15, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    save_chart(fig, "chat_fingerprint.png")


# ==============================================================================
# 9. Relationships Timeline (Lifecycles)
# ==============================================================================
def generate_relationships_timeline():
    contacts = [
        "Олександр (Tech Lead)", "Марія", "Dev Team Chat", "Дмитро", "Катерина",
        "Gaming Squad", "Андрій", "Книжковий клуб", "Богдан", "University Group"
    ]

    # 2019-2026 months (96 periods)
    np.random.seed(101)
    matrix = np.zeros((len(contacts), 96))

    # Alex: active 2021-2026
    matrix[0, 24:] = np.random.uniform(30, 90, 72)
    # Maria: active 2022-2026
    matrix[1, 38:] = np.random.uniform(40, 100, 58)
    # Dev Team: active 2021-2026
    matrix[2, 30:] = np.random.uniform(50, 120, 66)
    # Dmitry: 2019-2023 active, then quiet
    matrix[3, :55] = np.random.uniform(20, 80, 55)
    # Kateryna: 2019-2022 active
    matrix[4, 5:45] = np.random.uniform(30, 85, 40)
    # Gaming: cyclical
    matrix[5, :] = [random.uniform(10, 60) if (i % 12 > 4) else 2 for i in range(96)]
    # Andriy: 2023-2026
    matrix[6, 50:] = np.random.uniform(20, 70, 46)
    # Book club: 2024-2026
    matrix[7, 62:] = np.random.uniform(15, 55, 34)
    # Bogdan: 2019-2021
    matrix[8, :30] = np.random.uniform(25, 75, 30)
    # University: 2019-2022
    matrix[9, :42] = np.random.uniform(40, 95, 42)

    fig = create_figure(13, 5.5)
    ax = fig.add_subplot(111)
    cax = ax.imshow(matrix, cmap="plasma", aspect="auto", interpolation="nearest")

    ax.set_yticks(range(len(contacts)))
    ax.set_yticklabels(contacts, fontsize=10, fontweight="bold")

    # Year ticks
    year_ticks = [0, 12, 24, 36, 48, 60, 72, 84]
    year_labels = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    ax.set_xticks(year_ticks)
    ax.set_xticklabels(year_labels, fontsize=10)

    cbar = fig.colorbar(cax, ax=ax, orientation="vertical", pad=0.02)
    cbar.ax.tick_params(colors=FG_COLOR)
    cbar.set_label("Інтенсивність листування", color=FG_COLOR, fontsize=10)

    apply_style(ax, "Життєвий цикл стосунків та діалогів у часі")
    save_chart(fig, "relationships_timeline.png")


# ==============================================================================
# 10. Speech Similarity Clustering (Dendrogram)
# ==============================================================================
def generate_speech_clustering():
    labels = [
        "Tech Lead (Work)", "Dev Team (Work)", "Dev Sync (Work)",
        "Марія (Close friend)", "Катерина (Close friend)",
        "Gaming Squad (Casual)", "Gaming Group (Casual)",
        "Family (Personal)", "University Friends (Old)", "Дмитро (Old friend)"
    ]
    n = len(labels)

    # Build distance matrix with natural clusters
    np.random.seed(55)
    dist = np.random.uniform(0.6, 0.9, (n, n))
    np.fill_diagonal(dist, 0)

    # Cluster 1: Work (0, 1, 2)
    for i in [0, 1, 2]:
        for j in [0, 1, 2]:
            if i != j:
                dist[i, j] = dist[j, i] = random.uniform(0.12, 0.25)

    # Cluster 2: Close friends (3, 4)
    dist[3, 4] = dist[4, 3] = random.uniform(0.18, 0.28)

    # Cluster 3: Gaming (5, 6)
    dist[5, 6] = dist[6, 5] = random.uniform(0.15, 0.26)

    # Cluster 4: Old friends (8, 9)
    dist[8, 9] = dist[9, 8] = random.uniform(0.22, 0.32)

    # Symmetric
    dist = (dist + dist.T) / 2
    np.fill_diagonal(dist, 0)

    condensed = squareform(dist)
    Z = linkage(condensed, method="ward")

    fig = create_figure(12, 5.5)
    ax = fig.add_subplot(111)

    dendrogram(
        Z,
        labels=labels,
        leaf_rotation=30,
        leaf_font_size=10,
        ax=ax,
        color_threshold=0.5,
        above_threshold_color=ACCENT_COLOR
    )

    apply_style(ax, "Кластеризація співрозмовників за подібністю вашого словника")
    ax.set_ylabel("Лінгвістична дистанція (Косинусна відстань)")
    ax.grid(axis="y", color=GRID_COLOR, alpha=0.3)
    save_chart(fig, "speech_clustering.png")


# ==============================================================================
# 11. Top N-Grams
# ==============================================================================
def generate_ngrams():
    bigrams = [
        ("треба зробити", 840), ("я думаю", 790), ("до речі", 680), ("добрий день", 610),
        ("може бути", 570), ("все добре", 530), ("дай знати", 480), ("на звʼязку", 450)
    ]
    trigrams = [
        ("якщо я правильно", 380), ("я маю на", 340), ("маю на увазі", 330),
        ("все буде добре", 290), ("дай мені знати", 260), ("треба буде подивитись", 240),
        ("з іншого боку", 210), ("як справи у", 190)
    ]

    fig = create_figure(12, 5.5)

    ax1 = fig.add_subplot(121)
    labels1 = [x[0] for x in bigrams]
    counts1 = [x[1] for x in bigrams]
    y1 = range(len(labels1))
    ax1.barh(y1, counts1, color=ACCENT_COLOR, alpha=0.85, edgecolor=BG_COLOR)
    ax1.set_yticks(y1)
    ax1.set_yticklabels(labels1, fontsize=9, fontweight="bold", color=FG_COLOR)
    ax1.invert_yaxis()
    apply_style(ax1, "Топ біграм (2 слова)")
    ax1.set_xlabel("Кількість вживань")
    ax1.grid(axis="x", color=GRID_COLOR, alpha=0.3)

    ax2 = fig.add_subplot(122)
    labels2 = [x[0] for x in trigrams]
    counts2 = [x[1] for x in trigrams]
    y2 = range(len(labels2))
    ax2.barh(y2, counts2, color=ACCENT2_COLOR, alpha=0.85, edgecolor=BG_COLOR)
    ax2.set_yticks(y2)
    ax2.set_yticklabels(labels2, fontsize=9, fontweight="bold", color=FG_COLOR)
    ax2.invert_yaxis()
    apply_style(ax2, "Топ триграм (3 слова)")
    ax2.set_xlabel("Кількість вживань")
    ax2.grid(axis="x", color=GRID_COLOR, alpha=0.3)

    fig.suptitle("Стійкі мовні звороти та колокації (N-грами)", color=FG_COLOR, fontsize=15, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    save_chart(fig, "ngrams.png")


# ==============================================================================
# 12. POS Evolution (Parts of Speech)
# ==============================================================================
def generate_pos_evolution():
    years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]

    verbs = [32.0, 31.2, 30.1, 28.5, 27.2, 26.4, 25.8, 25.1]
    nouns = [24.5, 25.4, 26.8, 28.1, 29.5, 30.8, 31.4, 32.2]
    adjectives = [10.2, 10.8, 11.5, 12.0, 12.8, 13.5, 14.1, 14.6]
    adverbs = [14.1, 13.8, 13.2, 12.8, 12.4, 11.9, 11.5, 11.2]
    pronouns = [19.2, 18.8, 18.4, 18.6, 18.1, 17.4, 17.2, 16.9]

    fig = create_figure(12, 5.5)
    ax = fig.add_subplot(111)

    ax.plot(years, verbs, "o-", color=ACCENT_COLOR, lw=2.4, label="Дієслова (Verbs — дія, процеси)")
    ax.plot(years, nouns, "s-", color=ACCENT2_COLOR, lw=2.4, label="Іменники (Nouns — предмети, сутності)")
    ax.plot(years, adjectives, "^-", color=ACCENT3_COLOR, lw=2.4, label="Прикметники (Adjectives — опис)")
    ax.plot(years, adverbs, "d-", color=ACCENT4_COLOR, lw=2.0, label="Прислівники (Adverbs)")
    ax.plot(years, pronouns, "v-", color="#b794f6", lw=2.0, label="Займенники (Pronouns)")

    apply_style(ax, "Морфологічний профіль: Еволюція частин мови за роками")
    ax.set_ylabel("Частка токенів у мовленні (%)")
    ax.grid(color=GRID_COLOR, alpha=0.3)
    setup_legend(ax, loc="upper right")
    save_chart(fig, "pos_evolution.png")


# ==============================================================================
# 13. Zipf Law
# ==============================================================================
def generate_zipf_law():
    ranks = np.arange(1, 8000)
    # Ideal Zipf: C / rank^1.0
    ideal = 80000 / (ranks ** 1.0)
    # Observed: slope ~ -1.02
    noise = np.random.normal(1, 0.05, len(ranks))
    observed = (82000 / (ranks ** 1.018)) * noise
    observed = np.sort(observed)[::-1]

    fig = create_figure(11, 5.5)
    ax = fig.add_subplot(111)

    ax.loglog(ranks, ideal, "--", color=ACCENT3_COLOR, lw=2.0, label="Ідеальний закон Ціпфа (нахил s = -1.000)")
    ax.loglog(ranks, observed, "-", color=ACCENT_COLOR, lw=2.2, label="Ваш корпус мовлення (нахил s = -1.018, R² = 0.994)")

    apply_style(ax, "Закон Ціпфа: Рангочастотний розподіл лем (Log-Log scale)")
    ax.set_xlabel("Ранг слова (1 = найчастіше)")
    ax.set_ylabel("Абсолютна частота вживання")
    ax.grid(True, which="both", color=GRID_COLOR, alpha=0.3)
    setup_legend(ax, loc="upper right")
    save_chart(fig, "zipf_law.png")


# ==============================================================================
# 14. Summary Dashboard Mockup Banner
# ==============================================================================
def generate_dashboard_preview():
    fig = create_figure(14, 7.5)

    # 4 Key stat cards on top
    cards = [
        ("400k+", "Чистих повідомлень", ACCENT_COLOR),
        ("52k / 22k", "Лем (всього / словникових)", ACCENT3_COLOR),
        ("130+", "Особистих діалогів", ACCENT2_COLOR),
        ("8 років", "Історії мовлення (2019–2026)", ACCENT4_COLOR)
    ]

    for i, (val, title, col) in enumerate(cards):
        ax_card = fig.add_axes([0.05 + i * 0.235, 0.80, 0.21, 0.15])
        ax_card.set_facecolor("#171b26")
        for s in ax_card.spines.values():
            s.set_color(col)
            s.set_linewidth(1.5)
        ax_card.set_xticks([])
        ax_card.set_yticks([])
        ax_card.text(0.5, 0.62, val, color=col, fontsize=20, fontweight="bold", ha="center", va="center")
        ax_card.text(0.5, 0.25, title, color=FG_COLOR, fontsize=10, ha="center", va="center")

    # Lower Left: Volume by year
    ax_left = fig.add_axes([0.05, 0.12, 0.42, 0.58])
    years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    volumes = [3, 40, 105, 215, 280, 240, 410, 360]
    bars = ax_left.bar(years, volumes, color=ACCENT_COLOR, edgecolor=BG_COLOR, alpha=0.85)
    for b in bars:
        ax_left.text(b.get_x() + b.get_width()/2, b.get_height() + 8, f"{int(b.get_height())}k", ha="center", color=FG_COLOR, fontsize=8)
    apply_style(ax_left, "Обсяг слів за роками (тис. слів)")
    ax_left.grid(axis="y", color=GRID_COLOR, alpha=0.3)

    # Lower Right: Hourly activity
    ax_right = fig.add_axes([0.53, 0.12, 0.42, 0.58])
    hours = list(range(24))
    act = [12, 8, 4, 1, 0, 0, 1, 3, 8, 18, 28, 35, 42, 38, 45, 52, 58, 62, 70, 75, 80, 78, 60, 32]
    ax_right.plot(hours, act, "o-", color=ACCENT2_COLOR, lw=2.2)
    ax_right.fill_between(hours, act, color=ACCENT2_COLOR, alpha=0.25)
    ax_right.set_xticks([0, 4, 8, 12, 16, 20, 23])
    ax_right.set_xticklabels(["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:00"])
    apply_style(ax_right, "Добовий профіль активності")
    ax_right.grid(axis="y", color=GRID_COLOR, alpha=0.3)

    save_chart(fig, "dashboard_preview.png")


def main():
    print("Generating plausible synthetic showcase charts for README...")
    generate_wordcloud()
    generate_activity_heatmap()
    generate_timeline_monthly()
    generate_sleep_evolution()
    generate_vocab_timeline()
    generate_laughter_evolution()
    generate_streamgraph_chats()
    generate_chat_fingerprints()
    generate_relationships_timeline()
    generate_speech_clustering()
    generate_ngrams()
    generate_pos_evolution()
    generate_zipf_law()
    generate_dashboard_preview()
    print("All demo charts generated successfully in docs/images/!")


if __name__ == "__main__":
    main()
