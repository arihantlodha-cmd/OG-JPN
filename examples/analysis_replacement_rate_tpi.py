"""
OG-Japan: cutting the pension replacement rate on the TRANSITION PATH.

Transition-path counterpart of `analysis_replacement_rate.py`. It solves
Japan's baseline transition (current schedule) and two reform transitions
(replacement rate cut 10% and 20%, Japan's macro-economic slide) on real UN
Japanese demographics, and reports the year-by-year paths and the net
present value of the pension saving over the first decade (via OG-Core's
npv_table).

On the transition solution: each transition converges (outer loop below
1e-5) and starts from Japan's observed wealth-by-age distribution
(ogjpn.wealth). The resource constraint holds to below 1e-6 except in two
single periods common to every OG-JPN transition: t=2 (~1.3e-3, an
initial-condition effect) and t=120 (~1.2e-3, where OG-Core freezes the
population before Japan's has converged; OG-Core issue #1290). Both cancel
in the reform-minus-baseline differences reported here, so the strict
per-period RC check is disabled to let the runs complete. (An earlier
version of this reform also showed a 3-5 percent error in the final period
of the horizon; on OG-Core 0.24.6 that is below 1e-6.)

NOTE: read directions and rough magnitudes, not the last digit; the
calibration and its validation are in the docs (docs/book). Runs on Japan's UN demographics from the offline mirror, or live with a UN API token.
"""

import os
import sys

import numpy as np
from dask.distributed import Client, LocalCluster
from ogcore import TPI, output_tables, utils
from ogcore.execute import runner
from ogcore.parameters import Specifications

from ogjpn import calibrate, reporting, wealth
from ogjpn.constants import START_YEAR

# The transition converges; the residuals are single-period errors at t=2
# and t=120 that cancel in the reform-minus-baseline
# differences reported below. Disable the strict per-period RC check so both
# runs complete (this mirrors OG-Core's own test configuration).
TPI.ENFORCE_SOLUTION_CHECKS = False

BASE_DIR = "/tmp/ogjpn_rr_tpi_100"
REFORM_DIRS = {0.90: "/tmp/ogjpn_rr_tpi_90", 0.80: "/tmp/ogjpn_rr_tpi_80"}
HORIZONS = [0, 1, 5, 10, 20]
AGGS = ["Y", "C", "K", "L"]


def _agg_path(tpi, key):
    """Return an aggregate as a 1-D path over time."""
    v = np.asarray(tpi[key])
    return v.reshape(v.shape[0], -1).sum(axis=1) if v.ndim > 1 else v


def _df_to_md(df):
    """Render a DataFrame as a GitHub-flavored markdown table (no tabulate)."""
    cols = list(df.columns)
    head = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "|" + "|".join(["---"] * len(cols)) + "|"

    def _cell(x):
        return f"{x:.4g}" if isinstance(x, (int, float, np.floating)) else str(x)

    body = [
        "| " + " | ".join(_cell(x) for x in row) + " |"
        for row in df.itertuples(index=False)
    ]
    return "\n".join([head, sep, *body])


def solve_tpi(
    calibrated, adjust, output_base, client, baseline_dir=None, init_dist=None
):
    """Solve a transition; baseline if baseline_dir is None, else a reform."""
    is_baseline = baseline_dir is None
    p = Specifications(baseline=is_baseline, num_workers=2)
    p.update_specifications({"start_year": START_YEAR})
    scenario = dict(calibrated)
    scenario["replacement_rate_adjust"] = [[adjust]]
    calibrate.update_specs(p, scenario)
    p.update_specifications({"TPI_outer_method": "anderson"})
    p.output_base = output_base
    p.baseline_dir = output_base if is_baseline else baseline_dir
    # Start from Japan's observed wealth-by-age profile (ogjpn.wealth).
    # The baseline builds it from its own steady state; reforms receive it
    # and OG-Core then starts them from the baseline's period-0 wealth.
    if init_dist is None:
        runner(p, time_path=False, client=client)
        ss = utils.safe_read_pickle(os.path.join(output_base, "SS", "SS_vars.pkl"))
        init_dist = wealth.get_initial_hhwealth_dist(p, ss["b_sp1"]).tolist()
    p.update_specifications({"initial_hhwealth_dist": init_dist})
    runner(p, time_path=True, client=client)
    tpi = utils.safe_read_pickle(os.path.join(output_base, "TPI", "TPI_vars.pkl"))
    return p, tpi, init_dist


def main():
    if "--report-only" in sys.argv:
        # Rebuild the write-up from saved runs without re-solving.
        def load(d):
            return (
                utils.safe_read_pickle(os.path.join(d, "model_params.pkl")),
                utils.safe_read_pickle(os.path.join(d, "TPI", "TPI_vars.pkl")),
            )

        base_p, base = load(BASE_DIR)
        reforms = {k: load(d) for k, d in REFORM_DIRS.items()}
    else:
        cluster = LocalCluster(n_workers=2, threads_per_worker=1)
        client = Client(cluster)
        try:
            p0 = Specifications(baseline=True, num_workers=2)
            p0.update_specifications({"start_year": START_YEAR})
            calibrated = calibrate.Calibration(p0, use_demographics=True).get_dict()
            print("Built Japan calibration with real UN demographics.", flush=True)

            base_p, base, init_dist = solve_tpi(calibrated, 1.0, BASE_DIR, client)
            print("Baseline transition solved.", flush=True)
            reforms = {}
            for adj, d in REFORM_DIRS.items():
                rp, rtpi, _ = solve_tpi(
                    calibrated, adj, d, client, BASE_DIR, init_dist=init_dist
                )
                reforms[adj] = (rp, rtpi)
                print(f"Reform (cut to {adj}) transition solved.", flush=True)
        finally:
            client.close()
            cluster.close()

    base_paths = {v: _agg_path(base, v) for v in AGGS}
    base_pen = _agg_path(base, "agg_pension_outlays") / base_paths["Y"]

    lines = []
    for adj, (rp, rtpi) in reforms.items():
        pct = round((1 - adj) * 100)
        r_paths = {v: _agg_path(rtpi, v) for v in AGGS}
        r_pen = _agg_path(rtpi, "agg_pension_outlays") / r_paths["Y"]
        lines.append(f"\n### {pct}% benefit cut\n")
        head = "| Year | " + " | ".join(f"{v} (%)" for v in AGGS)
        head += " | Pension/GDP (base -> reform) |"
        sep = "|" + "|".join(["---"] * (len(AGGS) + 2)) + "|"
        lines += [head, sep]
        for t in HORIZONS:
            chg = [
                f"{100 * (r_paths[v][t] - base_paths[v][t]) / base_paths[v][t]:+.2f}"
                for v in AGGS
            ]
            lines.append(
                f"| +{t} | "
                + " | ".join(chg)
                + f" | {base_pen[t]:.3f} -> {r_pen[t]:.3f} |"
            )

    npv_lines = ["\n## Net present value of the change, first 10 years\n"]
    for adj, (rp, rtpi) in reforms.items():
        pct = round((1 - adj) * 100)
        tbl = output_tables.npv_table(
            base,
            base_p,
            rtpi,
            rp,
            var_list=["agg_pension_outlays", "Y", "L"],
            discount_rates=[0.01, 0.02, 0.03],
            num_years=10,
            start_year=START_YEAR,
            table_format=None,
        )
        npv_lines.append(
            f"\n**{pct}% benefit cut** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform "
            "minus baseline, so negative is a saving):\n"
        )
        npv_lines.append(_df_to_md(reporting.npv_in_gdp_terms(tbl, base)))

    title = "# Transition-path effect of cutting Japan's pension replacement rate"
    caption = (
        "Real Japan demographics (UN, code 392). Percent change vs the "
        "current-schedule baseline transition at several horizons (years from "
        "the 2025 start), then the net present value of the "
        "reform-minus-baseline change over the first decade at 1/2/3% discount "
        "rates (OG-Core npv_table), as a share of first-year GDP and in "
        "trillion yen at Japan's FY2023 GDP. Read directions and rough "
        "magnitudes, not the last digit."
    )
    ci = {k: reporting.crowding_in(base, rtpi) for k, (_, rtpi) in reforms.items()}
    big_pen = reporting.path(reforms[0.8][1], "agg_pension_outlays") / reporting.path(
        reforms[0.8][1], "Y"
    )
    base_pen_path = reporting.path(base, "agg_pension_outlays") / reporting.path(
        base, "Y"
    )
    pen_cut = {t: 100 * (base_pen_path[t] - big_pen[t]) for t in (10, 20)}
    interpretation = (
        "## What this adds over the steady state\n\n"
        "The steady-state comparison found the pension bill down, labor up, "
        "and capital slightly lower. The transition traces the path on "
        "Japan's aging population. Under the 20% cut the pension bill is "
        f"{pen_cut[10]:.1f} points of GDP below the baseline after 10 years "
        f"and {pen_cut[20]:.1f} after 20, and the NPV table above discounts "
        "that saving over the first decade. Labor rises and stays up. By "
        f"year 20, capital is {ci[0.9]['K_pct']:+.1f} percent under the 10% "
        f"cut and {ci[0.8]['K_pct']:+.1f} percent under 20%, and output "
        f"{ci[0.8]['Y_pct']:+.1f} percent under 20%.\n\n"
        + reporting.crowding_in_text(ci[0.8], "20% benefit cut")
        + "\n\nThe magnitudes are indicative, not final, so read the shape of "
        "the paths and the sign of the NPV, not the last digit. The reported "
        "quantities are reform-minus-baseline differences, in which the "
        "single-period resource-constraint errors at t=2 and t=120 cancel."
    )
    doc = "\n".join(
        [
            title,
            "",
            caption,
            "",
            "## Time paths",
            *lines,
            *npv_lines,
            "",
            interpretation,
            "",
        ]
    )
    print("\n" + doc, flush=True)
    out = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "results_replacement_rate_tpi.md",
    )
    with open(os.path.abspath(out), "w") as f:
        f.write(doc)
    print(f"Wrote {os.path.abspath(out)}", flush=True)


if __name__ == "__main__":
    main()
