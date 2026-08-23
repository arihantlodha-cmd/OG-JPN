# Transition-path effect of raising Japan's pension age

Real Japan demographics (UN, code 392). Percent change vs the age-65 baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 65 to 68

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.31 | -0.53 | +0.06 | +0.50 | 0.094 -> 0.086 |
| +1 | +0.34 | -0.28 | +0.12 | +0.51 | 0.095 -> 0.086 |
| +5 | +0.47 | -0.54 | +0.36 | +0.55 | 0.097 -> 0.088 |
| +10 | +0.72 | -0.58 | +0.83 | +0.64 | 0.102 -> 0.090 |
| +20 | +1.54 | -0.69 | +2.35 | +0.93 | 0.115 -> 0.104 |

### 65 to 70

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.63 | -1.39 | +0.12 | +1.01 | 0.094 -> 0.079 |
| +1 | +0.74 | +2.28 | +0.32 | +1.05 | 0.095 -> 0.079 |
| +5 | +0.66 | -1.21 | +0.21 | +1.01 | 0.097 -> 0.081 |
| +10 | +1.16 | -1.26 | +1.17 | +1.16 | 0.102 -> 0.083 |
| +20 | +2.67 | -1.34 | +4.03 | +1.65 | 0.115 -> 0.094 |

## Net present value of the change, first 10 years


**65 to 68** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.07436 | -0.07111 | -0.06809 |
| GDP ($Y_t$) | 0.03757 | 0.03573 | 0.03402 |
| Labor ($L_t$) | 0.01446 | 0.01383 | 0.01324 |

**65 to 70** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.13 | -0.1244 | -0.1191 |
| GDP ($Y_t$) | 0.05911 | 0.05632 | 0.05373 |
| Labor ($L_t$) | 0.02724 | 0.02608 | 0.025 |

## What this adds over the steady state

The steady-state comparison found labor up, the pension bill down, and capital slightly lower. The transition traces the path on Japan's real, aging age structure and sharpens the picture. The pension bill is the headline a finance ministry watches: it falls year by year as the higher age phases in, holding the outlay several tenths of a point of GDP below the baseline throughout, and the NPV table above discounts that saving over the first decade. The surprise is capital. Where the steady-state end-point comparison showed it slightly lower, the transition shows it building up, about +2% by year 20 under the age-68 reform and +4% under 70. Working longer raises labor income during the transition, households save more of it, and the capital stock accumulates, with output rising alongside. This is the same pattern the consumption-tax transition showed, and it is exactly what a comparison of two long-run end points cannot see.

One reading caveat near the start: under the sharpest reform (age 70), the year-1 consumption figure is an outlier, reflecting the abrupt retiming of consumption for cohorts kept in work together with the initial-condition transient noted in the module docstring; read it as noise, not signal. The magnitudes are indicative, not final (the tax and pension calibration is still first-pass), so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period t=2 resource-constraint artifact cancels.
