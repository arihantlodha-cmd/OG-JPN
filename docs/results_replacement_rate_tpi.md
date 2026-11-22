# Transition-path effect of cutting Japan's pension replacement rate

Real Japan demographics (UN, code 392). Percent change vs the current-schedule baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table), as a share of first-year GDP and in trillion yen at Japan's FY2023 GDP. Read directions and rough magnitudes, not the last digit.

## Time paths

### 10% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.29 | -0.77 | +0.05 | +0.47 | 0.101 -> 0.091 |
| +1 | +0.33 | -0.78 | +0.13 | +0.47 | 0.101 -> 0.091 |
| +5 | +0.50 | -0.80 | +0.50 | +0.49 | 0.103 -> 0.093 |
| +10 | +0.78 | -0.83 | +1.09 | +0.55 | 0.107 -> 0.097 |
| +20 | +1.71 | -0.92 | +2.86 | +0.85 | 0.121 -> 0.108 |

### 20% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.59 | -1.56 | +0.10 | +0.95 | 0.101 -> 0.081 |
| +1 | +0.66 | -1.57 | +0.27 | +0.96 | 0.101 -> 0.081 |
| +5 | +1.01 | -1.62 | +1.03 | +1.01 | 0.103 -> 0.083 |
| +10 | +1.59 | -1.66 | +2.21 | +1.13 | 0.107 -> 0.086 |
| +20 | +3.44 | -1.84 | +5.80 | +1.70 | 0.121 -> 0.096 |

## Net present value of the change, first 10 years


**10% benefit cut** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -9.6% of GDP (¥-57 tn) | -9.2% of GDP (¥-55 tn) | -8.8% of GDP (¥-53 tn) |
| GDP ($Y_t$) | 4.7% of GDP (¥28 tn) | 4.5% of GDP (¥27 tn) | 4.2% of GDP (¥25 tn) |
| Labor ($L_t$) | 0.0143 (model units) | 0.0136 (model units) | 0.0131 (model units) |

**20% benefit cut** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -19.4% of GDP (¥-115 tn) | -18.5% of GDP (¥-110 tn) | -17.8% of GDP (¥-106 tn) |
| GDP ($Y_t$) | 9.6% of GDP (¥57 tn) | 9.1% of GDP (¥54 tn) | 8.6% of GDP (¥51 tn) |
| Labor ($L_t$) | 0.0291 (model units) | 0.0278 (model units) | 0.0266 (model units) |

## What this adds over the steady state

The steady-state comparison found the pension bill down, labor up, and capital slightly lower. The transition traces the path on Japan's aging population. Under the 20% cut the pension bill is 2.2 points of GDP below the baseline after 10 years and 2.5 after 20, and the NPV table above discounts that saving over the first decade. Labor rises and stays up. By year 20, capital is +2.9 percent under the 10% cut and +5.8 percent under 20%, and output +3.4 percent under 20%.

Where the capital comes from. OG-Core holds government purchases at a fixed share of GDP for the first 20 years, so the budget gain from the 20% benefit cut goes to paying down debt: by year 20, debt is 1.04 times GDP against 1.62 in the baseline. Lower debt frees household saving for private capital. That, not extra household saving, is what lifts capital: household wealth is 0.8 percent lower (households save less), while capital is +5.8 percent at year 20. After year 20 OG-Core's closure rule brings debt back to its target, and capital ends the path -0.8 percent from baseline. Most of the capital gain along the transition is therefore a consequence of using the proceeds to pay down debt, as OG-Core's fiscal closure does.

The magnitudes are indicative, not final, so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period resource-constraint errors at t=2 and t=120 cancel.
