(Chap_Taxes)=
# Taxes

Japan has no open-source tax microsimulation model (no equivalent of the US [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator)), so `OG-JPN` cannot estimate OG-Core's tax functions from household microdata the way OG-USA does. Instead the personal income tax is fitted to **administrative tax data by salary bracket**, and the other taxes use published statutory rates (`ogjpn/tax_params.py`, `ogjpn/income_tax.py`).

## Personal income tax

### Data

The National Tax Agency's 2023 salary survey (民間給与実態統計調査, 令和5年分) reports, for 14 salary brackets of full-year private-sector earners, the number of earners, total salary, number of taxpayers, and national income tax withheld (tables 3 and 16; `scripts/fetch_nta_tax_data.py`). The data cover 50.8 million earners, 233 trillion yen of salary (mean 4.60 million yen), and 11.9 trillion yen of tax. 2023 is used rather than 2024 because 2024 withholding includes the one-off flat tax cut (定額減税).

Employers do not withhold resident tax (住民税, a flat 10 percent of taxable income plus a per-capita levy), so it is reconstructed. Taxable income per taxpayer is recovered by inverting the national bracket schedule (5 to 45 percent, plus the 2.1 percent reconstruction surtax) on tax withheld per taxpayer. As a check, the recovered taxable income for the 4-5 million yen bracket is within 2 percent of a statutory calculation for a single earner at that salary.

### Effective and marginal rates

| Mean salary (million yen) | 0.8 | 2.5 | 4.5 | 7.5 | 11.8 | 17.3 | 42.1 |
|---|---|---|---|---|---|---|---|
| Effective rate (national + resident) | 1.6% | 5.7% | 6.7% | 8.9% | 15.9% | 23.9% | 40.4% |
| Statutory marginal rate on labor income | 2.4% | 7.9% | 12.3% | 22.0% | 31.5% | 41.1% | 47.9% |

The marginal rate is the statutory rate at the bracket's mean salary: (national bracket rate x 1.021 + 10 percent resident) x (1 - slope of the employment income deduction - employee social insurance), scaled by the share of the bracket that pays tax.

### Functional form

Both schedules are fitted, weighted by the number of earners, with OG-Core's `DEP_totalinc` form,

$$
\tau(I) = (\tau^{max} - \tau^{min}) \frac{A I^2 + B I}{A I^2 + B I + 1} + \tau^{min},
$$

a curve bounded between a minimum and a maximum rate. It tracks Japan's schedule within about 2 percentage points across all brackets. (A two-parameter Heathcote-Storesletten-Violante function cannot: its rate flattens as income rises while Japan's steepens, and it puts the top bracket at 17 percent against an actual 40.) The fit is on income relative to mean salary and is rescaled to the model's income anchor (`mean_income_data`), so progressivity relative to the mean is right whichever currency the anchor is in. Capital income keeps a flat marginal rate of 20.315 percent.

The finding that matters for the model: **at mean income, Japan's marginal income tax rate is about 12 percent**, not the 30 percent the earlier flat calibration used. A flat 30 percent is correct only around 10 to 12 million yen. Since labor supply responds to the marginal rate, this changes the economy: in the steady state, labor supply is 9 percent higher and output 8 percent higher than under the flat calibration, and tax revenue rises from 32.2 to 33.3 percent of GDP.

The earlier flat calibration is still available as `Calibration(p, income_tax="linear")`.

## Other taxes

| Tax | Model rate | Source |
|---|---|---|
| Capital income, marginal (`mtry_params`) | 20.315% | 15% national + 5% local + 0.315% reconstruction surtax on dividends, interest, and listed capital gains |
| Social insurance (`tau_payroll`) | 30% | pension 18.3% + health ~10% + long-term care ~0.8% (blended) + employment ~0.9%; employer and employee shares, both borne by labor (Japan Pension Service, MHLW) |
| Corporate income (`cit_rate`) | 30% | national 23.2% plus local corporate, inhabitant, and enterprise taxes (PwC, JETRO) |
| Consumption (`tau_c`) | 10% | standard rate since October 2019 (National Tax Agency) |

## A US tax system cannot fund a Japanese government

With OG-Core's default US tax functions and Japan's debt target, the government budget only closed with **negative** government purchases. Japan's actual rates, mainly the 30 percent social insurance contribution, raise revenue enough to close the budget with positive purchases. The tax side, not only the demographics, now belongs to Japan.

## Known limitations

* **Personal income tax revenue runs high.** The model collects about 7.3 percent of GDP in personal income tax against about 6.4 percent in Japan (OECD *Revenue Statistics*: 18.9 percent of tax revenue in 2021). OG-Core's total-income form applies the progressive schedule to capital income as well, while Japan taxes most capital income separately at 20.315 percent and exempts some (NISA, pension savings) entirely.
* **Salary earners only.** The survey covers private-sector salary earners; the self-employed and public employees are not in it.
* **Deductions are averaged.** The inversion treats all deductions other than the basic deduction as part of an average; it does not distinguish dependants or spouses.
* **No contribution cap in the payroll tax.** Social insurance contributions in Japan are capped; `tau_payroll` is flat, which overstates the rate for high earners.
* **Property tax not modeled.** Japan's Fixed Asset and City Planning Tax (about 2 percent of GDP) can be added through OG-Core's wealth tax, but it made the consumption-tax reform fail to converge, so it is deferred.
