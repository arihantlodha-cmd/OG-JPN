"""
Japan's progressive personal income tax, for OG-Core's ``DEP_totalinc``
tax functions.

Effective rates come from administrative data, not a tax simulator. The
National Tax Agency's 2023 salary survey (民間給与実態統計調査, see
scripts/fetch_nta_tax_data.py) reports, for each salary bracket, the number
of earners, total salary, number of taxpayers, and national income tax
withheld. From these:

* **National income tax** per bracket is the tax withheld (it includes the
  2.1% reconstruction surtax).
* **Resident tax** (住民税, 10% of taxable income plus a flat per-capita
  levy) is not withheld by employers, so it is built from taxable income.
  Taxable income per taxpayer is recovered by inverting the national
  bracket schedule on tax withheld per taxpayer; resident taxable income is
  higher by the 50,000 yen gap between the national (480,000) and resident
  (430,000) basic deductions.
* **Effective rate** = (national + resident tax) / salary, over all earners
  in the bracket, taxpayers or not.

Marginal rates on labor income are statutory, evaluated at each bracket's
mean salary: (national bracket rate x 1.021 + 10% resident) x (1 - slope of
the employment income deduction - employee social insurance rate), scaled
by the share of the bracket that pays tax.

Both are fitted with OG-Core's ``DEP_totalinc`` form,

    rate(I) = (max - min) * (A I^2 + B I) / (A I^2 + B I + 1) + min,

on income expressed relative to mean salary, then rescaled to the model's
income anchor (``mean_income_data``), so the progressivity relative to the
mean is right whatever currency the anchor is in.

Labor and capital income are taxed separately in Japan: salaries on the
progressive schedule, most financial income at a flat rate. OG-Core's
``DEP_totalinc`` form takes total income I, but its parameters can vary by
age. At age s with labor share of income lambda_s, the separable tax
lambda tau_L(lambda I) + (1 - lambda) tau_k is again a DEP_totalinc curve
(``age_specific_params``), so each age gets its own curve. The labor shares
come from the model's own steady state (``labor_share_by_age``, iterated to
a fixed point by scripts/calibrate_labor_share.py and stored in
data/labor_share_by_age.csv).

The capital rate tau_k is an effective rate, not the 20.315% statute:
Japan taxes interest, dividends, and investment-trust income at 20.315%,
but leaves untaxed the return on owner-occupied housing and the investment
income of insurance and pension reserves, which together are most of
household capital income (``effective_capital_tax_rate``).

Limits: the survey covers private-sector salary earners only; deductions
other than the basic deduction are averaged into the inversion; the labor
share is an average over lifetime-income groups at each age; realized
capital gains, rental income (taxed progressively), and NISA exemptions are
left out of the capital rate.
"""

from importlib import resources

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

# National income tax schedule (所得税, 2015 onward): upper bound of taxable
# income, rate, and the quick-calculation deduction (控除額), in yen.
NATIONAL_SCHEDULE = [
    (1_950_000, 0.05, 0),
    (3_300_000, 0.10, 97_500),
    (6_950_000, 0.20, 427_500),
    (9_000_000, 0.23, 636_000),
    (18_000_000, 0.33, 1_536_000),
    (40_000_000, 0.40, 2_796_000),
    (np.inf, 0.45, 4_796_000),
]
SURTAX = 1.021  # special income tax for reconstruction (復興特別所得税)
RESIDENT_RATE = 0.10  # 住民税 所得割 (prefectural 4% + municipal 6%)
RESIDENT_BASIC_GAP = 50_000  # 480,000 national vs 430,000 resident basic deduction
RESIDENT_PER_CAPITA = 5_000  # 均等割, approximate
# Employee social insurance on salary, and the pension contribution cap.
SI_EMPLOYEE = 0.15  # pension 9.15% + health ~5% + care/employment ~0.9%
PENSION_EMPLOYEE = 0.0915
PENSION_CAP_SALARY = 650_000 * 12 + 1_500_000  # top standard monthly pay + bonus cap


# Statutory flat rate on interest, dividends, and listed capital gains
# (15% national + 5% local + 0.315% reconstruction surtax).
CAPITAL_TAX_STATUTORY = 0.20315

# Household (incl. unincorporated enterprises) primary income, FY2023,
# trillion yen (Cabinet Office, 2023年度国民経済計算, 制度部門別所得支出勘定
# 家計, table 1: 第1次所得の配分勘定).
SNA_FY2023_HH_PROPERTY_INCOME = 30.5  # 財産所得（受取）
SNA_FY2023_HH_OWNER_OCCUPIED_SURPLUS = 18.0  # 営業余剰（持ち家）（純）
# The parts taxed at the flat rate: interest actually received (before the
# FISIM adjustment), dividends, and investment-trust income.
SNA_FY2023_HH_INTEREST_PRE_FISIM = 3.6
SNA_FY2023_HH_DIVIDENDS = 9.5
SNA_FY2023_HH_INVESTMENT_TRUST = 0.6


def effective_capital_tax_rate():
    """
    Income tax collected per yen of household capital income in Japan.

    The statutory 20.315% applies to interest, dividends, and investment
    trust income; household capital income also includes the return on
    owner-occupied housing and on insurance and pension reserves, which are
    not taxed as they accrue. FY2023 national accounts give about 5.7%.

    Returns:
        (float): effective average tax rate on household capital income
    """
    taxed = (
        SNA_FY2023_HH_INTEREST_PRE_FISIM
        + SNA_FY2023_HH_DIVIDENDS
        + SNA_FY2023_HH_INVESTMENT_TRUST
    )
    total = SNA_FY2023_HH_PROPERTY_INCOME + SNA_FY2023_HH_OWNER_OCCUPIED_SURPLUS
    return CAPITAL_TAX_STATUTORY * taxed / total


def load_labor_share_by_age():
    """
    Steady-state labor share of household income by model age, stored by
    scripts/calibrate_labor_share.py.

    Returns:
        (Numpy array): labor share at each of the S model ages
    """
    path = resources.files("ogjpn").joinpath("data/labor_share_by_age.csv")
    with path.open() as f:
        return pd.read_csv(f).labor_share.to_numpy()


def labor_share_by_age(ss, p):
    """
    Labor share of household income (labor + capital) at each age, averaged
    over lifetime-income groups with population weights.

    Args:
        ss (dict): OG-Core SS_vars
        p (OG-Core Specifications object): model parameters

    Returns:
        (Numpy array): labor share at each of the S ages
    """
    labor = np.asarray(ss["labor_income"])
    capital = np.asarray(ss["capital_income"])
    weights = np.asarray(p.omega_SS).reshape(labor.shape[0], -1)
    if weights.shape[1] != labor.shape[1]:
        weights = weights * np.asarray(p.lambdas).reshape(1, -1)
    return (weights * labor).sum(1) / (weights * (labor + capital)).sum(1)


def age_specific_params(etr, mtrx, labor_share, tau_k, mean_income):
    """
    DEP_totalinc parameters by age for a separable labor/capital tax.

    With labor share lambda at an age, labor income is lambda I, so the tax
    on labor is lambda I tau_L(lambda I) and on capital (1 - lambda) I
    tau_k. Dividing by I, the effective rate is lambda tau_L(lambda I) +
    (1 - lambda) tau_k: a DEP_totalinc curve with A and B scaled by lambda^2
    and lambda, and the top and bottom rates by lambda plus the constant
    capital term. The marginal rate on labor is the labor schedule at
    lambda I (A and B scaled, rates unchanged); the marginal rate on capital
    is tau_k.

    Args:
        etr (array_like): A, B, max, min of the labor effective rate on
            income relative to mean salary (fit_dep_totalinc)
        mtrx (array_like): same for the labor marginal rate
        labor_share (array_like): labor share of income at each age
        tau_k (float): flat tax rate on capital income
        mean_income (float): model income at the mean salary

    Returns:
        (tuple): etr, mtrx, mtry parameters, each a list of S lists of six
            OG-Core DEP_totalinc coefficients
    """
    out_etr, out_mtrx, out_mtry = [], [], []
    for lam in np.clip(np.asarray(labor_share, float), 0.0, 1.0):
        A, B, mx, mn = etr
        c = (1 - lam) * tau_k
        out_etr.append(
            to_model_units(
                [A * lam**2, B * lam, lam * mx + c, lam * mn + c], mean_income
            )
        )
        A, B, mx, mn = mtrx
        out_mtrx.append(to_model_units([A * lam**2, B * lam, mx, mn], mean_income))
        out_mtry.append(to_model_units([0.0, 0.0, tau_k, tau_k], mean_income))
    return out_etr, out_mtrx, out_mtry


def load_nta_2023():
    """
    Salary-bracket data from the NTA 2023 salary survey.

    Returns:
        (pandas DataFrame): one row per salary bracket with earners,
            taxpayers, total salary, and income tax withheld (yen)
    """
    path = resources.files("ogjpn").joinpath("data/nta_2023_salary_tax.csv")
    with path.open() as f:
        return pd.read_csv(f)


def _invert_national(tax_base):
    """Taxable income that produces ``tax_base`` under the national schedule."""
    for upper, rate, deduction in NATIONAL_SCHEDULE:
        taxable = (tax_base + deduction) / rate
        if taxable <= upper:
            return taxable
    raise ValueError("tax out of range")


def _national_rate(taxable):
    for upper, rate, _ in NATIONAL_SCHEDULE:
        if taxable <= upper:
            return rate
    return NATIONAL_SCHEDULE[-1][1]


def _employment_deduction_slope(salary):
    """Slope of the employment income deduction (給与所得控除, 2020 onward)."""
    for upper, slope in [
        (1_625_000, 0.0),
        (1_800_000, 0.4),
        (3_600_000, 0.3),
        (6_600_000, 0.2),
        (8_500_000, 0.1),
    ]:
        if salary <= upper:
            return slope
    return 0.0


def bracket_rates(df=None):
    """
    Effective and marginal income tax rates by salary bracket.

    Args:
        df (pandas DataFrame): bracket data; defaults to load_nta_2023()

    Returns:
        (pandas DataFrame): mean salary, income relative to the mean
            (``x``), taxable income per taxpayer, effective rate (national
            + resident), and statutory marginal rate on labor income, with
            earners and total salary as weights
    """
    df = load_nta_2023() if df is None else df
    earners = df.earners.to_numpy()
    taxpayers = df.taxpayers.to_numpy()
    salary = df.salary_total_yen.to_numpy()
    tax = df.income_tax_withheld_yen.to_numpy()

    mean_salary = salary / earners
    mean_all = salary.sum() / earners.sum()
    taxable = np.array(
        [_invert_national(t / n / SURTAX) for t, n in zip(tax, taxpayers)]
    )
    resident = taxpayers * (
        RESIDENT_RATE * (taxable + RESIDENT_BASIC_GAP) + RESIDENT_PER_CAPITA
    )
    etr = (tax + resident) / salary

    si = np.where(
        mean_salary <= PENSION_CAP_SALARY,
        SI_EMPLOYEE,
        SI_EMPLOYEE - PENSION_EMPLOYEE,
    )
    slope = np.array([_employment_deduction_slope(s) for s in mean_salary])
    nat = np.array([_national_rate(a) for a in taxable])
    mtr = (nat * SURTAX + RESIDENT_RATE) * (1 - slope - si) * taxpayers / earners

    return pd.DataFrame(
        {
            "mean_salary_yen": mean_salary,
            "x": mean_salary / mean_all,
            "taxable_yen": taxable,
            "etr": etr,
            "mtr_labor": mtr,
            "earners": earners,
            "salary_total_yen": salary,
        }
    )


def dep_totalinc(params, income):
    """OG-Core's DEP_totalinc rate at ``income`` (shift terms zero)."""
    A, B, max_rate, min_rate = params
    q = A * income**2 + B * income
    return (max_rate - min_rate) * q / (q + 1) + min_rate


def fit_dep_totalinc(x, rate, weights, max_cap=0.56):
    """
    Weighted least-squares fit of DEP_totalinc to rates on relative income.

    Args:
        x (array_like): income relative to mean salary
        rate (array_like): tax rates to fit
        weights (array_like): observation weights
        max_cap (float): upper bound on the top rate (Japan's top combined
            statutory rate is 45% x 1.021 + 10% = 55.9%)

    Returns:
        (Numpy array): A, B, max_rate, min_rate on relative income
    """
    x, rate = np.asarray(x, float), np.asarray(rate, float)
    w = np.sqrt(np.asarray(weights, float) / np.sum(weights))
    fit = least_squares(
        lambda p: (dep_totalinc(p, x) - rate) * w,
        x0=[0.05, 0.05, 0.4, 0.0],
        bounds=([0.0, 0.0, 0.0, 0.0], [np.inf, np.inf, max_cap, 0.2]),
    )
    return fit.x


def to_model_units(params, mean_income):
    """
    Rescale DEP_totalinc parameters from relative income to the model's
    income units, where mean income equals ``mean_income``, and append
    OG-Core's two shift terms (zero).
    """
    A, B, max_rate, min_rate = params
    return [
        float(A) / mean_income**2,
        float(B) / mean_income,
        float(max_rate),
        float(min_rate),
        0.0,
        0.0,
    ]
