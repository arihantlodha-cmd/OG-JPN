(Chap_Roadmap)=
# Roadmap

## Done

* Country skeleton on OG-Core, with Japan's UN demographics (code 392).
* Macro and fiscal calibration from IMF, Penn World Table, and national sources.
* **Progressive personal income tax** fitted to the National Tax Agency's 2023 salary-bracket tax data; social insurance, capital, corporate, and consumption taxes from statutory rates.
* **Japan's two-tier public pension** (basic + employees' pension) in yen, with the model's income anchored to the 2023 mean salary.
* Japan's observed initial wealth distribution from the 2019 national survey.
* Validated against Japan: first-year pension outlays 10.2 percent of GDP against 10.4 percent actual; tax revenue 33.3 against 34.4 percent.
* Converging transition path on OG-Core 0.24.6, and three policy reforms (consumption tax, pension age, replacement rate), each as a steady-state comparison and on the transition path, with net present values.

## Next

1. **The t = 120 population freeze.** OG-Core fixes the population at `1.5 * S` periods even when it has not converged ([OG-Core #1290](https://github.com/PSLmodels/OG-Core/issues/1290)). Moving the freeze to period 200 removes the t = 120 error and halves it at the new freeze point; a convergence-based rule is the real fix.
2. **The t = 2 resource-constraint error.** The observed initial wealth distribution cut it by about 30 percent; the rest has another source.
3. **Personal income tax revenue** runs about a point of GDP high because OG-Core's total-income form taxes capital income progressively; OG-Core's separate labor/capital (`DEP`) form, or a lower effective rate on capital income, would fix it.
4. **Level of initial wealth.** Test `initial_wealth_ratio` at the national-accounts value (3.69 times GDP excluding land).
5. **Pension details:** the spouse's basic pension, survivor benefits, and the macroeconomic slide as part of the baseline rather than a reform.
6. **Income-mortality gradient** from Japanese data.
7. **Property tax** through OG-Core's wealth tax, once the convergence problem with the consumption-tax reform is understood.

## Contributions upstream

| Contribution | Status |
|---|---|
| Japan's UN data in the shared offline mirror ([EAPD-DRB/Population-Data #14](https://github.com/EAPD-DRB/Population-Data/pull/14)) | merged |
| Japan and Fiji in OG-Core's `country_dict` ([OG-Core #1196](https://github.com/PSLmodels/OG-Core/pull/1196)) | merged |
| `npv_table` for the net present value of a reform ([OG-Core #1195](https://github.com/PSLmodels/OG-Core/pull/1195)) | merged |
| Custom initial wealth distribution ([OG-Core #1209](https://github.com/PSLmodels/OG-Core/pull/1209)) | superseded by the maintainers' [#1254](https://github.com/PSLmodels/OG-Core/pull/1254), merged |
| Resource-constraint failure diagnostics ([OG-Core #1213](https://github.com/PSLmodels/OG-Core/pull/1213)) | merged |
| Population frozen before convergence for fast-aging countries ([OG-Core #1290](https://github.com/PSLmodels/OG-Core/issues/1290)) | issue, with test |
| Non-dollar initial guess for the currency factor ([OG-Core #1292](https://github.com/PSLmodels/OG-Core/pull/1292)) | open |
| `age_specific` parameter description ([OG-Core #1291](https://github.com/PSLmodels/OG-Core/pull/1291)) | open |
| OG-JPN in OG-Core's list of country calibrations ([OG-Core #1289](https://github.com/PSLmodels/OG-Core/pull/1289)) | open |
