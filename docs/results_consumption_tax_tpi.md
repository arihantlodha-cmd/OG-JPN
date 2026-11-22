# Transition-path effect of raising Japan's consumption tax

Real Japan demographics (UN, code 392). Percent change vs the 10% baseline transition at several horizons (years from the 2025 start), then the net present value of the reform-minus-baseline change over the first decade at 1/2/3% discount rates (OG-Core npv_table), as a share of first-year GDP and in trillion yen at Japan's FY2023 GDP. Read directions and rough magnitudes, not the last digit.

## Time paths

### 10% to 12%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.05 | -1.34 | +0.01 | +0.09 | 0.318 -> 0.330 |
| +1 | +0.11 | -1.35 | +0.11 | +0.11 | 0.317 -> 0.330 |
| +5 | +0.35 | -1.35 | +0.58 | +0.18 | 0.316 -> 0.328 |
| +10 | +0.73 | -1.33 | +1.34 | +0.28 | 0.316 -> 0.328 |
| +20 | +1.89 | -1.32 | +3.63 | +0.59 | 0.315 -> 0.326 |

### 10% to 15%

| Year | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP (base -> reform) |
|---|---|---|---|---|---|
| +0 | +0.14 | -3.29 | +0.02 | +0.23 | 0.318 -> 0.349 |
| +1 | +0.27 | -3.30 | +0.27 | +0.27 | 0.317 -> 0.348 |
| +5 | +0.87 | -3.30 | +1.43 | +0.46 | 0.316 -> 0.346 |
| +10 | +1.80 | -3.25 | +3.30 | +0.69 | 0.316 -> 0.345 |
| +20 | +4.54 | -3.20 | +8.87 | +1.39 | 0.315 -> 0.342 |

## Net present value of the change, first 10 years


**10% to 12%** (share of first-year GDP and trillion yen at FY2023 GDP):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 13.1% of GDP (¥78 tn) | 12.5% of GDP (¥75 tn) | 12.0% of GDP (¥71 tn) |
| GDP ($Y_t$) | 3.2% of GDP (¥19 tn) | 3.0% of GDP (¥18 tn) | 2.8% of GDP (¥17 tn) |
| Consumption ($C_t$) | -9.0% of GDP (¥-54 tn) | -8.7% of GDP (¥-52 tn) | -8.3% of GDP (¥-49 tn) |

**10% to 15%** (share of first-year GDP and trillion yen at FY2023 GDP):

| Variable | 1.0% | 2.0% | 3.0% |
|---|---|---|---|
| Total tax revenue ($REV_t$) | 32.1% of GDP (¥191 tn) | 30.7% of GDP (¥183 tn) | 29.5% of GDP (¥175 tn) |
| GDP ($Y_t$) | 7.9% of GDP (¥47 tn) | 7.4% of GDP (¥44 tn) | 7.0% of GDP (¥42 tn) |
| Consumption ($C_t$) | -22.1% of GDP (¥-132 tn) | -21.2% of GDP (¥-126 tn) | -20.3% of GDP (¥-121 tn) |

## What this adds over the steady state

The steady-state comparison found capital roughly flat in the long run. The transition shows a large swing on the way there: by year 20, capital is +3.6 percent under the 12% rate and +8.9 percent under 15%, and output +4.5 percent under 15%. Consumption drops immediately and stays down, while labor edges up throughout.

Where the capital comes from. OG-Core holds government purchases at a fixed share of GDP for the first 20 years, so the budget gain from the 15% consumption tax goes to paying down debt: by year 20, debt is 0.77 times GDP against 1.62 in the baseline. Lower debt frees household saving for private capital. That, not extra household saving, is what lifts capital: household wealth is 0.9 percent lower (households save less), while capital is +8.9 percent at year 20. After year 20 OG-Core's closure rule brings debt back to its target, and capital ends the path -0.6 percent from baseline. Most of the capital gain along the transition is therefore a consequence of using the proceeds to pay down debt, as OG-Core's fiscal closure does.

A check on the revenue line: in the first year, each point of consumption tax raises about ¥3.9 trillion at Japan's FY2023 GDP, against about ¥3.0 trillion in Japan (FY2024 budget: ¥30.2 trillion of national and local consumption tax at 10%). The model's consumption share of GDP is about a third too high (see the validation chapter), which is about the size of the gap.

The revenue gain accrues year by year, and discounting that stream over the first decade (the NPV table above) gives a finance ministry the object it would actually weigh, which a steady-state comparison cannot produce.

The magnitudes are indicative, not final, so read the shape of the paths and the sign of the NPV, not the last digit. The reported quantities are all reform-minus-baseline differences, so the single-period resource-constraint errors at t=2 and t=120 noted in the module docstring cancel out.
