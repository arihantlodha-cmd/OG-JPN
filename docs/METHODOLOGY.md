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
| Income / payroll taxes | OG-Core defaults | **not yet calibrated to Japan** |

Live UN demographics require a free UN Data Portal API token (see the main
README); the model then pulls Japan's fertility, mortality, and population
and solves.

## Validation against Japan

Solving the steady state and comparing to Japan's actual ratios:

| Ratio | Model | Japan | |
|---|---|---|---|
| Interest rate `r` | 0.040 | ~0.01-0.04 | matches |
| Pension outlays / GDP | 0.112 | ~0.10-0.11 | matches |
| Debt / GDP | 2.00 | ~2.1 | matches (at cap) |
| Tax revenue / GDP | 0.248 | ~0.20-0.30 | matches |
| Capital-output `K/Y` | 4.68 | ~3.0-3.5 | too high |
| Consumption / GDP `C/Y` | 0.80 | ~0.53-0.55 | too high |

**The fiscal and demographic side matches Japan.** These are the
quantities driven by the real data in the calibration, and the closest
result is the one nobody told the model: fed only Japan's age structure,
it reproduces a public pension burden of ~11-12% of GDP, close to Japan's
actual figure.

**The real-side ratios are too high, for understandable reasons.** In the
model's steady state, `K/Y = gamma / (r + delta)` exactly, so the
capital-output ratio is pinned by the capital share, the return on
capital, and depreciation. Grounding `gamma` in the Penn World Table
raised it from the earlier 0.38 first-pass to the actual 0.43, which
pushed `K/Y` from 4.42 up to 4.68. That is worth stating plainly: the
correctly sourced, higher capital share widens the `K/Y` overshoot rather
than closing it, which localizes the miss. The overshoot is not a `gamma`
artifact (the earlier lower value was partly masking it); it is structural,
the closed-economy over-accumulation of capital given Japan's high saving
and low return, so the fix belongs in `delta` and the open-economy margin,
not in understating the capital share. Every well-identified target (`r`,
pension outlays, revenue, debt) still matches after the change. The high
`C/Y` partly reflects the same closed-economy structure, since Japan runs
large current-account surpluses with low domestic investment.

## A finding along the way

Japan's real gross debt (214.5% of GDP, 2024) is so extreme it exceeds
OG-Core's built-in maximum for the debt parameter (200%). Japan is
literally beyond what the model's defaults anticipated, which is a fair
reflection of it being the developed world's fiscal outlier.

## Known limitations

- Macro parameters other than debt are first-pass; the income/payroll tax
  side is still OG-Core defaults, not fitted to Japanese effective rates.
- Results are steady-state only so far. The transition path (`examples/
  run_ogjpn_tpi.py`) has been attempted and does not yet converge: it
  plateaus at a ~0.16% resource-constraint imbalance, and switching to
  Anderson acceleration lands on the same value, so it is a
  calibration-consistency issue rather than solver tuning. A converged
  transition needs the same preference/production/fiscal calibration the
  steady-state validation points to.
- `K/Y` and `C/Y` need preference/production calibration (see above).
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
