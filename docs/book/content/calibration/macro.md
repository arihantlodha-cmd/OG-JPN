(Chap_Macro)=
# Macroeconomic and fiscal parameters

The macro parameters are set in `ogjpn/macro_params.py`. Each value is sourced in a comment next to it.

| Parameter | Value | Source |
|---|---|---|
| `g_y_annual` (labor-augmenting productivity growth) | 0.008 | IMF WEO real GDP growth (~0.7% in 2023), conservative for a shrinking workforce |
| `gamma` (capital share) | 0.43 | Penn World Table labor share for Japan, 2013-2023 mean 0.568 (FRED `LABSHPJPA156NRUG`) |
| `debt_ratio_ss` (steady-state debt/GDP) | 2.0 | IMF WEO gross general government debt, 214.5% of GDP (2024), capped at OG-Core's maximum of 2.0 |
| `initial_debt_ratio` | 2.0 | same |
| `alpha_G` (government purchases/GDP) | 0.058 | steady-state residual, see below |
| `alpha_T` (non-pension transfers/GDP) | 0.09 | composition of IMF total expenditure (39.1% of GDP) |

## Debt beyond OG-Core's range

Japan's gross debt of 214.5 percent of GDP is above OG-Core's built-in maximum for the debt parameters (200 percent). The model therefore uses 2.0. Net debt (about 1.3 to 1.6 times GDP) would fit inside the range, but gross debt at the cap is closer to Japan's headline burden.

## Why `alpha_G` is not national-accounts government consumption

Japan's general government final consumption is about 20 percent of GDP, but that figure is the wrong value for `alpha_G`. OG-Core books public pensions and non-pension transfers (`alpha_T`) as separate outlays, so `alpha_G` is only the remaining government purchases. Much of Japan's measured government consumption is in-kind health and long-term care, which overlaps the social insurance already modeled.

The value that closes the government budget at the steady-state debt ratio, given model revenue of about 32 percent of GDP, is about 5.8 percent of GDP under the default calibration (6.2 percent under the earlier flat-tax calibration). That is exactly the `G/Y` the steady state produces as a residual. The transition has to run the same fiscal policy as the steady state it converges to: before OG-Core's debt-closure rule engages, the transition spends `G = alpha_G * Y` directly. With `alpha_G = 0.20` that is roughly four times what the budget can sustain, debt explodes, and the transition does not converge. Setting `alpha_G` to the steady-state residual fixed it.

## Recalibration for OG-Core 0.19 and later

OG-Core 0.19 changed `tau_payroll` to a time-by-income-group array, and with that change `alpha_T = 0.10` no longer cleared the steady state. The current values (`alpha_T = 0.09`, `alpha_G = 0.062`) solve, and the solution region is narrow: `alpha_T` of 0.05 and 0.07 to 0.09 solve, while 0 and 0.10 do not. All three policy experiments were rerun under this calibration. Their headline results moved by at most 0.1 point of GDP.
