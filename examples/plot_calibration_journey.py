"""
The calibration's progression, stage by stage.

Every number here is a recorded solved steady state from the calibration log --
see docs/CALIBRATION_JOURNEY.md for what happened at each stage and why. This is
presentation material: it shows where the model started (inherited, mostly US
defaults), what each intervention bought, and what remained.

Run:
    PYTHONPATH=. python examples/plot_calibration_journey.py
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# (label, short, C/Y, K/Y, revenue/Y, K_f/K)  -- None where not measured
STAGES = [
    ("Inherited\n(US defaults)", "S0", 0.671, 3.87, None, 0.015),
    ("Sourced macro\ndelta, gamma, alpha_T", "S1", 0.5651, 3.50, 0.3364, 0.015),
    ("Warm start +\ntax dials tuned", "S2", 0.5586, 3.503, 0.3337, 0.0149),
    ("Capital openness\nfrom the IIP", "S3", 0.5309, 3.614, 0.3369, 0.1654),
    ("Fiscal path:\nrate, debt, pensions", "S4", 0.5437, 3.498, 0.3372, 0.1637),
]
TARGETS = {"C/Y": 0.536, "K/Y": 3.70, "revenue/Y": 0.337, "K_f/K": 0.164}

PANELS = [
    ("C/Y", 2, "Consumption / Y", "{:.3f}"),
    ("K/Y", 3, "Capital-output K / Y", "{:.2f}"),
    ("revenue/Y", 4, "Total tax revenue / Y", "{:.4f}"),
    ("K_f/K", 5, "Foreign-owned capital K_f / K", "{:.3f}"),
]

fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
fig.suptitle(
    "OG-Japan: what each stage of the calibration bought",
    fontsize=15,
    fontweight="bold",
    y=0.98,
)

x = np.arange(len(STAGES))
labels = [s[0] for s in STAGES]

for ax, (key, idx, title, fmt) in zip(axes.flat, PANELS):
    vals = [s[idx] for s in STAGES]
    tgt = TARGETS[key]
    have = [(i, v) for i, v in enumerate(vals) if v is not None]
    xs = [i for i, _ in have]
    ys = [v for _, v in have]

    ax.axhline(tgt, color="#c0392b", lw=2, ls="--", zorder=1)
    ax.annotate(
        f"target {fmt.format(tgt)}",
        xy=(-0.38, tgt),
        color="#c0392b",
        fontsize=9,
        va="bottom",
        ha="left",
        fontweight="bold",
    )
    ax.plot(xs, ys, "-o", color="#2c3e50", lw=2.2, ms=9, zorder=3)

    for i, v in have:
        gap = v - tgt
        close = abs(gap) <= abs(0.03 * tgt)
        ax.annotate(
            f"{fmt.format(v)}\n({gap:+.3f})" if key != "K/Y" else f"{v:.3f}\n({gap:+.3f})",
            xy=(i, v),
            xytext=(0, 14 if v >= tgt else -32),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color="#1e8449" if close else "#2c3e50",
            fontweight="bold" if close else "normal",
        )

    ax.set_title(title, fontsize=11.5, fontweight="bold", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_xlim(-0.45, len(STAGES) - 0.45)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    lo, hi = min(ys + [tgt]), max(ys + [tgt])
    pad = (hi - lo) * 0.35 + 1e-9
    ax.set_ylim(lo - pad, hi + pad)

fig.text(
    0.5,
    0.015,
    "S0 inherited: 7 parameters set, the rest silently American.   "
    "S3: the IIP number that macro_params.py had been asking for since S0.",
    ha="center",
    fontsize=9.5,
    style="italic",
    color="#555",
)
fig.tight_layout(rect=[0, 0.035, 1, 0.955])
fig.savefig("docs/calibration_journey.png", dpi=150)
print("wrote docs/calibration_journey.png")
