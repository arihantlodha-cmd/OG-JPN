"""
OG-Japan calibration-fit figure: how close the solved steady state lands to the
actual Japanese economy.

Reads a solved steady state and plots it against the Japanese data targets, with
a source for every target. Three panels, each answering a different question:

  A  Did we collect the right taxes?      (the sharpest validator)
  B  Does the economy look like Japan?    (structural moments)
  C  Why does Japan need a negative rate? (the r - g arithmetic)

Run after a solve:
    PYTHONPATH=. python examples/validate_japan.py
    PYTHONPATH=. python examples/plot_calibration_fit.py

Style note: OG-Core ships ``OGcorePlots.mplstyle``, whose structural choices
(no spines, faint dotted grid) are used here. Its colour cycle is not -- the
cycle is ``brgcmykg``, which puts red and green adjacent and is unreadable for
the ~8% of men with red-green colour vision deficiency. This figure's whole job
is distinguishing two series, so it uses a blue/orange pair verified to separate
under protanopia, deuteranopia and tritanopia.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from ogcore import utils

# Two categorical series, fixed order, never cycled. Verified CVD separation
# dE 24.7 (protan) / 32.7 (tritan) against a light surface.
MODEL = "#2a78d6"
ACTUAL = "#eb6834"
INK = "#1a1a19"
INK_MUTED = "#6b6b68"
GOOD = "#0ca30c"

# Japan data targets. Every one sourced; see docs/CALIBRATION_AUDIT.md.
REVENUE_TARGETS = [
    ("Social insurance", "payroll_tax_revenue", 0.1318),
    ("Consumption + indirect", "cons_tax_revenue", 0.0682),
    ("Personal income", "iit_revenue", 0.0617),
    ("Corporate income", "business_tax_revenue", 0.0470),
    ("Property / wealth", "wealth_tax_revenue", 0.0221),
    ("Inheritance", "bequest_tax_revenue", 0.0055),
]

STRUCTURAL_TARGETS = [
    ("Foreign-held debt  $D_f/D$", 0.137, "MOF, Mar 2026"),
    ("Capital-output  $K/Y$", 3.70, "Penn World Table"),
    ("Pension outlays / GDP", 0.093, "OECD PaG 2023"),
    ("Consumption / GDP", 0.536, "World Bank 2023"),
]


def _s(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def _panel_a(ax, ss, Y):
    """Revenue by instrument: model vs Japan, in percent of GDP."""
    labels = [lab for lab, _, _ in REVENUE_TARGETS]
    model = [100 * _s(ss[key]) / Y for _, key, _ in REVENUE_TARGETS]
    actual = [100 * tgt for _, _, tgt in REVENUE_TARGETS]

    y = np.arange(len(labels))[::-1]
    h = 0.36
    gap = 0.02  # 2px-equivalent surface gap between adjacent bars

    ax.barh(y + (h + gap) / 2, model, height=h, color=MODEL, zorder=3)
    ax.barh(y - (h + gap) / 2, actual, height=h, color=ACTUAL, zorder=3)

    for yi, m, a in zip(y, model, actual):
        ax.text(m + 0.15, yi + (h + gap) / 2, f"{m:.2f}", va="center",
                fontsize=8, color=INK)
        ax.text(a + 0.15, yi - (h + gap) / 2, f"{a:.2f}", va="center",
                fontsize=8, color=INK_MUTED)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("percent of GDP", fontsize=9)
    ax.set_xlim(0, max(max(model), max(actual)) * 1.22)
    # Computed, not hard-coded: a stale claim in a figure caption is exactly
    # the doc/number drift the value-pinning tests exist to prevent.
    worst = max(abs(m - a) for m, a in zip(model, actual))
    ax.set_title(
        "A   Revenue by instrument\n"
        f"every line within {worst:.2f}pp of GDP of its target",
        fontsize=10, loc="left", color=INK, pad=10,
    )
    ax.legend(
        handles=[Patch(color=MODEL, label="OG-JPN model"),
                 Patch(color=ACTUAL, label="Japan actual")],
        loc="lower right", frameon=False, fontsize=8.5,
    )


def _panel_b(ax, ss, Y):
    """Structural moments as model/target, so mixed units share one axis."""
    model_vals = [
        _s(ss["D_f"]) / _s(ss["D"]),
        _s(ss["K"]) / Y,
        _s(ss["agg_pension_outlays"]) / Y,
        _s(ss["C"]) / Y,
    ]
    labels = [lab for lab, _, _ in STRUCTURAL_TARGETS]
    targets = [t for _, t, _ in STRUCTURAL_TARGETS]
    srcs = [s for _, _, s in STRUCTURAL_TARGETS]
    ratios = [m / t for m, t in zip(model_vals, targets)]

    y = np.arange(len(labels))[::-1]
    ax.axvline(1.0, color=INK, lw=1, zorder=2)
    ax.axvspan(0.95, 1.05, color=GOOD, alpha=0.07, zorder=1)

    for yi, r in zip(y, ratios):
        exact = abs(r - 1.0) < 0.012
        # A perfect hit puts both dots on the same point. Nudge them apart so
        # the reader sees two series meeting, not one series plotted.
        dy = 0.085 if exact else 0.0
        ax.plot([1.0, r], [yi, yi], color=INK_MUTED, lw=1.5, zorder=3)
        ax.plot([r], [yi + dy], "o", ms=9, color=MODEL, zorder=4,
                markeredgecolor="white", markeredgewidth=1.5)
        ax.plot([1.0], [yi - dy], "o", ms=9, color=ACTUAL, zorder=4,
                markeredgecolor="white", markeredgewidth=1.5)

    for yi, r, m, t, src in zip(y, ratios, model_vals, targets, srcs):
        off = 0.035 if r >= 1.0 else -0.035
        ax.text(r + off, yi, f"{m:.3g} vs {t:.3g}",
                va="center", ha="left" if r >= 1.0 else "right",
                fontsize=8, color=INK)
        ax.text(0.0, yi - 0.27, src, va="center", ha="left",
                fontsize=7, color=INK_MUTED, transform=ax.get_yaxis_transform())

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("model ÷ Japan actual   (1.0 = exact)", fontsize=9)
    ax.set_xlim(0.55, 1.55)
    ax.set_ylim(-0.75, len(labels) - 0.4)
    ax.set_title(
        "B   Structural moments\n"
        "shaded band = within 5% of the data",
        fontsize=10, loc="left", color=INK, pad=10,
    )


def _panel_c(ax, ss, p):
    """The r - g arithmetic: why the interest assumption decides Japan."""
    g = float(np.exp(np.asarray(p.g_y).flat[0])
              * (1 + np.asarray(p.g_n_ss).flat[0]) - 1)
    D = 1.0  # debt_ratio_ss

    cases = [
        ("OG-Core default\nwedge", 0.025, MODEL),
        ("OG-JPN\n(model floor)", _s(ss["r_gov"]), MODEL),
        ("Japan actual\neffective rate", -0.006, ACTUAL),
    ]
    names = [c[0] for c in cases]
    pbstar = [100 * (r - g) / (1 + g) * D for _, r, _ in cases]
    colors = [c[2] for c in cases]

    x = np.arange(len(cases))
    ax.bar(x, pbstar, width=0.55, color=colors, zorder=3)
    ax.axhline(0, color=INK, lw=1, zorder=4)

    japan_actual_pb = -1.79
    ax.axhline(japan_actual_pb, color=ACTUAL, lw=1.5, ls="--", zorder=2)
    ax.text(len(cases) - 0.5, japan_actual_pb - 0.28,
            "Japan's actual primary balance, 2024  (−1.79)",
            ha="right", va="top", fontsize=8, color=ACTUAL)

    for xi, v, (_, r, _) in zip(x, pbstar, cases):
        ax.text(xi, v + (0.13 if v >= 0 else -0.13), f"{v:+.2f}",
                ha="center", va="bottom" if v >= 0 else "top",
                fontsize=9, color=INK)
        ax.text(xi, -3.20, f"$r_{{gov}}$ = {100*r:+.1f}%",
                ha="center", fontsize=8, color=INK_MUTED)

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8.5)
    ax.set_ylabel("primary balance required to hold debt\n(percent of GDP)",
                  fontsize=9)
    ax.set_ylim(-3.6, 3.6)
    ax.set_title(
        f"C   Why the rate decides Japan\n"
        f"at g = {100*g:+.2f}%, debt 1.0×GDP",
        fontsize=10, loc="left", color=INK, pad=10,
    )


def main(ss_dir="/tmp/ogjpn_validate", out="docs/calibration_fit.png"):
    ss = utils.safe_read_pickle(os.path.join(ss_dir, "SS", "SS_vars.pkl"))
    p = utils.safe_read_pickle(os.path.join(ss_dir, "model_params.pkl"))
    Y = _s(ss["Y"])

    fig = plt.figure(figsize=(15, 5.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.22, 1.05, 0.80], wspace=0.50)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]

    for ax in axes:
        ax.grid(axis="x", color=INK, ls=":", lw=0.5, alpha=0.2, zorder=0)
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.tick_params(length=0, colors=INK_MUTED, labelsize=8.5)

    _panel_a(axes[0], ss, Y)
    _panel_b(axes[1], ss, Y)
    axes[2].grid(axis="x", visible=False)
    axes[2].grid(axis="y", color=INK, ls=":", lw=0.5, alpha=0.2, zorder=0)
    _panel_c(axes[2], ss, p)

    fig.suptitle(
        "OG-Japan calibration fit — solved steady state vs the Japanese economy",
        fontsize=12.5, x=0.008, ha="left", y=0.99, color=INK,
    )
    fig.text(
        0.008, 0.008,
        "Sources: OECD Revenue Statistics 2025 (2023); OECD Pensions at a Glance 2023; "
        "OECD Economic Outlook; MOF Japan JGB/T-Bill holders Mar 2026; "
        "Penn World Table; World Bank WDI.  Model: ogcore 0.19.0 on UN WPP demographics.",
        fontsize=7, color=INK_MUTED, ha="left",
    )
    fig.subplots_adjust(top=0.78, bottom=0.19, left=0.125, right=0.975)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.savefig(out, dpi=200, facecolor="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
