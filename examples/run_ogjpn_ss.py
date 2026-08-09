"""
OG-Japan Phase 0 feasibility run.

Goal: pull Japan's demographics into an OG-Core Specifications object and
solve the steady state, proving the OG-JPN calibration pipeline works end
to end.

Pulling live Japan demographics requires a free UN API token saved as
``un_api_token.txt`` (see the project README). If no token is present,
OG-Core's offline data mirror does not yet include Japan, so this script
falls back to OG-Core's default demographics and clearly says so, which
still exercises the full calibrate -> Specifications -> solve pipeline.
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
        c = calibrate.Calibration(p)
        p.update_specifications(c.get_dict())
        using_japan_demographics = True
        print(f"Loaded {COUNTRY_NAME} (UN 392) demographics.")
    except Exception as exc:  # noqa: BLE001 - report any failure clearly
        print(
            f"Could not load {COUNTRY_NAME} demographics "
            f"({type(exc).__name__}: {exc}).\n"
            "Falling back to OG-Core default demographics so the "
            "pipeline can still be exercised. Add a UN API token "
            "(un_api_token.txt) to pull live Japan data."
        )

    p.baseline_dir = p.output_base = output_base
    runner(p, time_path=False, client=None)

    ss = utils.safe_read_pickle(os.path.join(output_base, "SS", "SS_vars.pkl"))
    Y = float(np.asarray(ss["Y"]).sum())
    pension_share = float(ss["agg_pension_outlays"]) / Y
    print("\n=== OG-JPN Phase 0 steady state ===")
    print(f"Japan demographics used: {using_japan_demographics}")
    print(f"Steady-state Y (aggregate): {Y:.4f}")
    print(f"Aggregate pension outlays / Y: {pension_share:.4f}")
    print("Steady state solved successfully.")


if __name__ == "__main__":
    main()
