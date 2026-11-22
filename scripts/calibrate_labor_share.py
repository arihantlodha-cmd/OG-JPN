"""
Iterate the labor share of income by age to a fixed point.

The progressive income tax (ogjpn.income_tax.age_specific_params) splits
each age's income into labor and capital using the labor share at that
age, which itself depends on the steady state the tax produces. Starting
from the stored shares, this solves the steady state, recomputes the
shares, and repeats until they stop moving, then writes
ogjpn/data/labor_share_by_age.csv.

    python scripts/calibrate_labor_share.py [--seed-from DIR] [--tol 1e-3]

``--seed-from`` writes the shares implied by an existing steady state
(DIR/SS/SS_vars.pkl and DIR/model_params.pkl) without solving.
"""

import argparse
import os

import numpy as np
import pandas as pd
from ogcore import utils
from ogcore.execute import runner
from ogcore.parameters import Specifications

from ogjpn import calibrate
from ogjpn import income_tax as it
from ogjpn.constants import START_YEAR

CSV = os.path.join(
    os.path.dirname(__file__), "..", "ogjpn", "data", "labor_share_by_age.csv"
)


def write(labor_share):
    pd.DataFrame(
        {"model_age": np.arange(len(labor_share)), "labor_share": labor_share}
    ).to_csv(CSV, index=False, float_format="%.6f")


def shares_from(out):
    ss = utils.safe_read_pickle(os.path.join(out, "SS", "SS_vars.pkl"))
    p = utils.safe_read_pickle(os.path.join(out, "model_params.pkl"))
    return it.labor_share_by_age(ss, p), ss


def solve(labor_share, out):
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    calibrate.update_specs(
        p,
        calibrate.Calibration(
            p, use_demographics=True, labor_share=labor_share
        ).get_dict(),
    )
    p.baseline_dir = p.output_base = out
    runner(p, time_path=False, client=None)
    return shares_from(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-from")
    ap.add_argument("--tol", type=float, default=1e-3)
    ap.add_argument("--max-iter", type=int, default=6)
    ap.add_argument("--out", default="/tmp/ogjpn_labor_share")
    args = ap.parse_args()

    if args.seed_from:
        lam, _ = shares_from(args.seed_from)
        write(lam)
        print("seeded from", args.seed_from)
        return

    lam = it.load_labor_share_by_age()
    for k in range(args.max_iter):
        new, ss = solve(lam, f"{args.out}_{k}")
        change = float(np.max(np.abs(new - lam)))
        Y = float(ss["Y"])
        print(
            f"iteration {k}: max change {change:.2e}, "
            f"PIT/GDP {float(ss['iit_revenue']) / Y:.4f}, "
            f"revenue/GDP {float(ss['total_tax_revenue']) / Y:.4f}, "
            f"G/GDP {float(ss['G']) / Y:.4f}",
            flush=True,
        )
        lam = new
        write(lam)
        if change < args.tol:
            break


if __name__ == "__main__":
    main()
