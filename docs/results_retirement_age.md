# Long-run (steady-state) effect of raising Japan's pension age

Real Japan demographics (UN, code 392); percent change in the steady-state aggregate vs the age-65 baseline. Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md), so read the signs and rough magnitudes, not the last digit. Baseline pension outlays are 11.4% of GDP.

| Reform | Y (%) | C (%) | K (%) | L (%) | Pension outlays/GDP |
|---|---|---|---|---|---|
| 65 -> 68 | -0.04 | -1.04 | -0.86 | +0.58 | 0.114 -> 0.104 |
| 65 -> 70 | -0.01 | -1.84 | -1.37 | +1.03 | 0.114 -> 0.095 |

## What this shows

Raising the age at which households can claim the public pension does what the fiscal debate expects, on Japan's real age structure. People work longer, so labor rises (and by more at the higher age); the pension bill falls directly, from about eleven and a half percent of GDP to under ten, because each cohort collects for fewer years. Capital edges down rather than up: with a shorter retirement to fund, households need less lifecycle wealth, so the saving they do over a working life buys a smaller capital stock. More labor and less capital roughly offset, leaving output close to flat, so the reform reads mainly as moving the adjustment onto the spending side of the budget rather than as a growth lever. The clean result is the pension line: moving the age to 70 takes almost two points of GDP off the public pension burden in the long run.

The magnitudes are indicative, not final. This is a comparison of two steady states, robust to the level miss in C/Y (see docs/METHODOLOGY.md) because both sides carry the same calibration, but the tax and pension calibration is still first-pass, so the honest reading is the direction and rough size, not the last digit. The transition-path version, with the year-by-year phase-in, is the natural next step.
