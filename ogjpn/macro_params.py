"""
OG-Japan macro calibration.

Every value here is sourced in the comment that sets it. Where a parameter can
only be pinned down by solving the model (the family calls this the in-model
tuning loop), the starting value is marked ``NEEDS TUNING`` and the target it
should be tuned to is stated.

The organising fact of Japanese public finance, and the thing this module exists
to get right, is that **Japan's government pays almost nothing to service its
debt**. Interest income on government financial assets roughly cancels interest
paid, so general government net interest is about zero and the real effective
rate is negative. That is why Japan can carry its debt while running primary
deficits, and a calibration that does not represent it will demand a primary
surplus Japan has never run. See ``docs/CALIBRATION_AUDIT.md``.

Debt is calibrated on a **net** basis. OG-Core's government holds no financial
assets, so charging debt service on gross debt while modelling none of the
offsetting assets (GPIF, foreign reserves, the Fiscal Loan Fund) overstates the
burden. Net is the concept the model's own accounting implies.

Sources
-------
OECD  Economic Outlook, general government series for Japan, retrieved from the
      OECD SDMX API 2026-08-10: GGFLQ (gross financial liabilities), GNFLQ (net
      financial liabilities), NLGQ (net lending), NLGXQ (primary balance).
IMF   World Economic Outlook via the DataMapper API: GGXWDG_NGDP, NGDP_RPCH.
MOF   Ministry of Finance Japan, "Japanese Public Finance Fact Sheet", April
      2025 (FY2025 General Account Budget); "Breakdown by JGB and T-Bill
      Holders", March 2026 preliminary (BOJ Flow of Funds).
WB    World Bank World Development Indicators: SL.GDP.PCAP.EM.KD, SP.POP.TOTL.
"""

# ---------------------------------------------------------------------------
# Productivity-growth window.
#
# Named constants with a rationale, per family practice. The window starts in
# 2000, after Japan's 1997-98 banking crisis, and ends in 2019, before COVID.
# ---------------------------------------------------------------------------
PRODUCTIVITY_GROWTH_START_YEAR = 2000
PRODUCTIVITY_GROWTH_END_YEAR = 2019

# Interest-rate window: a ten-year average, so the steady-state anchor is not a
# single year of an unusually loose monetary regime.
INTEREST_RATE_START_YEAR = 2015
INTEREST_RATE_END_YEAR = 2024


def get_macro_params():
    """
    Return a dict of Japan macro parameters for
    ``Specifications.update_specifications``.

    Returns:
        macro_parameters (dict): Japan macro parameters
    """
    macro_parameters = {}

    # -----------------------------------------------------------------------
    # Long-run labour-productivity growth.
    #
    # g_y is labour-augmenting productivity growth, NOT GDP growth: in the model
    # GDP growth is g_y plus population growth, and population growth arrives
    # separately from the demographics. Justifying g_y with GDP growth would
    # count Japan's demographic decline twice.
    #
    # It is productivity per HOUR, not per worker. OG-Core's labour input is
    # people x hours x ability -- `n` is the fraction of the time endowment
    # supplied -- and in a steady state hours per worker are CONSTANT. Japan's
    # measured hours per worker fell about 0.47%/yr over this window, which is a
    # transitional adjustment, not a balanced-growth feature. Anchoring g_y on
    # output per WORKER would import that transitional decline into the steady
    # state as if it were permanent.
    #
    # This is the same argument that sets the window below: Japan's employment
    # ALSO rose faster than population over the period, as participation among
    # women and older workers increased, and that too cannot continue for ever.
    # Both adjustments have to be stripped out, or neither.
    #
    # Penn World Table via FRED (RGDPNAJPA666NRUG real GDP, EMPENGJPA148NRUG
    # persons engaged, AVHWPEJPA065NRUG average hours), compound annual growth:
    #
    #     window       GDP/worker   hours/worker   GDP/HOUR
    #     1995-2019      +0.760%       -0.491%      +1.257%
    #     2000-2019      +0.557%       -0.472%      +1.035%   <- used
    #     2000-2023      +0.454%       -0.478%      +0.937%
    #     2010-2019      +0.152%       -0.548%      +0.704%
    #
    # The window starts in 2000, after Japan's 1997-98 banking crisis, and ends
    # in 2019, before COVID.
    # -----------------------------------------------------------------------
    macro_parameters["g_y_annual"] = 0.0104

    # -----------------------------------------------------------------------
    # Depreciation rate of capital.
    #
    # OG-Core's default of 0.05 is a United States value and was silently in
    # force. Japan's capital stock wears out noticeably faster.
    #
    # Derived from Japan's own accounts: delta = CFC / K = (CFC/Y) / (K/Y).
    # World Bank NY.ADJ.DKAP.GN.ZS converted to a GDP basis gives consumption
    # of fixed capital of 23.5-24.1% of GDP over 2016-2019 (the pre-COVID
    # window; 2020-21 readings of 25-26% are distorted by the output
    # collapse). Against a Penn World Table capital-output ratio of ~3.7:
    #
    #     0.237 / 3.7 = 0.064        (0.061 at the model's own K/Y of 3.87)
    #
    # 0.062 is taken as the midpoint of that range. Japan's high depreciation
    # reflects a short-lived, earthquake-resilient building stock and heavy
    # machinery intensity.
    #
    # This matters more than it looks: in the steady state, investment is
    # I/Y = (g + delta) * K/Y, so with Japan's NEGATIVE g the depreciation rate
    # is almost the ONLY thing generating investment demand. At delta = 0.05
    # the model invested 17.3% of GDP against Japan's actual 27.8%, and the
    # shortfall landed on consumption.
    # -----------------------------------------------------------------------
    macro_parameters["delta_annual"] = 0.062

    # -----------------------------------------------------------------------
    # Capital share of income.
    #
    # gamma = 1 - labour share, from the Penn World Table's share of labour
    # compensation in GDP at current national prices for Japan (PWT 10.01
    # series `labsh`, via FRED LABSHPJPA156NRUG):
    #
    #     2000-2019 mean  labsh 0.557  ->  gamma 0.443
    #     2015-2023 mean  labsh 0.571  ->  gamma 0.429
    #     2023            labsh 0.588  ->  gamma 0.413
    #
    # 0.43 is taken from the 2015-2023 window. Japan's labour share stepped up
    # after 2019 (profits fell faster than wages through COVID and the share has
    # not returned), so the longer window would overstate the capital share for
    # a forward-looking steady state, while 2023 alone would read one year of a
    # still-unwinding shock as permanent.
    #
    # The first pass used 0.38, which is below every reading in the series.
    # NOTE: the labour share implied here (0.57) is also the denominator for the
    # effective payroll-tax rate in ogjpn.tax_params -- the two must agree.
    # -----------------------------------------------------------------------
    macro_parameters["gamma"] = [0.43]

    # -----------------------------------------------------------------------
    # Government debt: NET, not gross.
    #
    # OECD general government net financial liabilities, Japan (GNFLQ):
    #     2020 125.6 | 2022 117.2 | 2023 98.6 | 2024 86.4 | 2025 78.5
    # Gross for comparison (GGFLQ): 2024 205.4, 2025 197.5.
    #
    # initial_debt_ratio is the MEASURED ratio at the start of the start year,
    # i.e. end-2024 for a 2025 start: 0.864.
    #
    # The sharp fall from 2020 is a valuation effect -- the government's equity
    # and foreign-currency assets rose with the equity rally and the weaker yen
    # -- not a fiscal consolidation. That is a reason not to anchor the
    # steady state on the latest reading alone.
    # -----------------------------------------------------------------------
    macro_parameters["initial_debt_ratio"] = 0.864

    # -----------------------------------------------------------------------
    # Steady-state debt target. A POLICY anchor, not a measurement, and a
    # deliberate choice rather than an inherited default (OG-Core's default of
    # 2.0 was silently in force before this).
    #
    # Set to 1.0: above the latest reading (0.864) and below the 2015-2022
    # plateau (~1.20), so the steady state does not bake in the recent asset
    # revaluation as permanent. Japan's own fiscal target is to stabilise and
    # then reduce the debt ratio, which this represents.
    # -----------------------------------------------------------------------
    macro_parameters["debt_ratio_ss"] = 1.0

    # -----------------------------------------------------------------------
    # Foreign-held share of government debt.
    #
    # MOF "Breakdown by JGB and T-Bill Holders", March 2026 preliminary:
    # foreigners hold 157.8 of 1,150.1 trillion yen = 13.7%. (Only 8.1% of JGBs
    # proper; the 55.6% foreign share of T-Bills lifts the combined figure.)
    # OG-Core's default is 0.4, which is about three times too high.
    #
    # This is the "Japan owes it to itself" fact, and it decides who bears the
    # burden of the debt: at 13.7% the interest is paid to Japanese households,
    # not abroad.
    #
    # zeta_D (foreign share of NEW issuance) is set equal to the stock share,
    # the family default when the flow is not separately measured.
    # -----------------------------------------------------------------------
    macro_parameters["initial_foreign_debt_ratio"] = 0.137
    macro_parameters["zeta_D"] = [0.137]

    # -----------------------------------------------------------------------
    # Sovereign interest-rate wedge:  r_gov = r_gov_scale * r - r_gov_shift
    #
    # This multiplies the WHOLE debt stock, so it is an average effective rate,
    # not a new-issue yield.
    #
    # Japan's effective rate, two independent routes, both from the government's
    # own accounts:
    #
    #  (a) Central government, MOF FY2025 budget: interest payments of 10.55
    #      trillion yen on 1,323.7 trillion of debt = 0.80% nominal.
    #  (b) General government, OECD (NLGXQ - NLGQ = net interest paid):
    #          2015-2024 average net interest  0.43% of GDP
    #          2015-2024 average net debt    114.8% of GDP
    #      => 0.375% nominal. Against realised inflation of ~0.95% over the same
    #         window, that is about -0.6% real.
    #
    #  The OECD's 2027 projection has net interest recovering to 0.86% of GDP
    #  (about -0.8% real) as policy rates normalise. The two routes and the
    #  projection agree on roughly -0.6% to -0.8% real, so the steady state is
    #  anchored there rather than on the 2024 reading of about -2% real, which
    #  reflects an unusually loose regime.
    #
    #  r_gov_scale is set to 0.25 rather than OG-Core's 1.0: Japanese sovereign
    #  yields are largely decoupled from the private return on capital, held
    #  down by Bank of Japan holdings (42.2% of JGBs and T-Bills) and by
    #  domestic demand for safe yen assets.
    #
    #  NEEDS TUNING: r_gov_shift is set assuming the model solves to r ~ 4.5%
    #  (r_gov = 0.25*0.045 - 0.017 = -0.0058). After the first steady-state
    #  solve, read the solved r and reset the shift so r_gov lands at -0.006.
    # -----------------------------------------------------------------------
    macro_parameters["r_gov_scale"] = [0.25]
    macro_parameters["r_gov_shift"] = [0.017]

    # -----------------------------------------------------------------------
    # Openness of the capital account.
    #
    # NEEDS TUNING: zeta_K is a marginal fill-share no dataset measures. It must
    # be tuned until the solved steady-state K_f/K matches Japan's IIP
    # foreign-owned share of the capital stock. Japan is the world's largest net
    # creditor, so the foreign-owned share of its DOMESTIC capital stock is
    # small; 0.10 is a low starting value pending the IIP anchor.
    # -----------------------------------------------------------------------
    macro_parameters["zeta_K"] = [0.10]

    # -----------------------------------------------------------------------
    # Government spending shares.
    #
    # These are set to satisfy the government budget identity at the debt
    # target, which is the constraint that decides whether the transition is
    # stable:
    #
    #     alpha_G + alpha_T + alpha_I = revenue/Y - pb*
    #     pb* = (r_gov - g) / (1 + g) * debt_ratio_ss
    #
    # With r_gov = -0.6% real, g = e^g_y (1 + g_n) - 1, and debt_ratio_ss = 1.0,
    # pb* is a primary DEFICIT of roughly 0.7% of GDP. Japan's actual primary
    # balance is -1.79% (2024) and -1.02% (2025) of GDP, so the steady state
    # embeds a modest consolidation relative to today -- which is what Japan's
    # own fiscal plan intends.
    #
    # A note on central versus general government, following OG-ETH's
    # treatment of the same problem (its macro.md "federal versus general
    # government" note). EVERY fiscal figure in this calibration is
    # GENERAL government -- central plus local, consolidated:
    #   - debt and interest      OECD Economic Outlook general-government series
    #   - taxes                  OECD Revenue Statistics ("net receipts for all
    #                            levels of government")
    #   - spending shares        World Bank general-government series
    # Mixing levels would be a live risk for Japan specifically, because the
    # central government's own budget routes 18,872.8 billion yen -- 16.4% of
    # its general account -- to prefectures and municipalities as Local
    # Allocation Tax Grants. Those are INTERGOVERNMENTAL transfers, not
    # household transfers: they must not enter alpha_T, and reading spending
    # off the central budget would double-count them against local spending.
    #
    # alpha_G: general government final consumption. World Bank
    #   NE.CON.GOVT.ZS for Japan = 20.1% of GDP (2024), stable at 20-21% since
    #   2020. Note OG-Core's steady-state closure overrides this to whatever
    #   balances the budget at the debt target -- alpha_G binds on the
    #   TRANSITION, not the steady state.
    # alpha_T: non-pension CASH transfers to households -- and ONLY cash.
    #   This is the parameter the first pass got most wrong (0.075, about three
    #   times too high), for a reason worth stating: Japan delivers most of its
    #   non-pension social spending IN KIND, not as cash.
    #
    #   Japan's social security spending, FY2023 (IPSS, total 135.5 trn yen
    #   against GDP of 594.5 trn):
    #       pensions               56.4 trn   9.49% of GDP   CASH (own block)
    #       healthcare             45.6 trn   7.67%          IN KIND
    #       long-term care         11.5 trn   1.93%          IN KIND
    #       welfare & other ex-LTC 22.0 trn   3.70%          mixed
    #
    #   The national accounts book in-kind health and long-term care as
    #   GOVERNMENT final consumption, which is why Japan's government
    #   consumption is 20.1% of GDP. In OG-Core those services belong in G,
    #   which does not enter the household budget -- not in TR, which does.
    #
    #   Two independent routes to the cash residual:
    #     (a) the cash share of welfare & other ex-LTC (child allowance, public
    #         assistance, employment insurance), roughly 40-45%  => ~1.6% of GDP
    #     (b) OECD SOCX cash/in-kind split: cash 11.9% of GDP less pensions
    #         9.3%                                                => ~2.6% of GDP
    #
    #   0.025 is taken from the upper end of that range.
    # alpha_I: public investment. Japan runs ~3% of GDP, high for the OECD.
    #   OG-Core's default is 0.0; leaving it there breaks the spending identity
    #   by the full 3 percentage points.
    #
    # NEEDS TUNING: re-check all three against the identity after the first
    # solve, once model revenue/Y and g_n_ss are known.
    # -----------------------------------------------------------------------
    macro_parameters["alpha_G"] = [0.201]
    macro_parameters["alpha_T"] = [0.025]
    macro_parameters["alpha_I"] = [0.03]

    # -----------------------------------------------------------------------
    # Household discount factor, calibrated to Japan's capital-output ratio.
    #
    # beta is not directly observable. The standard practice in this literature
    # is to calibrate it to an observable aggregate, and the capital-output
    # ratio is the conventional one. OG-Core ships OG-USA's 0.96.
    #
    # In the steady state the firm's first-order condition pins
    #     K/Y = gamma_effective / (r + delta)
    # with gamma and delta both sourced independently here, so K/Y is a
    # function of r, and r is what beta moves. Solving on the model:
    #
    #     beta 0.971  ->  K/Y 3.474,  r 4.80%
    #     beta 0.980  ->  K/Y 3.736,  r 4.05%
    #     interpolating to the Penn World Table's 3.70  ->  beta 0.979
    #
    # Recalibrated after the demographic data window was widened (see
    # ogjpn.constants.DEMOGRAPHIC_DATA_YEARS): a less negative population
    # growth rate raises g, which lowers K/Y at a fixed beta.
    #
    # Note this lever only became available once g_y was corrected to a
    # per-hour basis: at the earlier per-worker g_y the model's K/Y already sat
    # on target, and moving beta would have broken it. The order of operations
    # matters -- calibrate the sourced parameters first, then use beta for what
    # is left.
    # -----------------------------------------------------------------------
    macro_parameters["beta_annual"] = [0.979] * 7

    # -----------------------------------------------------------------------
    # Steady-state solver seeds: LEFT AT OG-CORE'S DEFAULTS, on evidence.
    #
    # These are OG-USA's solved values, and one of them is wrong in a way worth
    # recording: `initial_guess_factor_SS = 139355.15` is the factor that maps
    # model units to US DOLLARS. `factor` scales with `mean_income_data`, so
    # Japan's correct seed is about 7.0 million yen -- and OG-Core validates the
    # parameter to a maximum of 500,000, so the right value cannot be entered at
    # all. That cap is currency-dependent and excludes every low-unit currency
    # (yen, won, rupiah, dong). It is reported in docs/UPSTREAM_OGCORE.md.
    #
    # Because income is expressed in MILLIONS of yen, Japan's factor solves to
    # about 7.0 rather than 7.0 million, so for the first time the seed CAN be
    # set to the right order of magnitude. The r and TR seeds are OG-USA's
    # solved values and are left alone -- the family's rule is to choose seeds
    # by solve-path robustness rather than proximity, and the shipped pair has
    # the longer record of working here.
    # -----------------------------------------------------------------------
    macro_parameters["initial_guess_factor_SS"] = 7.0

    # -----------------------------------------------------------------------
    # Solver settings.
    #
    # Anderson acceleration on the TPI outer loop (ogcore >= 0.16.4). The
    # family's experience is that it cuts a single-industry transition from
    # 30-70 damped iterations to 11-12, with monotonically declining distances.
    # It belongs in the base calibration, not only in a multi-industry overlay.
    #
    # Watch the distance series on a first run: if it oscillates or stalls,
    # fall back to damped Picard with a lower `nu`. Note that neither damping
    # nor Anderson fixes a FISCAL runaway -- solver knobs treat oscillation,
    # not an unbalanced budget (see the identity in docs/CALIBRATION_AUDIT.md).
    # -----------------------------------------------------------------------
    macro_parameters["TPI_outer_method"] = "anderson"

    return macro_parameters
