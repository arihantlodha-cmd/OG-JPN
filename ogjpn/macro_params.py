"""
OG-Japan macro calibration.

Sourced values (IMF World Economic Outlook via the IMF DataMapper API,
retrieved 2026-08-09):
  - initial_debt_ratio: Japan gross general government debt, 214.5% of GDP
    (2024), indicator GGXWDG_NGDP.
  - g_y_annual: consistent with Japan real GDP growth of ~0.7% (2023,
    indicator NGDP_RPCH); a conservative proxy for labor-productivity
    growth given Japan's shrinking workforce.

Still first-pass / to verify (no clean open API pull yet):
  - gamma (capital share), alpha_G (govt consumption/GDP),
    alpha_T (non-pension transfers/GDP).
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

    # Capital share of income. ~0.38 is a standard value for Japan.
    # First pass -- verify against Penn World Table (1 - labor share).
    macro_parameters["gamma"] = [0.38]

    # Initial government-debt-to-GDP ratio. Japan's gross general
    # government debt is 214.5% of GDP in 2024 (IMF WEO, GGXWDG_NGDP) --
    # so extreme that it exceeds OG-Core's built-in maximum for this
    # parameter (200%). We use the cap, 2.0. (Japan's NET debt, ~1.5-1.6x
    # GDP, would sit comfortably inside the range; gross-at-the-cap is
    # used here to reflect Japan's headline debt burden.)
    macro_parameters["initial_debt_ratio"] = 2.0

    # Government consumption spending as a share of GDP. Japan ~0.20.
    # First pass -- verify against OECD govt final consumption / GDP.
    macro_parameters["alpha_G"] = [0.20]

    # Government non-pension transfers as a share of GDP. First pass --
    # verify against OECD social spending less public pensions / GDP.
    macro_parameters["alpha_T"] = [0.10]

    return macro_parameters
