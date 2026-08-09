# OG-Japan (OG-JPN)

An overlapping-generations model of Japanese fiscal policy, built on
[OG-Core](https://github.com/PSLmodels/OG-Core). OG-JPN is a country
calibration of OG-Core, in the same family as OG-USA, OG-UK, OG-BRA, and
OG-THA. To our knowledge no open-source OG model of Japan exists yet.

Japan is an unusually important case for this class of model: it has the
oldest population of any large economy and a gross public debt of roughly
250 percent of GDP. Those are exactly the fiscal-demographic dynamics
overlapping-generations models are built to study.

## Status: Phase 0 (feasibility)

A country model is a thin calibration layer on top of OG-Core that
supplies demographics, macro parameters, earnings profiles, an
input-output structure, and tax parameters. Phase 0 establishes the
skeleton and de-risks the hardest dependency, demographics.

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

This also surfaces two clean give-back contributions to the upstream
ecosystem:
1. Add `"392": "JPN"` to the country map in `ogcore/demographics.py`.
2. Contribute Japan's demographic CSVs to `EAPD-DRB/Population-Data` so
   Japan works offline like the other country models.

## Roadmap

- **Phase 0 (done here):** skeleton + demographics feasibility.
- **Phase 1:** real Japanese macro parameters (debt/GDP, growth,
  interest rate, government spending shares) from OECD/IMF/World Bank;
  confirm the steady state and a baseline transition solve and look
  sane.
- **Phase 2:** age-earnings profiles and a documented first-pass tax
  calibration (Japan has no open tax microsimulator, so v0.1 uses
  OG-Core's simpler tax functions calibrated to published effective
  rates, with the limitation documented).
- **Phase 3:** analyze one real policy question (a consumption-tax
  change, a higher retirement age, or a pension reform) and write it up.
- **Phase 4:** documentation, tests, and sharing with the PSL community.

## Layout

```
ogjpn/
  constants.py   country code (392) and metadata
  calibrate.py   Calibration class (demographics wired in Phase 0)
examples/
  run_ogjpn_ss.py   Phase 0 feasibility: load demographics + solve SS
```

## Running the feasibility check

With OG-Core installed in the environment:

```
PYTHONPATH=. python examples/run_ogjpn_ss.py
```

Add `un_api_token.txt` first to use live Japan demographics; otherwise
the script falls back to OG-Core defaults and says so.
