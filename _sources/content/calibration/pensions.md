(Chap_Pensions)=
# Public pensions and the yen anchor

## Japan's two-tier pension

Japan's public pension has two tiers:

1. **Basic pension** (国民年金・老齢基礎年金): a flat 795,000 yen a year for 40 years of contributions (FY2023, Japan Pension Service).
2. **Employees' pension** (厚生年金・報酬比例部分): annual benefit = average indexed standard remuneration x 5.481/1000 x months of coverage (the post-2003 rate, bonuses included). Over a 40-year career this is 0.005481 x 40 = **21.9 percent** of average earnings.

## Mapping it onto OG-Core

OG-Core's "US-Style Social Security" system computes a monthly benefit (PIA) from average indexed monthly earnings (AIME), using three bracket rates that pass through the origin. `ogjpn/pension_params.py` sets:

| Parameter | Value | Meaning |
|---|---|---|
| `PIA_rate_bkt_2`, `PIA_rate_bkt_3` | 0.219 | employees' pension accrual over 40 years |
| `AIME_bkt_1` | 97,317 yen/month | bend point where 0.9 x AIME = basic pension + 0.219 x AIME |
| `PIA_minpayment` | 66,250 yen/month | the basic pension, as a floor |
| `PIA_maxpayment` | 236,161 yen/month | basic pension + 0.219 x the contribution ceiling (650,000 yen/month plus a 1.5 million yen bonus) |

Above the bend point the bracket formula is exactly Japan's,

$$
PIA = 0.9\, b_1 + 0.219\,(AIME - b_1) = \text{basic pension} + 0.219\, AIME, \qquad AIME \ge b_1,
$$

because $b_1 = \text{basic}/(0.9 - 0.219)$. Below the bend point the floor pays the basic pension, which understates Japan's benefit by at most about 16,000 yen a month just under the bend. The test suite checks the match at several earnings levels.

Because this uses OG-Core's existing system, the pension-age reform (`retirement_age`) and the replacement-rate reform (`replacement_rate_adjust`) work without changes.

## The yen anchor

The formula is in yen, so the model's income must be in yen. OG-Core converts model units to currency with a factor set so that mean model income equals `mean_income_data`; the OG-Core default is US mean income (about \$58,645). `OG-JPN` sets it to the mean salary of full-year private-sector earners in 2023, **4.595 million yen** (National Tax Agency 民間給与実態統計調査), the same source and year as the income-tax calibration ({ref}`Chap_Taxes`), whose functions are rescaled to the same anchor.

## Result

With Japan's formula and the yen anchor, the model's currency factor is about 6.7 million yen per model unit, and:

| | US formula, dollar anchor | Japan formula, yen anchor | Japan |
|---|---|---|---|
| Pension outlays / GDP, first year of transition | 0.096 | **0.102** | 0.104 (MHLW, FY2022) |
| Pension outlays / GDP, steady state | 0.115 | 0.121 | |

The two-tier formula pays more at the bottom (the flat basic pension) than the US formula's bend points, which brings the first-year bill to within 0.2 points of GDP of Japan's. Labor, output, capital, and revenue change by under 0.5 percent; government purchases absorb the higher pension bill, falling from 7.0 to 6.5 percent of GDP.

OG-Core caps `initial_guess_factor_SS` at 500,000, and the steady state does not converge from a guess at that cap when the factor is 6.7 million, so `ogjpn.calibrate.update_specs` sets the guess directly. [OG-Core #1292](https://github.com/PSLmodels/OG-Core/pull/1292) proposes raising the cap.

## Known limitations

* The spouse's basic pension (第3号被保険者) and survivor benefits are not modeled.
* AIME averages the best 35 years (`avg_earn_num_years`) rather than all months of coverage.
* `mean_income_data` is mean salary, while OG-Core defines it as mean income in the tax microdata; Japan has no comparable public microdata.
* The macroeconomic slide (マクロ経済スライド) is studied as a reform ({ref}`Chap_ReplRate`), not built into the baseline.
