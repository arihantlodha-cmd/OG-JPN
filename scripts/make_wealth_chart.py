"""
Generate docs/initial_wealth.png: the share of Japan's household wealth held
by each age band at the start of the transition, from the 2019 National
Survey of Family Income, Consumption and Wealth (as used by OG-JPN) against
OG-Core's default (the terminal steady state's profile, rescaled to today's
population).

Needs a solved baseline transition with model_params.pkl and SS_vars.pkl,
for example from ``python examples/run_ogjpn_tpi.py``:

    python scripts/make_wealth_chart.py /tmp/ogjpn_tpi_data
"""

import os
import sys

import matplotlib
import numpy as np
from ogcore import utils

from ogjpn import wealth

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#52514e"
C_DATA = "#2a78d6"
C_SS = "#b4b2ad"
BANDS = [(21, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 101)]
LABELS = ["21-29", "30s", "40s", "50s", "60s", "70s", "80+"]


def band_shares(dist, ages):
    return np.array([dist[(ages >= lo) & (ages < hi)].sum() * 100 for lo, hi in BANDS])


def main(run_dir):
    p = utils.safe_read_pickle(os.path.join(run_dir, "model_params.pkl"))
    ss = utils.safe_read_pickle(os.path.join(run_dir, "SS", "SS_vars.pkl"))
    ages = p.E + np.arange(p.S) + 2

    data = wealth.get_initial_hhwealth_dist(p, ss["b_sp1"])
    proxy = ss["b_sp1"] * p.omega_S_preTP
    proxy = proxy / proxy.sum()
    s_data, s_ss = band_shares(data, ages), band_shares(proxy, ages)

    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    x = np.arange(len(BANDS))
    w = 0.38
    ax.bar(x - w / 2, s_ss, w, color=C_SS, label="OG-Core default (steady state)")
    ax.bar(x + w / 2, s_data, w, color=C_DATA, label="Japan survey data (2019)")
    for xi, v in zip(x + w / 2, s_data):
        ax.text(xi, v + 0.6, f"{v:.0f}", ha="center", color=INK, fontsize=8.5)
    for xi, v in zip(x - w / 2, s_ss):
        ax.text(xi, v + 0.6, f"{v:.0f}", ha="center", color=MUTED, fontsize=8.5)

    ax.set_title(
        "Where Japan's household wealth sits at the start of the transition",
        color=INK,
        fontsize=12.5,
        fontweight="bold",
        loc="left",
        pad=28,
    )
    ax.text(
        0,
        1.05,
        "share of household wealth by age (%): 2019 national survey vs OG-Core default",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=9,
    )
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("% of household wealth", color=MUTED, fontsize=10)
    ax.set_ylim(0, max(s_data.max(), s_ss.max()) * 1.18)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(axis="y", color="#e6e5e2", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#d8d7d3")
    ax.tick_params(colors=MUTED, labelsize=9)

    out = os.path.join(ROOT, "docs", "initial_wealth.png")
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor=SURFACE, bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ogjpn_tpi_data")
