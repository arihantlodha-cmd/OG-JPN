"""
OG-Japan tax calibration.

This is a first-pass calibration of Japan's income, payroll, capital, and
consumption taxes, grounded in published rates rather than a tax
microsimulator (Japan has no open-source equivalent of the US
Tax-Calculator). It uses OG-Core's linear (constant-rate) tax functions,
which the model supports directly, so each rate is a single, sourced
number rather than a fitted polynomial that would imply precision the
underlying data does not support.

Sources (all real, retrieved 2026-08):
  - Consumption tax 10% since Oct 2019 (National Tax Agency / MOF).
  - Personal income tax: national schedule 5-45% over seven brackets plus
    a flat 10% local inhabitant tax and a 2.1% reconstruction surtax on
    the national tax (PwC Worldwide Tax Summaries: Japan). The average
    effective personal income tax burden is low because of large
    deductions: OECD Taxing Wages 2025 puts the net average tax rate for a
    single worker at the average wage at 22.0%, of which roughly 15 points
    are employee social insurance, leaving income tax alone near 7-8%.
  - Social insurance (payroll on labor): the full combined contribution is
    about 30% of remuneration (Japan Pension Service / MHLW): pension 18.3%,
    health ~10%, long-term care ~1.6% (age 40+), employment ~0.9%, with
    employer and employee sides both borne by labor. OG-Core's payroll tax
    revenue funds general government rather than an earmarked pension pot,
    so all of it correctly finances spending.
  - Capital income: listed dividends, interest, and share capital gains
    are taxed at a flat 20.315% (15% national + 5% local + 0.315%
    reconstruction surtax) (PwC Worldwide Tax Summaries: Japan).
  - Corporate income: effective combined rate about 30% (national 23.2%
    plus local corporate, inhabitant, and enterprise taxes) (PwC / JETRO).

What is still first-pass: the income tax is treated as a single average
effective rate with a separate constant marginal rate, rather than the full
progressive schedule (refining it needs the income distribution behind the
published effective rates). The social insurance contribution cap and the
frac_tax_payroll split are not modeled. Even with the full social insurance
in place, model revenue reaches about 32% of GDP against Japan's 37.6%,
because Japan raises roughly ten points of GDP in property and other taxes
that OG-Core does not represent.
"""

# Japan effective/marginal tax rates as constant (linear) tax functions.
ETR_INCOME = 0.08  # average effective personal income tax on total income
MTR_LABOR = 0.30  # marginal on labor income (20% national + 10% local band)
MTR_CAPITAL = 0.20315  # flat tax on listed financial income (real)
# Combined social insurance on labor, ~30%: employees' pension 18.3% +
# health ~10.0% + long-term care ~0.8% (age 40+, blended) + employment
# ~0.9% (Japan Pension Service / MHLW, employer+employee, labor bears both).
# Payroll-tax revenue in OG-Core funds general government, not an earmarked
# pension pot, so the non-pension pieces correctly finance government
# spending. The contribution cap is not modeled, which overstates the rate
# for high earners.
TAU_PAYROLL = 0.30
CIT_RATE = 0.30  # effective combined corporate income tax rate (real)
TAU_C = 0.10  # consumption tax since October 2019 (real)


def _linear_params(rate, num_ages):
    """
    Build an OG-Core tax-function parameter array for a constant rate.

    For ``tax_func_type="linear"`` each of etr/mtrx/mtry is a single
    coefficient per age and year; the array is a list of budget-window
    years, each a list of ``num_ages`` ages, each a one-element list with
    the rate. One year is supplied and OG-Core holds it constant over the
    horizon.

    Args:
        rate (float): the constant tax rate
        num_ages (int): number of age groups S in the model

    Returns:
        params (list): nested list of shape (1, num_ages, 1)
    """
    return [[[rate] for _ in range(num_ages)]]


def get_tax_params(num_ages=80):
    """
    Return Japan tax parameters for ``Specifications.update_specifications``.

    Args:
        num_ages (int): number of age groups S in the model, used to size
            the linear income-tax function arrays (default 80, OG-Core's S)

    Returns:
        tax_parameters (dict): Japan tax parameters
    """
    tax_parameters = {
        # Constant (linear) income tax functions, one sourced rate each.
        "tax_func_type": "linear",
        "etr_params": _linear_params(ETR_INCOME, num_ages),
        "mtrx_params": _linear_params(MTR_LABOR, num_ages),
        "mtry_params": _linear_params(MTR_CAPITAL, num_ages),
        # Payroll (pension) tax and corporate income tax.
        "tau_payroll": [TAU_PAYROLL],
        "cit_rate": [[CIT_RATE]],
        # Consumption tax: 10% since October 2019.
        "tau_c": [[TAU_C]],
    }
    return tax_parameters
