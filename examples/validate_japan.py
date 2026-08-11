"""
OG-Japan steady-state validation dashboard.

Solves the steady state on Japan's calibration and compares it to Japanese data,
moment by moment, with a source for every target.

The governing idea, inherited from the OG-Core country family: most parameters
are only weakly identified on their own, so the real test of a calibration is
whether the steady state they *jointly* produce resembles the economy. Fiscal
moments lead the dashboard because they are published precisely, map one-to-one
onto model ratios, and are self-checking through the government budget identity.

Run:
    PYTHONPATH=. python examples/validate_japan.py
"""

import os

import numpy as np

from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogcore import utils

from ogjpn import calibrate, rgov_floor, warm_start
from ogjpn.constants import START_YEAR


def _s(x):
    """Collapse a model object to a scalar."""
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


# (label, how to compute from the SS dict, target, source)
# Revenue lines first -- the sharpest validators -- then the external and
# fiscal anchors, then the second-tier production/preference moments.
DASHBOARD = [
    (
        "Total tax revenue / Y",
        lambda ss, Y: _s(ss["total_tax_revenue"]) / Y,
        0.337,
        "OECD Revenue Statistics 2025, Japan (2023)",
    ),
    (
        "  Income tax (PIT) / Y",
        lambda ss, Y: _s(ss["iit_revenue"]) / Y,
        0.0617,
        "OECD RevStats 2025: 36,703 of 594,490 yen bn",
    ),
    (
        "  Corporate tax / Y",
        lambda ss, Y: _s(ss["business_tax_revenue"]) / Y,
        0.0470,
        "OECD RevStats 2025: 27,942 yen bn",
    ),
    (
        "  Consumption+indirect / Y",
        lambda ss, Y: _s(ss["cons_tax_revenue"]) / Y,
        0.0682,
        "OECD RevStats 2025: VAT 29,355 + excises 7,533",
    ),
    (
        "  Payroll / social ins. / Y",
        lambda ss, Y: _s(ss["payroll_tax_revenue"]) / Y,
        0.1318,
        "OECD RevStats 2025: 78,335 yen bn",
    ),
    (
        "Pension outlays / Y",
        lambda ss, Y: _s(ss["agg_pension_outlays"]) / Y,
        0.093,
        "OECD Pensions at a Glance 2023 (2022)",
    ),
    (
        # NOT a data target: D/Y in the steady state IS debt_ratio_ss, a policy
        # anchor we chose. Japan's measured net debt (1.148 at end-2024, OECD
        # GNFLQ) is the INITIAL condition, which the transition starts from.
        # Scoring the SS against it would be scoring a choice against a
        # measurement.
        "Debt / Y  (= SS anchor)",
        lambda ss, Y: _s(ss["D"]) / Y,
        None,
        "policy anchor debt_ratio_ss=1.0; measured start 1.148",
    ),
    (
        "Foreign-held debt  D_f/D",
        lambda ss, Y: _s(ss["D_f"]) / _s(ss["D"]),
        0.137,
        "MOF JGB/T-Bill holders, Mar 2026 preliminary",
    ),
    (
        # This row is why zeta_K sat at a placeholder through fourteen tuning
        # rounds: the moment was not scored, so nothing pulled the parameter.
        # The IIP publishes it -- foreign equity claims on Japanese capital
        # (DI equity 25.040 + reinvested 9.460 + portfolio equity 334.799
        # = 369.3 trillion yen) over GDP 609, divided by K/Y 3.70 = 16.4%.
        # Band is 12% (market value deflated by Tobin's q) to 20% (including
        # foreign holdings of corporate debt).
        "Foreign-owned capital K_f/K",
        lambda ss, Y: _s(ss["K_f"]) / _s(ss["K"]),
        0.164,
        "MOF IIP end-2024: DI + portfolio equity, 60.6% of GDP",
    ),
    (
        "Sovereign real rate r_gov",
        lambda ss, Y: _s(ss["r_gov"]),
        -0.006,
        "OECD EO net interest / net debt, 2015-2024 avg",
    ),
    (
        "Consumption / Y",
        lambda ss, Y: _s(ss["C"]) / Y,
        0.536,
        "World Bank NE.CON.PRVT.ZS, Japan 2023",
    ),
    (
        # Every component of the resource constraint, so a consumption gap can
        # be attributed instead of guessed at. C = Y - I - I_g - G - NX.
        "  Investment (I+I_g) / Y",
        lambda ss, Y: (_s(ss["I_total"]) + _s(ss["I_g"])) / Y,
        0.260,
        "World Bank NE.GDI.FTOT.ZS: GFCF, private AND public",
    ),
    (
        "  Government G / Y",
        lambda ss, Y: _s(ss["G"]) / Y,
        0.201,
        "World Bank NE.CON.GOVT.ZS; gap = the embedded consolidation",
    ),
    (
        # NX is the TRADE balance, and Japan's is near zero -- that is what
        # this row scores. Japan's ~3.8% current-account surplus is almost
        # entirely PRIMARY INCOME on its net foreign assets, which this model
        # has no room for: households hold domestic capital and domestic debt
        # only, so the 1,659tn yen Japan holds abroad is absent from B and the
        # income it earns is absent from the resource constraint. See
        # docs/NEXT_STEPS.md section 0c.
        "  Net exports NX / Y",
        lambda ss, Y: 1.0
        - (_s(ss["C"]) + _s(ss["I_total"]) + _s(ss["I_g"]) + _s(ss["G"])) / Y,
        0.000,
        "BOP goods+services balance ~0 (the 3.8% CA is primary income)",
    ),
    (
        # Not forced when epsilon != 1, so this is a genuine free check on gamma.
        "Labour share w*L / Y",
        lambda ss, Y: _s(ss["w"]) * _s(ss["L"]) / Y,
        0.571,
        "PWT labsh via FRED LABSHPJPA156NRUG (= 1 - gamma)",
    ),
    (
        "Capital-output K / Y",
        lambda ss, Y: _s(ss["K"]) / Y,
        3.7,
        "Penn World Table (family trait: model runs high)",
    ),
    (
        "Interest rate r",
        lambda ss, Y: _s(ss["r"]),
        None,
        "no data target; open-economy modelling latitude",
    ),
]


def main(out="/tmp/ogjpn_validate"):
    rgov_floor.enable()   # see ogjpn/rgov_floor.py
    warm_start.enable()   # see ogjpn/warm_start.py
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    p.update_specifications(
        calibrate.Calibration(p, use_demographics=True).get_dict()
    )
    p.baseline_dir = p.output_base = out
    runner(p, time_path=False, client=None)
    ss = utils.safe_read_pickle(os.path.join(out, "SS", "SS_vars.pkl"))

    Y = _s(ss["Y"])

    print("\n=== OG-Japan steady state vs Japanese data ===\n")
    print(f"{'Moment':30s}{'Model':>10s}{'Target':>10s}{'Gap':>10s}  Source")
    print("-" * 110)
    for label, fn, target, source in DASHBOARD:
        try:
            model = fn(ss, Y)
        except KeyError as exc:
            print(f"{label:30s}{'n/a':>10s}{'':>10s}{'':>10s}  missing key {exc}")
            continue
        if target is None:
            print(f"{label:30s}{model:>10.4f}{'--':>10s}{'--':>10s}  {source}")
        else:
            print(
                f"{label:30s}{model:>10.4f}{target:>10.4f}"
                f"{model - target:>+10.4f}  {source}"
            )

    # The government budget identity is the self-check: if the spending side
    # and the revenue side do not meet at the debt target, the steady state
    # will still solve but the transition will run away.
    print("\n--- fiscal consistency check ---")
    g_y = float(np.asarray(p.g_y).flat[0])
    g_n = float(np.asarray(p.g_n_ss).flat[0])
    g = np.exp(g_y) * (1 + g_n) - 1
    r_gov = _s(ss["r_gov"])
    D_Y = _s(ss["D"]) / Y
    pb_star = (r_gov - g) / (1 + g) * D_Y
    revenue = _s(ss["total_tax_revenue"]) / Y
    primary_spending = revenue - pb_star
    # Pensions are a primary outlay. Leaving them out of the identity is how
    # alpha_G ended up 0.63pp too high: the SS closure absorbs the error into
    # G, so the steady state looks fine and only the transition over-spends.
    pensions = _s(ss["agg_pension_outlays"]) / Y
    alphas = (
        float(np.asarray(p.alpha_G).flat[-1])
        + float(np.asarray(p.alpha_T).flat[-1])
        + float(np.asarray(p.alpha_I).flat[-1])
    )
    print(f"  model growth g            = {g:+.5f}")
    print(f"  sovereign rate r_gov      = {r_gov:+.5f}")
    print(f"  r_gov - g                 = {r_gov - g:+.5f}")
    print(f"  debt-stabilising pb*      = {pb_star:+.5f} of GDP")
    print(f"  implied primary spending  = {primary_spending:.5f} of GDP")
    print(f"  alpha_G+alpha_T+alpha_I    = {alphas:.5f}")
    print(f"    + pension outlays        = {alphas + pensions:.5f}"
          f"   residual {alphas + pensions - primary_spending:+.5f}")
    print("  Japan actual primary balance: -0.0179 (2024), -0.0102 (2025)")
    print("    [OECD Economic Outlook NLGXQ]")


if __name__ == "__main__":
    main()
