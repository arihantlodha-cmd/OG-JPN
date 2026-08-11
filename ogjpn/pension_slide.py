"""
Make ``replacement_rate_adjust`` work under the Defined Benefits pension system.

WHAT IS BROKEN. OG-Core's ``replacement_rate_adjust`` is a (T+S, J) multiplier on
the pension replacement rate -- exactly the right shape for a legislated benefit
glide. But it is read in **one** place, ``pensions.SS_amount()``, which serves
only ``pension_system = "US-Style Social Security"``. ``DB_amount()``,
``NDC_amount()`` and ``PS_amount()`` never reference it. Set it under any of
those three and it silently does nothing -- the same failure class as
``alpha_db`` defaulting to 0.0, where a parameter that looks calibrated has no
effect under the system you chose.

Verified against the source: ``grep replacement_rate_adjust`` in
``ogcore/pensions.py`` returns six hits, all inside ``SS_amount``; zero inside
``DB_amount``.

WHY JAPAN NEEDS IT. Japan does not hold its replacement rate fixed as it ages --
the *macroeconomic slide* automatically cuts benefits to keep the system solvent.
The MHLW 2024 actuarial review (low-growth case) projects the income replacement
rate falling from 61.2% in FY2024 to 50.4% in FY2057, a factor of 0.8235. Without
a working adjustment, OG-Core's DB block pays a fixed replacement rate and the
pension bill rises mechanically with the old-age ratio to 12.6% of GDP -- a
policy Japan does not have. With it, the model can match today's 9.3% AND carry
the legislated glide, instead of being forced to choose one end or the other.

HOW. Wrap ``pensions.pension_amount``, which (unlike the per-system helpers) is
handed both ``t`` and ``method``, and scale whatever the underlying system
returns. The steady state takes the terminal value, matching how ``SS_amount``
itself reads ``[-1]``.

This is a monkeypatch of a third-party library. The proper fix is upstream --
move the adjustment out of ``SS_amount`` into ``pension_amount`` so every system
honours it. See ``docs/UPSTREAM_OGCORE.md``. Enable it explicitly.
"""

import numpy as np

from ogcore import pensions

_original = None


def enable():
    """Apply replacement_rate_adjust to non-US pension systems. True if newly applied."""
    global _original
    if _original is not None:
        return False
    _original = pensions.pension_amount

    def pension_amount_adjusted(
        r, w, n, Y, theta, t, j, shift, method, e, factor, p
    ):
        pension = _original(r, w, n, Y, theta, t, j, shift, method, e, factor, p)
        if p.pension_system == "US-Style Social Security":
            return pension  # already applied inside SS_amount

        adj = np.asarray(p.replacement_rate_adjust)
        if method == "SS":
            # terminal value, matching how SS_amount reads it
            scale = adj[-1, :] if j is None else adj[-1, j]
        else:
            idx = min(int(t), adj.shape[0] - 1)
            scale = adj[idx, :] if j is None else adj[idx, j]

        pension = np.asarray(pension)
        if np.ndim(scale) and pension.ndim and pension.shape[-1] == np.size(scale):
            return pension * scale
        return pension * np.asarray(scale).item() if np.size(scale) == 1 else pension * scale

    pensions.pension_amount = pension_amount_adjusted
    print("replacement_rate_adjust now applied to DB pensions (ogjpn/pension_slide.py)")
    return True


def disable():
    """Restore ogcore's version."""
    global _original
    if _original is None:
        return False
    pensions.pension_amount = _original
    _original = None
    return True
