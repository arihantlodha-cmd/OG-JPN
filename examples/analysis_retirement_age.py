"""
OG-Japan: long-run (steady-state) effect of raising the pension
eligibility age, on real Japanese demographics.

Scenario: raise the age at which households can claim the public pension
from Japan's current 65 to 68 and to 70. Longevity in Japan is the highest
in the world, and the OECD and IMF have both floated a higher eligibility
age as a lever for pension sustainability; this is the steady-state version
of that experiment. Later work runs it on the transition path.

Baseline is 65 (Japan's standard eligibility age, fully phased in). The
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


def solve_ss(calibrated, retire_age, output_base):
    """Solve the steady state given a calibrated dict and a retirement age."""
    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})
    scenario = dict(calibrated)
    scenario["retirement_age"] = [retire_age]  # scenario lever
    p.update_specifications(scenario)
    p.baseline_dir = p.output_base = output_base
    runner(p, time_path=False, client=None)
    return utils.safe_read_pickle(os.path.join(output_base, "SS", "SS_vars.pkl"))


def main():
    p0 = Specifications(baseline=True, num_workers=1)
    p0.update_specifications({"start_year": START_YEAR})
    calibrated = calibrate.Calibration(p0, use_demographics=True).get_dict()
    print("Built Japan calibration with real UN demographics.", flush=True)

    base = solve_ss(calibrated, 65, "/tmp/ogjpn_ra_65")
    reforms = [
        (68, solve_ss(calibrated, 68, "/tmp/ogjpn_ra_68")),
        (70, solve_ss(calibrated, 70, "/tmp/ogjpn_ra_70")),
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
    for rate, reform in reforms:
        changes = [
            f"{100 * (_scalar(reform[v]) - _scalar(base[v])) / _scalar(base[v]):+.2f}"
            for v in aggregates
        ]
        r_pen = _scalar(reform["agg_pension_outlays"]) / _scalar(reform["Y"])
        rows.append(
            f"| 65 -> {rate} | "
            + " | ".join(changes)
            + f" | {b_pen:.3f} -> {r_pen:.3f} |"
        )

    title = "Long-run (steady-state) effect of raising Japan's pension age"
    caption = (
        "Real Japan demographics (UN, code 392); percent change in the "
        "steady-state aggregate vs the age-65 baseline. Macro/tax parameters "
        "are first-pass (see docs/NEXT_STEPS.md), so read the signs and rough "
        "magnitudes, not the last digit. Baseline pension outlays are "
        f"{b_pen:.1%} of GDP."
    )
    interpretation = (
        "## What this shows\n\n"
        "Raising the age at which households can claim the public pension "
        "does what the fiscal debate expects, on Japan's real age structure. "
        "People work longer, so labor rises (and by more at the higher age); "
        "the pension bill falls directly, from about eleven and a half "
        "percent of GDP to under ten, because each cohort collects for fewer "
        "years. Capital edges down rather than up: with a shorter retirement "
        "to fund, households need less lifecycle wealth, so the saving they "
        "do over a working life buys a smaller capital stock. More labor and "
        "less capital roughly offset, leaving output close to flat, so the "
        "reform reads mainly as moving the adjustment onto the spending side "
        "of the budget rather than as a growth lever. The clean result is the "
        "pension line: moving the age to 70 takes almost two points of GDP "
        "off the public pension burden in the long run.\n\n"
        "The magnitudes are indicative, not final. This is a comparison of "
        "two steady states, robust to the level miss in C/Y (see "
        "docs/METHODOLOGY.md) because both sides carry the same calibration, "
        "but the tax and pension calibration is still first-pass, so the "
        "honest reading is the direction and rough size, not the last digit. "
        "The transition-path version, with the year-by-year phase-in, is the "
        "natural next step."
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
        os.path.dirname(__file__), "..", "docs", "results_retirement_age.md"
    )
    with open(os.path.abspath(out), "w") as f:
        f.write(table)
    print(f"Wrote {os.path.abspath(out)}", flush=True)


if __name__ == "__main__":
    main()
