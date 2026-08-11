"""
Store a solved steady state as the warm-start seed.

Run this after any large recalibration, pointing it at a solve that converged:

    python examples/save_warm_start.py examples/OG-JPN-Example/OUTPUT_BASELINE

See ogjpn/warm_start.py for why the seed matters — OG-Core's cold-start values
are badly wrong for a wealthy, ageing population and the solve fails without it.
"""

import os
import sys

from ogcore import utils

from ogjpn import warm_start


def main(out_dir):
    ss = utils.safe_read_pickle(os.path.join(out_dir, "SS", "SS_vars.pkl"))
    path = warm_start.save_seed(ss)
    print(f"wrote warm-start seed to {os.path.relpath(path)}")


if __name__ == "__main__":
    main(sys.argv[1])
