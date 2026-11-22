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

1. **Upstream OG-Core feature.** Done and submitted: OG-Core PR #1209 adds
   a `use_initial_b_dist` flag and an `initial_b_dist` (S x J) array so a
   country model can supply an observed initial wealth distribution. When
   the flag is off (default) `get_initial_SS_values` reproduces the old
   SS-derived `initial_b` exactly; when on it takes the shape from
   `initial_b_dist` and still rescales the aggregate to the steady-state B.
2. **Japan wealth-by-age data.** Feed that hook Japan's observed household
   net worth by age of head, published in the National Survey of Family
   Income and Expenditure (全国家計構造調査, formerly 全国消費実態調査,
   Statistics Bureau). Map it onto the model's S ages and J lifetime-income
   groups. This is the remaining piece once #1209 lands.

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

Done (second reform, both versions): `examples/analysis_retirement_age.py`
raises Japan's pension eligibility age from 65 to 68 and 70 and compares the
steady states (`docs/results_retirement_age.md`); it takes almost two points
of GDP off the public pension burden at age 70 (11.4% to 9.5%), with labor
up and output roughly flat. The transition version
(`examples/analysis_retirement_age_tpi.py`,
`docs/results_retirement_age_tpi.md`) traces the pension bill falling year by
year and the NPV of the saving; it also shows capital building up over the
horizon, the same transition feature the consumption-tax reform showed and
the opposite of what the steady-state end-point comparison suggested.

Done (third reform, both versions): `examples/analysis_replacement_rate.py`
cuts the pension replacement rate by 10% and 20% (Japan's macro-economic
slide, マクロ経済スライド), in `docs/results_replacement_rate.md`; the pension
bill falls (11.4% of GDP to 10.3% and 9.1%), labor rises, and capital edges
down in the steady-state comparison. The transition version
(`examples/analysis_replacement_rate_tpi.py`,
`docs/results_replacement_rate_tpi.md`) traces the pension saving year by
year with its NPV and, like the other two transitions, shows capital building
up over the horizon rather than down. All three reforms (consumption tax,
retirement age, replacement rate) now have both a steady-state and a
transition writeup.

Still to do: the initial-condition refinement in item 4 (removes the one
residual t=2 artifact). OG-Core now has the hook for item 4 submitted as
PR #1209 (a supplied initial wealth distribution); pairing it with Japan's
observed wealth-by-age data is what closes the artifact.

## 6. The income anchor is still US-based (needed for currency output)

Found while wiring up OG-Core's `npv_table` currency option: OG-JPN never
sets `mean_income_data`, so it inherits OG-Core's US default (about
$58,645). `factor = mean_income_data / average_income_model` therefore
anchors the model to US dollars, not yen, so NPVs and any other
currency-denominated output cannot simply be relabeled as yen. Two
consequences:

- To report results in yen, set `mean_income_data` to Japan's mean income
  from a published source (for example the National Tax Agency 民間給与実態
  統計調査 average annual salary, or the MHLW 国民生活基礎調査 mean household
  income), with the year and figure documented.
  Sourced candidate (Nov 2026): OG-Core defines `mean_income_data` as mean
  income in the tax microdata (per tax unit), so the closest Japanese
  concept is the NTA 民間給与実態統計調査 mean annual salary of full-year
  private-sector earners: 4.60 million yen for 2023 and 4.78 million yen
  for 2024 (令和6年分). Use 4.78 million yen (2024) with the start year.
- `factor` feeds the pension replacement rate `theta`, and the default
  pension benefit formula (US Social Security bend points) is dollar-
  denominated, so changing the anchor by the roughly 78x dollar-to-yen
  scale would flow into the pension block. The current pension result
  (outlays about 11.4% of GDP, which matches Japan) is produced with the
  US anchor and the US benefit formula, so switching to a yen anchor
  requires calibrating Japan's actual pension formula and re-validating,
  not just changing one number. Treat the currency output as a real
  calibration task, not a relabel.

## 7. Steady state stopped converging against current OG-Core (0.19.1)

**Status (Nov 2026): baseline steady state fixed.** OG-Core 0.19 changed `tau_payroll` to a (T, J) array and `alpha_T = 0.10` no longer clears the budget. Now `tau_payroll = [[0.30]]`, `alpha_T = 0.09`, `alpha_G = 0.062`. Result: pension/Y 0.1145, revenue/Y 0.322, debt/Y 2.0, G/Y 0.051, K/Y 4.37, C/Y 0.73. alpha_T = 0 and 0.10 fail, 0.05 and 0.07-0.09 solve, so the solution region is narrow. The three reform experiments and their docs were rerun under this calibration (Nov 8); headline numbers moved by at most 0.1 point of GDP. Verified to still solve on OG-Core 0.21.2. Still to do: a younger-age-mix counterfactual (swapping omega_SS to Japan's 1990 mix did not converge, even with g_n_ss matched; it needs a consistent fertility-based population, not a swap).

Original diagnosis below, kept for the record.

Found while scoping a switch to Japan's defined-benefit pension system. The
baseline `run_ogjpn_ss.py` now raises "Steady state aggregate resource
constraint not satisfied" (resource constraint difference on the order of
1e27, government spending G driven negative). A pure OG-Core default steady
state still solves cleanly on the same tree, so this is an OG-JPN
calibration issue against the newer OG-Core, not an OG-Core regression.

Bisecting the calibration dict onto the OG-Core default isolates two
independent causes:

- **Payroll tax.** `tau_payroll = 0.30` breaks the steady state on its own.
  OG-Core's default is `tau_payroll = 0`, and the explicit-payroll revenue
  path (revenue = tau_payroll * w * L, added into total revenue) means a 30%
  flat payroll tax now floods government revenue without a matching outlay,
  so the budget-closure residual drives G below zero until the resource
  constraint diverges. Any positive tau_payroll tested (0.05 to 0.18) fails;
  only `tau_payroll = 0` solves. Fix is a calibration decision: either drop
  the standalone payroll tax and fold Japan's pension contributions into the
  income/payroll tax function (OG-Core's default representation), or add the
  offsetting pension outlay so the payroll revenue is spent, not banked.

- **A negative-G interaction in the full calibration.** With payroll set to
  zero, each block solves on its own against Japan's demographics: Japan
  demographics alone (pension/Y about 0.125), Japan macro alone, and Japan
  tax-without-payroll alone all clear the steady state. So do the pairs
  demographics+macro and demographics+tax. Only the full combination
  (demographics + macro + tax, payroll off) fails. The tell is that every
  partial configuration already runs government purchases G negative (about
  -0.04 to -0.08): revenue net of pensions, transfers (alpha_T), and
  interest is below alpha_G * Y, so the budget identity is forcing G down to
  clear. Stacking the blocks compounds that pressure until no non-negative G
  satisfies the resource constraint. The demographic arrays themselves are
  sane (omega sums to 1 per period, no NaNs, g_n_ss about -1.07%, correct
  for a shrinking Japan), so this is a fiscal-closure calibration problem,
  not bad population data.

  Note: a quick alpha_G / alpha_T sweep on the failing combination is not
  yet trustworthy: several runs returned numbers identical to the OG-Core
  default (pension/Y 0.0867, r 0.0628), which means the calibration dict did
  not take in those runs. The sweep needs to be redone with a check that the
  Japan parameters are actually applied before drawing conclusions about
  which fiscal share to move.

Order of work: fix the payroll representation first (it breaks even without
demographics). Then, on a verified-applied calibration, find the fiscal
closure that clears the full combination under Japan demographics: the
candidates are lowering alpha_G, lowering alpha_T, or raising modeled
revenue back toward the roughly 32% of GDP the original alpha_G = 0.054
derivation assumed (the payroll change is what dropped it). Then re-validate
pension outlays and re-run the three reforms. Do not paper over either
failure by loosening the solver tolerance; both are real budget-identity
failures.

## How to run

```
PYTHONPATH=. python examples/run_ogjpn_ss.py   # steady state
PYTHONPATH=. python -m pytest tests/           # scaffolding tests
```
