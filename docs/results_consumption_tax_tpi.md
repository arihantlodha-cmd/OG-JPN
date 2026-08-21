# Transition-path effect of raising Japan's consumption tax

Real Japan demographics (UN, code 392). Percent change vs the 10% baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 10% to 12%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.07 | -1.38 | +0.01 | +0.11 | 0.321 -> 0.334 |
| +1 | +0.13 | -1.24 | +0.13 | +0.13 | 0.321 -> 0.334 |
| +5 | +0.39 | -1.36 | +0.62 | +0.21 | 0.320 -> 0.333 |
| +10 | +0.81 | -1.31 | +1.47 | +0.32 | 0.320 -> 0.332 |
| +20 | +2.13 | -1.24 | +4.03 | +0.72 | 0.320 -> 0.331 |

### 10% to 15%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.17 | -3.38 | +0.03 | +0.28 | 0.321 -> 0.352 |
| +1 | +0.33 | -3.01 | +0.31 | +0.34 | 0.321 -> 0.352 |
| +5 | +0.95 | -3.34 | +1.52 | +0.53 | 0.320 -> 0.350 |
| +10 | +1.99 | -3.20 | +3.60 | +0.79 | 0.320 -> 0.349 |
| +20 | +5.12 | -2.99 | +9.83 | +1.70 | 0.320 -> 0.346 |

## Net present value of the change, first 10 years


**10% to 12%** (model units):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 0.1127 | 0.1078 | 0.1033 |
| GDP ($Y_t$) | 0.02975 | 0.02803 | 0.02645 |
| Consumption ($C_t$) | -0.07749 | -0.07421 | -0.07115 |

**10% to 15%** (model units):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 0.2763 | 0.2644 | 0.2532 |
| GDP ($Y_t$) | 0.07322 | 0.069 | 0.0651 |
| Consumption ($C_t$) | -0.1896 | -0.1816 | -0.1741 |

## What this adds over the steady state

The steady-state experiment compares two long-run end points and found capital roughly flat. The transition shows why that understated the story: it traces the path between the end points on Japan's real, aging age structure, and the striking feature is the capital build-up. Taxing consumption shifts households toward saving, so the capital stock rises steadily over the horizon (about +4% by year 20 under the 12% reform and near +10% under 15%), and output climbs with it, from almost nothing on impact to a couple of percent or more two decades out. Consumption drops immediately as households retime purchases and stays down, while labor edges up throughout. The revenue gain accrues year by year, and discounting that stream over the first decade (the NPV table above) gives a finance ministry the object it would actually weigh, which a steady-state comparison cannot produce.

The magnitudes are indicative, not final (the tax side is still first-pass), so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are all reform-minus-baseline differences, so the single-period initial-condition artifact noted in the module docstring cancels out.
