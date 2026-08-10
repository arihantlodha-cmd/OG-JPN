"""
Tests for the OG-JPN calibration.

These do not require network access or a model solve. They check that the
calibration modules are wired correctly and that the calibrated values are the
ones the documentation says they are -- the family's "value-pinning" pattern,
which is what stops documentation drifting away from shipped numbers.
"""

import pytest

from ogjpn import constants, income, macro_params, pension_params, tax_params


# ---------------------------------------------------------------------------
# Country identity.
#
# The family's #1 copy-paste regression is a country model that silently keeps
# the sibling repo's country_id and calibrates the wrong country's demographics.
# OG-ETH shipped South Africa's code twice. This test is cheap insurance.
# ---------------------------------------------------------------------------
def test_country_code_is_japan():
    assert constants.UN_COUNTRY_CODE == "392"
    assert constants.COUNTRY_ABBR == "JPN"
    assert constants.COUNTRY_NAME == "Japan"


def test_calibrate_uses_the_named_country_constant():
    """calibrate.py must reference the constant, not an inline literal."""
    import inspect

    from ogjpn import calibrate

    source = inspect.getsource(calibrate)
    assert "UN_COUNTRY_CODE" in source
    assert '"392"' not in source, "country id should not be inlined"


# ---------------------------------------------------------------------------
# Macro block.
# ---------------------------------------------------------------------------
def test_macro_params_keys_present():
    m = macro_params.get_macro_params()
    for key in [
        "g_y_annual",
        "gamma",
        "initial_debt_ratio",
        "debt_ratio_ss",
        "initial_foreign_debt_ratio",
        "zeta_D",
        "zeta_K",
        "r_gov_scale",
        "r_gov_shift",
        "alpha_G",
        "alpha_T",
        "alpha_I",
    ]:
        assert key in m, f"{key} missing -- it would fall back to a US default"


def test_debt_is_calibrated_net_not_gross():
    """
    OECD general government NET financial liabilities for Japan were 86.4% of
    GDP at end-2024 (GNFLQ). Gross was 205.4%. OG-Core's government holds no
    financial assets, so the net concept is the one its accounting implies --
    and unlike gross it is not truncated by OG-Core's 2.0 ceiling.
    """
    m = macro_params.get_macro_params()
    assert m["initial_debt_ratio"] == pytest.approx(0.864)
    assert m["initial_debt_ratio"] < 2.0, "must not sit at OG-Core's cap"


def test_ss_debt_target_is_chosen_not_inherited():
    """OG-Core's default debt_ratio_ss is 2.0; leaving it is a silent choice."""
    m = macro_params.get_macro_params()
    assert m["debt_ratio_ss"] == pytest.approx(1.0)
    assert m["debt_ratio_ss"] != 2.0


def test_foreign_debt_share_matches_mof():
    """
    MOF, Breakdown by JGB and T-Bill Holders (Mar 2026 preliminary): foreigners
    hold 157.8 of 1,150.1 trillion yen = 13.7%. OG-Core's default is 0.4.
    """
    m = macro_params.get_macro_params()
    assert m["initial_foreign_debt_ratio"] == pytest.approx(0.137)
    assert m["zeta_D"][0] == pytest.approx(0.137)


def test_capital_share_matches_pwt():
    """
    gamma = 1 - PWT labour share for Japan (FRED LABSHPJPA156NRUG). The
    2015-2023 window averages labsh 0.571. The first pass used 0.38, which is
    below every observation in the series.
    """
    m = macro_params.get_macro_params()
    assert m["gamma"][0] == pytest.approx(0.43, abs=1e-3)
    # the payroll denominator in tax_params must track it
    assert tax_params.LABOR_SHARE == pytest.approx(1 - m["gamma"][0], abs=1e-3)


def test_depreciation_is_japans_not_the_us_default():
    """
    OG-Core's delta_annual default of 0.05 is a US value. Japan's consumption of
    fixed capital is 23.5-24.1% of GDP (2016-19), which against K/Y ~3.7 implies
    ~0.064. With Japan's NEGATIVE growth rate, delta is almost the only thing
    generating steady-state investment demand.
    """
    m = macro_params.get_macro_params()
    assert m["delta_annual"] == pytest.approx(0.062, abs=1e-3)
    assert not isinstance(m["delta_annual"], list), "delta_annual is a scalar"


def test_productivity_growth_window_is_named():
    """g_y is productivity growth, not GDP growth, over a stated window."""
    assert macro_params.PRODUCTIVITY_GROWTH_START_YEAR == 2000
    assert macro_params.PRODUCTIVITY_GROWTH_END_YEAR == 2019
    m = macro_params.get_macro_params()
    # World Bank SL.GDP.PCAP.EM.KD, Japan, 2000-2019 CAGR = 0.563%
    assert m["g_y_annual"] == pytest.approx(0.0056, abs=1e-4)


# ---------------------------------------------------------------------------
# Tax block.
# ---------------------------------------------------------------------------
def test_social_insurance_is_collected():
    """
    Japan's largest tax instrument is social insurance at 13.18% of GDP, 39.1%
    of all tax revenue. OG-Core's default tau_payroll is 0.0, which collects
    none of it. Effective rate = 0.1318 / labour share 0.57 (PWT).
    """
    t = tax_params.get_tax_params()
    assert t["tau_payroll"][0] == pytest.approx(0.2312, abs=1e-3)
    assert t["tau_payroll"][0] > 0.0


def test_payroll_income_split_matches_data():
    """frac_tax_payroll = SSC / (SSC + PIT) so reporting matches the data."""
    t = tax_params.get_tax_params()
    assert t["frac_tax_payroll"][0] == pytest.approx(78335 / (78335 + 36703), abs=1e-3)


def test_consumption_tax_is_effective_not_statutory():
    """
    tau_c must carry ALL indirect taxes, not VAT alone, and must be tuned to
    deliver the revenue rather than copied from a data ratio.

    Japan's statutory consumption tax is 10%. The data ratio (6.82% of GDP over
    consumption of 53.6%) implies 12.7%. But the model's consumption share runs
    at 62.7% of GDP, because a shrinking steady state needs much less
    investment than Japan currently undertakes -- so the rate that delivers
    Japan's indirect-tax revenue in the model is 0.0682 / 0.627 = 10.9%.
    """
    t = tax_params.get_tax_params()
    assert t["tau_c"] == [[pytest.approx(0.1123)]]
    assert t["tau_c"][0][0] != 0.10, "statutory rate is not the model input"


def test_cit_adjustment_factor_is_set():
    """
    tau_b = cit_rate * c_corp_share_of_assets * adjustment_factor. Leaving the
    adjustment factor at OG-Core's US default of 0.309 collected 1.56% of GDP
    against Japan's 4.70%.
    """
    t = tax_params.get_tax_params()
    assert "adjustment_factor_for_cit_receipts" in t
    assert t["adjustment_factor_for_cit_receipts"][0] > 0.309
    assert t["adjustment_factor_for_cit_receipts"][0] == pytest.approx(0.868, abs=1e-3)


def test_income_tax_is_not_the_us_functions():
    """
    OG-Core's default tax_func_type is "DEP", fitted to US Tax-Calculator
    microdata. Japan uses the Gouveia-Strauss progressive form, whose top
    asymptote is the statutory top marginal rate (45% national + 10% local).
    """
    t = tax_params.get_tax_params()
    assert t["tax_func_type"] == "GS"
    assert t["etr_params"][0][0][0] == pytest.approx(0.55)
    # GS floors the effective rate at zero; HSV would go negative at the bottom
    assert len(t["etr_params"][0][0]) == 3


def test_property_and_bequest_taxes_are_set():
    """
    Japan collects 2.75% of GDP in property taxes and has a genuinely material
    inheritance tax (~0.58% of GDP), unusually for the family.
    """
    t = tax_params.get_tax_params()
    assert t["p_wealth"][0] > 0.0
    assert t["m_wealth"][0] > 0.0, "m_wealth = 0 divides 0/0 at zero wealth"
    assert t["tau_bq"][0] > 0.0


# ---------------------------------------------------------------------------
# Pension block.
# ---------------------------------------------------------------------------
def test_pension_system_is_japanese_not_american():
    """
    Japan's public pension is an earnings-related defined-benefit scheme.
    OG-Core's default is "US-Style Social Security", which applies US bend
    points in US dollars.
    """
    pp = pension_params.get_pension_params()
    assert pp["pension_system"] == "Defined Benefits"
    assert pp["pension_system"] != "US-Style Social Security"


def test_alpha_db_reproduces_the_oecd_replacement_rate():
    """
    OG-Core's DB benefit is (avg earnings) x yr_contrib x alpha_db, so
    yr_contrib * alpha_db IS the gross replacement rate: 32.4% for Japan.

    OG-Core's alpha_db default is 0.0 -- switching pension_system without
    setting it produces zero pensions.

    The rate is an EFFECTIVE system-wide rate above the OECD's 32.4%: part
    derived (survivors' and disability pensions, which OG-Core's single DB block
    cannot separate) and part fitted to the outlay target. See
    ogjpn/pension_params.py for the honest split.
    """
    pp = pension_params.get_pension_params()
    assert pp["alpha_db"] > 0.0
    replacement = pp["yr_contrib"] * pp["alpha_db"]
    assert replacement == pytest.approx(0.399, abs=1e-6)
    assert replacement > pension_params.GROSS_REPLACEMENT_RATE_OECD
    # most of the gap should be the derived survivors/disability uplift
    derived = (pension_params.GROSS_REPLACEMENT_RATE_OECD
               * pension_params.SURVIVORS_DISABILITY_UPLIFT)
    assert abs(replacement - derived) < 0.04, "fitted residual must stay small"


def test_income_anchor_is_in_yen():
    """
    mean_income_data sets the currency income at which the tax functions and
    the pension formula are evaluated. OG-Core's default is US$58,644.92.
    """
    pp = pension_params.get_pension_params()
    assert pp["mean_income_data"] == pytest.approx(4.6e6)
    assert pp["mean_income_data"] != pytest.approx(58644.924039576625)


def test_pension_validation_target_is_japans_actual():
    """
    Japan's public pension expenditure is 9.3% of GDP, not the 11-12% the
    project previously claimed as a validated result.
    """
    assert pension_params.PENSION_EXPENDITURE_TARGET_SHARE_OF_GDP == pytest.approx(
        0.093
    )


# ---------------------------------------------------------------------------
# The calibration must actually deliver every block.
# ---------------------------------------------------------------------------
def test_calibration_dict_covers_all_blocks():
    """
    Anything absent from this dict silently keeps an OG-Core US default, so the
    breadth of the dict is itself the thing being tested.
    """
    from ogjpn import calibrate

    c = calibrate.Calibration.__new__(calibrate.Calibration)
    c.macro_params = macro_params.get_macro_params()
    c.tax_params = tax_params.get_tax_params()
    c.pension_params = pension_params.get_pension_params()
    c.demographic_params = None
    c.e = None

    d = c.get_dict()
    for key in [
        "g_y_annual",
        "delta_annual",
        "initial_debt_ratio",
        "debt_ratio_ss",
        "initial_foreign_debt_ratio",
        "tau_payroll",
        "tau_c",
        "cit_rate",
        "tax_func_type",
        "pension_system",
        "alpha_db",
        "mean_income_data",
    ]:
        assert key in d, f"{key} not delivered to Specifications"


def test_calibration_passes_ogcore_validators():
    """
    Apply the whole calibration to a real Specifications object.

    Checking that keys are PRESENT is not enough -- every value also has to
    satisfy OG-Core's schema. A scalar parameter wrapped in a list (delta_annual
    = [0.062] instead of 0.062) passes every other test in this file and then
    fails at solve time, minutes into a run. This test costs a second.
    """
    from ogcore.parameters import Specifications

    from ogjpn import calibrate
    from ogjpn.constants import START_YEAR

    p = Specifications(baseline=True, num_workers=1)
    p.update_specifications({"start_year": START_YEAR})

    c = calibrate.Calibration.__new__(calibrate.Calibration)
    c.macro_params = macro_params.get_macro_params()
    c.tax_params = tax_params.get_tax_params()
    c.pension_params = pension_params.get_pension_params()
    c.demographic_params = None
    c.e = None

    # Raises ValidationError if any value has the wrong type, shape, or range.
    p.update_specifications(c.get_dict())

    assert p.tax_func_type == "GS"
    assert p.pension_system == "Defined Benefits"


# ---------------------------------------------------------------------------
# Earnings ability.
# ---------------------------------------------------------------------------
def test_gini_target_is_japans_and_concept_matches():
    """
    Japan's World Bank Gini (SI.POV.GINI) is 32.3 for 2020, on an INCOME basis.
    The US reference in income.py must be the same welfare concept -- mixing an
    income Gini against a consumption Gini is the family's standing trap and
    systematically mis-states the tilt.
    """
    import inspect

    assert income.JAPAN_GINI == pytest.approx(32.3)
    src = inspect.getsource(income.get_e_interp)
    assert "gini_usa_data = 41.5" in src
    # Japan is MORE equal than the US, so the tilt must compress, not stretch
    assert income.JAPAN_GINI < 41.5


def test_demographic_gradients_are_deliberately_absent():
    """
    ogcore accepts fert_gradient / mort_gradient / infmort_gradient, but the
    EAPD-DRB/Demographic-Gradients library covers 78 developing countries and
    explicitly excludes high-income ones: its income-based fallback is valid
    only between $200 and $10,000 GNI per head. Japan is ~$39,000.

    This test pins the DECISION so nobody later wires in an extrapolated
    gradient thinking it was an oversight.
    """
    import inspect

    from ogjpn import calibrate

    src = inspect.getsource(calibrate)
    for gradient in ("fert_gradient", "mort_gradient", "infmort_gradient"):
        assert f"{gradient}=" not in src, (
            f"{gradient} must not be passed: Japan is out of the library's scope"
        )
    # but income_percentiles IS passed, so the arrays stay J-wide
    assert "income_percentiles" in src
