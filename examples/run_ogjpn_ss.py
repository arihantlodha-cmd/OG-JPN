"""
OG-Japan feasibility run.

Goal: assemble the OG-Japan calibration (macro, tax, and demographics)
into an OG-Core Specifications object and solve the steady state, proving
the OG-JPN pipeline works end to end.

Pulling live Japan demographics requires a free UN API token saved as
``un_api_token.txt`` (see the project README). If no token is present,
OG-Core's offline data mirror does not yet include Japan, so this script
falls back to the macro + tax calibration on top of OG-Core's default
demographics and clearly says so.
"""

import os
import numpy as np

from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogcore import utils

from ogjpn import calibrate
from ogjpn.constants import START_YEAR, COUNTRY_NAME


def main(output_base="/tmp/ogjpn_phase0"):
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})

    using_japan_demographics = False
    try:
        c = calibrate.Calibration(p, use_demographics=True)
        using_japan_demographics = True
        print(f"Loaded {COUNTRY_NAME} demographics + macro + tax.")
    except Exception as exc:  # noqa: BLE001 - report any failure clearly
        print(
            f"Could not load {COUNTRY_NAME} demographics "
            f"({type(exc).__name__}: {exc}).\n"
            "Falling back to Japan macro + tax on OG-Core default "
            "demographics. Add a UN API token (un_api_token.txt) to pull "
            "live Japan data."
        )
        c = calibrate.Calibration(p, use_demographics=False)

    p.update_specifications(c.get_dict())

    p.baseline_dir = p.output_base = output_base
    runner(p, time_path=False, client=None)

    ss = utils.safe_read_pickle(os.path.join(output_base, "SS", "SS_vars.pkl"))
    Y = float(np.asarray(ss["Y"]).sum())
    G = float(ss["G"])
    print("\n=== OG-JPN steady state ===")
    print(f"Japan demographics used:   {using_japan_demographics}")
    print(f"Steady-state Y (aggregate): {Y:.4f}")
    print(f"Total tax revenue / Y:      {float(ss['total_tax_revenue']) / Y:.4f}")
    print(f"Pension outlays / Y:        {float(ss['agg_pension_outlays']) / Y:.4f}")
    print(f"Debt / Y:                   {float(ss['D']) / Y:.4f}")
    print(f"Govt spending G:            {G:.5f} ({'positive' if G >= 0 else 'NEGATIVE'})")
    print("Steady state solved successfully.")


if __name__ == "__main__":
    main()
