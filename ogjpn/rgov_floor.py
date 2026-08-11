"""
Remove OG-Core's zero floor on the sovereign real rate.

``ogcore.fiscal.get_r_gov`` wraps the sovereign wedge in ``np.maximum(..., 0.00)``:

    r_gov = np.maximum(r_gov_scale*r - r_gov_shift + r_gov_DY*DY + r_gov_DY2*DY**2, 0.00)

For most countries that is harmless. For Japan it silently deletes the single
most important fact about the public finances. Japan's general government pays
net interest of roughly 0.43% of GDP on net debt of 114.8% -- about 0.375%
nominal, or **-0.6% real** against realised inflation. The wedge as calibrated
returns exactly that: 0.25*0.04391 - 0.017 = -0.6023%. The floor then discards
it and reports 0.0000.

WHY IT MATTERS, in one line: the debt-stabilising primary balance is
``pb* = (r_gov - g)/(1 + g) * D/Y``, so clipping r_gov from -0.60% to 0.00%
raises the primary balance Japan must run by **0.68 percentage points of GDP**.
That is the difference between a model whose fiscal stance matches Japan's and
one that demands a primary surplus Japan has never run -- which is precisely
what ``macro_params`` says this calibration exists to avoid.

IS IT SAFE? Yes, and this was checked against the source rather than assumed.
``r_gov`` enters the model **linearly everywhere** -- there is no division by
it, no power of it, no log or sqrt of it anywhere in ogcore. It has exactly two
consumers:

    debt_service = r_gov * D                        (fiscal.get_D_ss / get_D_t)
    r_p = (r_gov*D + r_K*K) / (D + K)               (aggregates.get_r_p)

Both are linear, and the r_p denominator ``D + K`` is strictly positive. A
negative r_gov simply means the government is a net receiver on its debt
position, and the household portfolio return blends a negative debt leg with a
positive capital leg.

WHAT IT COSTS. The household Euler pins the PORTFOLIO return r_p, so
``r = [r_p*(K+D) - r_gov*D] / K``: a more negative r_gov forces the capital leg
to pay MORE to keep the blend where preferences want it. Higher r means lower
K/Y. So this trade buys a correct fiscal stance at the price of a slightly worse
capital-output ratio. Both effects are reported rather than hidden.

This is a monkeypatch of a third-party library and should not be permanent. The
proper fix is upstream -- see ``docs/UPSTREAM_OGCORE.md``. Enable it explicitly;
it is never on by default.
"""

import numpy as np

from ogcore import fiscal

_original = None


def enable():
    """Patch out the zero floor. Returns True if newly applied."""
    global _original
    if _original is not None:
        return False
    _original = fiscal.get_r_gov

    def get_r_gov_unfloored(r, DY_ratio, p, method, t=None):
        if method == "scalar":
            return (
                p.r_gov_scale[t] * r
                - p.r_gov_shift[t]
                + p.r_gov_DY * DY_ratio
                + p.r_gov_DY2 * DY_ratio**2
            )
        return (
            p.r_gov_scale[: p.T] * r[: p.T]
            - p.r_gov_shift[: p.T]
            + p.r_gov_DY * DY_ratio[: p.T]
            + p.r_gov_DY2 * DY_ratio[: p.T] ** 2
        )

    fiscal.get_r_gov = get_r_gov_unfloored
    print("r_gov zero floor REMOVED (ogjpn/rgov_floor.py)")
    return True


def disable():
    """Restore ogcore's floored version."""
    global _original
    if _original is None:
        return False
    fiscal.get_r_gov = _original
    _original = None
    return True
