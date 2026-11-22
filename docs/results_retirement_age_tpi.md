# Transition-path effect of raising Japan's pension age

Real Japan demographics (UN, code 392). Percent change vs the age-65 baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table), as a share of first-year GDP and in trillion yen at Japan's FY2023 GDP. Read directions and rough magnitudes, not the last digit.

## Time paths

### 65 to 68

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.31 | -0.74 | +0.05 | +0.50 | 0.101 -> 0.091 |
| +1 | +0.35 | -0.73 | +0.13 | +0.51 | 0.101 -> 0.091 |
| +5 | +0.52 | -0.72 | +0.48 | +0.55 | 0.103 -> 0.092 |
| +10 | +0.80 | -0.73 | +1.02 | +0.63 | 0.107 -> 0.094 |
| +20 | +1.64 | -0.86 | +2.59 | +0.92 | 0.121 -> 0.108 |

### 65 to 70

| Year | Y (%) | C (%) | K (%) | L (%) | Pension/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.53 | -1.27 | +0.09 | +0.86 | 0.101 -> 0.083 |
| +1 | +0.60 | -1.26 | +0.23 | +0.87 | 0.101 -> 0.084 |
| +5 | +0.90 | -1.25 | +0.84 | +0.94 | 0.103 -> 0.085 |
| +10 | +1.38 | -1.27 | +1.78 | +1.08 | 0.107 -> 0.087 |
| +20 | +2.85 | -1.51 | +4.56 | +1.58 | 0.121 -> 0.098 |

## Net present value of the change, first 10 years


**65 to 68** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -10.1% of GDP (¥-60 tn) | -9.7% of GDP (¥-57 tn) | -9.2% of GDP (¥-55 tn) |
| GDP ($Y_t$) | 4.9% of GDP (¥29 tn) | 4.7% of GDP (¥28 tn) | 4.4% of GDP (¥26 tn) |
| Labor ($L_t$) | 0.0158 (model units) | 0.0151 (model units) | 0.0144 (model units) |

**65 to 70** (share of first-year GDP and trillion yen at FY2023 GDP; pensions are reform minus baseline, so negative is a saving):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Pensions ($Pensions_{t}$) | -17.1% of GDP (¥-102 tn) | -16.3% of GDP (¥-97 tn) | -15.7% of GDP (¥-93 tn) |
| GDP ($Y_t$) | 8.5% of GDP (¥50 tn) | 8.0% of GDP (¥48 tn) | 7.6% of GDP (¥45 tn) |
| Labor ($L_t$) | 0.027 (model units) | 0.0258 (model units) | 0.0247 (model units) |

## What this adds over the steady state

The steady-state comparison found labor up, the pension bill down, and capital slightly lower. The transition traces the path on Japan's aging population. The pension bill is the headline a finance ministry watches: under the age-70 reform it is 2.1 points of GDP below the baseline after 10 years and 2.3 after 20, and the NPV table above discounts that saving over the first decade. By year 20, capital is +2.6 percent under the age-68 reform and +4.6 percent under 70, and output +2.8 percent under 70.

Where the capital comes from. OG-Core holds government purchases at a fixed share of GDP for the first 20 years, so the budget gain from the move to a pension age of 70 goes to paying down debt: by year 20, debt is 1.07 times GDP against 1.62 in the baseline. Lower debt frees household saving for private capital. That, not extra household saving, is what lifts capital: household wealth is 1.6 percent lower (households save less), while capital is +4.6 percent at year 20. After year 20 OG-Core's closure rule brings debt back to its target, and capital ends the path -1.3 percent from baseline. Most of the capital gain along the transition is therefore a consequence of using the proceeds to pay down debt, as OG-Core's fiscal closure does.

The magnitudes are indicative, not final, so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are reform-minus-baseline differences, in which the single-period resource-constraint errors at t=2 and t=120 cancel.
