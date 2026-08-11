# OG-Japan (OG-JPN)

An overlapping-generations model of Japanese fiscal policy, built on
[OG-Core](https://github.com/PSLmodels/OG-Core). OG-JPN is a country
calibration of OG-Core, in the same family as OG-USA, OG-UK, OG-BRA, and
OG-THA. To our knowledge no open-source OG model of Japan exists yet.

Japan is an unusually important case for this class of model: it has the
oldest population of any large economy and a gross public debt of roughly
250 percent of GDP. Those are exactly the fiscal-demographic dynamics
overlapping-generations models are built to study.

![Japan is aging: population by age, 1990 vs 2030](docs/japan_aging.png)

The model runs on this real UN population data, and now on a Japanese
fiscal calibration to match: net debt, Japan's near-zero effective
interest rate, its social-insurance-heavy tax structure, and a
defined-benefit pension system.

**See [docs/METHODOLOGY.md](docs/METHODOLOGY.md)** for how it's built, the
data sources, and an honest validation of the steady state against Japan's
actual ratios (what matches, what's still first-pass, and why).

## Status

A country model is a thin calibration layer on top of OG-Core that
supplies demographics, macro parameters, earnings profiles, an
input-output structure, and tax parameters. Phase 0 established the
skeleton and de-risked the hardest dependency, demographics. Phases 1
and 2 are now substantially done — see
[docs/CALIBRATION_AUDIT.md](docs/CALIBRATION_AUDIT.md) for what was
found and what each value is sourced from.

The thing to understand about a country port is that **anything the
calibration does not set keeps OG-Core's United States value.** The
calibration now overrides 34 parameters rather than 7, plus the
earnings matrix and the demographic arrays. What is still on US
defaults is listed explicitly in `ogjpn/calibrate.py`, and
[docs/CALIBRATION_TABLE.md](docs/CALIBRATION_TABLE.md) gives every
calibrated value with its source.

**What works:** OG-Core's `demographics` module can pull Japan's
fertility, mortality, and population data from the UN World Population
Prospects data portal using country code `392`. The calibration
pipeline (`ogjpn.calibrate.Calibration` -> `Specifications` -> steady
state solve) is wired and runnable via `examples/run_ogjpn_ss.py`.

**Known prerequisite (data access):** The UN data portal now requires a
free API token. Save it as `un_api_token.txt` in the run directory.
Without a token, OG-Core falls back to an offline data mirror
([EAPD-DRB/Population-Data](https://github.com/EAPD-DRB/Population-Data)),
which currently covers 11 countries but **not Japan**. So live Japan
demographics require the token today.

Two give-backs would fix that, and they only work as a pair:
1. Add `"392": "JPN"` to the country map in `ogcore/demographics.py`.
2. Contribute Japan's demographic CSVs to `EAPD-DRB/Population-Data` so
   Japan works offline like the other country models.

They are items 4 and 5 of six in
[docs/UPSTREAM_OGCORE.md](docs/UPSTREAM_OGCORE.md).

## What is calibrated to Japan

Every value is sourced in the module that sets it.

| Block | Key values | Source |
|---|---|---|
| Debt | net debt 0.864 of GDP; SS target 1.0 | OECD Economic Outlook GNFLQ |
| Interest | `r_gov` ≈ −0.6% real | OECD net interest ÷ net debt, 2015–2024 |
| Foreign debt | 13.7% foreign-held | MOF JGB/T-Bill holders, Mar 2026 |
| Growth | `g_y` 1.04%/yr per HOUR, 2000–2019 | Penn World Table via FRED |
| Social insurance | effective 23.1% of wages (13.2% of GDP) | OECD Revenue Statistics 2025 |
| Income tax | Gouveia-Strauss, top rate 55% | OECD RevStats; Japan statutory schedule |
| Consumption | effective 12.3% (all indirect taxes) | OECD RevStats 2025 |
| Corporate | 29.74% statutory | OECD RevStats 2025 |
| Property / bequest | wealth tax + material inheritance tax | OECD RevStats; MOF FY2025 budget |
| Pension | Defined Benefits, effective 41.4% replacement | OECD Pensions at a Glance 2023 |
| Income anchor | ¥4.6m mean salary | National Tax Agency, 2023 |
| Depreciation | 6.2%/yr | World Bank consumption of fixed capital |
| Capital share | 0.43 | Penn World Table labour share |
| Discount factor | 0.979, calibrated to K/Y = 3.70 | Penn World Table |
| Earnings profile | NTA age shape + Gini tilt to 32.3 | NTA; World Bank |
| Demographics | 20 years of UN projection, not 2 | UN WPP |

Still on OG-Core's US values and documented as such: `chi_n` (the
labour-disutility profile). For Japan that borrow is defensible to within
1% — Japan works 10.5% fewer hours per worker but employs far more people,
so total labour input per working-age person is 1,278 hours against the
US 1,288.

Six limitations found in OG-Core and the shared data repos are recorded in
[docs/UPSTREAM_OGCORE.md](docs/UPSTREAM_OGCORE.md) rather than worked
around. Three of them affect every country repo in the family, not just
Japan.

## Roadmap

- **Phase 0 (done):** skeleton + demographics feasibility.
- **Phase 1 (done):** Japanese macro parameters — debt on a net basis, the
  sovereign interest wedge, openness, growth, spending shares.
- **Phase 2 (done):** tax calibration from collections by instrument, a
  defined-benefit pension system, and the earnings profile — both halves of
  the family method, an NTA age-shape adjustment and the Gini tilt. Japan has
  no open tax microsimulator, so the income tax uses OG-Core's
  Gouveia-Strauss form fit to the statutory schedule and tuned to published
  collections.
- **Phase 2b (done):** the in-model tuning loop, fourteen rounds. Every
  fiscal moment now lands within 0.1 percentage points of GDP.
- **Phase 3 (next):** analyze one real policy question. The obvious
  candidate is no longer the consumption tax but **interest-rate
  normalisation**: Japan's fiscal position is far more sensitive to the Bank
  of Japan unwinding than to a 2pp VAT change, and the model is now
  calibrated to say by how much.
- **Phase 4:** documentation, and sharing with the PSL community.

## Layout

```
ogjpn/
  constants.py       country code (392), start year, demographic window
  calibrate.py       assembles every block into one Specifications dict
  macro_params.py    growth, capital, debt, the sovereign wedge, spending
  tax_params.py      payroll, consumption, corporate, property, bequest, PIT
  pension_params.py  defined-benefit system and the yen income anchor
  income.py          the e matrix: NTA age shape + Gini tilt
  data/              NTA labour-income age profiles (JPN, USA)
examples/
  run_ogjpn.py                    baseline + reform, SS and transition
  validate_japan.py               steady state vs Japanese data
  plot_calibration_fit.py         model vs data figure
  plot_calibration_diagnostics.py the model's inputs
  calibration_table.py            every value with its source
scripts/
  fetch_nta_age_profiles.py       pull NTA profiles (session form, no API)
docs/
  CALIBRATION_AUDIT.md   what was found, what it lands at, what is not done
  CALIBRATION_TABLE.md   generated parameter table
  UPSTREAM_OGCORE.md     limitations to fix in OG-Core, not here
```

## Running

Live Japan demographics need a free UN Data Portal API token saved as
`un_api_token.txt` in the run directory.

```
python examples/validate_japan.py    # steady state vs Japanese data
python examples/run_ogjpn.py         # baseline + reform, SS and transition
python -m pytest tests/              # calibration tests
```

The steady state is solved serially and the transition in parallel with
Anderson acceleration — see the note in `examples/run_ogjpn.py` for why
that split matters.
