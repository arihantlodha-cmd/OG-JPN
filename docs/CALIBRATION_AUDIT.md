# OG-JPN calibration audit

Reviewed against the OG-Core country-model family conventions (OG-USA, OG-PHL,
OG-ZAF, OG-IDN, OG-BRA, OG-ETH) at commit `babbe80`.

The scaffolding here is sound and the demographics wiring is right. The problem
is narrower and more serious than "some values are provisional": **most of the
parameters that decide Japan's answer are never set at all, so they silently
keep OG-Core's built-in United States values.** The five parameters in
`macro_params.py` are the visible part of the calibration. The invisible part is
larger and is currently American.

Everything below is sourced. Nothing is from memory.

---

## The headline problem: what is actually being solved

`ogjpn.calibrate.Calibration` passes OG-Core exactly seven things: five macro
parameters, one consumption tax rate, and the demographic arrays. Every other
parameter falls through to `ogcore/default_parameters.json`, which is calibrated
to the United States.

So the model as it stands is **Japanese demographics on an American economy**:

| Block | What OG-JPN sets | What the model actually uses |
|---|---|---|
| Income tax | nothing | `tax_func_type = "DEP"` — the 12-parameter form fitted to **US** Tax-Calculator microdata |
| Payroll / social insurance | nothing | `tau_payroll = 0.0` — Japan collects **13.2% of GDP** here |
| Pension system | nothing | `"US-Style Social Security"`, US bend points in **US dollars** |
| Mean income anchor | nothing | `mean_income_data = 58,644.92` — **US** dollars |
| Corporate tax | nothing | `cit_rate = 0.21` — the **US federal** rate |
| Earnings profile `e` | nothing | OG-USA's matrix, no Japan tilt |
| Labour disutility `chi_n` | nothing | OG-USA's profile (family-wide norm, but must be *documented*) |
| Foreign share of debt | nothing | `0.4` — Japan's actual is **0.137** |
| Sovereign rate wedge | nothing | `r_gov_shift = 0.02` — implies Japan pays ~2.5% real; it pays **about −1%** |
| SS debt target | nothing | `debt_ratio_ss = 2.0`, inherited, never chosen |
| Wealth / property tax | nothing | `p_wealth = 0.0` — Japan collects **2.75% of GDP** in property taxes |

---

## Finding 1 — the pension claim in the README is not true

The README says the model "reproduces Japan's public pension burden (~11-12% of
GDP) directly from the demographics", and `validate_japan.py` scores pension
outlays against a target of "~0.10-0.11".

Two problems.

**The target is wrong.** Japan's public pension expenditure is **9.3% of GDP**
(OECD *Pensions at a Glance 2023*, 2022 data), not 11–12%. The model is
overshooting by two to three percentage points and the validation script is
built to accept that.

**The mechanism is not Japan's.** `pension_system` is never set, so it stays at
`"US-Style Social Security"`. OG-Core then computes benefits with the US Social
Security formula — AIME bend points of \$749 and \$4,517, PIA replacement rates
of 90% / 32% / 15%, a maximum payment of \$3,501/month
(`ogcore/pensions.py:replacement_rate_vals`). Those are applied to model earnings
converted to currency by `factor`, which is solved against `mean_income_data` —
still the US value of \$58,645.

So the number being presented as validation is *Japanese demographics × US mean
income × the US Social Security benefit formula*. Getting ~11% out of that is
arithmetic, not evidence that the calibration is right.

**Fix:** OG-Core supports `pension_system = "Defined Benefits"`
(`ogcore/pensions.py:103`). Japan's Employees' Pension Insurance (厚生年金) is an
earnings-related defined-benefit scheme, so that is the structurally correct
choice. Set `mean_income_data` to Japanese mean income in yen, and target the
9.3% of GDP figure.

---

## Finding 2 — the interest rate is the parameter that decides everything

This is the most consequential item in the audit, and it is the one that makes
Japan different from every other country in the family.

Japan's government pays almost nothing on its debt. From the MOF FY2025 budget
(*Japanese Public Finance Fact Sheet*, April 2025): interest payments of
**¥10.55 trillion** on **¥1,323.7 trillion** of outstanding debt.

That is an effective **nominal** rate of **0.80%**. With inflation at the BOJ's
2% target, the effective **real** rate is about **−1.2%**.

OG-Core's default wedge (`r_gov_scale = 1.0`, `r_gov_shift = 0.02`) applied to a
model return of ~4.5% gives a real `r_gov` of about **+2.5%**. That is roughly
**3.7 percentage points too high, on a debt stock of 200% of GDP.**

The damage runs through the government budget identity. For debt to hold at the
steady-state target, the primary balance must satisfy
`pb* = (r_gov − g)/(1+g) × debt_ratio_ss`:

| Interest assumption | implied `pb*` at `debt_ratio_ss = 2.0` |
|---|---|
| OG-Core default (`r_gov ≈ +2.5%`) | **+4.4% of GDP primary surplus** |
| Japan actual (`r_gov ≈ −0.5%`) | **−1.6% of GDP primary deficit** |

Japan has never run a 4.4% primary surplus. Its FY2025 general-account primary
balance is about **−0.1% of GDP** (primary revenue ¥86.55tn less primary
expenses ¥87.33tn); general government runs a deficit of a few percent.

With the default wedge the model can only balance its books by cutting spending
to a level Japan has never chosen, or by over-collecting tax. Re-anchoring
`r_gov_shift` to Japan's actual effective rate lands `pb*` inside Japan's real
range and makes the whole fiscal block honest. **A negative `r − g` is precisely
why Japan can carry 200% debt while running primary deficits — the model has to
be allowed to represent that or it is not modelling Japan.**

Note also that the Bank of Japan holds **42.2%** of JGBs and T-Bills (MOF, March
2026), which is a large part of why the effective rate is so low. Worth stating
in the docs whichever debt concept is chosen.

---

### The consistency check that settles it

Pairing net debt with Japan's actual interest rate makes the fiscal block close
on its own. From the OECD Economic Outlook (general government, Japan):

| | 2023 | 2024 | 2025 |
|---|---:|---:|---:|
| Gross financial liabilities, % GDP | 218.1 | 205.4 | 197.5 |
| Net financial liabilities, % GDP | 98.6 | **86.4** | 78.5 |
| Net interest paid, % GDP | 0.02 | **−0.12** | −0.02 |
| Primary balance, % GDP | −2.31 | **−1.79** | −1.02 |

Japan's general government pays **approximately zero net interest** — interest
income on its financial assets roughly cancels interest on its debt. That is a
real effective rate of about **−2%**.

Feeding that into the identity with net debt of 0.864 and `g ≈ 0.3%`:

```
pb* = (−0.020 − 0.003)/1.003 × 0.864 = −1.97% of GDP
```

Japan's actual 2024 primary balance is **−1.79% of GDP**. The calibration lands
on the country's real fiscal position without being forced there.

For contrast, gross debt at the 2.0 cap with the same rate gives `pb* = −4.6%`,
a deficit larger than Japan runs; and the *current* OG-Core defaults give
`pb* = +4.4%`, a surplus Japan has never run.

**Caveat to document:** −2% real is a present-day rate supported by BOJ holdings
and near-zero policy rates. The OECD's own 2027 projection has net interest
rising to 0.86% of GDP (about −0.77% real). A long-run steady state should be
anchored nearer the normalised value, not today's.

## Finding 3 — the debt ratio is at a cap, and the SS target was never chosen

`initial_debt_ratio = 2.0` is the maximum OG-Core permits
(`default_parameters.json`, `range.max = 2.0`). The comment says gross debt is
214.5% of GDP so the cap is used. That figure is correct (IMF WEO
`GGXWDG_NGDP`, 2024 = 214.5; 2025 = 206.5).

Two things follow that the code does not address.

**Gross is the wrong concept for this model.** OG-Core's government pays
`r_gov × D` on the whole stock and holds no offsetting assets. Japan's general
government holds very large financial assets — the GPIF, the Fiscal Loan Fund,
and social-security reserves. Public pensions and the Fiscal Loan Fund alone
hold ¥75.1tn of JGBs, and general government another ¥17.1tn. Charging debt
service on gross debt while modelling none of the assets overstates the fiscal
burden. Net debt (~1.3–1.5× GDP) is the concept the model's own accounting
implies.

**`debt_ratio_ss` is never set,** so it silently sits at OG-Core's default of
`2.0`. That parameter is a *policy anchor* — the debt ratio the economy is
assumed to converge to — and it is doing enormous work in the steady state. It
should be a documented choice, not an inheritance.

---

## Finding 4 — the tax side is missing about two-thirds of Japan's revenue

Japan's tax structure, from the OECD *Revenue Statistics 2025* country note
(2023, total ¥200,343bn = 33.7% of GDP, implied GDP ¥594.5tn):

| Instrument | ¥bn | % of GDP | Set in OG-JPN? |
|---|---:|---:|---|
| Social security contributions | 78,335 | **13.18** | no — `tau_payroll = 0` |
| Personal income tax | 36,703 | **6.17** | no — US `DEP` functions |
| Corporate income tax | 27,942 | **4.70** | no — US 21% rate |
| VAT (consumption tax) | 29,355 | **4.94** | partly — `tau_c = 0.10` statutory |
| Excises | 7,533 | **1.27** | no |
| Taxes on property | 16,330 | **2.75** | no — `p_wealth = 0` |
| Other | 497 | 0.08 | no |
| **Total** | **200,343** | **33.70** | |

The single largest gap is **social insurance at 13.2% of GDP** — Japan relies on
it more than almost any OECD country (39.1% of all tax revenue, 4th highest in
the OECD). The model currently collects none of it.

On the consumption tax specifically: the family rule is that `tau_c` should
carry *all* indirect taxes, not VAT alone. Japan's goods-and-services taxes are
6.82% of GDP against household consumption of 53.6% of GDP, implying an
effective rate of about **12.7%**, not the statutory 10%. The statutory rate is
a fact; it is not the right model input.

Japan is also the one country where the standing family warning about bequest
taxes runs the other way. Inheritance tax raises **¥3,461bn** in the FY2025
budget (~0.56% of GDP) — genuinely material, unlike most countries. `tau_bq`
should be calibrated from collections rather than left at zero.

---

## Finding 5 — Japan's debt is domestically held, and the model assumes otherwise

`initial_foreign_debt_ratio` and `zeta_D` are never set, so both sit at OG-Core's
defaults of **0.4**.

Japan's actual foreign-held share is **13.7%** (MOF, *Breakdown by JGB and
T-Bill Holders*, March 2026 preliminary: foreigners ¥157.8tn of ¥1,150.1tn).
Foreigners hold only 8.1% of JGBs proper; the 55.6% foreign share of T-Bills is
what lifts the combined figure.

This matters for who bears the burden. At 40% foreign, debt service is a
transfer abroad and crowds out domestic households less. At 13.7%, Japanese
households hold the debt and receive the interest. That "Japan owes it to
itself" fact is one of the most-cited features of Japanese public finance and
the model currently gets it about three times wrong.

`zeta_K` is likewise unset (default `0.1`) and should be tuned so the solved
`K_f/K` matches Japan's IIP — Japan is the world's largest net creditor, so this
needs care rather than a default.

---

## Finding 6 — `g_y_annual` is defensible but justified by the wrong quantity

`macro_params.py` sets `g_y_annual = 0.008` and justifies it as "consistent with
Japan's low real GDP growth (~0.7% in 2023)".

`g_y` is not GDP growth. It is labour-augmenting productivity growth. In the
model, GDP growth is `g_y` *plus* population growth, and population growth comes
separately from the demographics — so justifying `g_y` by GDP growth confuses two
different quantities.

Measured labour productivity for Japan (World Bank `SL.GDP.PCAP.EM.KD`, GDP per
person employed, constant PPP):

| Window | growth/yr |
|---|---:|
| 1995–2019 | 0.69% |
| 2000–2019 | 0.56% |
| 2000–2024 | 0.45% |
| 2010–2024 | 0.15% |

The value 0.8% sits just above the top of that range. It is not indefensible,
but it needs a **named window and a stated rationale**, per family practice, and
it must be checked for consistency with whatever `debt_ratio_ss` is chosen.

Note the wrinkle that makes Japan interesting: Japan's *employment* grew (+0.36%
a year, 2010–2024) even as population fell (−0.23%), because participation among
women and older workers rose. That is a transitional effect that cannot continue
indefinitely, which is a reason to prefer a longer window.

---

## Finding 7 — structural divergence from the family

Every other country repo ships a packaged `og<xxx>_default_parameters.json` as
the single source of truth — OG-ZAF's has 129 keys. OG-JPN builds parameters in
Python functions instead.

That is why so much falls through to US defaults: with a JSON you see the whole
parameter surface at once and the gaps are obvious; with two small functions
returning six values, everything unset is invisible.

Recommend adopting the family layout. It also unlocks the family's
drift-prevention tooling (value-pinning tests, `{glue:text}` docs).

Smaller items:

- **`gamma = 0.38`** is plausible but unsourced. Needs Penn World Table
  (1 − labour share) for Japan.
- **`alpha_G = 0.20`, `alpha_T = 0.10`** are unsourced placeholders. Japan's
  total social security spending is 22.8% of GDP, of which pensions are 9.3% —
  so non-pension transfers are nearer 13% than 10%, though the split between
  `alpha_T` and government consumption needs care.
- **`alpha_I` is unset** (default 0.0), so public investment is zero. The
  spending identity `alpha_G + alpha_T + alpha_I = revenue/Y − pb*` cannot close
  correctly without it.
- **`initial_wealth_ratio` is unset.** For an unusually *old* population this is
  the parameter that determines whether initial households get a windfall or a
  confiscation. This bit OG-PHL badly and was invisible in reform-vs-baseline
  tables. Should be diagnosed before any policy run is trusted.
- **The `e` earnings matrix has no Japan tilt.** The family method is a
  single-scalar exponential tilt on OG-USA's matrix solved to match the
  country's Gini. Japan's World Bank Gini is 32.3 (2020).
- **No `un_api_token.txt` is needed on this machine** — one already exists in
  several sibling repos, so the README's "known prerequisite" blocker is already
  solvable locally.
- **Japan is genuinely missing from OG-Core's offline mirror.** The
  `country_dict` in `ogcore/demographics.py:121` has 11 countries and no `"392"`.
  The README's two upstream give-back items are correct and worth doing.

---

## Suggested order of work

Ordered by how much each changes the answer.

1. **`r_gov_shift`** — re-anchor to Japan's 0.80% nominal effective rate. Nothing
   else in the fiscal block can be right until this is.
2. **Debt concept** — choose net vs gross vs BOJ-consolidated, set
   `debt_ratio_ss` deliberately, and document it.
3. **`tau_payroll`** — 13.2% of GDP of social insurance is the largest single
   missing piece.
4. **Pension system** — switch to `Defined Benefits`, set `mean_income_data` in
   yen, target 9.3% of GDP.
5. **`initial_foreign_debt_ratio` / `zeta_D` → 0.137.**
6. **PIT** — fit the Gouveia-Strauss form to Japan's statutory schedule, tuned to
   6.17% of GDP. (The family default is GS, not HSV: GS floors the effective rate
   at zero, and HSV's negative rate at the bottom has caused transition debt
   runaways elsewhere.)
7. **CIT, `tau_c`, property taxes, `tau_bq`** — each from collections.
8. **Close the spending identity** — set `alpha_G`, `alpha_T`, `alpha_I` so
   primary spending equals revenue minus `pb*`.
9. **`e` matrix tilt** to Japan's Gini; document `chi_n` as uncalibrated.
10. **Repackage** as `ogjpn_default_parameters.json` and build the steady-state
    validation dashboard.

## Sources

- IMF World Economic Outlook, DataMapper API (`GGXWDG_NGDP`, `NGDP_RPCH`), Japan.
- OECD, *Revenue Statistics 2025 — Japan* country note (2023 data).
- OECD, *Pensions at a Glance 2023 — Japan* country note (2022 data).
- Ministry of Finance Japan, *Japanese Public Finance Fact Sheet*, April 2025
  (FY2025 General Account Budget).
- Ministry of Finance Japan, *Breakdown by JGB and T-Bill Holders*, March 2026
  preliminary (BOJ Flow of Funds).
- World Bank World Development Indicators (`SL.GDP.PCAP.EM.KD`,
  `NE.CON.PRVT.ZS`, `SP.POP.TOTL`, `SL.TLF.TOTL.IN`, `SI.POV.GINI`), Japan.
- OG-Core `ogcore/default_parameters.json`, `ogcore/pensions.py`,
  `ogcore/demographics.py` (v0.19.0).
