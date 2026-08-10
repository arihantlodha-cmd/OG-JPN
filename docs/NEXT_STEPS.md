# OG-Japan: what to do next

Phases 1 and 2 are now substantially done. `docs/CALIBRATION_AUDIT.md` records
what was found and where every value comes from. This file is what is left.

## 0. Demographics (unchanged)

Live Japan demographics need a free UN Data Portal API token, saved as
`un_api_token.txt` in the directory you run from (already gitignored).
Register at https://population.un.org/dataportal/about/dataapi.

## 0b. Make the warm start automatic  <- carries across projects

`ogjpn/warm_start.py` currently needs a seed produced by hand
(`examples/save_warm_start.py`) and `warm_start.enable()` called by each entry
point. Without a seed the steady state does not converge at all, so this is a
sharp edge for anyone picking the repo up.

It should be automatic:

- write the seed on **every** successful solve, so it is always fresh;
- `enable()` by default, with a flag to force a cold start for testing;
- factor the shim into something shareable — every country repo will hit this,
  and this family has hit it before.

The real fix is upstream (`docs/UPSTREAM_OGCORE.md` item 3): ogcore should derive
its seeds from parameters it already has rather than hardcoding `0.07`, and
accept a warm start. But the repo-side helper is worth having regardless, because
it also makes reruns cheap.

## 1. Run the in-model tuning loop  <- the main remaining task

Several parameters cannot be pinned down from published data alone. They are
ratios the model produces, so they have to be tuned against a solved steady
state. Each is marked `NEEDS TUNING` in the source with its target.

The loop is cheap — a warm steady-state solve is roughly a minute with
`client=None` — and converges in three to five iterations for all dials at once:

```
PYTHONPATH=. python examples/validate_japan.py
```

then adjust and re-solve. The dials and their targets:

| Parameter | Where | Tune until |
|---|---|---|
| `etr_params` phi2 | `tax_params.py` | `iit_revenue/Y` = 0.0617 |
| `tau_c` | `tax_params.py` | `cons_tax_revenue/Y` = 0.0682 |
| `adjustment_factor_for_cit_receipts` | not yet set | `business_tax_revenue/Y` = 0.0470 |
| `p_wealth` | `tax_params.py` | property-tax revenue = 2.21% of GDP |
| `tau_bq` | `tax_params.py` | bequest-tax revenue = 0.55% of GDP |
| `r_gov_shift` | `macro_params.py` | solved `r_gov` = −0.006 |
| `zeta_K` | `macro_params.py` | solved `K_f/K` = Japan's IIP share |
| `alpha_G`, `alpha_T`, `alpha_I` | `macro_params.py` | budget identity closes (below) |

Two cautions from the family's experience:

- Revenue responds **concavely** to the Gouveia-Strauss `phi2` — top incomes sit
  in the saturated region — so expect two or three iterations rather than one
  proportional step.
- Re-validate `zeta_K` after **any** tax change. Tax recalibration moves domestic
  saving, which moves `K_f/K` at fixed `zeta_K`.

### The budget identity is the stability constraint

For debt to hold at the target in the steady state:

```
alpha_G + alpha_T + alpha_I  =  revenue/Y  -  pb*
pb* = (r_gov - g) / (1 + g) * debt_ratio_ss
```

OG-Core's steady state silently forces spending to the consistent level, so
**the SS will solve and look fine even if this is violated** — and then the
transition blows up, because TPI holds `alpha_G` and `alpha_T` at their input
values for the first `tG1` periods. If the baseline transition diverges, check
this identity before touching any solver knob.

`validate_japan.py` prints the identity's terms at the end of every run.

## 2. Fit the income-tax schedule properly

`etr_params` currently uses `phi0 = 0.55` (Japan's statutory top marginal rate:
45% national + 10% local), which is an anchor rather than a fit, and a
family-analogous `phi1 = 1.30`, which is **not** fitted to Japan's schedule.

Fit `phi1` to Japan's actual national brackets (5/10/20/23/33/40/45%) plus the
flat 10% local inhabitant tax, then tune `phi2` to collections.

## 3. Tilt the earnings matrix to Japan

The `e` ability matrix is still OG-USA's, untilted. The family method is a
single-scalar exponential tilt, `e_country = e_USA * exp(a * e_USA)`, solving the
one scalar `a` by bisection so the model Gini matches Japan's.

Watch the concept trap: the target Gini and the US reference Gini must be the
same welfare concept. Japan's World Bank income Gini is 32.3 (2020) against the
World Bank US anchor of 41.5.

## 4. Diagnose `initial_wealth_ratio`

Japan has the oldest population of any large economy, which is exactly the case
where this bites. Without the parameter, the transition imposes the steady-state
wealth profile rescaled so aggregate B(0) = B_ss, which hands initial households
a uniform windfall or confiscation.

Compute the implied scale `B_ss / get_B(b_sp1, p, "SS", True)`. Anything far from
1 is a problem. The fingerprint is a violent year-1-or-2 consumption spike
concentrated in ages 60+, an investment collapse, and a spurious debt paydown.

It is invisible in reform-minus-baseline tables, because both paths share the
initial condition — so it survives every reform validation. Diagnose it before
trusting any level exercise.

## 5. Consider adopting the family's packaged-JSON layout

Every other country repo ships an `og<xxx>_default_parameters.json` as the single
source of truth; OG-ZAF's has 129 keys. Building parameters in Python functions
is why so much silently fell through to US defaults — with a JSON you see the
whole parameter surface at once.

This is a structural choice for the maintainer, not an obvious win: the Python
modules carry their sourcing in comments, which a JSON cannot.

## 6. Give back upstream

Both items from the original plan still stand and are still worth doing:

1. Add `"392": "JPN"` to the `country_dict` in `ogcore/demographics.py:121`
   (verified: it has 11 countries and no Japan) — but only together with (2),
   since the entry is useless without data behind it.
2. Contribute Japan's demographic CSVs to `EAPD-DRB/Population-Data` so Japan
   works offline like the other country models.

## 7. Then Phase 3

Pick one real Japanese policy question and run baseline vs reform: a
consumption-tax change, a higher retirement age, or a pension reform. With a
defined-benefit pension system now in place, the retirement-age and
replacement-rate levers are both meaningful — `retirement_age` and `alpha_db` in
`ogjpn/pension_params.py`.

## How to run

```
PYTHONPATH=. python examples/run_ogjpn_ss.py     # steady state
PYTHONPATH=. python examples/validate_japan.py   # SS vs Japanese data
PYTHONPATH=. python -m pytest tests/             # calibration tests
```
