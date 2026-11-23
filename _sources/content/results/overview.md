(Chap_Results)=
# Policy results

Three fiscal reforms that Japan is actually debating, each solved on Japan's demographics as a long-run steady-state comparison and on the transition path.

| Reform | Long-run effect |
|---|---|
| {ref}`Consumption tax 10 to 12 and 15 percent <Chap_ConsTax>` | tax revenue up 1.3 and 3.2 points of GDP; consumption down, labor slightly up |
| {ref}`Pension age 65 to 68 and 70 <Chap_RetAge>` | long-run pension outlays from 12.0 to 10.8 and 9.9 percent of GDP; labor up |
| {ref}`Replacement-rate cut of 10 and 20 percent <Chap_ReplRate>` | long-run pension outlays from 12.0 to 10.8 and 9.6 percent of GDP; labor up |

```{figure} ../../../policy_results.png
:name: FigPolicyResults
:width: 95%

Long-run effects of the three reforms.
```

## What the transition adds

Each reform improves the government budget, and for the first 20 years OG-Core holds government purchases at a fixed share of GDP, so the gain goes to **paying down debt**. Lower debt frees household saving for private capital, so capital rises along the transition (by about 9 percent at year 20 under the 15 percent consumption tax) even where households themselves save less. After year 20 OG-Core's debt-closure rule brings debt back to its target and capital returns toward its new steady state, which for all three reforms is close to or slightly below the baseline. The capital gain on the path is therefore mainly a consequence of using the proceeds to reduce debt, which is how OG-Core closes the budget, not a change in household saving. Each result page measures this channel from the solved paths.

The steady-state comparison cannot show any of this, and it cannot give the year-by-year pension and revenue paths or their present values, which are what a finance ministry would weigh. The transition pages report those present values as a share of first-year GDP and in trillion yen at Japan's FY2023 GDP.

## How to read the numbers

Read results for their direction and rough size rather than their last digit. Reform-minus-baseline comparisons are robust to the model's level misses in `C/Y` and household wealth, because the baseline and the reform carry the same calibration. The single-period resource-constraint errors at t = 2 and t = 120 (both from OG-Core's population path, see {ref}`Chap_Demog`) are common to baseline and reform and cancel in the differences.

All results use the default calibration (progressive labor income tax, effective capital income tax, Japan's two-tier pension in yen), and the transitions start from Japan's observed initial wealth distribution ({ref}`Chap_Wealth`).

### Household solver errors in a few cohorts

Checking the household first-order conditions along each solved transition (not only the aggregate resource constraint) finds that in some runs a few cohorts have large Euler-equation errors. In the current set, six of the nine transitions are clean (errors below 1e-11); the 12 percent consumption tax and both replacement-rate cuts have bad cohorts entering between years 6 and 12. The cause is in OG-Core: when its sparse-Jacobian household solve stops without converging, it does not fall back to dense finite differences, and the remaining retry can also stop short, with no warning. With the fix proposed upstream ([OG-Core #1294](https://github.com/PSLmodels/OG-Core/pull/1294)), re-solving the 20 percent replacement-rate cut removes the errors (below 1e-11) and changes its aggregates by at most 0.06 percent (labor and the interest rate, around year 13), and its year-20 effects on output, capital, labor, pension outlays, revenue, and debt not at all at two decimals. The reform effects reported here are 0.3 to 9 percent, so the results stand. The transitions will be rerun once the fix is released.
