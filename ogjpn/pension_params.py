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

# Replacement rate for a full-career average earner. OECD Pensions at a Glance
# 2023 reports 32.4% GROSS and 38.8% NET for Japan.
#
# CALIBRATED to 39.9%, above the OECD's 32.4%. Part derived, part fitted -- and
# the honest split matters, so it is written out here.
#
# An earlier version of this file justified the gap by claiming OG-Core has one
# pension tier while Japan has two. That reasoning was WRONG: the OECD country
# profile states plainly that its modelling covers the whole public system --
# "The public pension system has two tiers: a basic, flat-rate scheme and an
# earnings-related plan" -- so 32.4% already includes both.
#
# The actual reason the derived rate under-delivers:
#
#   DERIVED PART. The OECD's 32.4% is an OLD-AGE replacement rate for a
#   full-career average earner. Japan's 9.3%-of-GDP pension spending also covers
#   SURVIVORS' pensions (遺族年金) and DISABILITY pensions (障害年金), which
#   OG-Core's single defined-benefit block has no separate home for. Those are
#   roughly 15% of benefits, so the block must carry about
#       0.324 x 1.15 ~= 0.373
#   to reproduce total public pension outlays.
#
#   FITTED PART. The remainder was tuned in-model to land outlays on 9.3% of
#   GDP. It reflects differences between the model's old-age dependency ratio
#   and Japan's, and OG-Core's use of an average of the last
#   `avg_earn_num_years` of earnings rather than the OECD's lifetime basis.
#
#   The fitted rate is sensitive to the assumed productivity growth, because
#   OG-Core's DB benefit averages earnings over the last `avg_earn_num_years`
#   and faster growth lowers that average relative to contemporaneous wages.
#   At g_y = 0.56%/yr the rate fitted to 0.358; at the corrected per-hour
#   g_y = 1.04%/yr it fits to 0.416. Worth noting that the OECD's own pension
#   modelling assumes real earnings growth of 1.25%/yr, so the corrected g_y is
#   much closer to the assumption under which the 32.4% was produced than the
#   per-worker figure was.
#
# So: treat this as an EFFECTIVE system-wide replacement rate, not as an accrual
# rate you could read off Japanese pension law. It is NOT independently
# corroborated by the OECD's net replacement rate of 38.8% -- that figure is net
# of tax and is a different concept; its numerical closeness is a coincidence
# and was cited as corroboration in an earlier version of this file in error.
REPLACEMENT_RATE = 0.422
GROSS_REPLACEMENT_RATE_OECD = 0.324   # OLD-AGE, whole public system, full career
SURVIVORS_DISABILITY_UPLIFT = 1.15    # benefits OG-Core's DB block cannot separate

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
    #     alpha_db = 0.416 / 40 = 0.01040
    #
    # IMPORTANT: OG-Core's default alpha_db is 0.0. Switching pension_system to
    # "Defined Benefits" WITHOUT setting alpha_db silently produces zero
    # pensions.
    pension_parameters["alpha_db"] = REPLACEMENT_RATE / YEARS_CONTRIBUTION

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
