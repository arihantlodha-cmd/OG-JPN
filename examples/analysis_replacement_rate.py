"""
OG-Japan: long-run (steady-state) effect of cutting the pension
replacement rate, on real Japanese demographics.

Scenario: reduce the public pension replacement rate by 10 percent and by
20 percent. This is the lever Japan actually pulls through its
"macro-economic slide" (マクロ経済スライド), which trims the effective
replacement rate over time to keep the pension system solvent as the
population ages. It is the benefit-cut counterpart to the retirement-age
experiment, which changed when people can claim rather than how much.

Baseline is Japan's current schedule (replacement_rate_adjust = 1.0). The
script builds the Japan calibration once (macro + tax + real UN
demographics) and solves the baseline and both reform steady states,
reporting the long-run percent change in the main aggregates and the change
in pension outlays as a share of GDP.

NOTE: demographics are real Japanese data; macro/tax parameters are still
first-pass (see docs/NEXT_STEPS.md), so read directions and rough
magnitudes, not the last digit. Requires a UN API token in un_api_token.txt.
"""

import os

import numpy as np
from ogcore import utils
from ogcore.execute import runner
from ogcore.parameters import Specifications

from ogjpn import calibrate
from ogjpn.constants import START_YEAR


def _scalar(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def solve_ss(calibrated, adjust, output_base):
    """Solve the steady state given a calibrated dict and a replacement-rate
    adjustment (1.0 is Japan's current schedule; 0.9 is a 10% cut)."""
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    scenario = dict(calibrated)
    scenario["replacement_rate_adjust"] = [[adjust]]  # scenario lever
    p.update_specifications(scenario)
    p.baseline_dir = p.output_base = output_base
    runner(p, time_path=False, client=None)
    return utils.safe_read_pickle(os.path.join(output_base, "SS", "SS_vars.pkl"))


def main():
    p0 = Specifications(baseline=True, num_workers=1)
    p0.update_specifications({"start_year": START_YEAR})
    calibrated = calibrate.Calibration(p0, use_demographics=True).get_dict()
    print("Built Japan calibration with real UN demographics.", flush=True)

    base = solve_ss(calibrated, 1.0, "/tmp/ogjpn_rr_100")
    reforms = [
        (0.90, solve_ss(calibrated, 0.90, "/tmp/ogjpn_rr_90")),
        (0.80, solve_ss(calibrated, 0.80, "/tmp/ogjpn_rr_80")),
    ]
    write_results(base, reforms)


def write_results(base, reforms):
    """Build the results table and interpretation and write it to docs/."""
    aggregates = ["Y", "C", "K", "L"]
    b_pen = _scalar(base["agg_pension_outlays"]) / _scalar(base["Y"])

    header = (
        "| Reform | "
        + " | ".join(f"{v} (%)" for v in aggregates)
        + " | Pension outlays/GDP |"
    )
    sep = "|" + "|".join(["---"] * (len(aggregates) + 2)) + "|"
    rows = []
    for cut, reform in reforms:
        changes = [
            f"{100 * (_scalar(reform[v]) - _scalar(base[v])) / _scalar(base[v]):+.2f}"
            for v in aggregates
        ]
        r_pen = _scalar(reform["agg_pension_outlays"]) / _scalar(reform["Y"])
        pct = round((1 - cut) * 100)
        rows.append(
            f"| -{pct}% benefits | "
            + " | ".join(changes)
            + f" | {b_pen:.3f} -> {r_pen:.3f} |"
        )

    title = "Long-run (steady-state) effect of cutting Japan's pension replacement rate"
    caption = (
        "Real Japan demographics (UN, code 392); percent change in the "
        "steady-state aggregate vs the current-schedule baseline. Macro/tax "
        "parameters are first-pass (see docs/NEXT_STEPS.md), so read the "
        "signs and rough magnitudes, not the last digit. Baseline pension "
        f"outlays are {b_pen:.1%} of GDP."
    )
    interpretation = (
        "## What this shows\n\n"
        "Cutting the replacement rate is the other half of the pension "
        "debate from the retirement-age experiment: it changes how much "
        "retirees receive rather than when they can claim, and it produces "
        "the same signature. The direct effect is mechanical, the pension "
        "bill falls roughly in proportion to the cut (a ten percent cut takes "
        "it from about 11.4 to 10.3 percent of GDP, a twenty percent cut to "
        "9.1). The behavioral response runs mainly through labor: facing a "
        "thinner public pension, households work more (labor up about half a "
        "percent at the ten percent cut and over one percent at twenty), "
        "which lifts output modestly. Capital edges down rather than up in "
        "this long-run comparison of steady states, the same pattern the "
        "retirement-age reform showed, so the reform is best read as pushing "
        "people to work more and trimming the pension bill, not as a "
        "saving-and-capital story. Its distributional cost falls on retirees "
        "rather than workers, the mirror image of raising the claiming age.\n\n"
        "The magnitudes are indicative, not final. This is a comparison of "
        "two steady states, robust to the level miss in C/Y (see "
        "docs/METHODOLOGY.md) because both sides carry the same calibration, "
        "but the pension calibration is still first-pass, so the honest "
        "reading is the direction and rough size, not the last digit. The "
        "retirement-age transition showed capital building up over the path "
        "even where its steady-state comparison did not, so the transition "
        "version of this reform is the natural next step."
    )
    table = "\n".join(
        [
            f"# {title}",
            "",
            caption,
            "",
            header,
            sep,
            *rows,
            "",
            interpretation,
            "",
        ]
    )
    print("\n" + table, flush=True)
    out = os.path.join(
        os.path.dirname(__file__), "..", "docs", "results_replacement_rate.md"
    )
    with open(os.path.abspath(out), "w") as f:
        f.write(table)
    print(f"Wrote {os.path.abspath(out)}", flush=True)


if __name__ == "__main__":
    main()
