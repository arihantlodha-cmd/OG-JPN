"""
OG-Japan: the standard run — baseline and reform, steady state and transition.

This is the family's conventional entry point (`run_og_<country>.py`) and it
calls the model the way the sibling repos do: one dask client, and **one**
``runner(p, time_path=True, client=client)`` per scenario.

That last point matters. ``ogcore.execute.runner`` always re-solves the steady
state, so splitting a run into a serial SS call followed by a separate TPI call
solves the steady state twice — the second time through the dask client, which
is the slow way round. Keep it as one call.

``TPI_outer_method = "anderson"`` is set in ``ogjpn.macro_params`` rather than
here, so it applies to every run of this calibration and not just this script.
Watch the distance series on a first run: it should decline monotonically. If it
oscillates or stalls, fall back to Picard with a lower ``nu`` — but note that
neither damping nor Anderson fixes a *fiscal* runaway, and neither fixes a
discontinuity in a time-varying input. See ``docs/CALIBRATION_AUDIT.md``.

Usage:
    python examples/run_ogjpn.py                 # baseline + reform, SS + TPI
    python examples/run_ogjpn.py --baseline-only
    python examples/run_ogjpn.py --ss-only
"""

import argparse
import multiprocessing
import os
import time

import numpy as np
from dask.distributed import Client

from ogcore import output_plots as op
from ogcore import output_tables as ot
from ogcore import utils
from ogcore.execute import runner
from ogcore.parameters import Specifications

from ogjpn import calibrate
from ogjpn.constants import COUNTRY_NAME, START_YEAR

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
SAVE_DIR = os.path.join(CUR_PATH, "OG-JPN-Example")
BASE_DIR = os.path.join(SAVE_DIR, "OUTPUT_BASELINE")
REFORM_DIR = os.path.join(SAVE_DIR, "OUTPUT_REFORM")

# The representative reform: Japan's consumption tax from 10% to 12%, sized by
# the revenue it raises rather than by a rate change — the model's consumption
# base is larger than Japan's, so a rate change does not transfer across. See
# examples/analysis_consumption_tax.py.
REVENUE_GAIN_TARGET_SHARE_OF_GDP = 0.0099


def _scalar(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def run_scenario(calibrated, output_dir, num_workers, client,
                 baseline=True, overrides=None, time_path=True):
    """
    Solve one scenario with a single runner call, as the sibling repos do.

    Args:
        calibrated (dict): the Japan calibration
        output_dir (str): where to write SS/ and TPI/ output
        num_workers (int): workers the dask client has
        client (dask Client): parallel client
        baseline (bool): True for the baseline, False for a reform
        overrides (dict): parameters to change relative to the baseline
        time_path (bool): solve the transition as well as the steady state
    """
    p = Specifications(
        baseline=baseline,
        num_workers=num_workers,
        baseline_dir=BASE_DIR,
        output_base=output_dir,
    )
    p.update_specifications({"start_year": START_YEAR})
    p.update_specifications(dict(calibrated, **(overrides or {})))
    runner(p, time_path=time_path, client=client)


def main(baseline_only=False, ss_only=False):
    t0 = time.time()
    num_workers = min(multiprocessing.cpu_count(), 7)
    client = Client(n_workers=num_workers, threads_per_worker=1)
    print(f"Number of workers = {num_workers}")

    try:
        p0 = Specifications(baseline=True, num_workers=num_workers)
        p0.update_specifications({"start_year": START_YEAR})
        calibrated = calibrate.Calibration(p0, use_demographics=True).get_dict()
        print(f"Built the {COUNTRY_NAME} calibration on live UN demographics.")

        print("\n[1] baseline")
        run_scenario(calibrated, BASE_DIR, num_workers, client,
                     baseline=True, time_path=not ss_only)

        if not baseline_only:
            base_ss = utils.safe_read_pickle(
                os.path.join(BASE_DIR, "SS", "SS_vars.pkl")
            )
            # Size the reform off the solved baseline's own consumption base.
            c_share = _scalar(base_ss["C"]) / _scalar(base_ss["Y"])
            tau_c = float(np.asarray(calibrated["tau_c"]).flat[0])
            reform_rate = tau_c + REVENUE_GAIN_TARGET_SHARE_OF_GDP / c_share
            print(
                f"\n[2] reform: tau_c {tau_c:.4f} -> {reform_rate:.4f} "
                f"(+{100*REVENUE_GAIN_TARGET_SHARE_OF_GDP:.2f}pp of GDP)"
            )
            run_scenario(calibrated, REFORM_DIR, num_workers, client,
                         baseline=False, overrides={"tau_c": [[reform_rate]]},
                         time_path=not ss_only)
            _report(ss_only)
    finally:
        client.close()

    print(f"\nrun time = {(time.time() - t0) / 60:.1f} min")


def _report(ss_only):
    """Write the standard comparison tables and plots."""
    base_ss = utils.safe_read_pickle(os.path.join(BASE_DIR, "SS", "SS_vars.pkl"))
    ref_ss = utils.safe_read_pickle(os.path.join(REFORM_DIR, "SS", "SS_vars.pkl"))

    print("\n=== steady-state percent change, reform vs baseline ===")
    print(ot.macro_table_SS(base_ss, ref_ss, include_business_tax=True))

    if ss_only:
        return

    base_p = utils.safe_read_pickle(os.path.join(BASE_DIR, "model_params.pkl"))
    ref_p = utils.safe_read_pickle(os.path.join(REFORM_DIR, "model_params.pkl"))
    base_tpi = utils.safe_read_pickle(os.path.join(BASE_DIR, "TPI", "TPI_vars.pkl"))
    ref_tpi = utils.safe_read_pickle(os.path.join(REFORM_DIR, "TPI", "TPI_vars.pkl"))
    print("\n=== transition, percent change by year ===")
    print(
        ot.macro_table(
            base_tpi, base_p, ref_tpi, ref_p,
            var_list=["Y", "C", "K", "L", "r", "w"],
            output_type="pct_diff", num_years=10, start_year=START_YEAR,
        )
    )
    plot_dir = os.path.join(SAVE_DIR, "plots")
    os.makedirs(plot_dir, exist_ok=True)
    op.plot_all(BASE_DIR, REFORM_DIR, plot_dir)
    print(f"\nplots written to {plot_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-only", action="store_true")
    ap.add_argument("--ss-only", action="store_true")
    args = ap.parse_args()
    main(baseline_only=args.baseline_only, ss_only=args.ss_only)
