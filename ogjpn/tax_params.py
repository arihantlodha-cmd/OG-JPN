"""
OG-Japan tax calibration.

Japan has no open-source tax microsimulation model (no equivalent of the US
Tax-Calculator), so taxes are calibrated from administrative data and
published rates:

  - Personal income tax (default, ``income_tax="progressive"``): Japan's
    progressive schedule on labor income, fitted to the National Tax
    Agency's 2023 salary-bracket data, plus a flat effective tax on capital
    income, combined age by age into OG-Core's DEP_totalinc form (see
    ogjpn.income_tax). The option ``income_tax="linear"`` keeps the earlier
    constant rates (8% average, 30% marginal on labor, 20.315% on capital).
  - Social insurance (payroll on labor): about 30% of remuneration (Japan
    Pension Service / MHLW): pension 18.3%, health ~10%, long-term care
    ~0.8% (blended), employment ~0.9%, employer and employee sides both
    borne by labor. OG-Core's payroll tax revenue funds general government
    rather than an earmarked pension pot. The contribution cap is not
    modeled.
  - Corporate income: effective combined rate about 30% (national 23.2%
    plus local corporate, inhabitant, and enterprise taxes) (PwC / JETRO).
  - Consumption tax: 10% since October 2019 (National Tax Agency / MOF).

Japan's property tax (Fixed Asset plus City Planning Tax, ~2% of GDP) could
be added through OG-Core's wealth tax but made the consumption-tax reform
fail to converge, so it is deferred.
"""

import numpy as np

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


def get_tax_params(
    num_ages=80,
    income_tax="progressive",
    mean_income=None,
    labor_share=None,
    capital_tax=None,
):
    """
    Return Japan tax parameters for ``Specifications.update_specifications``.

    Args:
        num_ages (int): number of age groups S in the model, used to size
            the income-tax function arrays (default 80, OG-Core's S)
        income_tax (str): "progressive" (default) for DEP_totalinc
            functions fitted to Japan's 2023 salary-bracket tax data (see
            ogjpn.income_tax), or "linear" for constant average (8%) and
            marginal (30% labor, 20.315% capital) rates
        mean_income (float): the model's income anchor
            (``mean_income_data``), used to put the progressive functions
            in model income units; defaults to OG-Core's default value
        labor_share (array_like): labor share of income at each age, for
            the progressive option; defaults to the stored steady-state
            shares (ogjpn.income_tax.load_labor_share_by_age)
        capital_tax (float): flat tax rate on capital income for the
            progressive option; defaults to Japan's effective rate
            (ogjpn.income_tax.effective_capital_tax_rate, about 5.7%)

    Returns:
        tax_parameters (dict): Japan tax parameters
    """
    tax_parameters = {
        # Payroll (social insurance) tax and corporate income tax.
        # OG-Core >= 0.19 takes tau_payroll as a (T, J) array, so a nested list.
        "tau_payroll": [[TAU_PAYROLL]],
        "cit_rate": [[CIT_RATE]],
        # Consumption tax: 10% since October 2019.
        "tau_c": [[TAU_C]],
    }
    if income_tax == "linear":
        # Constant (linear) income tax functions, one sourced rate each.
        tax_parameters.update(
            {
                "tax_func_type": "linear",
                "etr_params": _linear_params(ETR_INCOME, num_ages),
                "mtrx_params": _linear_params(MTR_LABOR, num_ages),
                "mtry_params": _linear_params(MTR_CAPITAL, num_ages),
            }
        )
    elif income_tax == "progressive":
        from ogjpn import income_tax as it

        if mean_income is None:
            from ogcore.parameters import Specifications

            mean_income = float(Specifications().mean_income_data)
        b = it.bracket_rates()
        etr = it.fit_dep_totalinc(b.x, b.etr, b.earners)
        mtrx = it.fit_dep_totalinc(b.x, b.mtr_labor, b.earners)
        if labor_share is None:
            # Stored for S = 80; other S get the same life-cycle profile.
            stored = it.load_labor_share_by_age()
            labor_share = np.interp(
                np.linspace(0, 1, num_ages),
                np.linspace(0, 1, len(stored)),
                stored,
            )
        if len(labor_share) != num_ages:
            raise ValueError(
                f"labor_share has {len(labor_share)} ages, model has {num_ages}"
            )
        if capital_tax is None:
            capital_tax = it.effective_capital_tax_rate()
        etr_s, mtrx_s, mtry_s = it.age_specific_params(
            etr, mtrx, labor_share, capital_tax, mean_income
        )
        tax_parameters.update(
            {
                "tax_func_type": "DEP_totalinc",
                "analytical_mtrs": False,
                "etr_params": [etr_s],
                "mtrx_params": [mtrx_s],
                "mtry_params": [mtry_s],
            }
        )
    else:
        raise ValueError("income_tax must be 'linear' or 'progressive'")
    return tax_parameters
