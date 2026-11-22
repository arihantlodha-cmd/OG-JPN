"""
Tests for the OG-JPN calibration.

Most of these do not require network access or a model solve; they check
that the calibration modules are wired correctly and return the sourced
parameter values. A couple guard specific values whose being wrong has
broken the model before, so they are regression tests as much as sanity
checks.
"""

import numpy as np
import pytest

from ogjpn import calibrate, constants, macro_params, tax_params


def test_country_code_is_japan():
    assert constants.UN_COUNTRY_CODE == "392"
    assert constants.COUNTRY_ABBR == "JPN"


# ---------------------------------------------------------------- macro ----


def test_macro_params_keys_and_ranges():
    m = macro_params.get_macro_params()
    for key in [
        "g_y_annual",
        "gamma",
        "debt_ratio_ss",
        "initial_debt_ratio",
        "alpha_G",
        "alpha_T",
    ]:
        assert key in m
    assert 0.0 < m["g_y_annual"] < 0.05
    assert 0.0 < m["initial_debt_ratio"] < 3.0
    assert 0.0 < m["gamma"][0] < 1.0


def test_capital_share_matches_penn_world_table():
    # gamma = 1 - labor share (0.568) from the Penn World Table for Japan.
    assert macro_params.get_macro_params()["gamma"] == [0.43]


def test_debt_ratios_set_explicitly_and_equal():
    # Both the steady-state and initial debt ratios must be set (the SS one
    # governs the steady state; the initial one only sets where the
    # transition starts), and Japan's debt is stable at its high level, so
    # they are both the 2.0 cap.
    m = macro_params.get_macro_params()
    assert m["debt_ratio_ss"] == 2.0
    assert m["initial_debt_ratio"] == 2.0


def test_alpha_G_is_the_steady_state_residual_not_national_accounts():
    """Regression guard. alpha_G is government PURCHASES as a share of GDP,
    which in this model is the residual after the separately-modeled
    pensions and transfers, about 5.4% of GDP. It is NOT Japan's ~20%
    national-accounts government-consumption figure: before the debt-closure
    rule engages the transition spends G = alpha_G * Y directly, so 0.20
    makes the economy spend roughly four times the sustainable level for
    twenty periods, debt explodes, and the transition fails to converge.
    """
    alpha_G = macro_params.get_macro_params()["alpha_G"][0]
    assert alpha_G == pytest.approx(0.065, abs=0.005)
    lin = macro_params.get_macro_params("linear", "us")["alpha_G"][0]
    assert lin == pytest.approx(0.062, abs=0.005)
    assert alpha_G < 0.10  # must not be the ~0.20 national-accounts value


# ------------------------------------------------------------------ tax ----


def test_consumption_tax_is_ten_percent():
    # Japan's consumption tax has been 10% since October 2019.
    assert tax_params.get_tax_params()["tau_c"] == [[0.10]]


def test_tax_rates_match_sourced_values():
    assert tax_params.ETR_INCOME == 0.08  # avg effective personal income tax
    assert tax_params.MTR_LABOR == 0.30  # 20% national + 10% local band
    assert tax_params.MTR_CAPITAL == 0.20315  # flat tax on financial income
    assert tax_params.TAU_PAYROLL == 0.30  # full social insurance on labor
    assert tax_params.CIT_RATE == 0.30  # effective combined corporate rate


def test_linear_tax_option_has_correct_shapes():
    S = 80
    t = tax_params.get_tax_params(S, income_tax="linear")
    assert t["tax_func_type"] == "linear"
    assert t["tau_payroll"] == [[0.30]]
    assert t["cit_rate"] == [[0.30]]
    for key, rate in [
        ("etr_params", 0.08),
        ("mtrx_params", 0.30),
        ("mtry_params", 0.20315),
    ]:
        arr = np.array(t[key])
        # linear tax functions are one coefficient per age and one year
        assert arr.shape == (1, S, 1)
        assert np.all(arr == rate)


def test_tax_params_size_to_number_of_ages():
    # the income-tax arrays must resize to the model's S age groups
    lin = tax_params.get_tax_params(50, income_tax="linear")
    assert np.array(lin["etr_params"]).shape == (1, 50, 1)
    prog = tax_params.get_tax_params(50, mean_income=1e5)
    assert np.array(prog["etr_params"]).shape == (1, 50, 6)


def test_linear_params_helper_shape():
    out = np.array(tax_params._linear_params(0.25, 40))
    assert out.shape == (1, 40, 1)
    assert np.all(out == 0.25)


# -------------------------------------------------------- calibration ------


def test_calibration_assembles_macro_and_tax_without_network():
    """Calibration with use_demographics=False must assemble the macro and
    tax blocks into one dict for Specifications.update_specifications,
    sizing the tax arrays to the model's S, with no network call."""
    from ogcore.parameters import Specifications

    p = Specifications()
    calibrated = calibrate.Calibration(p, use_demographics=False).get_dict()
    # macro keys present
    for key in ["gamma", "alpha_G", "debt_ratio_ss"]:
        assert key in calibrated
    # tax keys present and sized to S
    assert calibrated["tau_c"] == [[0.10]]
    assert calibrated["tax_func_type"] == "DEP_totalinc"
    assert np.array(calibrated["etr_params"]).shape == (1, p.S, 6)
    linear = calibrate.Calibration(
        p, use_demographics=False, income_tax="linear", pension="us"
    ).get_dict()
    assert np.array(linear["etr_params"]).shape == (1, p.S, 1)
    assert linear["alpha_G"] == [0.062] and calibrated["alpha_G"] == [0.065]
    # default: Japan's pension formula, anchored to yen
    assert calibrated["pension_system"] == "US-Style Social Security"
    assert calibrated["mean_income_data"] == pytest.approx(4.595e6, rel=1e-3)
    with pytest.raises(ValueError):
        macro_params.get_macro_params("linear", "japan")


def test_update_specs_sets_the_yen_factor_guess_past_ogcore_cap():
    """OG-Core caps initial_guess_factor_SS at 500,000; update_specs sets the
    yen-scale guess directly, and it survives later updates."""
    from ogcore.parameters import Specifications

    p = Specifications()
    calibrate.update_specs(
        p, calibrate.Calibration(p, use_demographics=False).get_dict()
    )
    assert p.initial_guess_factor_SS == pytest.approx(6.7e6)
    p.update_specifications({"tau_c": [[0.12]]})
    assert p.initial_guess_factor_SS == pytest.approx(6.7e6)


def test_net_worth_profile_matches_survey_bands():
    """The 2019 全国家計構造調査 band means are reproduced at band midpoints,
    and the profile is flat beyond the first and last midpoints."""
    from ogjpn import wealth

    assert wealth.net_worth_by_age(45) == pytest.approx(19035.0)
    assert wealth.net_worth_by_age(85) == pytest.approx(43860.0)
    assert wealth.net_worth_by_age(21) == pytest.approx(2568.0)
    assert wealth.net_worth_by_age(100) == pytest.approx(43860.0)
    # hump that keeps rising into old age, as the survey reports
    prof = wealth.net_worth_by_age(np.arange(25, 86, 10))
    assert np.all(np.diff(prof) > 0)


def test_initial_hhwealth_dist_shape_and_split():
    """The distribution is S x J, sums to one, takes its age profile from
    the survey and its within-age split across income groups from the
    steady state."""
    from types import SimpleNamespace

    from ogjpn import wealth

    S, J, E = 80, 3, 20
    lambdas = np.array([0.5, 0.3, 0.2])
    omega_age = np.full(S, 1.0 / S)
    p = SimpleNamespace(
        S=S,
        J=J,
        E=E,
        lambdas=lambdas,
        omega=(omega_age[:, None] * lambdas[None, :])[None, :, :],
    )
    # steady state where group j saves (j + 1) times as much at every age
    b_ss = np.tile(np.array([1.0, 2.0, 3.0]), (S, 1))
    dist = wealth.get_initial_hhwealth_dist(p, b_ss)
    assert dist.shape == (S, J)
    assert dist.sum() == pytest.approx(1.0)
    # within-age ratios follow the steady state (per person: share / pop)
    per_person = dist / p.omega[0]
    assert per_person[40, 2] / per_person[40, 0] == pytest.approx(3.0)
    # across ages, per-person wealth follows the survey profile
    ages = E + np.arange(S) + 2
    prof = wealth.net_worth_by_age(ages)
    ratio = per_person[:, 0] / prof
    assert np.allclose(ratio, ratio[0])


def test_household_wealth_ratio_from_national_accounts():
    """End-2023 household net worth / FY2023 GDP: ~5.0 with land, ~3.7 on
    the model-comparable (no-land) basis."""
    from ogjpn import wealth

    assert wealth.HH_WEALTH_TO_GDP_INCL_LAND == pytest.approx(4.98, abs=0.01)
    assert wealth.HH_WEALTH_TO_GDP_EXCL_LAND == pytest.approx(3.69, abs=0.01)


def test_nta_bracket_data_matches_published_totals():
    """The packaged 2023 NTA salary-survey data reproduce the published
    totals: 50.76 million full-year earners, mean salary 4.60 million yen,
    11.89 trillion yen of income tax withheld."""
    from ogjpn import income_tax

    df = income_tax.load_nta_2023()
    assert len(df) == 14
    assert df.earners.sum() == pytest.approx(50_761_385, abs=10)
    mean = df.salary_total_yen.sum() / df.earners.sum()
    assert mean == pytest.approx(4.595e6, rel=1e-3)
    assert df.income_tax_withheld_yen.sum() == pytest.approx(11.89e12, rel=1e-3)


def test_taxable_income_inversion_matches_statute():
    """Taxable income recovered from tax withheld matches a statutory
    calculation for a single earner at the bracket mean (4.48 million yen:
    employment deduction 20% + 440k, social insurance ~15%, basic 480k)."""
    from ogjpn import income_tax

    b = income_tax.bracket_rates()
    row = b.iloc[4]
    s = row.mean_salary_yen
    statutory = s - (0.2 * s + 440_000) - 0.15 * s - 480_000
    assert row.taxable_yen == pytest.approx(statutory, rel=0.05)


def test_progressive_rates_rise_with_income_and_fit_the_data():
    """Effective rates rise from ~2% to ~40% across brackets, and the
    fitted DEP_totalinc function tracks them within 2.5 points."""
    from ogjpn import income_tax

    b = income_tax.bracket_rates()
    assert b.etr.iloc[0] < 0.03 and b.etr.iloc[-1] > 0.35
    assert np.all(np.diff(b.etr) > 0)
    p = income_tax.fit_dep_totalinc(b.x, b.etr, b.earners)
    fitted = income_tax.dep_totalinc(p, b.x.to_numpy())
    assert np.max(np.abs(fitted - b.etr.to_numpy())) < 0.025
    # at mean income the marginal rate is far below the old flat 30%
    pm = income_tax.fit_dep_totalinc(b.x, b.mtr_labor, b.earners)
    assert income_tax.dep_totalinc(pm, 1.0) < 0.15


def test_progressive_params_scale_with_the_income_anchor():
    """Rates at the anchor's mean income do not depend on the anchor."""
    from ogjpn import income_tax

    p = [0.03, 0.05, 0.5, 0.03]
    for m in (58_645.0, 4.6e6):
        q = income_tax.to_model_units(p, m)
        assert income_tax.dep_totalinc(q[:4], m) == pytest.approx(
            income_tax.dep_totalinc(p, 1.0)
        )
    t = tax_params.get_tax_params(80, income_tax="progressive", mean_income=1e5)
    assert t["tax_func_type"] == "DEP_totalinc"
    assert np.asarray(t["etr_params"]).shape == (1, 80, 6)
    assert t["mtry_params"][0][0][2:4] == [0.20315, 0.20315]


def _og_core_pia(aime, p):
    """OG-Core's US-style PIA bracket formula (pensions.replacement_rate_vals)."""
    if aime < p["AIME_bkt_1"]:
        pia = p["PIA_rate_bkt_1"] * aime
    elif aime < p["AIME_bkt_2"]:
        pia = p["PIA_rate_bkt_1"] * p["AIME_bkt_1"] + p["PIA_rate_bkt_2"] * (
            aime - p["AIME_bkt_1"]
        )
    else:
        pia = (
            p["PIA_rate_bkt_1"] * p["AIME_bkt_1"]
            + p["PIA_rate_bkt_2"] * (p["AIME_bkt_2"] - p["AIME_bkt_1"])
            + p["PIA_rate_bkt_3"] * (aime - p["AIME_bkt_2"])
        )
    return min(max(pia, p["PIA_minpayment"]), p["PIA_maxpayment"])


def test_pension_brackets_reproduce_japans_two_tier_formula():
    """Above the first bend point the bracket formula equals Japan's basic
    pension plus 0.5481% x 40 years of average earnings, up to the cap; at
    zero earnings it pays the basic pension."""
    from ogjpn import pension_params as pp

    p = pp.get_pension_params()
    assert p["mean_income_data"] == pytest.approx(4.595e6, rel=1e-3)
    assert p["PIA_minpayment"] == pytest.approx(66_250)
    for aime in [p["AIME_bkt_1"], 150_000, 383_000, 600_000, 775_000, 2e6]:
        assert _og_core_pia(aime, p) == pytest.approx(
            pp.japan_monthly_benefit(aime), rel=1e-9
        )
    assert _og_core_pia(0.0, p) == pytest.approx(66_250)
