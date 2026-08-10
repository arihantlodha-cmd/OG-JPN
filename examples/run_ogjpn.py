"""
OG-Japan: the standard run — baseline and reform, steady state and transition.

This is the family's conventional entry point (`run_og_<country>.py`): it solves
a baseline, solves one representative reform, and writes the comparison tables
and plots. Edit ``REFORM`` below to run a different policy.

Run engineering follows the family's guidance, which is not cosmetic:

  * the STEADY STATE is solved SERIALLY (``client=None``). Dask's distribution
    overhead dominates a steady-state solve — the family has measured 12+
    minutes through a 7-worker client against ~1 minute serial.
  * the TRANSITION is solved in PARALLEL, because TPI genuinely benefits from
    parallelism across the J lifetime-income groups.
  * ``TPI_outer_method = "anderson"`` (set in ogjpn.macro_params) replaces
    damped Picard iteration on the outer loop. Watch the distance series on a
    first run: it should decline monotonically. If it oscillates or stalls, fall
    back to Picard with a lower ``nu``.

Neither Anderson nor damping fixes a *fiscal* runaway. If the baseline
transition diverges, check the government budget identity first — see
``docs/CALIBRATION_AUDIT.md``.

Usage:
    python examples/run_ogjpn.py                # baseline + reform, SS + TPI
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
BASE_DIR = os.path.join(CUR_PATH, "OUTPUT_BASELINE")
REFORM_DIR = os.path.join(CUR_PATH, "OUTPUT_REFORM")

# The representative reform: Japan's consumption tax from 10% to 12%, sized by
# the revenue it raises rather than by a rate change. See
# examples/analysis_consumption_tax.py for why that distinction matters.
REVENUE_GAIN_TARGET_SHARE_OF_GDP = 0.0099


def _scalar(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def build_calibration():
    """Assemble the Japan calibration once; demographics are pulled here."""
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    return calibrate.Calibration(p, use_demographics=True).get_dict()


def solve(calibrated, output_dir, baseline=True, overrides=None,
          time_path=True, client=None, num_workers=1):
    """
    Solve one scenario.

    Args:
        calibrated (dict): the Japan calibration
        output_dir (str): where to write SS/ and TPI/ output
        baseline (bool): True for the baseline, False for a reform
        overrides (dict): parameters to change relative to the baseline
        time_path (bool): solve the transition as well as the steady state
        client (dask Client): parallel client, or None to run serially
        num_workers (int): workers the client has

    Returns:
        str: the output directory
    """
    p = Specifications(
        baseline=baseline, num_workers=num_workers, output_base=output_dir
    )
    p.update_specifications({"start_year": START_YEAR})
    p.update_specifications(dict(calibrated, **(overrides or {})))
    p.baseline_dir = BASE_DIR
    p.output_base = output_dir
    runner(p, time_path=time_path, client=client)
    return output_dir


def main(baseline_only=False, ss_only=False):
    t0 = time.time()
    calibrated = build_calibration()
    print(f"Built the {COUNTRY_NAME} calibration on live UN demographics.")

    # --- baseline -------------------------------------------------------
    # SS serial: the dask client's overhead dominates a steady-state solve.
    print("\n[1] baseline steady state (serial)")
    solve(calibrated, BASE_DIR, baseline=True, time_path=False)

    client, workers = None, 1
    if not ss_only:
        workers = max(1, multiprocessing.cpu_count() - 2)
        client = Client(n_workers=workers, threads_per_worker=1)
        print(f"\n[2] baseline transition (Anderson, {workers} workers)")
        solve(calibrated, BASE_DIR, baseline=True, time_path=True,
              client=client, num_workers=workers)

    try:
        if not baseline_only:
            base_ss = utils.safe_read_pickle(
                os.path.join(BASE_DIR, "SS", "SS_vars.pkl")
            )
            # Size the reform off the solved baseline's own consumption base.
            c_share = _scalar(base_ss["C"]) / _scalar(base_ss["Y"])
            tau_c = np.asarray(calibrated["tau_c"]).flat[0]
            reform = {
                "tau_c": [[tau_c + REVENUE_GAIN_TARGET_SHARE_OF_GDP / c_share]]
            }
            print(
                f"\n[3] reform: tau_c {tau_c:.4f} -> "
                f"{reform['tau_c'][0][0]:.4f} "
                f"(+{100*REVENUE_GAIN_TARGET_SHARE_OF_GDP:.2f}pp of GDP)"
            )
            solve(calibrated, REFORM_DIR, baseline=False, overrides=reform,
                  time_path=not ss_only, client=client, num_workers=workers)

            _report(ss_only)
    finally:
        if client is not None:
            client.close()

    print(f"\ndone in {(time.time() - t0) / 60:.1f} min")


def _report(ss_only):
    """Write the standard comparison tables and plots."""
    base_ss = utils.safe_read_pickle(os.path.join(BASE_DIR, "SS", "SS_vars.pkl"))
    ref_ss = utils.safe_read_pickle(os.path.join(REFORM_DIR, "SS", "SS_vars.pkl"))
    base_p = utils.safe_read_pickle(os.path.join(BASE_DIR, "model_params.pkl"))
    ref_p = utils.safe_read_pickle(os.path.join(REFORM_DIR, "model_params.pkl"))

    print("\n=== steady-state percent change, reform vs baseline ===")
    print(ot.macro_table_SS(base_ss, ref_ss, include_business_tax=True))

    if ss_only:
        return

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
    plot_dir = os.path.join(CUR_PATH, "OUTPUT_REFORM", "plots")
    os.makedirs(plot_dir, exist_ok=True)
    op.plot_all(BASE_DIR, REFORM_DIR, plot_dir)
    print(f"\nplots written to {plot_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-only", action="store_true")
    ap.add_argument("--ss-only", action="store_true")
    args = ap.parse_args()
    main(baseline_only=args.baseline_only, ss_only=args.ss_only)
