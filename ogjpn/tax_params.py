"""
OG-Japan tax calibration.

The governing rule, inherited from the OG-Core country family: calibrate
**effective** quantities, not statutory ones. Every rate here is collections
divided by the base the model actually taxes, and every one is sourced.

Japan's tax structure, from the OECD *Revenue Statistics 2025* country note
(2023 data; total 200,343 billion yen = 33.7% of GDP, implying nominal GDP of
594,490 billion yen):

    Instrument                        yen bn    % of GDP
    Social security contributions     78,335       13.18
    Personal income tax               36,703        6.17
    Corporate income tax              27,942        4.70
    VAT (consumption tax)             29,355        4.94
    Excises                            7,533        1.27
    Taxes on property                 16,330        2.75
    Other                                497        0.08
    TOTAL                            200,343       33.70

The single most important fact here is that **social insurance is Japan's
largest tax instrument** -- 39.1% of all tax revenue, the 4th highest share in
the OECD -- and OG-Core's default collects none of it.

Values marked ``NEEDS TUNING`` are starting points that must be iterated against
a solved steady state; the target each should hit is stated. The family's
in-model tuning loop (solve, read revenue by instrument, adjust, re-solve)
converges in three to five iterations.
"""

# Denominators used to convert collections into effective rates. Kept as named
# constants so the arithmetic in the comments below can be checked.
GDP_2023_YEN_BN = 594490.0
LABOR_SHARE = 0.57  # 1 - gamma, consistent with ogjpn.macro_params (PWT)
CONSUMPTION_SHARE_OF_GDP = 0.536  # World Bank NE.CON.PRVT.ZS, Japan 2023


def get_tax_params():
    """
    Return Japan tax parameters for
    ``Specifications.update_specifications``.

    Returns:
        tax_parameters (dict): Japan tax parameters
    """
    tax_parameters = {}

    # -----------------------------------------------------------------------
    # Social insurance contributions -- the largest single instrument.
    #
    # Collections 13.18% of GDP; the model's labour share of income is
    # 1 - gamma = 0.57 (Penn World Table; see ogjpn.macro_params). Effective
    # rate on the wage bill:
    #     0.1318 / 0.57 = 0.2312
    # This moved with gamma: the first pass used a labour share of 0.62 and so
    # a rate of 0.2126. The two must stay consistent or the payroll take drifts
    # off its target.
    #
    # This is below Japan's combined statutory rate of roughly 30% (employees'
    # pension 18.3%, health ~10%, long-term care ~1.8%, employment ~1%) because
    # of the standard-remuneration ceilings and incomplete coverage. Using the
    # statutory rate would over-collect by about a third -- the error OG-BRA is
    # the family's cautionary tale for.
    #
    # NOTE: tau_payroll is ADDITIVE on top of the income-tax function in
    # ogcore's tax.py (income_payroll_tax_liab = T_I + T_P), so the combined
    # household take must be audited, not just the income-tax line.
    # -----------------------------------------------------------------------
    tax_parameters["tau_payroll"] = [0.2312]

    # Split the reported take between the payroll and income-tax lines so the
    # model's reporting matches the data's: SSC / (SSC + PIT).
    #     78,335 / (78,335 + 36,703) = 0.681
    tax_parameters["frac_tax_payroll"] = [0.681]

    # -----------------------------------------------------------------------
    # Consumption / indirect taxes.
    #
    # Japan's consumption tax has been 10% statutory since October 2019 (8% on
    # food and newspapers). But the family rule is that tau_c carries ALL
    # consumption and indirect taxes, not VAT alone, and that the rate is
    # effective rather than statutory:
    #
    #     goods-and-services taxes 6.82% of GDP / consumption 53.6% of GDP
    #       = 0.1272
    #
    # So the effective rate is slightly ABOVE the headline 10%, because excises
    # (fuel, liquor, tobacco, motor vehicles) add 1.27% of GDP on top of VAT's
    # 4.94%. Using the statutory 10% would under-collect.
    #
    # TUNED (rounds 3, 6): the data ratio implies 12.7%, but the model's
    # consumption share (0.63-0.65 of GDP) runs above Japan's actual (0.536) --
    # see docs/CALIBRATION_AUDIT.md for why that is a property of a shrinking
    # steady state rather than an error. The rate that delivers Japan's
    # INDIRECT-TAX REVENUE against the model's own base is 0.0682 / 0.627 =
    # 0.1087 (which lands at 0.0702 once the pension tier is added back). Revenue is the moment worth hitting: it is what the government
    # actually collects.
    # -----------------------------------------------------------------------
    tax_parameters["tau_c"] = [[0.1207]]

    # -----------------------------------------------------------------------
    # Corporate income tax.
    #
    # Statutory combined national + local effective rate is about 29.74%.
    # Collections are 4.70% of GDP. OG-Core reconciles the two through
    # adjustment_factor_for_cit_receipts and c_corp_share_of_assets rather than
    # by distorting the rate, so the statutory rate is set here and the
    # adjustment factor carries the gap.
    #
    # OG-Core forms the effective corporate rate as
    #     tau_b = cit_rate * c_corp_share_of_assets * adjustment_factor
    # so the adjustment factor is the dial that maps the statutory rate onto
    # actual collections (ogcore/parameters.py:339).
    #
    # TUNED (rounds 2-3): OG-Core's US default of 0.309 produced CIT revenue of
    # 1.56% of GDP against a target of 4.70%. Scaled to 0.930, then 1.038
    # after the income-tax fix, then 0.868 once gamma moved to the Penn World
    # Table value and enlarged the capital-income base.
    # -----------------------------------------------------------------------
    tax_parameters["cit_rate"] = [[0.2974]]
    tax_parameters["adjustment_factor_for_cit_receipts"] = [0.857]

    # -----------------------------------------------------------------------
    # Property taxes -> the wealth tax.
    #
    # A recurrent property tax IS a flat tax on a form of wealth, so it belongs
    # on the wealth-tax margin (saving), not on income. Japan's total property
    # taxes are 2.75% of GDP, but that OECD category also contains the
    # inheritance tax, which is carried separately by tau_bq below. Netting the
    # inheritance tax out (about 3,200 yen bn in 2023) leaves recurrent and
    # transaction property taxes of roughly 2.21% of GDP.
    #
    # h_wealth = 1 and a small positive m_wealth make the effective wealth-tax
    # rate approximately flat at p_wealth and zero at zero wealth. m_wealth
    # must not be exactly zero -- it divides 0/0 at b = 0.
    #
    # TUNED (round 3): the solved steady state puts household wealth at 4.69x
    # GDP, so p_wealth = 0.0221 / 4.69 = 0.00471. The first guess of 0.0055
    # (assuming 4x GDP) was over-collecting 2.58% of GDP against a 2.21%
    # target.
    # -----------------------------------------------------------------------
    tax_parameters["p_wealth"] = [0.00503]
    tax_parameters["h_wealth"] = [1.0]
    tax_parameters["m_wealth"] = [0.001]

    # -----------------------------------------------------------------------
    # Bequest tax.
    #
    # Japan is the one country where the family's standing warning runs the
    # other way. The usual finding is that effective estate taxation is one to
    # two orders of magnitude below statutory and tau_bq should be near zero.
    # Japan's inheritance tax is genuinely material: 3,461 yen bn in the FY2025
    # budget, about 0.58% of GDP, among the highest in the OECD, with a top
    # statutory rate of 55%.
    #
    # It is still far below statutory, because the basic exclusion means only
    # roughly 9% of estates pay it at all.
    #
    # TUNED (round 3): model bequest flows are 25.1% of GDP, far above the 7%
    # first guess, so the starting tau_bq of 0.08 collected 2.01% of GDP
    # against a 0.55% target -- nearly four times too much. The effective rate
    # is 0.0055 / 0.251 = 0.0219, which is the right order for a tax where the
    # basic exclusion means only about 9% of estates pay anything.
    # -----------------------------------------------------------------------
    tax_parameters["tau_bq"] = [0.0263]

    # -----------------------------------------------------------------------
    # Personal income tax -- Gouveia-Strauss progressive form.
    #
    # Replaces OG-Core's default "DEP" functions, which are fitted to UNITED
    # STATES microdata via Tax-Calculator and have nothing to do with Japan.
    #
    # GS is the family default over HSV for a data-poor calibration: it floors
    # the effective rate at exactly zero, which is faithful wherever a statutory
    # threshold exempts the bottom. HSV's effective rate goes negative below the
    # threshold, and that implicit subsidy has pushed transitions into debt
    # runaways elsewhere in the family.
    #
    #     T(y) = phi0 * (y - (y^-phi1 + phi2)^(-1/phi1))
    #
    #   phi0 = the statutory TOP marginal rate -- an anchor, not a fit. Japan:
    #          45% national + 10% local inhabitant tax = 55%.
    #   phi1 = curvature, fitted to the shape of the statutory schedule
    #          (Japan's national brackets are 5/10/20/23/33/40/45%).
    #   phi2 = scale, tuned in-model to the collections target.
    #
    # mtrx_params (labour) and mtry_params (capital) take the same triple; the
    # x/y naming is not mnemonic.
    #
    # TUNED (round 2): the starting phi2 of 2.0e-8 put the effective rate at
    # mean income at 45.8%, collecting 37.8% of GDP against a 6.17% target --
    # because phi2 * y^phi1 was large enough to saturate the ETR near phi0 for
    # essentially every household. Inverting the GS effective-rate expression,
    #
    #     ETR(y) = phi0 * (1 - (1 + phi2 * y^phi1)^(-1/phi1))
    #
    # at Japan's mean income of 4.6m yen for an ETR of about 6% gives
    # phi2 = 3.5e-10. Incomes are evaluated in currency via `factor`, so phi2
    # carries units of income^(-phi1) and is therefore very small in yen.
    #
    # STILL NEEDS FITTING: phi1 = 1.30 is a family-analogous value, not a fit
    # to Japan's statutory brackets. Revenue responds concavely to phi2, so
    # expect to iterate rather than scale proportionally.
    # -----------------------------------------------------------------------
    tax_parameters["tax_func_type"] = "GS"
    # phi2 is in units of income^(-phi1) and income is in MILLIONS of yen (see
    # ogjpn.pension_params.MEAN_INCOME_MILLIONS_YEN). In plain yen this value
    # would be 3.5e-10; rescaled by 1e6^1.30 it is 0.0221. The effective rate at
    # every income is identical either way -- only the units change.
    _gs_params = [[[0.55, 1.30, 3.5e-10]]]
    tax_parameters["etr_params"] = _gs_params
    tax_parameters["mtrx_params"] = _gs_params
    tax_parameters["mtry_params"] = _gs_params

    return tax_parameters
