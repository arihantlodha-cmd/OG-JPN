(Chap_Roadmap)=
# Roadmap

## Done

* Country skeleton on OG-Core, with Japan's UN demographics (code 392).
* Macro and fiscal calibration from IMF, Penn World Table, and national sources.
* Tax calibration from published Japanese rates (income, social insurance, capital, corporate, consumption).
* Validated steady state and a converging transition path, on OG-Core 0.24.6.
* Three policy reforms (consumption tax, pension age, replacement rate), each as a steady-state comparison and on the transition path, with net present values.
* Japan's observed initial wealth distribution from the 2019 national survey.

## Next

1. **Rerun the reform transitions from the observed initial wealth distribution**, and update the result pages.
2. **Find the rest of the t = 2 resource-constraint error.** The observed wealth distribution cut it by 31 percent; the remainder has a different source.
3. **The t = 120 population freeze.** Report upstream that OG-Core fixes the population at `1.5 * S` periods even when it has not converged, and propose a convergence-based alternative.
4. **Yen income anchor.** OG-JPN still uses OG-Core's US mean income (`mean_income_data`, about \$58,645), so currency output is in effect US dollars. The candidate is the National Tax Agency's mean salary of full-year private-sector earners, 4.78 million yen (2024). The pension benefit formula is dollar-denominated, so switching needs a Japan pension formula and revalidation, not just a relabel.
5. **Progressive income tax**, fitted to Japan's seven-bracket schedule and the income distribution.
6. **Level of initial wealth.** Test `initial_wealth_ratio` at the national-accounts value (3.69 times GDP excluding land).
7. **Income-mortality gradient** from Japanese data.
8. **Property tax** through OG-Core's wealth tax, once the convergence problem with the consumption-tax reform is understood.

## Contributions upstream

| Contribution | Status |
|---|---|
| Japan's UN data in the shared offline mirror ([EAPD-DRB/Population-Data #14](https://github.com/EAPD-DRB/Population-Data/pull/14)) | merged |
| Japan and Fiji in OG-Core's `country_dict` ([OG-Core #1196](https://github.com/PSLmodels/OG-Core/pull/1196)) | merged |
| `npv_table` for the net present value of a reform ([OG-Core #1195](https://github.com/PSLmodels/OG-Core/pull/1195)) | merged |
| Custom initial wealth distribution ([OG-Core #1209](https://github.com/PSLmodels/OG-Core/pull/1209)) | superseded by the maintainers' [#1254](https://github.com/PSLmodels/OG-Core/pull/1254), merged |
| Resource-constraint failure diagnostics ([OG-Core #1213](https://github.com/PSLmodels/OG-Core/pull/1213)) | merged |
