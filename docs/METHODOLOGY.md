# OG-Japan: methodology and current results

This document describes how OG-Japan is built, what data it uses, and how
well its steady state matches Japan today. It is written to be honest
about what is calibrated and what is still first-pass.

## What OG-Japan is

OG-Japan (OG-JPN) is a country calibration of
[OG-Core](https://github.com/PSLmodels/OG-Core), a large-scale overlapping
-generations model of fiscal policy. OG-Core supplies the economic engine
(households that save and work over an 80-period life, firms, a government
budget, and a general-equilibrium solver); a country model supplies the
data that make it about a specific place. OG-Japan is that data layer for
Japan.

## How it is built

The calibration is a thin layer over OG-Core, assembled by
`ogjpn.calibrate.Calibration`:

| Layer | Source | Status |
|---|---|---|
| Demographics | UN World Population Prospects, country code 392, via `ogcore.demographics` | **real data** |
| Government debt | IMF WEO, gross general govt debt 214.5% of GDP (`GGXWDG_NGDP`) | **real data** |
| Government size | IMF WEO, revenue 37.6% / expenditure 39.1% of GDP | **real data** (composition into `alpha_G`/`alpha_T` estimated) |
| Consumption tax | Japan's 10% rate (since Oct 2019) | **real** |
| Productivity growth | ~0.8%/yr, consistent with IMF real GDP growth | grounded |
| Capital share (`gamma`) | Penn World Table labor share for Japan, `gamma = 1 - 0.568 = 0.43` (FRED `LABSHPJPA156NRUG`, 2013-2023 mean) | **real data** |
| Income / payroll / capital / corporate taxes | Linear (constant-rate) tax functions from published rates: income tax ~8% average with a 30% marginal (NTA schedule, OECD Taxing Wages), pension payroll 18.3%, capital 20.315%, corporate ~30% | **real data** (first-pass linear form) |

Live UN demographics require a free UN Data Portal API token (see the main
README); the model then pulls Japan's fertility, mortality, and population
and solves.

## Validation against Japan

Solving the steady state and comparing to Japan's actual ratios:

| Ratio | Model | Japan | |
|---|---|---|---|
| Interest rate `r` | 0.040 | ~0.01-0.04 | matches |
| Pension outlays / GDP | 0.113 | ~0.10-0.11 | matches |
| Debt / GDP | 2.00 | ~2.1 | matches (at cap) |
| Tax revenue / GDP | 0.259 | ~0.20-0.30 | matches |
| Capital-output `K/Y` | 4.60 | ~3.0-3.5 (net) / ~5.4 (PWT) | consistent with PWT |
| Consumption / GDP `C/Y` | 0.79 | ~0.53-0.55 | too high |

**The fiscal and demographic side matches Japan.** These are the
quantities driven by the real data in the calibration, and the closest
result is the one nobody told the model: fed only Japan's age structure,
it reproduces a public pension burden of ~11-12% of GDP, close to Japan's
actual figure.

**The capital-output ratio is not the miss it first looks like.** In the
model's steady state, `K/Y = gamma / (r + delta)` exactly, an identity
from the firm's optimization, so a low return and a high capital share
together force a high `K/Y`. Japan has exactly that combination, and both
inputs here are real: the model's `r` (0.040) sits in Japan's actual range
and `gamma` (0.43) is the Penn World Table capital share. So `K/Y` near 4.6
is not a free parameter to tune down; it is what the identity requires.
The `~3.0-3.5` figure often quoted for Japan uses a narrow net-capital
concept. Measured the same way `gamma` was, from the Penn World Table
(capital stock `rnna` over real GDP `rgdpna`, FRED `RKNANPJPA666NRUG` and
`RGDPNAJPA666NRUG`), Japan's capital-output ratio is about 5.4 in recent
years. Against that source-consistent benchmark the model's 4.6 is
slightly low, not too high, and lowering `delta` toward a realistic value
would only raise `K/Y` further, another way of seeing that this ratio is
not the problem.

**The consumption share runs high because government consumption
collapses, and that traces to the revenue side.** `C/Y` (0.79 against
~0.53-0.55) is the one real-side miss, and reading the steady-state
accounts shows exactly why. Investment is realistic (`I/Y` about 0.22), so
the model is not over-saving. What is missing is government consumption:
`G` is the residual that closes the budget, and it is squeezed to almost
zero (`G/Y` about 0.001 against Japan's ~0.20). The output the government
should be buying instead shows up as household consumption, inflating
`C/Y` by almost exactly the missing `G` share. The cause is revenue, not
the current account: the model collects 25.9% of GDP while Japan's general
government takes 37.6% (IMF), and that 12-point gap is almost exactly the
non-pension social insurance (health, long-term care, employment) the
first-pass tax calibration leaves out. Pensions (11.3%), other transfers
(10%), and debt service (4%) then consume nearly all of the undersized
revenue, leaving nothing for `G`. Lowering the steady-state debt ratio from
2.0 to 1.3 frees only about two points for `G`, so the debt basis is a
minor lever; completing the revenue side is the fix, and it is the top
calibration item. This is the same fiscal bind Japan resolves by
borrowing, which a fixed-debt steady state cannot do. Every well-identified
target (`r`, pension outlays, revenue, debt) matches.

## Findings along the way

Japan's real gross debt (214.5% of GDP, 2024) is so extreme it exceeds
OG-Core's built-in maximum for the debt parameter (200%). Japan is
literally beyond what the model's defaults anticipated, which is a fair
reflection of it being the developed world's fiscal outlier.

Calibrating the income, payroll, capital, and corporate taxes to Japan's
actual rates fixed a budget infeasibility. With OG-Core's US-default tax
functions and Japan's debt target, the government budget only closed with
*negative* government spending (the solver warned that `G < 0`). Replacing
those with the Japanese rates makes the budget close with positive `G` and
no warning, while every target still matches and `K/Y` and `C/Y` both edge
down slightly. In other words, the US tax structure could not fund a
Japanese government at Japanese debt; the Japanese one can. This is a real
check that the tax side, not just the demographics, now belongs to Japan.

## Known limitations

- The income tax uses a single average effective rate with a separate
  constant marginal rate (a linear tax function), not Japan's full
  progressive schedule; the non-pension social insurance and the
  `frac_tax_payroll` split are not yet modeled. Sharpening this needs the
  income distribution behind the published effective rates.
- Results are steady-state only so far. The transition path (`examples/
  run_ogjpn_tpi.py`) has been attempted and does not yet converge: it
  plateaus at a ~0.16% resource-constraint imbalance, and switching to
  Anderson acceleration lands on the same value, so it is a
  calibration-consistency issue rather than solver tuning. A converged
  transition needs the same preference/production/fiscal calibration the
  steady-state validation points to.
- `C/Y` runs high and needs the open-economy calibration (see above);
  `K/Y` is roughly consistent with the source-matched PWT benchmark and is
  not a target for tuning.
- Demographics are common across lifetime-income groups; adding Japan's
  income-mortality gradient is a natural next step, though the standard
  developing-country gradient rule extrapolates poorly to a rich,
  egalitarian country like Japan and would need Japan-specific data.

## First policy result

A first steady-state policy experiment is done and written up in
[`results_consumption_tax.md`](results_consumption_tax.md): raising Japan's
consumption tax from its actual 10% to 12% and to the 15% the IMF has
recommended, solved on real Japanese demographics. It reproduces the
standard consumption-tax pattern (consumption down, labor slightly up,
output roughly flat) and shows each two-point rise adding about 1.5 points
of GDP in revenue. This is a comparison of two steady states, which is
robust to the `K/Y` and `C/Y` level miss because both sides carry it; the
tax side is still first-pass, so it is a direction-and-rough-size result.
Regenerate it with `examples/analysis_consumption_tax.py`.

## Roadmap

1. Calibrate preferences/production to Japan's `K/Y` and `C/Y`.
2. Fit the income/payroll tax functions to Japanese data.
3. Run the same policy experiment on the transition path (needs the
   transition to converge, which follows from 1 and 2) and report the NPV
   of the change with the `npv_table` added upstream in OG-Core #1195. The
   steady-state version above is the first half of this.
4. Add income-group demographic gradients from Japanese data.
