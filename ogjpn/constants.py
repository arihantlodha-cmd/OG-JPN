import os

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
# Set to the FULL UN horizon. UN WPP runs to 2100 and ogcore asserts on
# start+75, so 74 years (to 2099) is the whole of it.
#
# The family convention (and OG-JPN's first pass) is start_year + 1, a
# three-year window. For most countries that is harmless. For Japan it is not:
# it freezes mortality at 2026 levels, so the model never receives the UN's
# projected longevity gains for the world's longest-lived and fastest-ageing
# population -- the very mechanism the model exists to study. With the narrow
# window g_n_ss came out at -1.070%/yr.
#
# Why the FULL horizon rather than a shorter one: `g_n_ss` is a STEADY-STATE
# rate, and ogcore computes it from the vital rates prevailing at
# `final_data_year`. The right rates are therefore the UN's TERMINAL ones, not
# a mid-transition snapshot. An earlier version of this file used 20 years on
# the reasoning that the resulting -0.698%/yr matched the UN's 2025-2100
# implied average of -0.676% -- but that average is a transitional quantity and
# matching a steady-state parameter to it was a category error. The UN's
# terminal rates imply -0.463%/yr.
#
# Note this does NOT fix the transition. ogcore replaces the population
# distribution with its fixed steady-state one at `fixper = int(1.5 * S)` =
# period 120, a step change that is invariant to this window (the immigration
# jump there measures 0.50-0.56 at every setting tried, from start+20 to
# start+74) and that breaches the default RC_TPI tolerance. See
# docs/UPSTREAM_OGCORE.md item 1.
DEMOGRAPHIC_DATA_YEARS = 74

# Where the processed demographic arrays are cached between runs. ogcore
# refetches the entire UN series on every call and never reads its own
# `download_path` back, so without this each solve pays the full download --
# substantial at a 74-year window -- and repeated runs can trip UN rate limits.
# A failed fetch is especially unhelpful: ogcore silently falls back to the
# offline mirror, which has no Japan, and the run dies with `KeyError: '392'`.
DEMOGRAPHIC_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "demographic_cache"
)
