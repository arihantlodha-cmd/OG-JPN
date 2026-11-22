"""
Japan's public pension formula and the yen income anchor.

Japan's public pension has two tiers:

1. **Basic pension** (国民年金・老齢基礎年金), a flat amount for 40 years of
   contributions: 795,000 yen a year in FY2023 (Japan Pension Service, 令和5
   年度, new recipients aged 67 or under).
2. **Employees' pension** (厚生年金・報酬比例部分), proportional to earnings:
   annual benefit = average indexed standard remuneration x 5.481/1000 x
   months of coverage (the post-April-2003 rate, bonuses included). Over a
   40-year career that is 0.005481 x 40 = 21.9 percent of average earnings.

OG-Core's "US-Style Social Security" system computes a monthly benefit
(PIA) from average indexed monthly earnings (AIME) with three bracket rates
through the origin. Setting the second and third rates to 21.9 percent and
placing the first bend point where 90 percent of AIME equals the basic
pension plus 21.9 percent of AIME reproduces Japan's formula exactly above
the bend point:

    PIA = 0.9 b1 + 0.219 (AIME - b1) = basic + 0.219 AIME,  AIME >= b1,

with b1 = basic / (0.9 - 0.219). Below it, the minimum payment (the basic
pension) is a floor. Benefits are capped at the basic pension plus 21.9
percent of the contribution ceiling (standard monthly remuneration of
650,000 yen plus a 1.5 million yen bonus a year).

The formula is in yen, so it needs the model's income anchor in yen:
``mean_income_data`` is set to the mean salary of full-year private-sector
earners in 2023 (NTA 民間給与実態統計調査, 4.595 million yen), the same data
year and source as the income-tax calibration (ogjpn.income_tax).

Limits: the spouse's basic pension (第3号被保険者) and survivor benefits are
not modeled; AIME averages the best 35 years (OG-Core's
``avg_earn_num_years``) rather than all months of coverage; and the
macroeconomic slide (マクロ経済スライド) is a policy experiment
(docs results), not part of the baseline formula.
"""

# Mean annual salary of full-year private-sector earners, 2023 (yen):
# 233,264,921 million yen of salary over 50,761,385 earners.
MEAN_INCOME_JPY_2023 = 233_264_921e6 / 50_761_385

BASIC_PENSION_ANNUAL = 795_000  # FY2023, 40 years of contributions
EMPLOYEES_PENSION_RATE = 5.481 / 1000  # per month of coverage
YEARS_OF_COVERAGE = 40
EARNINGS_RATE = EMPLOYEES_PENSION_RATE * YEARS_OF_COVERAGE  # ~0.219
CEILING_MONTHLY = (650_000 * 12 + 1_500_000) / 12  # contribution ceiling
PIA_RATE_1 = 0.9  # OG-Core's first bracket rate, kept


def get_pension_params():
    """
    Return Japan's pension and income-anchor parameters for
    ``Specifications.update_specifications``.

    Returns:
        (dict): pension system parameters (yen, monthly) and
            ``mean_income_data`` (yen, annual)
    """
    basic_monthly = BASIC_PENSION_ANNUAL / 12
    bend = basic_monthly / (PIA_RATE_1 - EARNINGS_RATE)
    return {
        "mean_income_data": MEAN_INCOME_JPY_2023,
        "pension_system": "US-Style Social Security",
        "AIME_bkt_1": bend,
        "AIME_bkt_2": CEILING_MONTHLY,
        "PIA_rate_bkt_1": PIA_RATE_1,
        "PIA_rate_bkt_2": EARNINGS_RATE,
        "PIA_rate_bkt_3": EARNINGS_RATE,
        "PIA_minpayment": basic_monthly,
        "PIA_maxpayment": basic_monthly + EARNINGS_RATE * CEILING_MONTHLY,
    }


def japan_monthly_benefit(aime):
    """Japan's two-tier monthly benefit at average monthly earnings ``aime``
    (yen), capped at the contribution ceiling: the target the OG-Core
    parameters reproduce."""
    return BASIC_PENSION_ANNUAL / 12 + EARNINGS_RATE * min(aime, CEILING_MONTHLY)
