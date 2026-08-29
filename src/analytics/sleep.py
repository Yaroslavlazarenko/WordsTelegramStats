"""
Sleep schedule and circadian rhythm analysis.
Infers bedtime, wake time, and sleep duration from longest nocturnal messaging gaps.
"""

from typing import Any

import numpy as np

from src.data.loader import parse_local_dt


def decimal_hour_to_str(decimal_hour: float) -> str:
    """Converts decimal hour (e.g. 23.5) to 'HH:MM' string (handles hours >= 24)."""
    h = int(decimal_hour) % 24
    m = int(round((decimal_hour - int(decimal_hour)) * 60))
    if m == 60:
        h = (h + 1) % 24
        m = 0
    return f"{h:02d}:{m:02d}"


def compute_sleep_schedule(chats: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Computes sleep and circadian statistics per year:
      - hour_grid (year x 24 hour heatmap)
      - avg_bedtimes, avg_wakes, avg_durations
    """
    dts = []
    for ch in chats:
        for d, _ in ch["messages"]:
            dt = parse_local_dt(d)
            if dt:
                dts.append(dt)
    dts.sort()

    if not dts:
        return {
            "years": [],
            "hour_grid": np.empty((0, 24)),
            "normalized_grid": np.empty((0, 24)),
            "stats": {},
        }

    years_set = sorted({dt.year for dt in dts})
    hour_grid = np.zeros((len(years_set), 24))
    yidx = {y: i for i, y in enumerate(years_set)}

    for dt in dts:
        hour_grid[yidx[dt.year], dt.hour] += 1

    norm_grid = hour_grid / hour_grid.max(axis=1, keepdims=True).clip(min=1)

    bedtimes = {y: [] for y in years_set}
    wakes = {y: [] for y in years_set}
    durs = {y: [] for y in years_set}

    for a, b in zip(dts, dts[1:], strict=False):
        gap = (b - a).total_seconds() / 3600
        if not (3 <= gap <= 13):
            continue
        a_h = a.hour + a.minute / 60
        b_h = b.hour + b.minute / 60
        if not (a.hour >= 19 or a.hour <= 4):
            continue
        if not (4 <= b.hour <= 16):
            continue
        # Map bedtimes after midnight to 24+ for continuous averaging
        a_val = a_h if a_h >= 12 else a_h + 24
        bedtimes[a.year].append(a_val)
        wakes[b.year].append(b_h)
        durs[a.year].append(gap)

    stats = {}
    for y in years_set:
        b_arr = np.array(bedtimes[y])
        w_arr = np.array(wakes[y])
        d_arr = np.array(durs[y])
        if len(b_arr) >= 5:
            stats[y] = {
                "n_nights": len(b_arr),
                "bed_mean": float(np.mean(b_arr)),
                "bed_median": float(np.median(b_arr)),
                "wake_mean": float(np.mean(w_arr)),
                "wake_median": float(np.median(w_arr)),
                "dur_mean": float(np.mean(d_arr)),
                "dur_median": float(np.median(d_arr)),
            }

    return {
        "years": years_set,
        "hour_grid": hour_grid,
        "normalized_grid": norm_grid,
        "stats": stats,
    }
