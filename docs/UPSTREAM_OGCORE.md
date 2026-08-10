# Upstream contributions this calibration identifies

Three things OG-JPN needs that belong in OG-Core or the shared data repos rather
than in this country model. Each is stated with what it costs to work around,
because that is what decides whether it is worth a maintainer's time.

---

## 1. `r_gov` is floored at zero, which Japan is permanently below

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

## 2. Japan is missing from the offline demographic mirror

**Where:** `ogcore/demographics.py`, the `country_dict` fallback (11 countries,
no `"392"`).

Live UN data works for Japan; the offline mirror does not, so a run without a UN
API token cannot reach Japanese demographics at all. Two paired changes:

1. add `"392": "JPN"` to `country_dict`; and
2. contribute Japan's fertility, mortality and population CSVs to
   [EAPD-DRB/Population-Data](https://github.com/EAPD-DRB/Population-Data) in the
   same format as the other countries.

Either alone is useless — the dictionary entry points at files that must exist.
The CSVs can be generated from the UN API once a token is in hand.

---

## 3. Demographic gradients have no high-income route

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

## Note on scope

None of these block the calibration. Items 2 and 3 were already identified in
the project README; item 1 was found by running the calibrated model and is new.
All three are recorded here rather than worked around, because a country repo
quietly compensating for an upstream limitation is how a limitation becomes
invisible.
