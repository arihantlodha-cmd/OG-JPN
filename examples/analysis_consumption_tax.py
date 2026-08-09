"""
OG-Japan Phase 3 demonstration: long-run effect of a consumption-tax
increase.

Scenario: raise Japan's consumption tax from 10 percent to 12 percent (a
policy option Japan has actually debated). The script solves the baseline
and reform STEADY STATES and reports the long-run percent change in the
main aggregates.

IMPORTANT: the numbers are PROVISIONAL and illustrative, not findings
about Japan. The calibration still uses placeholder macro parameters and
OG-Core default (non-Japan) demographics until a UN API token and
verified data are added (see docs/NEXT_STEPS.md). The point of this
script is to show the baseline-vs-reform analysis pipeline works end to
end. The richer version reports the transition path and uses the
`npv_table` added to OG-Core (PR #1195) to compute the NPV of the change
in GDP; that requires a transition-path solve and is the next step once
the calibration is real.
"""

import os
import numpy as np

from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogcore import utils

from ogjpn import calibrate
from ogjpn.constants import START_YEAR


def solve_ss(tau_c_rate, output_base):
    """Solve the OG-Japan steady state at a given consumption tax rate."""
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    calibrated = calibrate.Calibration(p, use_demographics=False).get_dict()
    calibrated["tau_c"] = [[tau_c_rate]]  # scenario lever
    p.update_specifications(calibrated)
    p.baseline_dir = p.output_base = output_base
    runner(p, time_path=False, client=None)
    return utils.safe_read_pickle(
        os.path.join(output_base, "SS", "SS_vars.pkl")
    )


def _scalar(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def main():
    base = solve_ss(0.10, "/tmp/ogjpn_base")
    reform = solve_ss(0.12, "/tmp/ogjpn_reform")

    print("\n=== Long-run effect of raising consumption tax 10% -> 12% ===")
    print("(PROVISIONAL, illustrative only: placeholder calibration)\n")
    for v in ["Y", "C", "K", "L"]:
        b, r = _scalar(base[v]), _scalar(reform[v])
        print(f"{v:>2}: {100 * (r - b) / b:+.2f}%")

    b_rev = _scalar(base["total_tax_revenue"]) / _scalar(base["Y"])
    r_rev = _scalar(reform["total_tax_revenue"]) / _scalar(reform["Y"])
    print(f"\nTotal tax revenue / GDP: {b_rev:.3f} -> {r_rev:.3f}")


if __name__ == "__main__":
    main()
