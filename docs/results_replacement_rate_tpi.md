# Transition-path effect of cutting Japan's pension replacement rate

Real Japan demographics (UN, code 392). Percent change vs the current-schedule baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table), as a share of first-year GDP and in trillion yen at Japan's FY2023 GDP. Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 10% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.29 | -0.78 | +0.05 | +0.46 | 0.102 -> 0.092 |
| +1 | +0.32 | -0.79 | +0.14 | +0.47 | 0.103 -> 0.092 |
| +5 | +0.51 | -0.83 | +0.52 | +0.50 | 0.105 -> 0.094 |
| +10 | +0.81 | -0.85 | +1.15 | +0.56 | 0.109 -> 0.098 |
| +20 | +1.83 | -0.96 | +3.11 | +0.88 | 0.122 -> 0.109 |

### 20% benefit cut

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.58 | -1.58 | +0.11 | +0.94 | 0.102 -> 0.082 |
| +1 | +0.66 | -1.60 | +0.28 | +0.95 | 0.103 -> 0.082 |
| +5 | +1.03 | -1.66 | +1.06 | +1.01 | 0.105 -> 0.084 |
| +10 | +1.65 | -1.73 | +2.33 | +1.15 | 0.109 -> 0.087 |
| +20 | +3.68 | -1.92 | +6.28 | +1.76 | 0.122 -> 0.097 |

## Net present value of the change, first 10 years


**10% benefit cut** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -9.7% of GDP (¥-58 tn) | -9.3% of GDP (¥-55 tn) | -8.9% of GDP (¥-53 tn) |
| GDP ($Y_t$) | 4.8% of GDP (¥28 tn) | 4.5% of GDP (¥27 tn) | 4.3% of GDP (¥26 tn) |
| Labor ($L_t$) | 0.0141 (model units) | 0.0135 (model units) | 0.0129 (model units) |

**20% benefit cut** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -19.5% of GDP (¥-116 tn) | -18.7% of GDP (¥-111 tn) | -17.9% of GDP (¥-107 tn) |
| GDP ($Y_t$) | 9.7% of GDP (¥58 tn) | 9.2% of GDP (¥55 tn) | 8.7% of GDP (¥52 tn) |
| Labor ($L_t$) | 0.0285 (model units) | 0.0273 (model units) | 0.0261 (model units) |

## What this adds over the steady state

The steady-state comparison found the pension bill down, labor up, and capital slightly lower. The transition traces the path on Japan's aging population. Under the 20% cut the pension bill is 2.2 points of GDP below the baseline after 10 years and 2.5 after 20, and the NPV table above discounts that saving over the first decade. Labor rises and stays up. By year 20, capital is +3.1 percent under the 10% cut and +6.3 percent under 20%, and output +3.7 percent under 20%.

Where the capital comes from. OG-Core holds government purchases at a fixed share of GDP for the first 20 years, so the budget gain from the 20% benefit cut goes to paying down debt: by year 20, debt is 0.98 times GDP against 1.59 in the baseline. Lower debt frees household saving for private capital. That, not extra household saving, is what lifts capital: household wealth is 1.0 percent lower (households save less), while capital is +6.3 percent at year 20. After year 20 OG-Core's closure rule brings debt back to its target, and capital ends the path -1.1 percent from baseline. Most of the capital gain along the transition is therefore a consequence of using the proceeds to pay down debt, as OG-Core's fiscal closure does.

The magnitudes are indicative, not final, so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period resource-constraint errors at t=2 and t=120 cancel.
