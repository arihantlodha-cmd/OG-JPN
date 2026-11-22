(Chap_Validation)=
# Validation against Japan

How well does the calibrated steady state match Japan? Figures are from the current calibration on OG-Core 0.24.6 (`python examples/run_ogjpn_ss.py`).

| Ratio | Model | Japan | |
|---|---|---|---|
| Interest rate `r` | 0.045 | ~0.01-0.04 | top edge of range |
| Public pension outlays / GDP | 0.115 | ~0.10-0.11 | matches |
| Government debt / GDP | 2.00 | ~2.1 (gross) | matches (at OG-Core's cap) |
| Tax revenue / GDP (incl. social insurance) | 0.322 | 0.376 (IMF) | short by the property and other-tax gap |
| Capital / GDP `K/Y` | 4.37 | ~5.4 (Penn World Table) | consistent with the source-matched benchmark |
| Household wealth / GDP | 5.53 | 3.69 (national accounts, excl. land) | high |
| Consumption / GDP `C/Y` | 0.73 | ~0.53-0.55 | high |
| Private investment / GDP `I/Y` | 0.17 | ~0.25 total gross fixed capital formation, incl. public | low (concepts differ) |

## What matches

The fiscal and demographic side matches Japan: the pension burden, the debt ratio, and the interest rate. The closest match is the one the model was never told. Fed Japan's age structure, it reproduces a public pension burden of about 11.5 percent of GDP.

## The capital-output ratio is not a free parameter

In the steady state, `K/Y = gamma / (r + delta)` exactly, from the firm's first-order condition. A low return and a high capital share together force a high `K/Y`, and both are real inputs here: `r` is in Japan's range and `gamma = 0.43` is the Penn World Table capital share. The ~3.0-3.5 figure often quoted for Japan uses a narrow net-capital concept. Measured from the same source as `gamma` (Penn World Table capital stock over real GDP, FRED `RKNANPJPA666NRUG` and `RGDPNAJPA666NRUG`), Japan's ratio is about 5.4, so the model's 4.37 is not too high. `K/Y` should not be tuned down.

## Consumption runs high because government purchases are squeezed

`G` is the residual that closes the government budget, so when revenue falls short, `G` is squeezed and output the government would buy shows up as household consumption instead. Adding Japan's full social insurance lifted revenue from 25.9 to 32.2 percent of GDP and brought `C/Y` down from 0.79. The remaining gap has a ceiling the model cannot remove: Japan's government spends about 39.1 percent of GDP and collects 37.6 percent, funding the difference by borrowing. A steady state with a fixed debt ratio must balance, so it cannot reproduce a government that permanently spends more than it collects.

## Household wealth

Household wealth is 5.53 times GDP in the model against 3.69 in the national accounts (excluding land). In the model, household wealth is the domestic capital stock plus the domestically held share of government debt, so the high `K/Y`, combined with Japan's debt, carries through. Whether the remaining gap reflects the treatment of foreign assets or of pension wealth is an open question.
