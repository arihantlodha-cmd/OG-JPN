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

- Done: consumption tax `tau_c = 0.10` (Japan since Oct 2019). Adding it
  is what made the steady-state budget close with positive G.
- To do: income and payroll effective/marginal tax rate functions. Japan
  has no open tax microsimulator (the US models use Tax-Calculator), so
  fit OG-Core's simpler tax functions to **published Japanese effective
  tax rates** by age/income. Start with OG-Core's `tax_func_type="linear"`
  or a low-order polynomial and target Japan's income-tax and social-
  insurance revenue as a share of GDP (NTA / MOF / OECD Revenue
  Statistics). Set `frac_tax_payroll` or `tau_payroll` for social
  insurance contributions.

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

Pick one real Japanese policy question and run baseline vs reform:
a consumption-tax change, a higher retirement age, or a pension reform.
Then use the `npv_table` you added to OG-Core (#1195) to report the NPV
of the change in GDP, and write it up. That writeup is the artifact.

## How to run

```
PYTHONPATH=. python examples/run_ogjpn_ss.py   # steady state
PYTHONPATH=. python -m pytest tests/           # scaffolding tests
```
