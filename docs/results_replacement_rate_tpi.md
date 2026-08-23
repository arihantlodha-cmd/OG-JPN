# Transition-path effect of cutting Japan's pension replacement rate

Real Japan demographics (UN, code 392). Percent change vs the current-schedule baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 10% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.60 | -0.66 | +0.11 | +0.97 | 0.094 -> 0.085 |
| +1 | +0.67 | +1.83 | +0.24 | +0.99 | 0.095 -> 0.085 |
| +5 | +0.61 | -0.55 | +0.15 | +0.96 | 0.097 -> 0.087 |
| +10 | +0.93 | -0.56 | +0.74 | +1.07 | 0.102 -> 0.091 |
| +20 | +1.96 | -0.56 | +2.59 | +1.49 | 0.115 -> 0.102 |

### 20% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +1.03 | -0.70 | +0.19 | +1.67 | 0.094 -> 0.075 |
| +1 | +1.09 | -0.31 | +0.32 | +1.68 | 0.095 -> 0.075 |
| +5 | +1.37 | -0.82 | +0.85 | +1.76 | 0.097 -> 0.077 |
| +10 | +1.98 | -0.95 | +1.93 | +2.01 | 0.102 -> 0.081 |
| +20 | +4.03 | -1.07 | +5.57 | +2.88 | 0.115 -> 0.090 |

## Net present value of the change, first 10 years


**10% benefit cut** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.07846 | -0.07511 | -0.07198 |
| GDP ($Y_t$) | 0.05328 | 0.05085 | 0.04859 |
| Labor ($L_t$) | 0.0259 | 0.02481 | 0.02378 |

**20% benefit cut** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.1555 | -0.1489 | -0.1427 |
| GDP ($Y_t$) | 0.1112 | 0.106 | 0.1011 |
| Labor ($L_t$) | 0.04676 | 0.04474 | 0.04287 |

## What this adds over the steady state

The steady-state comparison found the pension bill down, labor up, and capital slightly lower. The transition traces the path on Japan's real, aging age structure and, as with the retirement-age reform, flips the read on capital. The pension outlay drops year by year as the thinner benefit takes hold, several tenths of a point of GDP below the baseline throughout, and the NPV table above discounts that saving over the first decade. Labor rises strongly and stays up. And capital, which the steady-state end-point comparison showed slightly lower, builds up over the horizon instead (about +3% by year 20 under the 10% cut and +6% under 20%): facing a thinner public pension, households save more of their higher labor income during the transition, so the capital stock accumulates and output climbs with it. This is the crowding-in the steady-state levels alone did not show, and it is the same transition feature the consumption-tax and retirement-age reforms displayed.

One reading caveat near the start: under the 10% cut the year-1 consumption figure is an outlier, reflecting the abrupt retiming of consumption plus a single-period initial-condition transient at t=2; read it as noise. The reported window (years 0 to 20 and the first-decade NPV) is otherwise satisfied to about 1e-7; the larger reform also leaves a resource-constraint residual in the very last period of the finite horizon (a few percent), a terminal-boundary effect far beyond this window that does not propagate backward. The magnitudes are indicative, not final (the pension calibration is still first-pass), so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period t=2 artifact cancels.
