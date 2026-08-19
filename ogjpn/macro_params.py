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

    # Initial government-debt-to-GDP ratio. Japan's gross general
    # government debt is 214.5% of GDP in 2024 (IMF WEO, GGXWDG_NGDP) --
    # so extreme that it exceeds OG-Core's built-in maximum for this
    # parameter (200%). We use the cap, 2.0. (Japan's NET debt, ~1.5-1.6x
    # GDP, would sit comfortably inside the range; gross-at-the-cap is
    # used here to reflect Japan's headline debt burden.)
    macro_parameters["initial_debt_ratio"] = 2.0

    # Government consumption spending as a share of GDP. Japan's general
    # government final consumption is ~20% of GDP -- about half of the
    # 39.1% total expenditure (IMF), the rest being pensions, other
    # transfers, interest, and investment.
    macro_parameters["alpha_G"] = [0.20]

    # Government non-pension transfers as a share of GDP. Estimated from
    # the composition of the 39.1% total (consumption ~20, public pensions
    # ~10 handled as a separate model outlay, leaving ~9 for other
    # transfers, interest, and investment). Verify against OECD social
    # spending less public pensions.
    macro_parameters["alpha_T"] = [0.10]

    return macro_parameters
