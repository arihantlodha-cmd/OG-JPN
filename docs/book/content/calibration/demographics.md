(Chap_Demog)=
# Demographics

Japan's demographics are the reason to build this model. `OG-JPN` takes them directly from the UN World Population Prospects through OG-Core's demographics module, with no Japan-specific adjustment.

## Source

`ogjpn.calibrate.Calibration` calls `ogcore.demographics.get_pop_objs` with:

| Argument | Value |
|---|---|
| `country_id` | `"392"` (Japan's UN M49 code) |
| `initial_data_year` / `final_data_year` | start year - 1 / start year + 1 (start year 2025) |
| ages | 0 to 99, mapped to the model's `E = 20` and `S = 80` |
| `income_percentiles` | OG-Core's lifetime-income group shares (`lambdas`), so the population arrays are `J` wide |

OG-Core uses the UN fertility, mortality, and population data to build the population distribution by age (`omega`), population growth (`g_n`), mortality (`rho`), and immigration rates along the transition path and in the steady state.

Japan's UN data are in the shared [EAPD-DRB/Population-Data](https://github.com/EAPD-DRB/Population-Data) mirror (added by this project in [Population-Data #14](https://github.com/EAPD-DRB/Population-Data/pull/14)), and Japan is in OG-Core's `country_dict` ([OG-Core #1196](https://github.com/PSLmodels/OG-Core/pull/1196)), so the model runs offline.

## What the data imply

Japan's population is shrinking: the steady-state population growth rate is about -1.07 percent a year. The age distribution in {numref}`FigJapanAging` shows the shift toward old age between 1990 and 2030.

This one input explains most of Japan's pension burden. Solved on Japan's demographics with otherwise standard parameters, the model's public pension outlays are about 11.5 percent of GDP, against about 8 to 9 percent on OG-Core's default (US-like) demographics.

## Known limitations

* **Common mortality across income groups.** Every lifetime-income group faces the same mortality. Japan's income-mortality gradient is not yet modeled; EAPD-DRB's [Demographic-Gradients](https://github.com/EAPD-DRB/Demographic-Gradients) project is the natural route, but its rules are built for developing countries and need Japan-specific data.
* **The population is fixed after 120 periods.** OG-Core holds the population distribution constant from period `fixper = 1.5 * S` (120). Japan's age distribution is still moving at that point (about 0.5 percent a period, L1 norm), so the freeze shows up as a small jump in population growth (-1.096 to -1.070 percent) and a one-period resource-constraint error of about 1.2e-3 at t = 120. It does not affect steady-state results.
