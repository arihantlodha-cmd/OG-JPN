# Transition-path effect of raising Japan's pension age

Real Japan demographics (UN, code 392). Percent change vs the age-65 baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 65 to 68

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.31 | -0.75 | +0.06 | +0.51 | 0.102 -> 0.092 |
| +1 | +0.35 | -0.75 | +0.14 | +0.52 | 0.103 -> 0.092 |
| +5 | +0.54 | -0.74 | +0.51 | +0.57 | 0.105 -> 0.093 |
| +10 | +0.84 | -0.76 | +1.09 | +0.65 | 0.109 -> 0.095 |
| +20 | +1.78 | -0.90 | +2.86 | +0.97 | 0.122 -> 0.109 |

### 65 to 70

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.54 | -1.29 | +0.10 | +0.87 | 0.102 -> 0.085 |
| +1 | +0.61 | -1.29 | +0.24 | +0.89 | 0.103 -> 0.085 |
| +5 | +0.93 | -1.28 | +0.89 | +0.96 | 0.105 -> 0.086 |
| +10 | +1.46 | -1.32 | +1.92 | +1.11 | 0.109 -> 0.087 |
| +20 | +3.08 | -1.58 | +5.01 | +1.65 | 0.122 -> 0.099 |

## Net present value of the change, first 10 years


**65 to 68** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -10.2% of GDP (¥-61 tn) | -9.8% of GDP (¥-58 tn) | -9.4% of GDP (¥-56 tn) |
| GDP ($Y_t$) | 5.1% of GDP (¥30 tn) | 4.8% of GDP (¥29 tn) | 4.6% of GDP (¥27 tn) |
| Labor ($L_t$) | 0.0159 (model units) | 0.0152 (model units) | 0.0146 (model units) |

**65 to 70** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -17.3% of GDP (¥-103 tn) | -16.6% of GDP (¥-99 tn) | -15.9% of GDP (¥-95 tn) |
| GDP ($Y_t$) | 8.8% of GDP (¥53 tn) | 8.4% of GDP (¥50 tn) | 8.0% of GDP (¥47 tn) |
| Labor ($L_t$) | 0.0275 (model units) | 0.0263 (model units) | 0.0252 (model units) |

## What this adds over the steady state

The steady-state comparison found labor up, the pension bill down, and capital slightly lower. The transition traces the path on Japan's aging population. The pension bill is the headline a finance ministry watches: under the age-70 reform it is 2.1 points of GDP below the baseline after 10 years and 2.3 after 20, and the NPV table above discounts that saving over the first decade. By year 20, capital is +2.9 percent under the age-68 reform and +5.0 percent under 70, and output +3.1 percent under 70.

Where the capital comes from. OG-Core holds government purchases at a fixed share of GDP for the first 20 years, so the budget gain from the move to a pension age of 70 goes to paying down debt: by year 20, debt is 1.01 times GDP against 1.59 in the baseline. Lower debt frees household saving for private capital. That, not extra household saving, is what lifts capital: household wealth is 1.8 percent lower (households save less), while capital is +5.0 percent at year 20. After year 20 OG-Core's closure rule brings debt back to its target, and capital ends the path -1.6 percent from baseline. Most of the capital gain along the transition is therefore a consequence of using the proceeds to pay down debt, as OG-Core's fiscal closure does.

The magnitudes are indicative, not final, so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period resource-constraint errors at t=2 and t=120 cancel.
