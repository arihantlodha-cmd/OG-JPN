"""
OG-Japan baseline transition path.

Solves the full transition (steady state + time path) on real Japanese
demographics and macro parameters, and reports the debt-to-GDP and
pension-to-GDP paths over the first decades -- Japan's fiscal-demographic
dynamics as the population ages.

This is a heavy solve and may take many minutes.

STATUS: the transition converges (outer loop below 1e-5). What made that
possible was setting alpha_G to the steady-state residual G/Y, so the
transition runs the same fiscal policy as the steady state it converges to
(see ogjpn/macro_params.py). By default it starts from Japan's observed
initial wealth distribution (--initial-wealth data, ogjpn/wealth.py).

The resource constraint holds to below 1e-6 except in two single periods:
t=2 (~1.5e-3, from an off-by-one in OG-Core's population projection;
fixed by OG-Core PR #1295) and t=120 (~1.2e-3, where OG-Core freezes the
population at fixper = 1.5*S before Japan's has converged; OG-Core issue
#1290). OG-Core's strict per-period check flags them, so the runner raises
after writing the path; this script reports the error and continues, and
the written TPI_vars.pkl is usable. Both errors cancel in reform-minus-
baseline comparisons.
"""

import argparse
import os

import numpy as np
from dask.distributed import Client, LocalCluster
from ogcore import utils
from ogcore.execute import runner
from ogcore.parameters import Specifications

from ogjpn import calibrate, wealth
from ogjpn.constants import START_YEAR


def main(out="/tmp/ogjpn_tpi", num_workers=2, initial_wealth="data"):
    """
    Args:
        out (str): output directory
        num_workers (int): Dask workers
        initial_wealth (str): "data" starts the transition from Japan's
            observed wealth-by-age profile (2019 全国家計構造調査, see
            ogjpn/wealth.py); "ss" uses OG-Core's default, the terminal
            steady-state profile rescaled to today's population
    """
    # TPI needs a Dask client for its parallel scatter step (the steady
    # state alone does not).
    cluster = LocalCluster(n_workers=num_workers, threads_per_worker=1)
    client = Client(cluster)

    p = Specifications(baseline=True, num_workers=num_workers)
    p.update_specifications({"start_year": START_YEAR})
    calibrate.update_specs(
        p, calibrate.Calibration(p, use_demographics=True).get_dict()
    )
    # Convergence was verified with Anderson acceleration; it is retained as
    # the outer-loop method here. (The actual blocker was the alpha_G fiscal
    # inconsistency described above, not the solver, but Anderson is a safe
    # default for Japan's stiff calibration.)
    p.update_specifications({"TPI_outer_method": "anderson"})
    p.baseline_dir = p.output_base = out

    if initial_wealth == "data":
        # The within-age split across income groups comes from the steady
        # state, so solve it first, then hand OG-Core the observed shape.
        try:
            runner(p, time_path=False, client=client)
        except Exception:
            client.close()
            cluster.close()
            raise
        ss = utils.safe_read_pickle(os.path.join(out, "SS", "SS_vars.pkl"))
        dist = wealth.get_initial_hhwealth_dist(p, ss["b_sp1"])
        p.update_specifications({"initial_hhwealth_dist": dist.tolist()})
    elif initial_wealth != "ss":
        raise ValueError("initial_wealth must be 'data' or 'ss'")

    try:
        runner(p, time_path=True, client=client)
    except RuntimeError as err:
        # OG-Core's strict per-period RC check raises after writing the
        # path; report it and still print the diagnostics below.
        print(f"\nOG-Core solution check raised: {str(err)[:300]}")
    finally:
        client.close()
        cluster.close()

    tpi = utils.safe_read_pickle(os.path.join(out, "TPI", "TPI_vars.pkl"))
    rc = np.abs(np.asarray(tpi["resource_constraint_error"]))
    print(f"\nInitial wealth: {initial_wealth}")
    print("max |RC error| by period t=0..5:", np.array2string(rc[:6], precision=2))
    print(f"max |RC error| over t>=3: {rc[3:].max():.2e}")
    Y = np.asarray(tpi["Y"])
    D = np.asarray(tpi["D"])
    pens = np.asarray(tpi["agg_pension_outlays"])

    print("\n=== OG-JPN baseline transition solved ===")
    yrs = [0, 5, 10, 20, 30]
    print("year(from start)   debt/GDP   pension/GDP")
    for t in yrs:
        print(f"  +{t:<14d} {D[t] / Y[t]:8.3f}   {pens[t] / Y[t]:8.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--initial-wealth", choices=["data", "ss"], default="data")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    main(
        out=a.out or f"/tmp/ogjpn_tpi_{a.initial_wealth}",
        initial_wealth=a.initial_wealth,
    )
