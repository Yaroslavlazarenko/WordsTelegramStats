"""
Visualization theming and plotting utilities for Matplotlib & WordCloud.
Standardizes dark theme styling, typography, and palette across all generated charts.
"""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.core.config import (
    BG_COLOR,
    FG_COLOR,
    GRID_COLOR,
    INFOGRAPHICS_DIR,
)

# Setup DejaVu Sans font (supports Cyrillic out of the box in matplotlib)
FONT_PATH = os.path.join(
    os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"
)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False


def apply_style(ax, title: str | None = None) -> None:
    """Applies dark theme styles to a matplotlib axes."""
    ax.set_facecolor(BG_COLOR)
    for s in ax.spines.values():
        s.set_color(GRID_COLOR)
    ax.tick_params(colors=FG_COLOR)
    ax.yaxis.label.set_color(FG_COLOR)
    ax.xaxis.label.set_color(FG_COLOR)
    if title:
        ax.set_title(title, color=FG_COLOR, fontsize=15, fontweight="bold", pad=14)


def create_figure(w: float = 11, h: float = 6) -> plt.Figure:
    """Creates a stylized figure with default background."""
    return plt.figure(figsize=(w, h), facecolor=BG_COLOR)


def setup_legend(ax, **kwargs):
    """Sets up dark-themed legend for axes."""
    default_kwargs = {
        "facecolor": BG_COLOR,
        "edgecolor": GRID_COLOR,
        "labelcolor": FG_COLOR,
        "fontsize": 9,
    }
    default_kwargs.update(kwargs)
    return ax.legend(**default_kwargs)


def save_figure(fig: plt.Figure, filename: str, dpi: int = 130) -> Path:
    """Saves a figure to the infographics directory and closes it."""
    INFOGRAPHICS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = INFOGRAPHICS_DIR / filename
    fig.savefig(out_path, dpi=dpi, facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✔] {out_path}")
    return out_path
