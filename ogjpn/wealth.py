"""
Japan's observed initial distribution of household wealth, for the start
of the transition path.

By default OG-Core starts a baseline transition from the terminal steady
state's wealth-by-age profile, rescaled to the initial population. For
Japan that proxy is poor: today's population is far older than the
terminal stable population, so the steady-state profile puts wealth in the
wrong cohorts, and the mismatch showed up as a one-period seam in the
resource constraint at t=2 (see docs/NEXT_STEPS.md, item 4).

OG-Core (PR #1254) lets a country model supply ``initial_hhwealth_dist``,
an S x J matrix of shares of aggregate household wealth. This module builds
it from Japanese survey data:

* **Age profile (data).** Mean household net worth (家計資産総額, which is
  the 純資産総額 of the statistical tables: net financial assets plus
  housing and residential land) by age of household head, all households,
  from the 2019 National Survey of Family Income, Consumption and Wealth
  (2019年全国家計構造調査), Statistics Bureau of Japan, 結果の概要
  (2021-05-18), Figure IV-4.
* **Within-age split across lifetime-income groups (model).** The survey
  summary does not cross age with lifetime income, so the split across the
  J groups at each age is taken from the model's own steady state. Only
  the age profile is replaced by data.

Known limits, stated rather than hidden:

* The survey reports wealth per household by the age of the head; the
  model is per person. Assigning household wealth to the head's age
  overstates wealth at young ages slightly (adult children living with
  their parents hold little but are counted at their own age in the
  model) and is the standard first-pass mapping.
* The survey uses age bands (under 30, 30s, ..., 80 and over). The profile
  is interpolated linearly between band midpoints and held flat beyond the
  first and last midpoints.
* Only the shape is taken from the data. The level of aggregate wealth is
  still the steady-state level unless ``initial_wealth_ratio`` is also set.
"""

import numpy as np

# Age-band midpoints and mean household net worth (thousand yen) by age of
# household head, 2019 全国家計構造調査, 総世帯, 図Ⅳ－４. The all-ages mean
# is 32,194 thousand yen.
NSFIE_2019_AGE_MIDPOINTS = np.array([25.0, 35.0, 45.0, 55.0, 65.0, 75.0, 85.0])
NSFIE_2019_NET_WORTH = np.array(
    [2568.0, 8701.0, 19035.0, 29067.0, 40351.0, 40903.0, 43860.0]
)
NSFIE_2019_ALL_AGES_MEAN = 32194.0

# Level of household wealth relative to GDP, for OG-Core's optional
# initial_wealth_ratio. Household (incl. unincorporated enterprises) balance
# sheet, end of 2023, from the Cabinet Office 2023年度国民経済計算年次推計
# (ストック編) ポイント, table 5, in trillion yen; nominal GDP is FY2023 from
# the same release's flow summary. The model has no land, so the comparable
# ratio excludes 土地・漁場.
SNA_2023_HH_NET_WORTH = 2965.1
SNA_2023_HH_LAND = 767.1
SNA_FY2023_NOMINAL_GDP = 595.2
HH_WEALTH_TO_GDP_INCL_LAND = SNA_2023_HH_NET_WORTH / SNA_FY2023_NOMINAL_GDP
HH_WEALTH_TO_GDP_EXCL_LAND = (
    SNA_2023_HH_NET_WORTH - SNA_2023_HH_LAND
) / SNA_FY2023_NOMINAL_GDP


def net_worth_by_age(ages):
    """
    Mean household net worth (thousand yen) at each age, interpolated from
    the 2019 survey's age bands.

    Args:
        ages (array_like): ages in years

    Returns:
        (Numpy array): net worth at each age, same shape as ``ages``
    """
    return np.interp(
        np.asarray(ages, dtype=float),
        NSFIE_2019_AGE_MIDPOINTS,
        NSFIE_2019_NET_WORTH,
    )


def get_initial_hhwealth_dist(p, b_sp1_ss):
    """
    Build OG-Core's ``initial_hhwealth_dist`` for Japan.

    Args:
        p (ogcore Specifications): model parameters with Japan demographics
            already applied (supplies E, S, J, lambdas, and omega)
        b_sp1_ss (Numpy array): S x J steady-state savings ``b_sp1``, used
            only for the within-age split across lifetime-income groups

    Returns:
        (Numpy array): S x J shares of aggregate household wealth, summing
            to one
    """
    b_sp1_ss = np.asarray(b_sp1_ss, dtype=float)
    lambdas = np.asarray(p.lambdas, dtype=float).ravel()
    if b_sp1_ss.shape != (p.S, p.J):
        raise ValueError(f"b_sp1_ss must be ({p.S}, {p.J}); got {b_sp1_ss.shape}")

    # b_sp1[s] is saved at model age index s and held at index s + 1, and
    # model index s is age E + s + 1, so row s is wealth held at age
    # E + s + 2.
    ages_held = p.E + np.arange(p.S) + 2
    per_person = net_worth_by_age(ages_held)

    # Within-age shape across j from the steady state, normalized so its
    # lambda-weighted mean at each age is one (the data then sets the
    # age-average). Rows where the steady state holds ~no wealth fall back
    # to an even split.
    b_pos = np.clip(b_sp1_ss, 0.0, None)
    row_mean = b_pos @ lambdas
    shape = np.ones_like(b_pos)
    ok = row_mean > 1e-12
    shape[ok] = b_pos[ok] / row_mean[ok, None]

    # Share of aggregate wealth = population share (omega, already joint
    # over age and income group) x wealth per person.
    omega0 = np.asarray(p.omega[0], dtype=float).reshape(p.S, p.J)
    dist = omega0 * per_person[:, None] * shape
    return dist / dist.sum()
