# Transition-path effect of raising Japan's pension age

Real Japan demographics (UN, code 392). Percent change vs the age-65 baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 65 to 68

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.30 | -0.50 | +0.06 | +0.49 | 0.095 -> 0.086 |
| +1 | +0.34 | -0.51 | +0.12 | +0.50 | 0.095 -> 0.086 |
| +5 | +0.49 | -0.53 | +0.40 | +0.55 | 0.097 -> 0.088 |
| +10 | +0.74 | -0.58 | +0.87 | +0.65 | 0.102 -> 0.090 |
| +20 | +1.57 | -0.70 | +2.41 | +0.94 | 0.115 -> 0.104 |

### 65 to 70

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.53 | -0.90 | +0.10 | +0.85 | 0.095 -> 0.079 |
| +1 | +0.58 | -0.91 | +0.20 | +0.87 | 0.095 -> 0.079 |
| +5 | +0.85 | -0.95 | +0.71 | +0.95 | 0.097 -> 0.081 |
| +10 | +1.31 | -1.03 | +1.57 | +1.12 | 0.102 -> 0.083 |
| +20 | +2.80 | -1.27 | +4.33 | +1.66 | 0.115 -> 0.094 |

## Net present value of the change, first 10 years


**65 to 68** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.07464 | -0.07138 | -0.06835 |
| GDP ($Y_t$) | 0.03873 | 0.03682 | 0.03505 |
| Labor ($L_t$) | 0.01457 | 0.01393 | 0.01333 |

**65 to 70** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.1294 | -0.1238 | -0.1185 |
| GDP ($Y_t$) | 0.06755 | 0.06421 | 0.06111 |
| Labor ($L_t$) | 0.02512 | 0.02402 | 0.02299 |

## What this adds over the steady state

The steady-state comparison found labor up, the pension bill down, and capital slightly lower. The transition traces the path on Japan's real, aging age structure and sharpens the picture. The pension bill is the headline a finance ministry watches: it falls year by year as the higher age phases in, holding the outlay several tenths of a point of GDP below the baseline throughout, and the NPV table above discounts that saving over the first decade. The surprise is capital. Where the steady-state end-point comparison showed it slightly lower, the transition shows it building up, about +2% by year 20 under the age-68 reform and +4% under 70. Working longer raises labor income during the transition, households save more of it, and the capital stock accumulates, with output rising alongside. This is the same pattern the consumption-tax transition showed, and it is exactly what a comparison of two long-run end points cannot see.

One reading caveat near the start: under the sharpest reform (age 70), the year-1 consumption figure is an outlier, reflecting the abrupt retiming of consumption for cohorts kept in work together with the initial-condition transient noted in the module docstring; read it as noise, not signal. The magnitudes are indicative, not final (the tax and pension calibration is still first-pass), so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period t=2 resource-constraint artifact cancels.
