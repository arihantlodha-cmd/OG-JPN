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
| `alpha_G` | govt purchases / GDP | NOT the ~0.20 national-accounts figure: this is residual purchases after pensions and transfers, and must equal the steady-state `G/Y` (~0.054) or the transition breaks (see item 4) |
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

## 4. Transition path: converges, with one open refinement

The baseline transition converges (`examples/run_ogjpn_tpi.py`). The
blocker was a fiscal-block inconsistency, not solver tuning: `alpha_G` was
set to Japan's ~20% national-accounts government consumption, but before
the debt-closure rule engages the transition spends `G = alpha_G * Y`
directly, about four times what the budget can sustain, so debt exploded.
Setting `alpha_G` to the steady-state residual share (~0.054) fixed it (see
METHODOLOGY and item 1). The outer loop now reaches its 1e-5 tolerance in
about thirteen iterations and debt holds near 2.0 across the path.

Open refinement (the initial wealth distribution). The resource constraint
holds to ~1e-7 at every period except the second, where a single localized
~1.8e-3 spike survives. It is Japan-specific: a plain OG-Core baseline is
clean there. The cause is the initial condition. OG-Core seeds a baseline
transition from the terminal steady state's wealth-by-age profile scaled to
the initial population (`TPI.get_initial_SS_values`, the `initial_b` line),
and Japan's terminal stable population differs so sharply from today's that
the proxy is a poor starting distribution, surfacing as one seam at the
start. It does not propagate and cancels in reform-minus-baseline
differences, so policy results are unaffected.

Eliminating it properly is a two-part contribution, scoped here as a
follow-up:

1. **Upstream OG-Core feature.** Add a way to inject a custom initial
   wealth distribution into a baseline transition. Today there is no hook:
   `initial_b` is always derived from the SS inside
   `get_initial_SS_values`, and the only `initial_*` parameters are for
   debt, foreign debt, and solver guesses. A clean design is an optional
   `initial_b_distribution` parameter (S x J, defaulting to the current
   SS-derived behavior when unset) so every country model can pass an
   observed distribution. This is a self-contained PR in the same spirit as
   the earlier OG-Core contributions.
2. **Japan wealth-by-age data.** Feed that hook Japan's observed household
   net worth by age of head, published in the National Survey of Family
   Income and Expenditure (全国家計構造調査, formerly 全国消費実態調査,
   Statistics Bureau). Map it onto the model's S ages and J lifetime-income
   groups.

Until then the transition is used as-is for policy (item 5), which is
valid because the artifact differences out.

## 5. After Phases 1 and 2: the payoff (Phase 3)

Done (steady-state version): `examples/analysis_consumption_tax.py` runs
Japan's consumption tax at 10% (actual), 12%, and 15% (the IMF's
recommendation) and compares the steady states on real demographics. The
writeup is `docs/results_consumption_tax.md`.

Done (transition version): `examples/analysis_consumption_tax_tpi.py` runs
the same reform on the transition path and reports the year-by-year paths
plus the NPV of the revenue change via OG-Core's `npv_table` (#1195). The
writeup is `docs/results_consumption_tax_tpi.md`. It shows the capital stock
building up over the horizon as the consumption tax tilts households toward
saving, which the steady-state comparison could not.

Done (second reform, steady-state): `examples/analysis_retirement_age.py`
raises Japan's pension eligibility age from 65 to 68 and 70 and compares the
steady states. The writeup is `docs/results_retirement_age.md`. It takes
almost two points of GDP off the public pension burden at age 70 (11.4% to
9.5%), with labor up and output roughly flat.

Still to do: the initial-condition refinement in item 4 (removes the one
residual t=2 artifact); the transition-path version of the retirement-age
reform; and a pension-replacement-rate change (Japan's macro-economic slide,
マクロ経済スライド).

## How to run

```
PYTHONPATH=. python examples/run_ogjpn_ss.py   # steady state
PYTHONPATH=. python -m pytest tests/           # scaffolding tests
```
