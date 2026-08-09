"""
OG-Japan first-pass macro calibration.

IMPORTANT: every value below is a PROVISIONAL placeholder, chosen to be
in the right ballpark for Japan and annotated with a public source to
verify. They are Phase-0/1 scaffolding, not a final calibration. Phase 1
replaces them with values pulled from OECD / IMF / World Bank data (the
way OG-THA's macro_params.py pulls from FRED and the World Bank). Do not
cite these numbers as accurate yet.
"""


def get_macro_params():
    """
    Return a dict of Japan macro parameters for
    ``Specifications.update_specifications``.

    Returns:
        macro_parameters (dict): provisional Japan macro parameters
    """
    macro_parameters = {}

    # Long-run productivity growth (real GDP per worker). Japan's trend
    # growth is low; ~0.8%/yr as a first pass.
    # Verify: OECD long-run productivity / World Bank GDP-per-capita growth.
    macro_parameters["g_y_annual"] = 0.008

    # Capital share of income. ~0.38 is a standard value for Japan.
    # Verify: Penn World Table labor share (1 - labor share).
    macro_parameters["gamma"] = [0.38]

    # Initial government-debt-to-GDP ratio. Japan's NET general government
    # debt is roughly 1.5x GDP (GROSS is ~2.5x). This first pass uses a
    # deliberately moderate 1.0 so the steady-state budget closure stays
    # feasible; raising it toward Japan's true ratio is a Phase-1 decision
    # that interacts with alpha_G (government spending share).
    # Verify: IMF WEO net general government debt for Japan.
    macro_parameters["initial_debt_ratio"] = 1.0

    # Government consumption spending as a share of GDP. Japan ~0.20.
    # Verify: OECD general government final consumption expenditure / GDP.
    macro_parameters["alpha_G"] = [0.20]

    # Government non-pension transfers as a share of GDP. First pass.
    # Verify: OECD social spending less public pensions, over GDP.
    macro_parameters["alpha_T"] = [0.10]

    return macro_parameters
