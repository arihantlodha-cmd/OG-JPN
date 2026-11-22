# Transition-path effect of raising Japan's consumption tax

Real Japan demographics (UN, code 392). Percent change vs the 10% baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 10% to 12%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.06 | -1.36 | +0.01 | +0.10 | 0.320 -> 0.333 |
| +1 | +0.12 | -1.36 | +0.12 | +0.13 | 0.320 -> 0.333 |
| +5 | +0.39 | -1.35 | +0.64 | +0.21 | 0.319 -> 0.332 |
| +10 | +0.82 | -1.31 | +1.48 | +0.32 | 0.319 -> 0.331 |
| +20 | +2.14 | -1.25 | +4.04 | +0.73 | 0.319 -> 0.330 |

### 10% to 15%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.16 | -3.32 | +0.03 | +0.26 | 0.320 -> 0.352 |
| +1 | +0.31 | -3.33 | +0.30 | +0.32 | 0.320 -> 0.351 |
| +5 | +0.97 | -3.31 | +1.56 | +0.52 | 0.319 -> 0.350 |
| +10 | +2.00 | -3.19 | +3.62 | +0.79 | 0.319 -> 0.348 |
| +20 | +5.13 | -3.01 | +9.85 | +1.72 | 0.319 -> 0.345 |

## Net present value of the change, first 10 years


**10% to 12%** (model units):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 0.1116 | 0.1068 | 0.1023 |
| GDP ($Y_t$) | 0.02998 | 0.02825 | 0.02665 |
| Consumption ($C_t$) | -0.07715 | -0.0739 | -0.07087 |

**10% to 15%** (model units):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 0.2736 | 0.2618 | 0.2508 |
| GDP ($Y_t$) | 0.07377 | 0.06951 | 0.06558 |
| Consumption ($C_t$) | -0.1888 | -0.1809 | -0.1735 |

## What this adds over the steady state

The steady-state experiment compares two long-run end points and found capital roughly flat. The transition shows why that understated the story: it traces the path between the end points on Japan's real, aging age structure, and the striking feature is the capital build-up. Taxing consumption shifts households toward saving, so the capital stock rises steadily over the horizon (about +4% by year 20 under the 12% reform and near +10% under 15%), and output climbs with it, from almost nothing on impact to a couple of percent or more two decades out. Consumption drops immediately as households retime purchases and stays down, while labor edges up throughout. The revenue gain accrues year by year, and discounting that stream over the first decade (the NPV table above) gives a finance ministry the object it would actually weigh, which a steady-state comparison cannot produce.

The magnitudes are indicative, not final (the tax side is still first-pass), so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are all reform-minus-baseline differences, so the single-period initial-condition artifact noted in the module docstring cancels out.
