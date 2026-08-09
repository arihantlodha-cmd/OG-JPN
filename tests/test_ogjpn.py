"""
Basic tests for the OG-JPN calibration scaffolding.

These do not require network access or a model solve; they check that the
calibration modules are wired correctly and return sane parameter values.
"""

from ogjpn import constants, macro_params, tax_params


def test_country_code_is_japan():
    assert constants.UN_COUNTRY_CODE == "392"
    assert constants.COUNTRY_ABBR == "JPN"


def test_macro_params_keys_and_ranges():
    m = macro_params.get_macro_params()
    for key in [
        "g_y_annual",
        "gamma",
        "initial_debt_ratio",
        "alpha_G",
        "alpha_T",
    ]:
        assert key in m
    # sanity ranges (provisional values must at least be plausible)
    assert 0.0 < m["g_y_annual"] < 0.05
    assert 0.0 < m["initial_debt_ratio"] < 3.0
    assert 0.0 < m["gamma"][0] < 1.0


def test_consumption_tax_is_ten_percent():
    # Japan's consumption tax has been 10% since October 2019.
    assert tax_params.get_tax_params()["tau_c"] == [[0.10]]
