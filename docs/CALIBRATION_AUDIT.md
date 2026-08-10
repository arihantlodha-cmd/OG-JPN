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

### OG-Core cannot represent a negative sovereign rate — an upstream limitation

Found by running the calibrated model. `ogcore/fiscal.py:390` computes

```python
r_gov = np.maximum(
    p.r_gov_scale[t] * r - p.r_gov_shift[t]
    + p.r_gov_DY * DY_ratio + p.r_gov_DY2 * DY_ratio**2,
    0.00,        # <- hard floor at zero
)
```

The wedge is **floored at zero**. With Japan's parameters the formula returns
−0.74%; the model reports exactly `0.0000`.

For most of the country family this floor never binds and is a sensible guard.
For Japan it binds permanently, because a negative real effective rate on
government debt is not an anomaly there — it is the defining feature of the
fiscal position and has held for a decade.

The practical cost is about 0.6 percentage points of GDP a year in debt service
the real Japan does not pay, which flips the debt-stabilising primary balance
from roughly zero to a small surplus. The calibration gets as close as the model
allows and the gap is reported in the dashboard rather than hidden.

**This is worth raising upstream** alongside the two give-back items already in
the README. A country in a sustained negative-real-rate regime is exactly the
case the floor was not designed for.

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

## Finding 6b — the steady state has NEGATIVE growth, which changes the debt arithmetic

This one only appears once the model is actually solved on Japanese demographics,
and it matters more than any single parameter.

Solving on UN data gives a steady-state population growth rate of

```
g_n_ss = -1.07% per year
```

so the model's steady-state growth rate is

```
g = e^{g_y}(1 + g_n_ss) - 1 = e^{0.0056} x (1 - 0.0107) - 1 = -0.51% per year
```

**Japan's steady state is a shrinking economy.** That is the correct
representation of a country with a total fertility rate near 1.2, but it inverts
the usual debt intuition, because the debt-stabilising primary balance depends on
`r_gov − g`:

| | `r_gov` | `g` | `r_gov − g` | `pb*` at `D/Y = 1.0` |
|---|---:|---:|---:|---:|
| Typical emerging economy | +2% | +4% | −2.0% | −2.0% (deficit OK) |
| Japan, this calibration | −0.6% | **−0.51%** | **−0.09%** | **≈ 0** |

So even with the negative real interest rate that makes Japan's debt famously
cheap, a shrinking economy pushes `r_gov − g` back to roughly zero. **The model
says Japan needs an approximately balanced primary budget in the long run**, not
the primary deficit its low interest rate alone would seem to permit.

Against Japan's actual primary balance of −1.79% (2024), the stable-debt steady
state therefore embeds a consolidation of roughly 1.8 percentage points of GDP.
That should be stated in the docs as something the calibration deliberately
assumes, not discovered later as a puzzle.

It also means the negative interest rate and the shrinking population are doing
**opposite** things to debt sustainability, and a calibration that gets one right
and the other wrong will be wrong twice over.

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

## Result: where the calibrated steady state lands

Solved on real UN demographics, ogcore 0.19.0, fourteen tuning rounds.

| Moment | Model | Target | Gap | Source |
|---|---:|---:|---:|---|
| **Total tax revenue / Y** | **0.3359** | **0.3370** | **−0.0011** | OECD RevStats 2025 |
| — Income tax (PIT) / Y | 0.0616 | 0.0617 | −0.0001 | OECD RevStats 2025 |
| — Corporate tax / Y | 0.0472 | 0.0470 | +0.0002 | OECD RevStats 2025 |
| — Consumption + indirect / Y | 0.0682 | 0.0682 | **0.0000** | OECD RevStats 2025 |
| — Payroll / social insurance / Y | 0.1316 | 0.1318 | −0.0002 | OECD RevStats 2025 |
| **Pension outlays / Y** | **0.0929** | **0.0930** | **−0.0001** | OECD PaG 2023 |
| Foreign-held debt `D_f/D` | 0.1370 | 0.1370 | **0.0000** | MOF, Mar 2026 |
| **Capital-output `K/Y`** | **3.696** | **3.700** | **−0.004** | Penn World Table |
| Consumption / Y | 0.5765 | 0.5310 | +0.0455 | World Bank |
| Sovereign real rate `r_gov` | 0.0000 | −0.0060 | +0.0060 | OECD EO (model floor) |
| Interest rate `r` | 0.0416 | — | — | no data target |

Every fiscal moment lands within **0.11 percentage points of GDP**. The
capital-output ratio, the consumption tax and the foreign debt share are exact
to the reported precision.

## The consumption gap, fully decomposed

Consumption fell from 0.671 to **0.5765** over the calibration, against a target
of 0.531. There is no consumption parameter in OG-Core — `C` is the residual of
the resource constraint — so the remaining 4.55pp is exactly the sum of the
other three components, and each now has a named, quantified cause:

| | Model | Japan | Gap | Cause |
|---|---:|---:|---:|---|
| Consumption / Y | 0.5765 | 0.531 | **+4.55pp** | the residual of the three below |
| Investment / Y | 0.2578 | 0.278 | −2.02pp | growth-rate difference |
| Government / Y | 0.1877 | 0.201 | −1.33pp | `r_gov` floor + consolidation |
| Net exports / Y | −0.0220 | −0.009 | −1.30pp | no investment-income balance |

**Investment, −2.0pp — the growth rate, and nothing else now.** With `K/Y`
exactly on target and `delta` sourced from Japan's own consumption of fixed
capital, steady-state investment `(g + delta)·K/Y` is pinned by `g` alone.
Japan's investment rate implies `g = +0.51%`; the model's demographic steady
state gives `g = −0.04%`. Every other route into this number is closed: raising
it through `beta` would break the `K/Y` match that `beta` was just calibrated to.

**Government, −1.3pp — half of it is an OG-Core limitation.** Measured by
removing the `r_gov` floor in a scratch copy: **0.51pp**. The remainder is the
consolidation the stable-debt steady state embeds relative to Japan's actual
primary deficit. See `docs/UPSTREAM_OGCORE.md`.

**Net exports, −1.3pp — OG-Core cannot represent Japan's creditor position.**
This one is structural and worth stating plainly, because it is specific to
Japan. Japan runs a current-account surplus of 3–4% of GDP that is almost
entirely **investment income** on the world's largest net foreign asset position
(+¥533 trillion, about +86% of GDP); its *trade* balance is near zero. OG-Core
has no income balance — net exports are a pure residual of the resource
constraint, and the model represents foreign ownership of domestic capital but
not domestic ownership of foreign capital. So the single largest external fact
about Japan has no home in the model at any parameter setting.

**An option considered and rejected: `alpha_RM`.** OG-Core's remittance channel
adds household income from abroad, and structurally that is what Japan's
investment income *is* — income accruing to residents from foreign assets. It
looks like the obvious home for Japan's +4.2%-of-GDP primary income balance.

It is the wrong home, and the reason is instructive. `RM` enters the resource
constraint as an inflow with no matching asset stock: households would receive
the income but have nowhere to accumulate the foreign assets that generate it.
Japan does not consume its investment income — it recycles it into further
foreign asset accumulation, which is why its consumption is only 53% of GDP
*despite* a GNI 4% above GDP. Switching `alpha_RM` on would add the income
without the saving, raising consumption and making the fit worse while
appearing to add realism. Left off deliberately.

### What that means for using the model

The fiscal block is calibrated to Japanese data essentially exactly, and the
capital stock is on target. The consumption *level* runs about 4.5pp of GDP high
for three reasons that are all understood and none of which is a free parameter.
Reform exercises reported as **percentage changes** are unaffected by the level;
level statements about consumption should carry the caveat.

### Earnings: the full two-part method### Earnings: the full two-part method

The family's earnings method (EAPD-DRB/OG-ZAF#18, tracked for the country repos
in #63) has two halves, and both are implemented here:

**1. Age shape, from NTA.** Japan's own labour-income-by-age profile replaces
the US one. `scripts/fetch_nta_age_profiles.py` pulls Japan (2004) and the US
(2003, nearest-year) from the National Transfer Accounts database — both on the
same variable and variable type, since NTA levels are not comparable to national
wage surveys. Each profile is normalised over prime working ages so only the
*shape* transfers, and the ratio becomes a multiplicative factor on OG-USA's
curves.

The factor carries Japan's signature clearly:

| age | 20 | 45 | 50 | 55 | 60 | 62 | 65 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Japan ÷ US | 0.73 | 1.08 | 1.09 | 1.09 | 0.91 | 0.73 | 0.62 |

Earnings rise more steeply than in the US through the fifties — the seniority
wage system (年功序列) — then fall much harder after mandatory retirement at 60.
Peak earnings age moves from **61 to 57**.

**2. Inequality tilt, to Japan's Gini.** The single-scalar tilt
`e_JPN = e_USA · exp(a·e_USA)`, solved so the model Gini stands in the same ratio
to the US model Gini as Japan's measured Gini (32.3, World Bank, income basis)
does to the US reference (41.5, same concept). Japan is markedly more equal than
the US, so the profile compresses rather than stretches.

**An unplanned cross-check.** Before the age-shape adjustment, the pension
replacement rate had to be fitted to 0.399 — 2.6pp *above* its derived value of
0.373. With Japan's own age profile in place it fell to **0.358**, 1.5pp *below*.
Fixing the earnings block moved an unrelated fitted parameter toward its
independently-derived value. That is the kind of agreement you cannot arrange by
tuning.

### The full resource constraint### The full resource constraint

The place to judge a calibration's realism is the whole national-accounts
identity, not one line of it:

| | Model | Japan | Gap |
|---|---:|---:|---:|
| Consumption / Y | 0.6038 | 0.531 | **+0.073** |
| Investment (private + public) / Y | 0.2361 | 0.278 | −0.042 |
| Government consumption / Y | 0.1820 | 0.201 | −0.019 |
| Net exports / Y (residual) | −0.0219 | −0.009 | −0.013 |

The consumption gap is **not an independent error** — there is no consumption
parameter in OG-Core. `C` is the residual, so its gap is exactly the sum of the
other three, and each of those has a specific cause.

**Investment, −4.2pp — a real growth-rate difference.** In any steady state
private investment is `(g + delta)·K/Y`. Japan's private GFCF of about 24.5% of
GDP (27.8% total less ~3.3% public), against `K/Y` of 3.62 and Japan's own
`delta` of 0.062, implies **`g = +0.56%`**. The model's demographic steady state
has **`g = −0.51%`**. Japan today invests like an economy growing at half a
percent; its demographics deliver one shrinking at half a percent. Closing this
would mean overriding the UN population projection.

**Government, −1.9pp — the consolidation gap, exactly.** The model's `pb*` is
+0.52% of GDP; Japan's actual primary balance is −1.79%. That is **2.3
percentage points** of consolidation the stable-debt steady state embeds, and it
shows up as government consumption 1.9pp below Japan's. The two match because
they are the same thing seen from different sides of the budget.

**Net exports, −1.3pp.** A residual of the resource constraint, not a modelled
trade sector.

## Answers to the open questions

Each of these was tested, not asserted.

### The `tau_c` base problem — FIXED

`tau_c` delivers Japan's indirect-tax revenue on a consumption base ~13% larger
than Japan's, so a *rate change* did not transfer across: applying Japan's
+1.85pp effective rise to the model's base over-collected by the base error.

The fix is to size the reform by the **revenue it must raise** rather than by a
rate change. Japan's 10% → 12% consumption tax raises VAT collections from 4.94%
to 5.93% of GDP, a gain of +0.99pp. So:

```
d(tau_c) = revenue gain / (model C/Y)
```

The oversized base now appears in both the numerator (via the calibrated `tau_c`)
and the denominator, and cancels exactly. Implemented as `reform_tau_c()` in
`examples/analysis_consumption_tax.py`, computed off the solved baseline rather
than hard-coded.

### The investment gap — mostly an artefact of comparing a steady state to today

The model's population growth is a **path**, not a constant: −0.33%/yr in 2025
(which is Japan today), deepening to −1.07% only in the long run as the age
structure matures. Steady-state investment uses the terminal rate.

| `g_n` used | `g` | model private I/Y | vs Japan 0.245 |
|---|---:|---:|---:|
| t=0 (2025, UN actual) | +0.23% | 0.2331 | −0.012 |
| t=10 (2035) | −0.10% | 0.2212 | −0.024 |
| t=20 (2045) | −0.46% | 0.2079 | −0.037 |
| steady state (~2100+) | −0.51% | 0.2061 | −0.039 |

**At Japan's current population growth the model invests 23.3% of GDP against
Japan's actual 24.5% — a 1.2pp gap, not 3.9pp.** The steady state is Japan's
demographic destiny, not Japan now; scoring it against today's data charges the
model for a decline that has not happened yet. The right comparison for "does
this look like Japan today" is the early transition, which is why the transition
validation matters more than it usually would.

### The government gap — 0.5pp is OG-Core's floor, measured

Tested by monkey-patching the `r_gov` floor out of a scratch copy of ogcore
(diagnostic only, not committed):

| | `r_gov` | model `G/Y` |
|---|---:|---:|
| floored (shipped ogcore) | +0.0000 | 0.1820 |
| floor removed | −0.0058 | **0.1871** |
| at Japan's *current* effective rate (−2%) | −0.0200 | 0.2021 |
| **Japan actual** | | **0.2010** |

So the floor costs **0.51 percentage points** of government consumption. The
remaining ~1.4pp is not a defect but a deliberate choice: anchoring `r_gov` to
the *normalised* long-run rate (−0.6%) rather than Japan's current one (−2%). At
Japan's current rate the model reproduces Japanese government consumption to
within 0.1pp.

### Preference parameters — not curve-fitting, arithmetically excluded

`beta`, `sigma` and `frisch` remain at OG-Core's values. This is not deference to
convention; there is no room for them:

```
I_private/Y = (g + delta) x K/Y
```

`K/Y` is already on target (3.62 against the PWT's 3.70) and `delta` is sourced
from Japan's own consumption of fixed capital. To reach Japan's private
investment rate you would need `K/Y = 4.31` — **16% above the PWT target**.
Investment and the capital-output ratio cannot both be hit while `g` is fixed.
Raising `beta` to lift investment would simply break `K/Y`. Only `g` is free, and
`g` is the UN's demographics.

### The `e` matrix — now tilted to Japan

Ported the family's single-scalar method (`ogjpn/income.py`, from OG-PHL):
`e_JPN = e_USA · exp(a·e_USA)`, solving one scalar so the model Gini stands in
the same ratio to the US model Gini as Japan's measured Gini does to the US.
Japan's World Bank Gini is **32.3** (2020) against the US reference of 41.5 —
both on the **income** concept, which is the family's standing trap (mixing an
income Gini against a consumption one mis-states the tilt).

Japan tilts the *opposite* way from most of the family: it is markedly more equal
than the US, so the profile compresses rather than stretches. The effect on the
dashboard is small and in the predicted direction — consumption +0.16pp (less
inequality means less saving) and revenue −0.27pp (a compressed distribution
yields less under a progressive schedule). It is the right thing to do for
accuracy even though it moves the consumption gap slightly the wrong way.

### `chi_n` — borrowed, and for Japan that is defensible to within 1%

`chi_n` stays at OG-USA's values, as everywhere in the family. For Japan this is
better than a convention, because the quantity the model actually needs to match
is total labour input per working-age person — OG-Core has no extensive margin,
so everyone supplies some `n`:

| | hours/worker | employment rate (15-64) | hours per working-age person |
|---|---:|---:|---:|
| Japan | 1,611 | 79.3% | 1,278 |
| United States | 1,799 | 71.6% | 1,288 |

**Ratio 0.992.** Japan works 10.5% fewer hours per worker but puts far more
people to work, and the two almost exactly cancel. A single-scalar re-tilt would
move `chi_n` by under 1%, which is inside the measurement noise. Documented as
borrowed, with the evidence that borrowing is harmless here.

### Income-differentiated demographics — deliberately not used

ogcore accepts `fert_gradient`, `mort_gradient` and `infmort_gradient`, and the
measured tilts live in EAPD-DRB/Demographic-Gradients. **Japan is in none of the
three files.** The library covers 78 developing countries, and its own AGENTS.md
is explicit that the income-based fallback is valid only between $200 and
$10,000 GNI per head — *"high-income countries are out of scope, not missing: do
not extrapolate to them."* Japan's GNI per head is about $39,000.

Japan does have a measured and widening socioeconomic mortality gradient in the
epidemiological literature, but it is **ecological** (municipality-level
deprivation), and the same AGENTS.md warns against pooling measurement bases.
Extrapolating a developing-country gradient could also get the *sign* wrong for
fertility, where Japan's pattern runs through marriage rates rather than family
size. So the gradients are left off; `income_percentiles` is still passed, so the
arrays stay J-wide with one set of rates per group.

**This is a well-scoped give-back:** Japan has the vital statistics to become the
library's first high-income entry.

### Where further tuning stops being calibration

Every remaining revenue gap is under 0.3pp of GDP. That is **below the precision
of the source data** — the family's own guidance flags that a GDP rebasing moves
tax-to-GDP ratios by 2–3pp (South Africa's 2021 rebasing moved it 2.6pp). Tuning
past this point fits noise.

## Adversarial check

Every load-bearing claim in this document was attacked deliberately, on the
principle that a calibration which has only been checked by the person who built
it has not been checked. **Two of the five attacks succeeded**, and both fixes
are in the numbers above.

**1. Are the revenue matches real, or offsetting errors? — MOSTLY SURVIVED.**
Hitting a revenue total can hide a wrong rate on a wrong base. Testing each
instrument's *base* rather than its yield: the payroll base is `wL/Y = 0.5700`
against a labour share of 0.570 — exact, so `tau_payroll × wL/Y = 0.1318` is the
target hit for the right reason. Wealth and bequest bases are the model's own
`B/Y` and `BQ/Y` and were tuned against them.

*But `tau_c` did not fully survive.* The model's consumption base is 14% larger
than Japan's, so the calibrated 11.2% is delivering Japan's indirect-tax revenue
on an oversized base; the rate that would do it on Japan's actual consumption
share is 12.8%. **Consequence for reform work:** the revenue level is right, but
a simulated consumption-tax *change* will over-deliver revenue relative to Japan
by roughly the base error. That is a real caveat for anyone running the
consumption-tax scenario, and it is the reason to prefer the reform's percentage
changes over its levels.

**2. Does `r_gov × D` reproduce Japan's actual interest bill? — SURVIVED.**
The worry is that netting government assets out of debt while keeping the *net*
interest rate double-counts the netting. It does not: the model's debt service is
`0.0000 × 1.0 = 0.00% of GDP`, and Japan's general-government net interest in
2024 was **−0.12% of GDP**. Both are approximately zero. The net-debt /
net-interest pairing is internally consistent.

**3. Does the fiscal identity actually hold in the solve? — SURVIVED.**
Not assumed, measured from the solved steady state: revenue 0.3364 less primary
spending 0.3312 gives an actual primary balance of +0.0051 against a required
`pb*` of +0.0052 — a residual of **2.7 × 10⁻⁵**.

**4. Is the investment gap as large as claimed? — FAILED, corrected.**
An earlier version of this document compared the model's `I_total` (which is
**private** investment) against Japan's gross fixed capital formation (which is
**private plus public**). That overstated the gap by the whole 3pp of public
investment. Corrected, the investment gap is 4.2pp rather than 6.9pp, and the
implied growth-rate difference is 1.1pp rather than 1.6pp.

**5. Is the pension replacement rate justified or rationalised? — FAILED,
corrected.** The earlier justification for raising `alpha_db` above the OECD's
32.4% was that OG-Core has one pension tier while Japan has two. That is wrong:
the OECD country profile states its modelling covers the whole public system —
*"The public pension system has two tiers: a basic, flat-rate scheme and an
earnings-related plan"* — so 32.4% already includes both. The earlier text also
cited the OECD's 38.8% *net* replacement rate as corroboration, which is a
different concept (net of tax); its numerical closeness was coincidence.

The real cause is that 32.4% is an **old-age** rate while Japan's 9.3% of GDP
also funds survivors' and disability pensions, which OG-Core's single
defined-benefit block cannot separate. That justifies roughly `0.324 × 1.15 =
0.373`; the remaining ~2.6pp to the calibrated 0.399 is **fitted, and is now
labelled as fitted** in `ogjpn/pension_params.py` rather than dressed up as a
derivation.

### What this check does not cover

The steady state is verified; the **transition is not**. The family's experience
is that a calibration can pass every steady-state check and still diverge on the
time path — the steady-state closure silently forces spending to balance, while
TPI holds `alpha_G` and `alpha_T` at their input values for `tG1` periods. A
baseline TPI run is the next verification step, and `initial_wealth_ratio`
(undiagnosed, see below) is the parameter most likely to distort it.

## What is still not calibrated

Stated plainly so it is not mistaken for finished work:

- **`chi_n`** is OG-USA's, uncalibrated. This is the family-wide default state —
  no country repo has recalibrated it — but it is borrowed, not calibrated.
- **The `e` earnings matrix** is OG-USA's, with no Japan Gini tilt.
- **`zeta_K = 0.10`** is not anchored to a constructed IIP share. In the final
  calibration it produces `K_f/K = −0.008` — a marginal net creditor position,
  which is at least the right *sign* for the world's largest net creditor
  (net international investment position +¥533tn, about +86% of GDP), though
  nowhere near the magnitude. Note OG-Core represents foreign ownership of
  domestic capital but not domestic ownership of foreign capital, so Japan's
  creditor position cannot be represented properly at any `zeta_K`.
- **`phi1 = 1.30`** in the income-tax function is a family-analogous value, not a
  fit to Japan's statutory brackets.
- **`initial_wealth_ratio`** has not been diagnosed. For the oldest population in
  the OECD this is the parameter most likely to distort the transition, and it is
  invisible in reform-versus-baseline tables.

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
