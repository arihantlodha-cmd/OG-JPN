"""
Warm-start the steady-state solve from a previously solved state.

WHY THIS EXISTS
---------------
OG-Core cold-starts every steady-state solve from constants: household savings
at a hardcoded 0.07 for every age and income group, labour at 0.35, and the
bequest guesses derived from those. For Japan that is catastrophic rather than
merely imprecise:

  * the bequest seed lands **134x too low** in aggregate and 349x too low for
    the top income group (Japan's households are old and wealthy: solved
    population-weighted savings are ~6.1 against the hardcoded 0.07);
  * domestic capital `K_d = B - D_d` therefore starts deeply NEGATIVE, since
    household wealth is seeded near zero while domestically-held government
    debt is ~0.86 of GDP. `SS_fsolve` clamps that and substitutes 1e9
    residuals, which destroys the finite-difference Jacobian the default `hybr`
    root-finder depends on; and
  * `initial_guess_factor_SS` is validated to a maximum of 500,000, while
    Japan's factor is ~7.0 million — so the correct seed cannot even be entered
    as a parameter.

The observable consequence is that `run_SS` fails and silently restarts down
its 39-rung `DEV_FACTOR_LIST` retry ladder. What looks like "hundreds of slow
iterations" is really several failed solves stacked end to end.

WHAT THIS DOES
--------------
Seeds the solver from a state that has already solved — the household matrices
AND every outer unknown together, so they are mutually consistent — and passes
`factor` directly, sidestepping the validator cap.

Measured effect on this calibration, same parameters, same 7-worker client:

    cold start   >175 evaluations, several restarts, no convergence
    warm start     22 evaluations, no restarts, residual 5.5e-11, 4.8 min

`b` and `n` are in MODEL units, so a seed stays valid across changes to the
currency scale, the demographic window and modest parameter moves. Regenerate it
with ``python examples/save_warm_start.py`` after any large recalibration.

This is a workaround for an upstream defect, not a modelling choice — see
``docs/UPSTREAM_OGCORE.md``. The proper fix is for OG-Core to derive its seeds
rather than hardcode them, and to accept a warm start.
"""

import os
import pickle

import numpy as np

import ogcore.SS as SS
from ogcore import firm

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
SEED_PATH = os.path.join(CUR_PATH, "data", "ss_warm_start.pkl")


def save_seed(ss_vars, path=SEED_PATH):
    """
    Store the parts of a solved steady state needed to warm-start another.

    Args:
        ss_vars (dict): a solved ``SS_vars.pkl``
        path (str): where to write the seed
    """
    scalar = lambda x: float(np.asarray(x).sum()) if np.ndim(x) else float(x)
    seed = {
        "b": np.asarray(ss_vars["b_sp1"], dtype=float),
        "n": np.asarray(ss_vars["n"], dtype=float),
        "r": scalar(ss_vars["r"]),
        "r_p": scalar(ss_vars["r_p"]),
        "TR": scalar(ss_vars["TR"]),
        "factor": scalar(ss_vars["factor"]),
        "BQ": np.asarray(ss_vars["BQ"], dtype=float).ravel(),
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        pickle.dump(seed, fh)
    return path


def enable(path=SEED_PATH):
    """
    Patch ``SS.SS_initial_guesses`` to start from the stored seed.

    Call once before solving. Silently does nothing if no seed is stored, so a
    fresh checkout still runs (slowly) rather than failing.

    Args:
        path (str): seed written by :func:`save_seed`

    Returns:
        bool: True if a warm start is now active
    """
    if not os.path.exists(path):
        return False
    with open(path, "rb") as fh:
        seed = pickle.load(fh)

    original = SS.SS_initial_guesses

    def warm(p, b_val=0.0055, n_val=0.4, r_tr_scalars=[1.0, 1.0]):
        if seed["b"].shape != (p.S, p.J):
            # Seed built for different model dimensions; fall back rather than
            # hand the solver a wrongly-shaped guess.
            return original(p, b_val, n_val, r_tr_scalars)

        # Scale by the retry-ladder factors so ogcore's DEV_FACTOR_LIST can
        # still explore around the warm point if the first attempt fails.
        r_g = r_tr_scalars[0] * seed["r"]
        r_p_g = r_tr_scalars[0] * seed["r_p"]
        TR_g = r_tr_scalars[1] * seed["TR"]
        Y_g = TR_g / p.alpha_T[-1]
        BQ_g = seed["BQ"] * r_tr_scalars[1]
        w_g = firm.get_w_from_r(r_g, p, "SS")

        guesses = ([r_p_g, r_g, w_g] + list(np.ones(p.M)) + [Y_g]
                   + list(BQ_g) + [TR_g])
        if p.baseline:
            # Passed directly: as a parameter this exceeds ogcore's 500,000 cap.
            guesses = guesses + [seed["factor"]]
        return guesses, seed["b"].copy(), seed["n"].copy()

    SS.SS_initial_guesses = warm
    return True
