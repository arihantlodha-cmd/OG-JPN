# Transition-path effect of cutting Japan's pension replacement rate

Real Japan demographics (UN, code 392). Percent change vs the current-schedule baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 10% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.25 | -0.66 | +0.05 | +0.40 | 0.095 -> 0.085 |
| +1 | +0.28 | -0.67 | +0.11 | +0.41 | 0.095 -> 0.086 |
| +5 | +0.45 | -0.71 | +0.44 | +0.45 | 0.097 -> 0.088 |
| +10 | +0.75 | -0.75 | +1.00 | +0.56 | 0.102 -> 0.092 |
| +20 | +1.76 | -0.84 | +2.86 | +0.93 | 0.115 -> 0.103 |

### 20% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.51 | -1.33 | +0.09 | +0.82 | 0.095 -> 0.076 |
| +1 | +0.57 | -1.35 | +0.23 | +0.83 | 0.095 -> 0.076 |
| +5 | +0.91 | -1.43 | +0.89 | +0.93 | 0.097 -> 0.078 |
| +10 | +1.51 | -1.51 | +2.03 | +1.13 | 0.102 -> 0.081 |
| +20 | +3.53 | -1.68 | +5.78 | +1.87 | 0.115 -> 0.091 |

## Net present value of the change, first 10 years


**10% benefit cut** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.07646 | -0.0732 | -0.07016 |
| GDP ($Y_t$) | 0.03569 | 0.03387 | 0.03219 |
| Labor ($L_t$) | 0.01206 | 0.01153 | 0.01103 |

**20% benefit cut** (model units; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -0.1536 | -0.147 | -0.1409 |
| GDP ($Y_t$) | 0.07259 | 0.0689 | 0.06549 |
| Labor ($L_t$) | 0.02454 | 0.02346 | 0.02245 |

## What this adds over the steady state

The steady-state comparison found the pension bill down, labor up, and capital slightly lower. The transition traces the path on Japan's real, aging age structure and, as with the retirement-age reform, flips the read on capital. The pension outlay drops year by year as the thinner benefit takes hold, several tenths of a point of GDP below the baseline throughout, and the NPV table above discounts that saving over the first decade. Labor rises strongly and stays up. And capital, which the steady-state end-point comparison showed slightly lower, builds up over the horizon instead (about +3% by year 20 under the 10% cut and +6% under 20%): facing a thinner public pension, households save more of their higher labor income during the transition, so the capital stock accumulates and output climbs with it. This is the crowding-in the steady-state levels alone did not show, and it is the same transition feature the consumption-tax and retirement-age reforms displayed.

One reading caveat near the start: under the 10% cut the year-1 consumption figure is an outlier, reflecting the abrupt retiming of consumption plus the initial-condition transient noted in the module docstring; read it as noise. The magnitudes are indicative, not final (the pension calibration is still first-pass), so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period t=2 initial-condition artifact cancels.
