"""
OG-Japan Phase 3: long-run effect of a consumption-tax increase, on real
Japanese demographics.

Scenario: raise Japan's consumption tax from 10 percent to 12 percent (a
policy option Japan has actually debated). The script builds the Japan
calibration once (macro + tax + pension + real UN demographics, pulled with a
token), then solves the baseline and reform STEADY STATES reusing those
demographics, and reports the long-run percent change in the main aggregates.

Careful with the rates -- twice over.

First, the model's ``tau_c`` is an EFFECTIVE rate covering ALL indirect taxes,
not the statutory consumption-tax rate. A statutory rise of 10% -> 12% is not
``tau_c`` going 0.10 -> 0.12, which would be a tax CUT.

Second, and less obvious: the model's consumption base is larger than Japan's,
so a rate change does not transfer across either. This script therefore sizes
the reform by the REVENUE it must raise (+0.99pp of GDP, Japan's actual gain
from 10% -> 12%) rather than by a rate change, which cancels the base error
exactly. See ``reform_tau_c`` below.

NOTE: several parameters are still marked NEEDS TUNING in the calibration
modules pending the in-model tuning loop, so treat magnitudes as indicative
rather than final. Requires a UN API token in un_api_token.txt.
"""

import os
import numpy as np

from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogcore import utils

from ogjpn import calibrate
from ogjpn.constants import START_YEAR


def _scalar(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def solve_ss(calibrated, tau_c_rate, output_base):
    """Solve the steady state given a calibrated dict and a tau_c rate."""
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    scenario = dict(calibrated)
    scenario["tau_c"] = [[tau_c_rate]]  # scenario lever
    p.update_specifications(scenario)
    p.baseline_dir = p.output_base = output_base
    runner(p, time_path=False, client=None)
    return utils.safe_read_pickle(
        os.path.join(output_base, "SS", "SS_vars.pkl")
    )


# Baseline effective indirect-tax rate, from ogjpn.tax_params.
BASELINE_TAU_C = 0.1123

# Japan's 10% -> 12% statutory consumption tax raises VAT collections by a
# fifth, from 4.94% to 5.93% of GDP: a revenue gain of +0.99pp of GDP.
REVENUE_GAIN_TARGET_SHARE_OF_GDP = 0.0099


def reform_tau_c(baseline_ss):
    """
    Size the reform by the REVENUE it must raise, not by a rate change.

    This matters, and it is the one thing to get right in this script. The
    model's consumption base is larger than Japan's (about 0.60 of GDP against
    Japan's 0.53), because a shrinking steady state needs less investment than
    Japan currently undertakes and the residual lands on consumption. tau_c was
    calibrated DOWN to compensate, so it delivers the right revenue on an
    oversized base.

    The consequence is that a rate CHANGE does not transfer across: applying
    Japan's +1.85pp effective-rate rise to the model's base would over-collect
    by the base error, roughly 14%. Sizing the reform by its revenue target
    instead cancels the error exactly, because the same oversized base appears
    in the numerator and the denominator.

        d(tau_c) = revenue gain / (C/Y)

    Args:
        baseline_ss (dict): solved baseline steady state

    Returns:
        float: the reformed effective consumption tax rate
    """
    Y = _scalar(baseline_ss["Y"])
    C_share = _scalar(baseline_ss["C"]) / Y
    return BASELINE_TAU_C + REVENUE_GAIN_TARGET_SHARE_OF_GDP / C_share


def main():
    # Build the Japan calibration once (real demographics pulled here).
    p0 = Specifications(baseline=True, num_workers=1)
    p0.update_specifications({"start_year": START_YEAR})
    calibrated = calibrate.Calibration(p0, use_demographics=True).get_dict()
    print("Built Japan calibration with real UN demographics.")

    base = solve_ss(calibrated, BASELINE_TAU_C, "/tmp/ogjpn_ct_base")
    # Size the reform off the SOLVED baseline, so it raises the revenue Japan's
    # policy would raise rather than applying a rate change to the wrong base.
    reform_rate = reform_tau_c(base)
    reform = solve_ss(calibrated, reform_rate, "/tmp/ogjpn_ct_reform")

    print("\n=== Long-run effect of raising Japan's consumption tax 10% -> 12% ===")
    print(
        f"(effective tau_c {BASELINE_TAU_C:.4f} -> {reform_rate:.4f}, sized to "
        f"raise {100*REVENUE_GAIN_TARGET_SHARE_OF_GDP:.2f}pp of GDP;\n"
        " real Japan demographics)\n"
    )
    for v in ["Y", "C", "K", "L"]:
        b, r = _scalar(base[v]), _scalar(reform[v])
        print(f"{v:>2}: {100 * (r - b) / b:+.2f}%")
    b_rev = _scalar(base["total_tax_revenue"]) / _scalar(base["Y"])
    r_rev = _scalar(reform["total_tax_revenue"]) / _scalar(reform["Y"])
    b_pen = _scalar(base["agg_pension_outlays"]) / _scalar(base["Y"])
    print(f"\nTotal tax revenue / GDP: {b_rev:.3f} -> {r_rev:.3f}")
    print(f"Pension outlays / GDP (baseline): {b_pen:.3f}")


if __name__ == "__main__":
    main()
