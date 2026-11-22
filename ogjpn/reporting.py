"""
Helpers for reporting reform transitions.

OG-Core holds government purchases at a fixed share of GDP until the
debt-closure rule starts (period ``tG1``, 20 by default). A reform that
raises revenue or cuts spending therefore pays down government debt over
those first 20 years. Lower debt frees household saving for private
capital ("crowding in"), so capital rises along the transition even when
households save less. After ``tG1`` the closure rule brings debt back to
its target and capital returns toward its new steady state. These helpers
measure that channel so the write-ups state it from the solved paths.
"""

import numpy as np


def path(tpi, key):
    """A TPI variable as a flat time path."""
    return np.asarray(tpi[key], dtype=float).ravel()


def crowding_in(base, reform, t=20):
    """
    Summarize the debt channel of a reform at year ``t``.

    Args:
        base (dict): baseline TPI_vars
        reform (dict): reform TPI_vars
        t (int): year to report (default 20, OG-Core's tG1)

    Returns:
        (dict): debt/GDP in baseline and reform at ``t``, and percent
            changes vs baseline in household wealth B and capital K at
            ``t`` and in K in the last period of the path
    """
    bY, rY = path(base, "Y"), path(reform, "Y")
    bD, rD = path(base, "D"), path(reform, "D")
    bB, rB = path(base, "B"), path(reform, "B")
    bK, rK = path(base, "K"), path(reform, "K")
    return {
        "Y_pct": 100 * (rY[t] - bY[t]) / bY[t],
        "t": t,
        "debt_base": bD[t] / bY[t],
        "debt_reform": rD[t] / rY[t],
        "B_pct": 100 * (rB[t] - bB[t]) / bB[t],
        "K_pct": 100 * (rK[t] - bK[t]) / bK[t],
        "K_pct_long_run": 100 * (rK[-1] - bK[-1]) / bK[-1],
    }


def crowding_in_text(summary, label):
    """One paragraph stating the debt channel for a reform."""
    s = summary
    if s["B_pct"] < 0:
        saving = (
            "That, not extra household saving, is what lifts capital: "
            f"household wealth is {abs(s['B_pct']):.1f} percent lower "
            "(households save less)"
        )
    else:
        saving = (
            "Households also save more (household wealth is "
            f"{s['B_pct']:.1f} percent higher), so both channels add to "
            "capital"
        )
    return (
        "Where the capital comes from. OG-Core holds government purchases "
        "at a fixed share of GDP for the first 20 years, so the budget gain "
        f"from the {label} goes to paying down debt: by year {s['t']}, debt "
        f"is {s['debt_reform']:.2f} times GDP against {s['debt_base']:.2f} in "
        "the baseline. Lower debt frees household saving for private "
        f"capital. {saving}, while capital is {s['K_pct']:+.1f} percent at "
        f"year {s['t']}. After year 20 OG-Core's closure rule brings debt "
        "back to its target, and capital ends the path "
        f"{s['K_pct_long_run']:+.1f} percent from baseline. Most of the "
        "capital gain along the transition is therefore a consequence of "
        "using the proceeds to pay down debt, as OG-Core's fiscal closure "
        "does."
    )


# npv_table row labels of variables that are not money (left in model units).
NON_MONETARY = ("Labor",)


def npv_in_gdp_terms(table, base, gdp_yen_tn=None):
    """
    Restate an ``ogcore.output_tables.npv_table`` result (model units)
    relative to the baseline's first-year GDP, and in trillion yen at
    Japan's actual GDP.

    The model's currency anchor (mean salary) is not the same concept as
    income per model person, so yen figures computed with the model's
    ``factor`` would not be economy-wide totals. Dividing by first-year
    model GDP gives a unit-free share, which is then scaled by Japan's
    measured nominal GDP.

    Args:
        table (pandas DataFrame): npv_table output; first column the
            variable label, other columns one per discount rate
        base (dict): baseline TPI_vars
        gdp_yen_tn (float): nominal GDP in trillion yen; defaults to FY2023
            (Cabinet Office national accounts, ogjpn.wealth)

    Returns:
        (pandas DataFrame): same layout, each cell "x.x% of GDP (¥y tn)"
    """
    from ogjpn import wealth

    gdp = wealth.SNA_FY2023_NOMINAL_GDP if gdp_yen_tn is None else gdp_yen_tn
    y0 = path(base, "Y")[0]
    out = table.copy()
    # Labor is in model hours, not currency, so it is not converted.
    monetary = ~out.iloc[:, 0].astype(str).str.startswith(NON_MONETARY)
    for col in out.columns[1:]:
        vals = out[col].astype(float)
        out[col] = [
            f"{100 * v / y0:.1f}% of GDP (¥{v / y0 * gdp:.0f} tn)"
            if is_money
            else f"{v:.3g} (model units)"
            for v, is_money in zip(vals, monetary)
        ]
    return out
