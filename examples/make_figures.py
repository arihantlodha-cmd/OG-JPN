"""
Generate the policy-results summary figure for OG-Japan.

Produces docs/policy_results.png, a two-panel summary of the long-run
(steady-state) effects of the three reforms, grouped by what each one does:
the pension-age and replacement-rate reforms cut the public pension burden,
and the consumption tax raises government revenue.

The values are the steady-state results reported in docs/results_*.md (real
Japanese demographics, first-pass macro and tax calibration). They are kept
here as constants so the figure regenerates without a model solve; if the
calibration changes, rerun the analysis scripts and update these numbers.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Public pension outlays as a share of GDP (docs/results_retirement_age.md,
# docs/results_replacement_rate.md). Baseline is 11.4%.
PENSION = {
    "Baseline": 11.4,
    "Pension age 68": 10.4,
    "Pension age 70": 9.5,
    "Replacement -10%": 10.3,
    "Replacement -20%": 9.1,
}
# Government revenue as a share of GDP under the consumption tax
# (docs/results_consumption_tax.md): 0.322 / 0.336 / 0.355.
REVENUE = {
    "10% (actual)": 32.2,
    "12%": 33.6,
    "15% (IMF)": 35.5,
}

BASE = "#4c4c4c"  # baseline / neutral
HL = "#1f77b4"  # reforms


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    # --- Panel 1: pension burden ---
    labels = list(PENSION.keys())
    vals = list(PENSION.values())
    colors = [BASE] + [HL] * (len(labels) - 1)
    bars = ax1.barh(range(len(labels)), vals, color=colors)
    ax1.set_yticks(range(len(labels)))
    ax1.set_yticklabels(labels)
    ax1.invert_yaxis()
    ax1.set_xlabel("Public pension outlays (% of GDP)")
    ax1.set_title("Pension reforms cut the pension burden", fontsize=11)
    ax1.set_xlim(0, 13)
    for b, v in zip(bars, vals):
        ax1.text(
            v + 0.15,
            b.get_y() + b.get_height() / 2,
            f"{v:.1f}",
            va="center",
            fontsize=9,
        )
    ax1.axvline(PENSION["Baseline"], color=BASE, ls=":", lw=1, alpha=0.6)

    # --- Panel 2: consumption-tax revenue ---
    labels2 = list(REVENUE.keys())
    vals2 = list(REVENUE.values())
    colors2 = [BASE] + [HL] * (len(labels2) - 1)
    bars2 = ax2.bar(range(len(labels2)), vals2, color=colors2, width=0.6)
    ax2.set_xticks(range(len(labels2)))
    ax2.set_xticklabels(labels2)
    ax2.set_ylabel("Government revenue (% of GDP)")
    ax2.set_title("A higher consumption tax raises revenue", fontsize=11)
    ax2.set_ylim(0, 40)
    for b, v in zip(bars2, vals2):
        ax2.text(
            b.get_x() + b.get_width() / 2, v + 0.4, f"{v:.1f}", ha="center", fontsize=9
        )

    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(
        "OG-Japan: long-run effects of three fiscal reforms",
        fontsize=13,
        y=1.02,
    )
    fig.text(
        0.5,
        -0.04,
        "Steady state on real Japanese demographics; macro and tax "
        "calibration first-pass. See docs/results_*.md.",
        ha="center",
        fontsize=8,
        color="#666666",
    )
    fig.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "..", "docs", "policy_results.png")
    fig.savefig(os.path.abspath(out), dpi=150, bbox_inches="tight")
    print(f"Wrote {os.path.abspath(out)}")


if __name__ == "__main__":
    main()
