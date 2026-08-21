"""
OG-Japan macro calibration.

Sourced from the IMF World Economic Outlook via the IMF DataMapper API
(retrieved 2026-08-18). Japan's general government, share of GDP:
  - gross debt 214.5% (2024, GGXWDG_NGDP)
  - total revenue 37.6% (2024, indicator "rev")
  - total expenditure 39.1% (2024, indicator "exp")
  - net lending/borrowing -1.7% (2024, GGXCNL_NGDP)
  - real GDP growth ~0.7% (2023, NGDP_RPCH)

These pin the debt ratio, the growth rate, and the overall size of
government. The split of total expenditure (39.1%) into its OG-Core
pieces -- government consumption (alpha_G), pensions (a separate model
outlay), non-pension transfers (alpha_T), interest, and investment -- is
estimated from the standard composition, since the aggregate API series
do not break it out. gamma (capital share) is still a standard value to
verify against the Penn World Table.
"""


def get_macro_params():
    """
    Return a dict of Japan macro parameters for
    ``Specifications.update_specifications``.

    Returns:
        macro_parameters (dict): Japan macro parameters
    """
    macro_parameters = {}

    # Long-run productivity growth (real GDP per worker). Set to ~0.8%/yr,
    # consistent with Japan's low real GDP growth (~0.7% in 2023, IMF WEO
    # NGDP_RPCH) and a conservative proxy for per-worker productivity
    # growth given the shrinking workforce.
    macro_parameters["g_y_annual"] = 0.008

    # Capital share of income, gamma = 1 - labor share. Grounded in the
    # Penn World Table share of labor compensation for Japan (FRED series
    # LABSHPJPA156NRUG): the 2013-2023 mean labor share is 0.568, so the
    # capital share is about 0.43. The pre-COVID 2010s average gives ~0.44
    # (2020-2023 are mildly elevated), so 0.43 sits in a tight, well-
    # identified band, above the 0.38 first-pass value used previously.
    macro_parameters["gamma"] = [0.43]

    # Government-debt-to-GDP ratio. Japan's gross general government debt is
    # 214.5% of GDP in 2024 (IMF WEO, GGXWDG_NGDP) -- so extreme that it
    # exceeds OG-Core's built-in maximum for this parameter (200%), so we
    # use the cap, 2.0. (Japan's NET debt, ~1.3-1.6x GDP, would sit inside
    # the range; gross-at-the-cap reflects Japan's headline burden.)
    #
    # Two separate parameters matter here and both must be set. debt_ratio_ss
    # is the ratio the STEADY STATE holds; initial_debt_ratio is the ratio
    # the transition STARTS from. OG-Core's default debt_ratio_ss is also
    # 2.0, so leaving it unset happens to give the same steady state, but we
    # set it explicitly so the calibration says what it means (Japan's debt
    # stabilized at its current high level) rather than relying on a default.
    macro_parameters["debt_ratio_ss"] = 2.0
    macro_parameters["initial_debt_ratio"] = 2.0

    # Government consumption spending as a share of GDP. Japan's headline
    # general government final consumption is ~20% of GDP, but that national-
    # accounts figure is not the right number for this parameter, and using
    # it breaks the transition. OG-Core books public pensions
    # (agg_pension_outlays, ~11% here) and other transfers (alpha_T, 10%)
    # separately, so alpha_G is only the residual government PURCHASES of
    # goods after those, and much of Japan's measured "government consumption"
    # is in-kind health and long-term care that overlaps the social-insurance
    # transfers already modeled. The value that closes the government budget
    # at debt_ratio_ss, given the model's revenue (~32% of GDP) and the
    # separately-modeled pensions and transfers, is about 5.4% of GDP -- and
    # that is exactly the G/Y the steady state produces as a residual. The
    # transition must run the SAME fiscal policy as the steady state it
    # converges to: before the debt-closure rule engages (t < tG1) the
    # transition sets G = alpha_G * Y directly, so an alpha_G of 0.20 would
    # make the economy spend ~4x the sustainable level for 20 periods,
    # exploding debt and forcing the closure rule to demand negative G later.
    # That inconsistency, not solver tuning, is why the transition would not
    # converge. Setting alpha_G to the steady-state residual share removes it.
    macro_parameters["alpha_G"] = [0.054]

    # Government non-pension transfers as a share of GDP. Estimated from
    # the composition of the 39.1% total (consumption ~20, public pensions
    # ~10 handled as a separate model outlay, leaving ~9 for other
    # transfers, interest, and investment). Verify against OECD social
    # spending less public pensions.
    macro_parameters["alpha_T"] = [0.10]

    return macro_parameters
