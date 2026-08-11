"""
OG-Japan baseline transition path.

Solves the full transition (steady state + time path) on real Japanese
demographics and macro parameters, and reports the debt-to-GDP and
pension-to-GDP paths over the first decades -- Japan's fiscal-demographic
dynamics as the population ages. Requires a UN API token.

This is a heavy solve and may take many minutes.

STATUS: with the current first-pass calibration the transition does NOT
converge. It plateaus at a resource-constraint error of ~0.0016 (0.16%),
and Anderson acceleration lands on the same value, so this is a
calibration-consistency issue (the converged path doesn't quite close the
resource constraint), not solver tuning. A converged transition needs the
preference/production/fiscal parameters tightened -- the same Phase-2
calibration the steady-state validation points to. The runner is kept
ready for when that calibration lands.
"""

import os
import numpy as np

from dask.distributed import Client, LocalCluster

from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogcore import utils

from ogjpn import calibrate
from ogjpn.constants import START_YEAR


def main(out="/tmp/ogjpn_tpi", num_workers=2):
    # TPI needs a Dask client for its parallel scatter step (the steady
    # state alone does not).
    cluster = LocalCluster(n_workers=num_workers, threads_per_worker=1)
    client = Client(cluster)

    p = Specifications(baseline=True, num_workers=num_workers)
    p.update_specifications({"start_year": START_YEAR})
    p.update_specifications(
        calibrate.Calibration(p, use_demographics=True).get_dict()
    )
    # The transition plateaus under the default damped iteration with
    # Japan's extreme calibration; Anderson acceleration is the documented
    # remedy for that limit-cycling.
    p.update_specifications({"TPI_outer_method": "anderson"})
    p.baseline_dir = p.output_base = out

    try:
        runner(p, time_path=True, client=client)
    finally:
        client.close()
        cluster.close()

    tpi = utils.safe_read_pickle(os.path.join(out, "TPI", "TPI_vars.pkl"))
    Y = np.asarray(tpi["Y"])
    D = np.asarray(tpi["D"])
    pens = np.asarray(tpi["agg_pension_outlays"])

    print("\n=== OG-JPN baseline transition solved ===")
    yrs = [0, 5, 10, 20, 30]
    print("year(from start)   debt/GDP   pension/GDP")
    for t in yrs:
        print(f"  +{t:<14d} {D[t] / Y[t]:8.3f}   {pens[t] / Y[t]:8.3f}")


if __name__ == "__main__":
    main()
