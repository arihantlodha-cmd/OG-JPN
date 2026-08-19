# Long-run (steady-state) effect of raising Japan's consumption tax

Real Japan demographics (UN, code 392); percent change in the steady-state aggregate vs the 10% baseline. Macro/tax parameters are first-pass (see docs/NEXT_STEPS.md), so read the signs and rough magnitudes, not the last digit. Baseline pension outlays are 11.3% of GDP.

| Reform | Y (%) | C (%) | K (%) | L (%) | Revenue/GDP |
|---|---|---|---|---|---|
| 10% -> 12% | +0.04 | -1.66 | -0.26 | +0.27 | 0.259 -> 0.274 |
| 10% -> 15% | +0.10 | -4.05 | -0.65 | +0.66 | 0.259 -> 0.294 |

## What this shows

The pattern is the standard consumption-tax result, and it holds on Japan's real age structure. Taxing consumption raises its effective price, so households consume less (C falls, and by more at the higher rate) and work a little more (L rises), leaving output essentially flat with a small positive tilt. Capital moves only slightly, and its sign depends on how the extra revenue is recycled under the calibration's fixed spending shares, so it is best read as roughly unchanged rather than as a clean saving effect. The revenue line is the point for Japan: each two-point increase raises revenue by about 1.5 points of GDP, a real lever against a fiscal gap where pension outlays alone are already 11.3% of GDP.

The magnitudes are indicative, not final. This is a comparison of two steady states, which is robust to the level miss in C/Y (see docs/METHODOLOGY.md; K/Y is roughly consistent with the Penn World Table benchmark) because both sides carry the same calibration, but the tax side is still first-pass, so the honest reading is the direction and rough size, not the last digit.
