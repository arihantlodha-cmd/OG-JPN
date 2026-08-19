"""
OG-Japan validation: solve the steady state on real Japanese demographics
and macro parameters, and compare the model's key ratios to Japan's actual
values. This is a sanity check on the calibration, not a policy run.
"""

import os

import numpy as np
from ogcore import utils
from ogcore.execute import runner
from ogcore.parameters import Specifications

from ogjpn import calibrate
from ogjpn.constants import START_YEAR


def _s(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def main(out="/tmp/ogjpn_validate"):
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    p.update_specifications(
        calibrate.Calibration(p, use_demographics=True).get_dict()
    )
    p.baseline_dir = p.output_base = out
    runner(p, time_path=False, client=None)
    ss = utils.safe_read_pickle(os.path.join(out, "SS", "SS_vars.pkl"))

    Y, K, C = _s(ss["Y"]), _s(ss["K"]), _s(ss["C"])
    rows = [
        ("Capital-output K/Y", K / Y, "~3.0-3.5"),
        ("Consumption/GDP C/Y", C / Y, "~0.53-0.55"),
        ("Interest rate r", _s(ss["r"]), "~0.01-0.04"),
        ("Pension outlays/GDP", _s(ss["agg_pension_outlays"]) / Y, "~0.10-0.11"),
        ("Debt/GDP", _s(ss["D"]) / Y, "~2.1 (gross)"),
        ("Tax revenue/GDP", _s(ss["total_tax_revenue"]) / Y, "~0.20-0.30"),
    ]
    print("\n=== OG-Japan steady state vs Japan (rough actuals) ===")
    for name, model, actual in rows:
        print(f"{name:22s} model={model:8.3f}   japan {actual}")


if __name__ == "__main__":
    main()
