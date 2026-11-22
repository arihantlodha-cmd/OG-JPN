(Chap_Validation)=
# Validation against Japan

How well does the calibrated model match Japan? Figures are from the default calibration (progressive income tax, Japan's two-tier pension in yen) on OG-Core 0.24.6.

## Pension outlays: compare the first year, not the steady state

The steady state describes Japan's **terminal** stable population, which is far older than today's, so its pension bill is not comparable to Japan's current spending. The right comparison is the first year of the transition path, which starts from today's population.

| Public pension outlays / GDP | Model | Japan |
|---|---|---|
| First year of the transition (2025) | **0.102** | **0.104** (MHLW, FY2022 budget: 58.9 trillion yen) |
| 10 years on | 0.109 | |
| 20 years on | 0.122 | |
| Steady state | 0.121 | |

Fed Japan's demographics, its pension formula, and its tax data, the model reproduces Japan's pension bill within 0.2 points of GDP, and shows it rising by about two points over the next two decades as the population ages further.

## Steady-state ratios

| Ratio | Model | Japan | |
|---|---|---|---|
| Interest rate `r` | 0.046 | ~0.01-0.04 | top edge of range |
| Government debt / GDP | 2.00 | ~2.1 (gross) | matches (at OG-Core's cap) |
| Tax revenue / GDP (incl. social insurance) | 0.333 | 0.344 (OECD, 2022) | close |
| Personal income tax / GDP | 0.073 | ~0.064 (OECD, 2021) | somewhat high, see {ref}`Chap_Taxes` |
| Capital / GDP `K/Y` | 4.33 | ~5.4 (Penn World Table) | consistent with the source-matched benchmark |
| Household wealth / GDP | 5.47 | 3.69 (national accounts, excl. land) | high |
| Consumption / GDP `C/Y` | 0.73 | ~0.53-0.55 | high |
| Private investment / GDP `I/Y` | 0.17 | ~0.25 total gross fixed capital formation, incl. public | low (concepts differ) |

The right benchmark for tax revenue is the OECD tax-to-GDP ratio (34.4 percent in 2022, including social security contributions). The IMF's 37.6 percent of GDP is total general government revenue, which also includes non-tax revenue such as property income, so it overstates the gap a tax-only model should close.

## What matches

The fiscal and demographic side matches Japan: the pension bill, the debt ratio, the tax take, and the interest rate. None of these was targeted; they follow from Japan's population, pension formula, tax schedule, and debt.

## The capital-output ratio is not a free parameter

In the steady state, `K/Y = gamma / (r + delta)` exactly, from the firm's first-order condition. A low return and a high capital share together force a high `K/Y`, and both are real inputs here: `r` is in Japan's range and `gamma = 0.43` is the Penn World Table capital share. The ~3.0-3.5 figure often quoted for Japan uses a narrow net-capital concept. Measured from the same source as `gamma` (Penn World Table capital stock over real GDP, FRED `RKNANPJPA666NRUG` and `RGDPNAJPA666NRUG`), Japan's ratio is about 5.4, so the model's 4.33 is not too high. `K/Y` should not be tuned down.

## Consumption runs high because government purchases are squeezed

`G` is the residual that closes the government budget, so when revenue falls short, `G` is squeezed and output the government would buy shows up as household consumption instead. Adding Japan's full social insurance lifted revenue from 25.9 to 32.2 percent of GDP and brought `C/Y` down from 0.79, and the progressive income tax lifted it to 33.3 percent and `C/Y` to 0.73. The remaining gap has a ceiling the model cannot remove: Japan's government spends about 39.1 percent of GDP and collects 37.6 percent, funding the difference by borrowing. A steady state with a fixed debt ratio must balance, so it cannot reproduce a government that permanently spends more than it collects. One measurable consequence of the high consumption share: in the model each point of consumption tax raises about 3.9 trillion yen (at FY2023 GDP), against about 3.0 trillion in Japan (FY2024 budget, 30.2 trillion yen at 10 percent), so consumption-tax revenue is overstated by roughly the same third.

## Household wealth

Household wealth is 5.47 times GDP in the model against 3.69 in the national accounts (excluding land). In the model, household wealth is the domestic capital stock plus the domestically held share of government debt, so the high `K/Y`, combined with Japan's debt, carries through. Whether the remaining gap reflects the treatment of foreign assets or of pension wealth is an open question.

## The debt path along the transition

Debt does not stay at its target along the transition. Government purchases are fixed at `alpha_G` times GDP for the first 20 years (OG-Core's `tG1`), and because today's pension bill (10.2 percent of GDP) is below its long-run level (12.1 percent), the government runs surpluses and debt falls from 2.0 to about 1.6 times GDP by year 20. OG-Core's debt-closure rule then adjusts purchases to bring debt back to target: purchases jump to about 11.5 percent of GDP in year 20 and settle back to 6.5 percent as debt returns to 2.0 by around year 40. The jump is a feature of the closure rule, not of Japan. It affects baseline and reform alike, so it largely differences out of reform comparisons, but year-20 levels of `G` should not be read literally.
