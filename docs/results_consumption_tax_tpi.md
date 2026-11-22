# Transition-path effect of raising Japan's consumption tax

Real Japan demographics (UN, code 392). Percent change vs the 10% baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table, model units). Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md); read directions and rough magnitudes, not the last digit.

## Time paths

### 10% to 12%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.06 | -1.35 | +0.01 | +0.09 | 0.333 -> 0.346 |
| +1 | +0.11 | -1.35 | +0.12 | +0.11 | 0.333 -> 0.346 |
| +5 | +0.38 | -1.37 | +0.62 | +0.20 | 0.332 -> 0.344 |
| +10 | +0.79 | -1.33 | +1.44 | +0.29 | 0.331 -> 0.343 |
| +20 | +2.03 | -1.32 | +3.94 | +0.62 | 0.330 -> 0.341 |

### 10% to 15%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.15 | -3.31 | +0.03 | +0.23 | 0.333 -> 0.365 |
| +1 | +0.28 | -3.32 | +0.28 | +0.28 | 0.333 -> 0.364 |
| +5 | +0.92 | -3.33 | +1.51 | +0.48 | 0.332 -> 0.362 |
| +10 | +1.90 | -3.27 | +3.53 | +0.68 | 0.331 -> 0.360 |
| +20 | +4.87 | -3.19 | +9.60 | +1.44 | 0.330 -> 0.357 |

## Net present value of the change, first 10 years


**10% to 12%** (share of first-year GDP and trillion yen at FY2023 GDP):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 13.2% of GDP (¥78 tn) | 12.6% of GDP (¥75 tn) | 12.1% of GDP (¥72 tn) |
| GDP ($Y_t$) | 3.4% of GDP (¥20 tn) | 3.2% of GDP (¥19 tn) | 3.0% of GDP (¥18 tn) |
| Consumption ($C_t$) | -9.1% of GDP (¥-54 tn) | -8.7% of GDP (¥-52 tn) | -8.3% of GDP (¥-50 tn) |

**10% to 15%** (share of first-year GDP and trillion yen at FY2023 GDP):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 32.3% of GDP (¥192 tn) | 30.9% of GDP (¥184 tn) | 29.6% of GDP (¥176 tn) |
| GDP ($Y_t$) | 8.4% of GDP (¥50 tn) | 7.9% of GDP (¥47 tn) | 7.4% of GDP (¥44 tn) |
| Consumption ($C_t$) | -22.2% of GDP (¥-132 tn) | -21.3% of GDP (¥-127 tn) | -20.4% of GDP (¥-121 tn) |

## What this adds over the steady state

The steady-state comparison found capital roughly flat in the long run. The transition shows a large swing on the way there: by year 20, capital is +3.9 percent under the 12% rate and +9.6 percent under 15%, and output +4.9 percent under 15%. Consumption drops immediately and stays down, while labor edges up throughout.

Where the capital comes from. OG-Core holds government purchases at a fixed share of GDP for the first 20 years, so the budget gain from the 15% consumption tax goes to paying down debt: by year 20, debt is 0.72 times GDP against 1.59 in the baseline. Lower debt frees household saving for private capital. That, not extra household saving, is what lifts capital: household wealth is 1.0 percent lower (households save less), while capital is +9.6 percent at year 20. After year 20 OG-Core's closure rule brings debt back to its target, and capital ends the path -0.7 percent from baseline. Most of the capital gain along the transition is therefore a consequence of using the proceeds to pay down debt, as OG-Core's fiscal closure does.

A check on the revenue line: in the first year, each point of consumption tax raises about ¥3.9 trillion at Japan's FY2023 GDP, against about ¥3.0 trillion in Japan (FY2024 budget: ¥30.2 trillion of national and local consumption tax at 10%). The model's consumption share of GDP is about a third too high (see the validation chapter), which is about the size of the gap.

The revenue gain accrues year by year, and discounting that stream over the first decade (the NPV table above) gives a finance ministry the object it would actually weigh, which a steady-state comparison cannot produce.

The magnitudes are indicative, not final (the tax side is still first-pass), so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are all reform-minus-baseline differences, so the single-period resource-constraint errors at t=2 and t=120 noted in the module docstring cancel out.
