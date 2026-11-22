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

a curve bounded between a minimum and a maximum rate. It tracks Japan's schedule within about 2 percentage points across all brackets. (A two-parameter Heathcote-Storesletten-Violante function cannot: its rate flattens as income rises while Japan's steepens, and it puts the top bracket at 17 percent against an actual 40.) The fit is on income relative to mean salary and is rescaled to the model's income anchor (`mean_income_data`), so progressivity relative to the mean is right whichever currency the anchor is in.

### Labor and capital income are taxed separately

Japan taxes salaries on the progressive schedule and most financial income at a flat rate, but OG-Core's `DEP_totalinc` form is a function of total income $I$. Its parameters can vary by age, though, and that is enough. If $\lambda_s$ is the labor share of income at age $s$, the separable tax

$$
\frac{T_s(I)}{I} = \lambda_s \, \tau_L(\lambda_s I) + (1 - \lambda_s) \, \tau_k
$$

is again a `DEP_totalinc` curve, with $A$ scaled by $\lambda_s^2$, $B$ by $\lambda_s$, and the top and bottom rates by $\lambda_s$ plus the constant $(1-\lambda_s)\tau_k$ (`ogjpn.income_tax.age_specific_params`). The marginal rate on labor is the labor schedule at labor income $\lambda_s I$, and the marginal rate on capital is $\tau_k$. The labor shares come from the model's own steady state: `scripts/calibrate_labor_share.py` solves the steady state, recomputes the shares, and repeats until they stop moving (two iterations, maximum change 0.0004), and stores them in `ogjpn/data/labor_share_by_age.csv`. The share is near 1 at age 21 and falls to about 0.2 at 100, as retirees live on their savings.

### The effective tax rate on capital income

The statutory 20.315 percent (15 percent national, 5 percent local, 0.315 percent reconstruction surtax) applies to interest, dividends, and investment-trust income. Most household capital income is not of that kind. In the FY2023 national accounts (Cabinet Office, household sector income accounts), households received 30.5 trillion yen of property income and 18.0 trillion yen of net operating surplus on owner-occupied housing, 48.5 trillion yen in all. Of this, only 13.7 trillion yen is taxed at the flat rate: interest actually received (3.6 trillion before the FISIM adjustment), dividends (9.5), and investment-trust income (0.6). The rest, the return on owner-occupied housing and the investment income of insurance and pension reserves, is untaxed as it accrues. Japan therefore collects about **5.7 yen of income tax per 100 yen of household capital income**, and that is the rate the model uses for capital (`ogjpn.income_tax.effective_capital_tax_rate`), on average and at the margin.

The earlier version applied the progressive schedule to total income and attributed its high personal income tax revenue (7.3 percent of GDP) to taxing capital income progressively. That was the wrong diagnosis. Taxing the model's capital income at the statutory 20.315 percent would have raised revenue further, to 8.9 percent of GDP, because the model's capital income (about 20 percent of GDP, the return on all household wealth including land and housing) is much broader than the income Japan actually taxes. Separating the two taxes and using the effective rate brings personal income tax to **5.75 percent of GDP**, against 5.3 percent in the national accounts (taxes on household income, 31.6 trillion yen in FY2023) and 6.4 percent in OECD *Revenue Statistics*, whose personal income tax category also includes tax withheld on dividends paid to companies.

Lower tax on capital raises saving: in the steady state the capital-output ratio rises from 4.33 to 4.50, the interest rate falls from 4.6 to 4.2 percent, and output rises 3.9 percent. Total tax revenue falls from 33.3 to 31.8 percent of GDP, and government purchases (the budget residual) from 6.5 to 5.8 percent.

The finding that matters for the model: **at mean income, Japan's marginal income tax rate is about 12 percent**, not the 30 percent the earlier flat calibration used. A flat 30 percent is correct only around 10 to 12 million yen. Since labor supply responds to the marginal rate, this changes the economy: in the steady state, labor supply was 9 percent higher and output 8 percent higher than under the flat calibration (both measured before the capital-tax change above).

The earlier flat calibration is still available as `Calibration(p, income_tax="linear")`.

## Other taxes

| Tax | Model rate | Source |
|---|---|---|
| Capital income, average and marginal | 5.7% | effective: the statutory 20.315% on interest, dividends, and investment-trust income, over all household capital income including owner-occupied housing (FY2023 national accounts); see above |
| Social insurance (`tau_payroll`) | 30% | pension 18.3% + health ~10% + long-term care ~0.8% (blended) + employment ~0.9%; employer and employee shares, both borne by labor (Japan Pension Service, MHLW) |
| Corporate income (`cit_rate`) | 30% | national 23.2% plus local corporate, inhabitant, and enterprise taxes (PwC, JETRO) |
| Consumption (`tau_c`) | 10% | standard rate since October 2019 (National Tax Agency) |

## A US tax system cannot fund a Japanese government

With OG-Core's default US tax functions and Japan's debt target, the government budget only closed with **negative** government purchases. Japan's actual rates, mainly the 30 percent social insurance contribution, raise revenue enough to close the budget with positive purchases. The tax side, not only the demographics, now belongs to Japan.

## Known limitations

* **Labor shares are averaged within each age.** The split between labor and capital income uses the population-weighted average share at each age, so a high-wealth and a low-wealth household of the same age face the same mix.
* **The capital rate leaves some income out.** Realized capital gains on shares (not income in the national accounts), rental income (taxed progressively), and NISA exemptions are not in the effective rate. The effective rate also serves as the marginal rate, which is right for the average saver but understates the margin for someone adding to taxable securities.
* **Salary earners only.** The survey covers private-sector salary earners; the self-employed and public employees are not in it.
* **Deductions are averaged.** The inversion treats all deductions other than the basic deduction as part of an average; it does not distinguish dependants or spouses.
* **No contribution cap in the payroll tax.** Social insurance contributions in Japan are capped; `tau_payroll` is flat, which overstates the rate for high earners.
* **Property tax not modeled.** Japan's Fixed Asset and City Planning Tax (about 2 percent of GDP) can be added through OG-Core's wealth tax, but it made the consumption-tax reform fail to converge, so it is deferred.
