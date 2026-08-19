# OG-Japan: what to do next (driving Phases 1 and 2 to completion)

The scaffolding is built and the pipeline solves. What remains is mostly
**data you fetch and verify**, not more code. This is the concrete list.

## 0. Unblock demographics (do this first, ~15 min)

Live Japan demographics need a free UN Data Portal API token.

1. Register at the UN Data Portal and request an API token
   (https://population.un.org/dataportal/about/dataapi).
2. Save the token as `un_api_token.txt` in the directory you run from
   (already in `.gitignore`, so it will not be committed).
3. Run `PYTHONPATH=. python examples/run_ogjpn_ss.py`. The console should
   say "Loaded Japan demographics + macro + tax" instead of falling back.

That single step is what makes the model actually about Japan rather than
US demographics.

## 1. Verify / replace the macro parameters (`ogjpn/macro_params.py`)

Every value there is a provisional placeholder. Replace each with a
sourced figure. Mapping of OG-Core parameter -> what to look up -> source:

| Parameter | What it is | Where to get it |
|---|---|---|
| `g_y_annual` | long-run real GDP-per-worker growth | OECD productivity, or World Bank GDP-per-capita growth trend |
| `gamma` | capital share of income | Penn World Table (1 - labor share) for Japan |
| `initial_debt_ratio` | govt debt / GDP at start | IMF WEO (net general govt debt ~1.5; gross ~2.5) |
| `alpha_G` | govt consumption / GDP | OECD govt final consumption / GDP (~0.20) |
| `alpha_T` | non-pension transfers / GDP | OECD social spending less public pensions, / GDP |

Follow OG-THA's `macro_params.py` if you want to pull these from an API
(it reads FRED and the World Bank) instead of hardcoding.

## 2. Finish the tax calibration (`ogjpn/tax_params.py`)

- Done (first-pass): linear (constant-rate) tax functions from published
  Japanese rates. Income tax ~8% average with a 30% marginal (NTA schedule
  plus 10% local, OECD Taxing Wages effective rates), pension payroll
  18.3%, capital income 20.315%, corporate ~30%, consumption 10%. This is
  what makes the budget close with positive `G` at Japan's debt target,
  where the US-default tax functions did not (see METHODOLOGY).
- To do: replace the single average income-tax rate with Japan's actual
  progression, using a low-order polynomial or `GS`/`mono` tax function
  fit to effective rates across the income distribution (the piece a
  microsimulator would give, so it needs the distribution behind the
  OECD/NTA rates). Model the non-pension social insurance (health,
  long-term care, employment) and set `frac_tax_payroll` accordingly.
  Validate against Japan's income-tax and social-insurance revenue shares
  of GDP (OECD Revenue Statistics).

## 3. Give back upstream (helps every future Japan run)

1. Add `"392": "JPN"` to the `country_dict` in `ogcore/demographics.py`
   -- but only together with (2), since the entry is useless without data
   behind it.
2. Contribute Japan's demographic CSVs (fertility, mortality, population)
   to `EAPD-DRB/Population-Data` in the same format as the other
   countries, so Japan works offline like they do. You can generate these
   from the UN API once you have the token.

## 4. Known issue: slow convergence

With the current parameters the steady state converges but sits in a long
outer-loop plateau first (it can look hung for minutes). If that bites,
try a lower `nu` (more damping) or `SS_root_method` / Anderson
acceleration. This is the same class of problem as OG-Core PR #1178
(TPI stall detection).

## 5. After Phases 1 and 2: the payoff (Phase 3)

Done (steady-state version): `examples/analysis_consumption_tax.py` runs
Japan's consumption tax at 10% (actual), 12%, and 15% (the IMF's
recommendation) and compares the steady states on real demographics. The
writeup is `docs/results_consumption_tax.md`.

Still to do: run the same reform on the transition path (once it
converges, see item 4 and the K/Y and C/Y calibration) and use the
`npv_table` added to OG-Core (#1195) to report the NPV of the change in
GDP. Other reforms worth the same treatment: a higher retirement age or a
pension-replacement-rate change.

## How to run

```
PYTHONPATH=. python examples/run_ogjpn_ss.py   # steady state
PYTHONPATH=. python -m pytest tests/           # scaffolding tests
```
