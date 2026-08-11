"""
OG-Japan transition-path validation against Japan's actual fiscal accounts.

The steady state is a destination decades away. This is the nearer, harder and
more believable test: does the model reproduce the fiscal accounts Japan is
actually running and is projected to run over the next several years?

It is also the only test that can see the debt LEVEL. In the steady state `D/Y`
is `debt_ratio_ss` -- a policy anchor we chose -- so scoring it there compares a
choice against a measurement and tells you nothing. The transition starts from
`initial_debt_ratio`, which IS a measurement, and every period after that is the
model's own answer. An error in the initial condition is invisible in the SS
dashboard and unmissable here: OG-JPN shipped `initial_debt_ratio = 0.864`
against an actual 1.148 for a full day, in a file whose own `r_gov` derivation
used the correct 114.8%.

Data: OECD Economic Outlook, general government, Japan, pulled live.
    NLGXQ  primary balance, % of GDP
    NLGQ   net lending, % of GDP        (NLGXQ - NLGQ = net interest paid)
    GNFLQ  net financial liabilities, % of GDP
    YPGTQ  government receipts, % of GDP

Run:
    PYTHONPATH=. python examples/validate_fiscal_path.py
"""

import json
import os
import urllib.request

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ogcore import utils

from ogjpn.constants import START_YEAR

OECD = (
    "https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,1.2/"
    "JPN.{code}.A?startPeriod=2015&endPeriod=2027"
    "&dimensionAtObservation=AllDimensions&format=jsondata"
)
CACHE = "ogjpn/data/oecd_fiscal_path.json"
SERIES = ["NLGXQ", "NLGQ", "GNFLQ", "YPGTQ"]
HORIZON = 12  # model periods to score; the OECD projects to 2027


def fetch_oecd():
    """Pull the fiscal series, caching so repeat runs do not hammer the API."""
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    out = {}
    for code in SERIES:
        req = urllib.request.Request(
            OECD.format(code=code), headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            d = json.load(resp)
        dims = d["data"]["structures"][0]["dimensions"]["observation"]
        names = [x["id"] for x in dims]
        ti = names.index("TIME_PERIOD")
        tvals = dims[ti]["values"]
        out[code] = {
            tvals[int(k.split(":")[ti])]["id"]: v[0]
            for k, v in d["data"]["dataSets"][0]["observations"].items()
        }
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(out, open(CACHE, "w"), indent=1)
    return out


def _s(x):
    return float(np.asarray(x).sum()) if np.ndim(x) else float(x)


def model_paths(tpi_dir="examples/OG-JPN-Example/OUTPUT_BASELINE"):
    tpi = utils.safe_read_pickle(os.path.join(tpi_dir, "TPI", "TPI_vars.pkl"))
    Y = np.asarray(tpi["Y"])[:HORIZON]
    if Y.ndim > 1:
        Y = Y.sum(axis=tuple(range(1, Y.ndim)))

    def ratio(key):
        a = np.asarray(tpi[key])[:HORIZON]
        if a.ndim > 1:
            a = a.sum(axis=tuple(range(1, a.ndim)))
        return a / Y

    rev = ratio("total_tax_revenue")
    pension = ratio("agg_pension_outlays")
    # primary spending = G + TR + I_g + pensions (all primary outlays)
    prim_spend = (
        ratio("G") + ratio("TR") + ratio("I_g") + ratio("agg_pension_outlays")
    )
    return {
        "D/Y": ratio("D"),
        "primary balance": rev - prim_spend,
        "revenue/Y": rev,
        "G/Y": ratio("G"),
        "pension/Y": pension,
    }


def main():
    oecd = fetch_oecd()
    years = [str(START_YEAR + t) for t in range(HORIZON)]
    m = model_paths()

    # OECD actuals/projections, converted to model units (fractions of GDP)
    # TIMING. Model D at period t is the stock at the START of year
    # START_YEAR+t, which is the END of the prior year. OECD's "2025" reading is
    # end-2025. So model period t must be scored against OECD year t-1.
    # Getting this wrong reads as a constant +1.4pp bias that is pure convention.
    def shifted(code):
        return {
            y: oecd[code].get(str(int(y) - 1), np.nan) / 100 for y in years
        }

    # CONCEPT. OECD YPGTQ is total government RECEIPTS (tax + non-tax property
    # income, fees, social transfers received). The model's total_tax_revenue is
    # TAX only. Japan's tax take is 33.7% of GDP against receipts of ~40.1%; the
    # ~6.4pp difference is non-tax revenue OG-Core does not model. Scoring
    # against receipts would report a 7pp failure that is entirely definitional.
    data = {
        "D/Y": shifted("GNFLQ"),
        "primary balance": {y: oecd["NLGXQ"].get(y, np.nan) / 100 for y in years},
        "revenue/Y": {y: 0.337 if y in ("2025", "2026") else np.nan for y in years},
        # what Japan actually spends on public pensions now (OECD PaG 2023).
        # This is the RIGHT place for it: the steady state is older than today
        # and must spend more, so scoring 9.3% there distorts the near term.
        "pension/Y": {y: 0.093 if y in ("2025", "2026") else np.nan for y in years},
    }

    print("\n=== OG-Japan fiscal PATH vs Japan's actual accounts ===")
    print("(OECD Economic Outlook; blank = beyond the projection horizon)\n")
    for key in ("D/Y", "primary balance", "revenue/Y", "pension/Y"):
        print(f"{key}")
        print(f"  {'year':6s}{'model':>10s}{'OECD':>10s}{'gap':>10s}")
        for t, y in enumerate(years):
            d = data[key].get(y, np.nan)
            if np.isnan(d):
                print(f"  {y:6s}{m[key][t]:>10.4f}{'--':>10s}{'--':>10s}")
            else:
                print(f"  {y:6s}{m[key][t]:>10.4f}{d:>10.4f}{m[key][t]-d:>+10.4f}")
        print()

    # ---- figure ----
    panels = [
        ("D/Y", "Net debt / GDP  (timing-aligned)", "GNFLQ"),
        ("primary balance", "Primary balance / GDP", "NLGXQ"),
        ("revenue/Y", "Tax revenue / GDP", "OECD RevStats"),
        ("pension/Y", "Public pensions / GDP", "OECD PaG"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(19, 4.6))
    fig.suptitle(
        "OG-Japan: the fiscal path, model vs Japan's actual accounts  "
        "(the near-term test the steady state cannot perform)",
        fontsize=13.5,
        fontweight="bold",
    )
    x = np.arange(HORIZON)
    for ax, (key, title, code) in zip(axes, panels):
        ax.plot(x, m[key], "-o", color="#1f77b4", lw=2.2, ms=5, label="OG-JPN model",
                zorder=3)
        if key in data:
            dv = [data[key].get(y, np.nan) for y in years]
            ax.plot(x, dv, "o", color="#d62728", ms=8, label=f"OECD {code}", zorder=4)
        ax.set_title(title, fontsize=11.5, fontweight="bold")
        ax.set_xticks(x[::2])
        ax.set_xticklabels(years[::2], fontsize=9)
        ax.axhline(0, color="#999", lw=0.8)
        ax.grid(alpha=0.25)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8.5, frameon=False)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    fig.savefig("docs/fiscal_path.png", dpi=150)
    print("wrote docs/fiscal_path.png")


if __name__ == "__main__":
    main()


def diagnose_primary_balance(m):
    """Why the model's early primary balance sits above Japan's actual.

    Two separable causes, both worth stating rather than tuning away:

    1. ogcore clips r_gov at zero, so the model prices debt service at a real
       rate of 0.00% against Japan's actual -0.60%. That raises the
       debt-stabilising primary balance by 0.68pp of GDP -- the model demands a
       tighter fiscal stance than Japan needs purely because of the floor.
    2. debt_ratio_ss = 1.0 against a measured 1.148 asks the model to
       consolidate 15pp of GDP. That surplus is transitional, not structural,
       and it is a POLICY CHOICE: Japan's debt is flat-to-slightly-declining and
       no published program targets 100%.

    pb* = (r_gov - g)/(1+g) * D/Y, g = 0.578%:

        r_gov  0.00% (clipped), D/Y 1.148  ->  pb* = -0.66%
        r_gov  0.00% (clipped), D/Y 1.000  ->  pb* = -0.57%
        r_gov -0.60% (actual),  D/Y 1.148  ->  pb* = -1.34%   <- closest to data
        r_gov -0.60% (actual),  D/Y 1.000  ->  pb* = -1.17%

    Japan actual: -1.89% (2025), -1.08% (2026). The un-clipped rate at the
    measured debt ratio reproduces Japan's fiscal stance; the shipped
    combination does not.
    """
