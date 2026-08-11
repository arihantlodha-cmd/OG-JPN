# Upstream contributions this calibration identifies

Seven things this calibration needs that belong in OG-Core or the shared data
repos rather than in a country model. Each is stated with what it costs to work
around, because that is what decides whether it is worth a maintainer's time.

Items 1, 3, 4 and 7 affect **every** country repo, not just Japan. Item 3 is
worst for countries whose households hold a lot of wealth; item 4 for those
whose currency is not the US dollar.

---

## replacement_rate_adjust ignored outside US-Style Social Security

**Reported: PSLmodels/OG-Core#1200.** `replacement_rate_adjust` is read only in
`pensions.SS_amount()`. `DB_amount`, `NDC_amount` and `PS_amount` ignore it.
Verified directly: US-Style scales exactly 0.50x when the adjustment is halved,
Defined Benefits does not move at all (0.92659 both ways).

Blocks modelling Japan's macroeconomic slide, which is the reason the DB block
would otherwise pay 12.6% of GDP in pensions against an actual 9.3%.

Worked around locally by `ogjpn/pension_slide.py`, which wraps
`pensions.pension_amount` (the one function that receives both `t` and `method`)
and applies the adjustment for non-US systems.

## r_gov clipped at zero

`fiscal.get_r_gov` wraps the wedge in `np.maximum(..., 0.00)`. Japan's sovereign
real rate is genuinely negative (-0.60% measured; the calibrated wedge returns
-0.6023%), and the clip discards it. It raises the debt-stabilising primary
balance by 0.68pp of GDP, which is the difference between a model whose fiscal
stance matches Japan's and one demanding a primary surplus Japan has never run.

`r_gov` enters the model **linearly everywhere** -- no division by it, no powers,
no logs -- with exactly two consumers, `debt_service = r_gov * D` and
`r_p = (r_gov*D + r_K*K)/(D + K)`, whose denominator is strictly positive. So
removing the floor is arithmetically safe. Worked around by
`ogjpn/rgov_floor.py`.

**TODO: offer this as a PR upstream once verified further.** Not yet reported --
the floor may be deliberate for sovereigns where a negative wedge is implausible,
so the right change is likely to make it opt-out rather than delete it.

## Payroll tax counted twice in v0.19.1 (not ours, but blocking)

**PSLmodels/OG-Core#1199** (not ours). PR #1184 adds
`iit_payroll_tax_revenue += payroll_tax_revenue`, double-counting the payroll
take, and any model with a nonzero `tau_payroll` then fails with
`Steady state aggregate resource constraint not satisfied`.

This repo pins **v0.19.0 + PR #1189 only**, which predates #1184, so it is not
affected. But `tau_payroll = 0.2312` here, so OG-JPN **will** break the moment
#1189 merges into a master carrying #1184. This cost several solves before it
was identified: installing the #1189 branch directly pulls in its merge commits
from upstream/master and therefore the bug. Build the base as v0.19.0 plus the
single PR diff instead.


## 1. `get_pop_objs` freezes the vital rates at `final_data_year`

**Where:** `ogcore/demographics.py`, `get_pop_objs()`.

**Status: identified here, PR to follow.**

Fertility, mortality and immigration are held constant at their
`final_data_year` values for the whole path. Every country repo in the family
passes a window of one to two years (`start_year + 1`; ogcore's own default is
`start_year + 2`), so every model runs on two years of UN data and then frozen
rates forever — even though the UN publishes projections to 2100 for all of
them.

**What it cost here.** With the family's window, Japanese mortality was frozen at
its 2026 level and the implied steady-state population growth came out at
**−1.070%/yr**, against the UN medium variant's own 2025–2100 implied average of
**−0.676%**. Widening to 20 years gives −0.698%, within 0.02pp of the UN. The
discontinuity where the window ends also produced a resource-constraint breach
two periods into the transition that failed the solve outright.

**It also breaks the transition, and widening the window is not a full fix.**
The freeze creates a discontinuity in `imm_rates` at the window boundary, and
OG-Core's own population stationarization creates a second one around t=118.
Both breach the default `RC_TPI` tolerance of 1e-4 for a country with sharp
demographic change, and the baseline transition raises
`RuntimeError: ... (RC_error)`.

Measured on Japan — only 2 of 320 periods breach, the neighbours being five
orders of magnitude smaller:

| window | `g_n_ss` | jump at window boundary | largest late jump |
|---|---:|---:|---:|
| start+20 | −0.698% | 1.30e-01 | 5.15e-01 (t=118) |
| start+40 | −0.568% | 4.83e-02 | 4.06e-01 (t=118) |
| start+60 | −0.463% | 4.36e-02 | 4.64e-01 (t=118) |

Widening shrinks the boundary jump but **the late discontinuity is invariant to
it**, at every window from start+20 to start+74 (jump 0.50–0.56, always at
t=118). Its mechanism is explicit in the source:

```python
# ogcore/demographics.py
fixper = int(1.5 * S)                    # = 120 for S = 80
...
target_pop[fixper] = total_pop * fixed_full_dist
```

At `fixper` the evolving population distribution is **replaced** by the fixed
steady-state one. That is a step change, it lands at period 120 regardless of
any country-side setting, and for a country with sharp demographic change it
breaches `RC_TPI`. No choice of `final_data_year` avoids it — the fix has to be
upstream.

Two smaller notes from the same area: `assert fixper > T0` caps the usable data
window at `1.5 * S` periods, and `final_data_year = start_year + 75` fails
outright because UN WPP ends at 2100 and the immigration residual needs the
following year. So the full usable horizon is 74 years.

**Proposed change (two parts).** First, let the demographic path optionally
follow the **UN projection** rather than freezing at a single year — for example a
`use_projection=True` flag, or accepting a `final_data_year` far enough out that
the projection is consumed and documenting that it is the intended use. Either
way the current behaviour is a trap: the parameter reads like a data-fetch
boundary and is in fact the assumption that sets the model's long-run growth
rate.

Second, **smooth or taper the `fixper` handoff** instead of substituting the
fixed distribution in one period. Blending over a few periods, or aligning the
handoff with where the projected rates have already flattened, would remove the
step without changing the steady state it converges to.

The first part alone is not enough: this repo now uses the full UN horizon
(`ogjpn.constants.DEMOGRAPHIC_DATA_YEARS = 74`) and the transition still
breaches at `fixper`.

---

## 2. `r_gov` is floored at zero, which Japan is permanently below

**Where:** `ogcore/fiscal.py`, `get_r_gov()` (both the scalar and the path branch).

```python
r_gov = np.maximum(
    p.r_gov_scale[t] * r - p.r_gov_shift[t]
    + p.r_gov_DY * DY_ratio + p.r_gov_DY2 * DY_ratio**2,
    0.00,        # <- hard floor
)
```

**Why it matters for Japan.** Japan's general government pays approximately
*zero net interest*: interest income on its financial assets (the GPIF, foreign
reserves, the Fiscal Loan Fund) roughly cancels interest paid. OECD Economic
Outlook puts net interest at **−0.12% of GDP in 2024**, and the effective real
rate on net debt averaged about **−0.6%** over 2015–2024. This is not a
transient anomaly — it has held for a decade and is the single most distinctive
feature of Japanese public finance.

With Japan's calibrated parameters the formula returns **−0.58%**; the model
reports exactly `0.0`.

**What it costs, measured.** Removing the floor in a scratch copy and re-solving:

| | `r_gov` | `G/Y` |
|---|---:|---:|
| shipped ogcore (floored) | +0.0000 | 0.1820 |
| floor removed | −0.0058 | **0.1871** |
| Japan actual | | 0.2010 |

**0.51 percentage points of GDP** of government consumption. The floor does not
distort the interest bill — `r_gov × D` is ~0 either way, which is right — it
distorts the debt-stabilising primary balance, because `pb*` depends on
`r_gov − g`.

There is no legitimate workaround inside a country calibration. `pb* = (r_gov −
g)/(1+g) × D` cannot be brought down by any admissible `D`, and compensating
elsewhere would mean deliberately mis-stating another parameter.

**Proposed change** — minimal and backwards-compatible. Add a parameter rather
than removing the guard, so existing behaviour is unchanged for every other
country:

```python
# ogcore/default_parameters.json
"r_gov_floor": {
    "title": "Lower bound on the real interest rate on government debt",
    "description": "Floor applied to r_gov. Zero for most countries; set
        negative for sovereigns in a sustained negative-real-rate regime.",
    "value": [{"value": 0.0}],
    "validators": {"range": {"min": -0.1, "max": 0.1}}
}

# ogcore/fiscal.py
r_gov = np.maximum(..., p.r_gov_floor)
```

Defaulting to `0.0` reproduces today's behaviour exactly.

---

## 3. The steady-state bequest seed is hardcoded, and it is two orders of magnitude out

**Where:** `ogcore/SS.py`, `SS_initial_guesses()` — carrying OG-Core's own TODO.

```python
if p.use_zeta:
    b_guess = np.ones((p.S, p.J)) * b_val      # b_val IS honoured here
    ...
else:
    b_guess = (
        np.ones((p.S, p.J)) * 0.07
    )  # TODO: remove hardcode here and next line
    BQguess = aggr.get_BQ(rguess, b_guess, None, p, "SS", False)
```

With `use_zeta = False` — the setting every country repo uses — the `b_val`
argument is **ignored** and household savings are seeded at a hardcoded `0.07`.
Bequests for all `J` groups are then derived from that.

**Measured on Japan**, comparing the seed against the solved steady state:

| group | seed | solved | ratio |
|---|---:|---:|---:|
| j=0 (bottom 25%) | 0.000330 | 0.0247 | 75× |
| j=3 | 0.000132 | 0.0219 | 166× |
| j=6 (top 1%) | 0.0000132 | 0.00461 | **349×** |
| **total** | **0.00132** | **0.177** | **134×** |

So **7 of the 14 unknowns start two orders of magnitude away**, and the error is
worst where the model is most nonlinear. Everything the calibration *can* control
is already at the solution — seeding `r` at 0.040 against a solved 0.0399, and
the derived `w` at 1.5464 against 1.5476 — and the solve still struggles, because
half the guess vector is untouchable.

The exposure scales with how much wealth a country's households hold: `0.07` is a
US-shaped number, and Japan's solved population-weighted savings are about 4.2.
An old, wealthy, high-saving population is the worst case, which is precisely the
kind of country this model exists to study.

**Proposed change.** Honour `b_val` in both branches, and default it to something
derived rather than fixed — the simplest defensible seed is
`b_val = target wealth-to-GDP × Y_guess`, both of which the calibration already
knows. Failing that, expose `b_val` as a `Specifications` parameter so a country
repo can set it; today it is a function argument that `run_SS` never passes.

---

## 4. `initial_guess_factor_SS` is capped below what a non-dollar currency needs

**Where:** `ogcore/default_parameters.json`, `initial_guess_factor_SS`
(`value` 139355.154, `range` max **500000**).

`factor` converts model units to the country's currency, so it scales directly
with `mean_income_data`. OG-Core's default is OG-USA's solved value in **US
dollars**, and the validator caps the parameter at 500,000.

Japan's solved factor is about **7.0 million** yen. The correct seed is
therefore not merely absent — it **cannot be entered**, because it exceeds the
maximum by a factor of 14.

The cap is currency-dependent in a way nothing in the parameter's name or
description suggests. Any country whose currency has a low unit value is
affected, and the further the unit value from the dollar the worse it gets:
Japanese yen, Korean won, Indonesian rupiah, Vietnamese dong. For a rupiah
calibration the required seed would be orders of magnitude beyond the cap.

**What it does and does not cost.** Raising the seed to the permitted maximum of
500,000 was tried here and took 569 GE iterations, against 30–267 on the shipped
default in earlier solves — though those had different parameter sets, so it is
not a controlled comparison. What is clear is that the cap is not what blocks a
solve on this calibration; the seeds are left at OG-Core's defaults.

The reason to fix it upstream is correctness rather than speed: a solver seed
that cannot be set to the right order of magnitude is a trap waiting for a
country whose solve is less forgiving, and the failure mode would be a slow
stall rather than a clean error. The further a currency's unit value sits from
the dollar, the larger the mismatch — a rupiah calibration would need a seed
orders of magnitude past the cap.

**Proposed change.** Raise or remove the maximum. The parameter is a solver
seed, not an economic quantity, so a wide bound costs nothing:

```python
"validators": {"range": {"min": 1.0, "max": 1e12}}
```

Better still, default it to something currency-neutral — e.g. derive the seed
from `mean_income_data` rather than shipping a US level.

---

## 5. Japan is missing from the offline demographic mirror — ALREADY IN FLIGHT

**Where:** `ogcore/demographics.py`, the `country_dict` fallback (11 countries,
no `"392"`).

**Status: PSLmodels/OG-Core#1196 is open**, paired with
EAPD-DRB/Population-Data#14 which supplies the data. Nothing further needed
here; recorded so the list is complete.

Live UN data works for Japan; the offline mirror does not, so a run without a UN
API token cannot reach Japanese demographics at all. Two paired changes:

1. add `"392": "JPN"` to `country_dict`; and
2. contribute Japan's fertility, mortality and population CSVs to
   [EAPD-DRB/Population-Data](https://github.com/EAPD-DRB/Population-Data) in the
   same format as the other countries.

Either alone is useless — the dictionary entry points at files that must exist.
The CSVs can be generated from the UN API once a token is in hand.

---

## 6. Demographic gradients have no high-income route

**Where:** [EAPD-DRB/Demographic-Gradients](https://github.com/EAPD-DRB/Demographic-Gradients).

The library covers 78 developing countries and its `AGENTS.md` is explicit that
the income-based fallback is valid only between $200 and $10,000 GNI per head:
*"high-income countries are out of scope, not missing: do not extrapolate to
them."* Japan is about $39,000, so `fert_gradient`, `mort_gradient` and
`infmort_gradient` are all left unset here — correctly, since extrapolating
could get the *sign* wrong for fertility, where Japan's income relationship runs
through marriage rates rather than family size.

Japan is a good candidate to become the library's **first high-income entry**:
it has complete vital statistics, a substantial epidemiological literature on
socioeconomic mortality differentials, and the differentials are measured and
widening. The obstacle is that the published Japanese work is *ecological*
(municipality-level deprivation), which the library's own guidance says must not
be pooled with its individual wealth-rank basis — so it needs a purpose-built
derivation rather than a citation.

---

## 7. The NTA age-shape method belongs in a shared place

**Where:** the country repos' `income.py`, or a shared helper.

**Status: implemented here, worth generalising.**

EAPD-DRB/OG-ZAF#18 sets out a two-part earnings method — an NTA age-shape
adjustment plus the Gini tilt — and #63 tracks getting it into the country
repos. Only the tilt is in the repos today, which leaves the *US* age profile in
place for every country.

This repo implements both halves (`ogjpn/income.py`,
`scripts/fetch_nta_age_profiles.py`). The fetch is the fiddly part and is
country-agnostic: NTA has no API, so it walks a session form and needs a
`Referer` header on the download POST. That machinery would be better shared than
re-derived per country.

For Japan the difference is not cosmetic — the seniority wage system and
mandatory retirement at 60 move peak earnings age from 61 to 57.

---

## Note on scope

None of these block the calibration outright. Item 4 was already identified in
the project README and is now an open PR; item 5 was identified there too. Items
1, 2, 3 and 6 were found by building and running this calibration. All are recorded here rather than quietly worked around, because a
country repo compensating for an upstream limitation is how a limitation becomes
invisible.
