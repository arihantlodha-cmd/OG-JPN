"""
Country constants for OG-Japan (OG-JPN).
"""

# UN M49 country code for Japan, used by ogcore.demographics to pull
# fertility, mortality, and population data from the UN World Population
# Prospects data portal (USA is "840"; Japan is "392").
UN_COUNTRY_CODE = "392"

COUNTRY_NAME = "Japan"
COUNTRY_ABBR = "JPN"
CURRENCY = "JPY"

# First model year of the baseline calibration.
START_YEAR = 2025

# Number of years of UN data the demographic path follows before rates are
# held constant. `ogcore.demographics.get_pop_objs` freezes fertility,
# mortality and immigration at their `final_data_year` values, so this decides
# how much of the UN projection the model actually sees.
#
# The family convention (and OG-JPN's first pass) is start_year + 1, a
# three-year window. For most countries that is harmless. For Japan it is not:
# it freezes mortality at 2026 levels, so the model never receives the UN's
# projected longevity gains for the world's longest-lived and fastest-ageing
# population -- the very mechanism the model exists to study.
#
# The cost was measurable. With the narrow window the implied steady-state
# population growth was -1.070%/yr, and the discontinuity where the data
# window ends produced a resource-constraint breach at t=2 that failed the
# transition solve outright.
#
# Widening to 20 years:
#   * g_n_ss becomes -0.698%/yr, within 0.02pp of the UN medium variant's own
#     2025-2100 implied average of -0.676%/yr -- an independent check that the
#     wider window is the faithful one, not merely the convenient one;
#   * mortality and immigration then vary over 21 periods rather than 2; and
#   * the discontinuity moves out of the early transition.
#
# Twenty years is also the horizon over which UN projections are most nearly
# data: the cohorts involved are already alive.
DEMOGRAPHIC_DATA_YEARS = 20
