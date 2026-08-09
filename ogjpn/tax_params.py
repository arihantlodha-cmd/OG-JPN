"""
OG-Japan first-pass tax calibration.

Only the consumption tax is set here, and it is a hard fact: Japan's
consumption tax (a VAT-style tax) has been 10% since October 2019.

The harder piece, estimating the income and payroll effective and
marginal tax rate functions, is deferred to Phase 2 proper. Japan has no
open-source tax microsimulator (unlike the US models, which use
Tax-Calculator), so that step will fit OG-Core's simpler tax functions to
published Japanese effective tax rates. Until then the income and payroll
tax side stays at OG-Core defaults.
"""


def get_tax_params():
    """
    Return provisional Japan tax parameters for
    ``Specifications.update_specifications``.

    Returns:
        tax_parameters (dict): provisional Japan tax parameters
    """
    tax_parameters = {}
    # Japan consumption tax rate: 10% since October 2019.
    # Source: National Tax Agency of Japan / Ministry of Finance.
    tax_parameters["tau_c"] = [[0.10]]
    return tax_parameters
