"""
OG-Japan Phase 3: long-run effect of a consumption-tax increase, on real
Japanese demographics.

Scenario: raise Japan's consumption tax from 10 percent to 12 percent (a
policy option Japan has actually debated). The script builds the Japan
calibration once (macro + tax + pension + real UN demographics, pulled with a
token), then solves the baseline and reform STEADY STATES reusing those
demographics, and reports the long-run percent change in the main aggregates.

Careful with the rates. The model's ``tau_c`` is an EFFECTIVE rate covering all
indirect taxes, not the statutory consumption-tax rate: Japan's statutory 10%
plus excises comes to 12.72% of consumption (see ogjpn/tax_params.py). So a
statutory rise of 10% -> 12% is NOT ``tau_c`` going 0.10 -> 0.12, which would
actually be a tax cut. It raises VAT collections by a fifth, from 4.94% to about
5.93% of GDP, which on consumption of 53.6% of GDP is an effective-rate rise of
about 1.85 percentage points.

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
BASELINE_TAU_C = 0.1272

# A 10% -> 12% statutory consumption tax raises VAT collections by a fifth:
# 4.94% -> 5.93% of GDP, i.e. +0.99pp of GDP. Against household consumption of
# 53.6% of GDP that is +1.85pp on the effective rate.
STATUTORY_RISE_IN_EFFECTIVE_POINTS = 0.0185
REFORM_TAU_C = BASELINE_TAU_C + STATUTORY_RISE_IN_EFFECTIVE_POINTS


def main():
    # Build the Japan calibration once (real demographics pulled here).
    p0 = Specifications(baseline=True, num_workers=1)
    p0.update_specifications({"start_year": START_YEAR})
    calibrated = calibrate.Calibration(p0, use_demographics=True).get_dict()
    print("Built Japan calibration with real UN demographics.")

    base = solve_ss(calibrated, BASELINE_TAU_C, "/tmp/ogjpn_ct_base")
    reform = solve_ss(calibrated, REFORM_TAU_C, "/tmp/ogjpn_ct_reform")

    print("\n=== Long-run effect of raising Japan's consumption tax 10% -> 12% ===")
    print(
        f"(effective tau_c {BASELINE_TAU_C:.4f} -> {REFORM_TAU_C:.4f}; "
        "real Japan demographics)\n"
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
