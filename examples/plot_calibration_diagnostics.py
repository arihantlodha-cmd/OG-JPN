"""
OG-Japan calibration diagnostics: the model's INPUTS, not its results.

`plot_calibration_fit.py` answers "does the solved steady state look like
Japan?". This answers the prior question — "are the things we fed it right?" —
by plotting the calibrated objects themselves: the population the model ages,
the growth path it converges along, the earnings profile it puts people on, the
mortality it kills them with, the tax schedule it charges them, and the labour
disutility it gives them.

Two of these panels exist mainly to make an honest point visible: `chi_n` is
OG-USA's, unchanged, and the tax function is a shape fitted to Japan's statutory
schedule rather than estimated from microdata.

Run after a solve:
    python examples/validate_japan.py
    python examples/plot_calibration_diagnostics.py
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from ogcore import utils

from ogjpn import income

# Same two-series palette as the fit figure, verified for colour-vision
# deficiency (dE 24.7 protan / 32.7 tritan on a light surface).
JPN = "#2a78d6"
USA = "#eb6834"
INK = "#1a1a19"
INK_MUTED = "#6b6b68"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def _style(ax):
    ax.grid(color=INK, ls=":", lw=0.5, alpha=0.2, zorder=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0, colors=INK_MUTED, labelsize=8)


def _title(ax, head, sub):
    ax.set_title(f"{head}\n{sub}", fontsize=9.5, loc="left", color=INK, pad=8)


def panel_population(ax, p):
    """Japan's age structure now vs the model's stationary population."""
    omega = np.asarray(p.omega)
    ages = np.arange(p.E, p.E + p.S)
    now = omega[0].sum(axis=1)
    ss = np.asarray(p.omega_SS).sum(axis=1)
    ax.plot(ages, 100 * now, color=JPN, lw=2, label="2025 (UN WPP)")
    ax.plot(ages, 100 * ss, color=USA, lw=2, ls="--", label="model steady state")
    ax.set_xlabel("age", fontsize=8.5)
    ax.set_ylabel("% of population", fontsize=8.5)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    _title(ax, "A   Population by age",
           "the steady state is older still than Japan today")


def panel_g_n(ax, p):
    """The population growth path the transition follows."""
    g_n = np.asarray(p.g_n).ravel()
    t = np.arange(len(g_n))
    ax.plot(t, 100 * g_n, color=JPN, lw=2)
    ax.axhline(100 * float(np.asarray(p.g_n_ss)), color=USA, lw=1.5, ls="--")
    ax.text(len(g_n) * 0.55, 100 * float(np.asarray(p.g_n_ss)) + 0.06,
            f"steady state {100*float(np.asarray(p.g_n_ss)):.2f}%",
            fontsize=8, color=USA)
    ax.set_xlim(0, 120)
    ax.set_xlabel("model period (years from 2025)", fontsize=8.5)
    ax.set_ylabel("population growth, %/yr", fontsize=8.5)
    _title(ax, "B   Population growth path",
           "−0.33%/yr today, deepening to −1.07%")


def panel_earnings(ax, p):
    """The e matrix: earnings ability by age and lifetime-income group."""
    e = np.asarray(p.e)
    if e.ndim == 3:
        e = e[0]
    ages = np.arange(p.E, p.E + p.S)
    for j in range(e.shape[1]):
        ax.plot(ages, e[:, j], color=SEQ[j % len(SEQ)], lw=1.6)
    ax.set_yscale("log")
    ax.set_xlabel("age", fontsize=8.5)
    ax.set_ylabel("ability (log scale)", fontsize=8.5)
    peak = p.E + int(np.argmax(e.mean(axis=1)))
    ax.axvline(peak, color=INK_MUTED, lw=1, ls=":")
    ax.text(peak + 1, ax.get_ylim()[0] * 1.6, f"peak {peak}",
            fontsize=8, color=INK_MUTED)
    _title(ax, "C   Earnings ability, 7 income groups",
           "NTA age shape + Japan Gini tilt; peaks at 57, not 61")


def panel_age_factor(ax):
    """The NTA Japan/US age factor -- the seniority-wage signature."""
    f = income.get_age_shape_factor(20, 80)
    ages = np.arange(20, 100)
    ax.axhline(1.0, color=INK, lw=1)
    ax.plot(ages, f, color=JPN, lw=2)
    ax.fill_between(ages, 1.0, f, where=f >= 1, color=JPN, alpha=0.15)
    ax.fill_between(ages, 1.0, f, where=f < 1, color=USA, alpha=0.15)
    ax.axvline(60, color=INK_MUTED, lw=1, ls=":")
    ax.text(59, 0.63, "mandatory\nretirement at 60", fontsize=7.5,
            color=INK_MUTED, ha="right")
    ax.set_xlim(20, 85)
    ax.set_xlabel("age", fontsize=8.5)
    ax.set_ylabel("Japan ÷ US labour income", fontsize=8.5)
    _title(ax, "D   Age-earnings shape vs the US",
           "steeper to 55 (seniority pay), then a cliff")


def panel_mortality(ax, p):
    """Survival: the mortality rates the model ages people with."""
    rho = np.asarray(p.rho)
    if rho.ndim == 3:
        rho = rho[0].mean(axis=1)
    elif rho.ndim == 2:
        rho = rho[0]
    ages = np.arange(p.E, p.E + p.S)
    surv = np.cumprod(1 - rho)
    ax.plot(ages, 100 * surv, color=JPN, lw=2)
    for q, lab in [(0.5, "half"), (0.1, "90% gone")]:
        idx = int(np.argmin(np.abs(surv - q)))
        ax.plot([ages[idx]], [100 * surv[idx]], "o", ms=7, color=USA,
                markeredgecolor="white", markeredgewidth=1.2)
        ax.text(ages[idx] - 2, 100 * surv[idx] + 5, f"{lab}: {ages[idx]}",
                fontsize=8, color=INK, ha="right")
    ax.set_xlabel("age", fontsize=8.5)
    ax.set_ylabel("% of cohort surviving", fontsize=8.5)
    _title(ax, "E   Survival curve (UN WPP mortality)",
           "the longest-lived population in the OECD")


def panel_tax(ax, p):
    """The Gouveia-Strauss effective rate against income."""
    phi0, phi1, phi2 = np.asarray(p.etr_params)[0, 0, :3]
    y = np.linspace(5e5, 3e7, 400)
    etr = phi0 * (1 - (1 + phi2 * y**phi1) ** (-1 / phi1))
    ax.plot(y / 1e6, 100 * etr, color=JPN, lw=2)
    ax.axhline(100 * phi0, color=USA, lw=1.5, ls="--")
    ax.text(30, 100 * phi0 - 5.5, f"asymptote = statutory top {100*phi0:.0f}%",
            fontsize=8, color=USA, ha="right", va="top")
    mean_income = 4.6
    ax.axvline(mean_income, color=INK_MUTED, lw=1, ls=":")
    at_mean = phi0 * (1 - (1 + phi2 * (mean_income * 1e6) ** phi1) ** (-1 / phi1))
    ax.plot([mean_income], [100 * at_mean], "o", ms=8, color=INK,
            markeredgecolor="white", markeredgewidth=1.2)
    ax.text(mean_income + 0.6, 100 * at_mean - 1.5,
            f"mean wage ¥4.6m: {100*at_mean:.1f}%", fontsize=8, color=INK)
    ax.set_xlabel("income, ¥ million", fontsize=8.5)
    ax.set_ylabel("effective income-tax rate, %", fontsize=8.5)
    ax.set_ylim(0, 60)
    _title(ax, "F   Income tax (Gouveia-Strauss)",
           "floored at zero; fitted to Japan's collections")


def panel_chi_n(ax, p):
    """chi_n -- borrowed from OG-USA, and labelled as such."""
    chi = np.asarray(p.chi_n)
    if chi.ndim == 2:
        chi = chi[0]
    ages = np.arange(p.E, p.E + p.S)
    ax.plot(ages, chi, color=USA, lw=2)
    ax.set_xlabel("age", fontsize=8.5)
    ax.set_ylabel("disutility weight", fontsize=8.5)
    _title(ax, "G   Labour disutility  χ_n  — NOT calibrated",
           "OG-USA's profile; Japan's labour input is within 1%")


def panel_lambdas(ax, p):
    """The lifetime-income group shares, byte-identical across the family."""
    lam = np.asarray(p.lambdas).ravel()
    labels = ["0-25", "25-50", "50-70", "70-80", "80-90", "90-99", "top 1%"]
    y = np.arange(len(lam))[::-1]
    ax.barh(y, 100 * lam, height=0.6,
            color=[SEQ[i % len(SEQ)] for i in range(len(lam))], zorder=3)
    for yi, v in zip(y, lam):
        ax.text(100 * v + 0.7, yi, f"{100*v:.0f}%", va="center",
                fontsize=8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("% of population", fontsize=8.5)
    ax.set_xlim(0, 30)
    _title(ax, "H   Lifetime-income groups  λ_j",
           "family-standard percentiles, not re-derived")


def main(ss_dir="/tmp/ogjpn_validate", out="docs/calibration_diagnostics.png"):
    p = utils.safe_read_pickle(os.path.join(ss_dir, "model_params.pkl"))

    fig, axes = plt.subplots(2, 4, figsize=(19, 8.6))
    for ax in axes.ravel():
        _style(ax)
    panel_population(axes[0, 0], p)
    panel_g_n(axes[0, 1], p)
    panel_earnings(axes[0, 2], p)
    panel_age_factor(axes[0, 3])
    panel_mortality(axes[1, 0], p)
    panel_tax(axes[1, 1], p)
    panel_chi_n(axes[1, 2], p)
    panel_lambdas(axes[1, 3], p)

    fig.suptitle(
        "OG-Japan calibration diagnostics — the model's inputs",
        fontsize=13, x=0.006, ha="left", y=0.985, color=INK,
    )
    fig.text(
        0.006, 0.008,
        "Demographics: UN WPP via ogcore, country 392.  Earnings: OG-USA e matrix, "
        "NTA age shape (JPN 2004 / USA 2003) + World Bank Gini tilt (32.3 vs 41.5).  "
        "Tax: Japan statutory schedule fitted to OECD Revenue Statistics 2025.  "
        "χ_n and λ_j: OG-USA, uncalibrated.",
        fontsize=7, color=INK_MUTED, ha="left",
    )
    fig.subplots_adjust(top=0.86, bottom=0.10, left=0.045, right=0.99,
                        hspace=0.42, wspace=0.30)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.savefig(out, dpi=170, facecolor="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
