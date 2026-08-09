"""
Generate docs/japan_aging.png: Japan's population age distribution in 1990
vs 2030, from the UN World Population Prospects data in Data/JPN. Shows the
aging that drives OG-Japan's high pension burden.
"""

import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#52514e"
C_1990 = "#2a78d6"  # blue (categorical slot 1)
C_2030 = "#008300"  # green (categorical slot 2)


def share_by_age(df, year):
    d = df[df.year == year].sort_values("age")
    return d.age.values, d.value.values / d.value.values.sum() * 100


def main():
    df = pd.read_csv(os.path.join(ROOT, "Data", "JPN", "UN_population_data.csv"))
    a90, s90 = share_by_age(df, 1990)
    a30, s30 = share_by_age(df, 2030)

    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.fill_between(a90, s90, color=C_1990, alpha=0.10, linewidth=0)
    ax.fill_between(a30, s30, color=C_2030, alpha=0.10, linewidth=0)
    ax.plot(a90, s90, color=C_1990, linewidth=2.0)
    ax.plot(a30, s30, color=C_2030, linewidth=2.0)

    # direct labels (identity without relying on a legend box)
    ax.text(a90[np.argmax(s90)], max(s90) + 0.03, "1990",
            color=C_1990, fontsize=11, fontweight="bold", ha="center")
    ax.text(82, s30[82] + 0.06, "2030", color=C_2030, fontsize=11,
            fontweight="bold", ha="center")

    ax.set_title("Japan is aging: population by age, 1990 vs 2030",
                 color=INK, fontsize=13, fontweight="bold", loc="left", pad=30)
    ax.text(0, 1.05, "share of population at each age (%), UN World Population Prospects",
            transform=ax.transAxes, color=MUTED, fontsize=9.5)
    ax.set_xlabel("age", color=MUTED, fontsize=10)
    ax.set_ylabel("% of population", color=MUTED, fontsize=10)

    ax.set_xlim(0, 99)
    ax.set_ylim(0, max(s90.max(), s30.max()) * 1.15)
    ax.grid(axis="y", color="#e6e5e2", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#d8d7d3")
    ax.tick_params(colors=MUTED, labelsize=9)

    out = os.path.join(ROOT, "docs", "japan_aging.png")
    fig.tight_layout()
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
