"""
OG-Japan pension calibration.

This module exists because the pension system is the whole point of an
overlapping-generations model of Japan, and it was previously the block running
furthest from Japanese reality.

Without these settings OG-Core defaults to ``pension_system = "US-Style Social
Security"``, which applies the United States benefit formula -- AIME bend points
of $749 and $4,517, PIA replacement rates of 90/32/15 percent, a maximum payment
of $3,501 a month -- to earnings scaled by ``mean_income_data``, which also
defaults to a US figure ($58,644.92). Japanese demographics were being run
through an American pension system priced in dollars.

Japan's public pension is a two-tier arrangement:

  * the Basic Pension (国民年金 / 基礎年金), a flat benefit earned by years of
    contribution; and
  * Employees' Pension Insurance (厚生年金), an earnings-related tier accruing at
    5.481/1000 of revalued monthly remuneration per month of contribution.

Both are earnings-history-based defined benefits, so OG-Core's ``"Defined
Benefits"`` system is the structurally correct representation. OG-Core computes

    pension = (average earnings over ``avg_earn_num_years``)
              x ``yr_contrib`` x ``alpha_db``

(``ogcore/pensions.py:DB_amount``), so ``yr_contrib * alpha_db`` IS the gross
replacement rate, which makes the parameter directly observable.

Sources
-------
OECD  *Pensions at a Glance 2023*, Japan country profile: gross replacement rate
      for an average earner at age 65 = 32.4%; public pension expenditure =
      9.3% of GDP (2022).
NTA   National Tax Agency, Survey on Private-Sector Wages 2023: average annual
      wage for employees working the full year = 4.60 million yen.
"""

# Gross replacement rate for a full-career average earner, OECD Pensions at a
# Glance 2023. This is the quantity alpha_db is derived from, kept as a named
# constant so the derivation below can be checked.
GROSS_REPLACEMENT_RATE = 0.324

# Full contribution period. Japan's Basic Pension requires 40 years for the
# full flat benefit, and 40 years is the standard career used in the OECD
# replacement-rate calculation, so the two are consistent.
YEARS_CONTRIBUTION = 40

# Japan's Employees' Pension Insurance revalues and averages earnings over the
# ENTIRE career, not a final-salary window. OG-Core's default of 35 is a US
# convention; 40 matches Japan and matches YEARS_CONTRIBUTION.
AVG_EARNINGS_YEARS = 40

# Pensionable age for both tiers. The Employees' Pension supplementary portion
# finished phasing up from 60 to 65 in 2025.
RETIREMENT_AGE = 65

# National Tax Agency Survey on Private-Sector Wages, 2023 (yen). Used by
# OG-Core to solve `factor`, which converts model units into currency so the
# tax functions and the pension formula are evaluated at Japanese income levels.
MEAN_INCOME_YEN = 4600000.0


def get_pension_params():
    """
    Return Japan pension parameters for
    ``Specifications.update_specifications``.

    Returns:
        pension_parameters (dict): Japan pension parameters
    """
    pension_parameters = {}

    # Structural choice: an earnings-related defined-benefit system.
    pension_parameters["pension_system"] = "Defined Benefits"

    # Accrual rate per year of contribution. Because OG-Core's DB benefit is
    # (average earnings) x yr_contrib x alpha_db, the product
    # yr_contrib * alpha_db is the replacement rate:
    #
    #     alpha_db = 0.324 / 40 = 0.0081
    #
    # IMPORTANT: OG-Core's default alpha_db is 0.0. Switching pension_system to
    # "Defined Benefits" WITHOUT setting alpha_db silently produces zero
    # pensions.
    pension_parameters["alpha_db"] = GROSS_REPLACEMENT_RATE / YEARS_CONTRIBUTION

    pension_parameters["yr_contrib"] = YEARS_CONTRIBUTION
    pension_parameters["avg_earn_num_years"] = AVG_EARNINGS_YEARS
    pension_parameters["retirement_age"] = [RETIREMENT_AGE]

    # Currency anchor for `factor`. Without this the model scales Japanese
    # incomes to US dollars, which mis-prices every tax function as well as the
    # pension.
    pension_parameters["mean_income_data"] = MEAN_INCOME_YEN

    return pension_parameters


# Validation target, not a model input: what the calibrated system should
# produce. Japan's public pension expenditure is 9.3% of GDP (OECD Pensions at
# a Glance 2023, 2022 data) -- NOT the 11-12% the repository previously claimed
# as a validated result.
PENSION_EXPENDITURE_TARGET_SHARE_OF_GDP = 0.093
