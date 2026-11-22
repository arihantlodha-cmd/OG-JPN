"""
OG-Japan (OG-JPN) calibration.

The Calibration class assembles the country-specific pieces (macro
parameters, tax parameters, and demographics) into a single dict that can
be handed to an OG-Core Specifications object via
``update_specifications``. This mirrors the Calibration classes in the
other country models (OG-USA, OG-THA, OG-BRA).

Phase status:
  - macro parameters: provisional first pass (ogjpn.macro_params)
  - tax parameters: first-pass linear calibration of income, payroll,
    capital, corporate, and consumption taxes from published Japanese
    rates (ogjpn.tax_params)
  - demographics: live UN data by country code 392, requires a UN API
    token (see README); optional so the pipeline still runs without it
"""

import numpy as np
from ogcore import demographics

from ogjpn import macro_params, pension_params, tax_params
from ogjpn.constants import UN_COUNTRY_CODE

# Initial guess for OG-Core's model-to-currency factor when the model is
# anchored to yen: the steady-state factor is about 6.7 million yen per
# model unit. OG-Core validates initial_guess_factor_SS against a maximum
# of 500,000, set with dollar-anchored models in mind, and the steady state
# does not converge from a guess at that cap, so update_specs sets it
# directly on the Specifications object.
FACTOR_GUESS_JPY = 6.7e6
_DIRECT_KEYS = ("initial_guess_factor_SS",)


def update_specs(p, params):
    """
    Apply a calibration dict to an OG-Core Specifications object.

    Use this instead of ``p.update_specifications(params)``: it passes
    everything through OG-Core's validation except the keys that must be
    set directly (the yen-scale ``initial_guess_factor_SS``).

    Args:
        p (ogcore Specifications): model parameters, updated in place
        params (dict): parameters, e.g. ``Calibration(p).get_dict()``
    """
    params = dict(params)
    direct = {k: params.pop(k) for k in _DIRECT_KEYS if k in params}
    p.update_specifications(params)
    for key, value in direct.items():
        setattr(p, key, value)


class Calibration:
    """OG-Japan calibration built on top of an OG-Core Specifications."""

    def __init__(
        self,
        p,
        use_demographics=True,
        demographic_data_path=None,
        income_tax="progressive",
        pension="japan",
    ):
        """
        Args:
            p (ogcore Specifications): model parameters (supplies the E,
                S, T, and start_year dimensions)
            use_demographics (bool): whether to pull live Japan
                demographics (needs a UN API token); if False, only the
                macro and tax blocks are calibrated
            demographic_data_path (str): optional path to cache the
                downloaded demographic data
            income_tax (str): "progressive" (default; functions fitted to
                Japan's salary-bracket tax data) or "linear" (constant
                rates); see ogjpn.tax_params.get_tax_params
            pension (str): "japan" (default) for Japan's two-tier pension
                formula with the model anchored to yen
                (ogjpn.pension_params), or "us" for OG-Core's default US
                Social Security formula and dollar anchor
        """
        self.macro_params = macro_params.get_macro_params(income_tax, pension)
        self.pension_params = {}
        mean_income = float(p.mean_income_data)
        if pension == "japan":
            self.pension_params = pension_params.get_pension_params()
            mean_income = self.pension_params["mean_income_data"]
            self.pension_params["initial_guess_factor_SS"] = FACTOR_GUESS_JPY
        elif pension != "us":
            raise ValueError("pension must be 'japan' or 'us'")
        # The income-tax functions are scaled to the income anchor in use.
        self.tax_params = tax_params.get_tax_params(
            p.S, income_tax=income_tax, mean_income=mean_income
        )

        self.demographic_params = None
        if use_demographics:
            # Japan demographics from UN WPP data (country code 392).
            # Requires a UN API token; without one, OG-Core's offline
            # mirror does not currently include Japan.
            self.demographic_params = demographics.get_pop_objs(
                p.E,
                p.S,
                p.T,
                0,
                99,
                country_id=UN_COUNTRY_CODE,
                initial_data_year=p.start_year - 1,
                final_data_year=p.start_year + 1,
                # income group shares (lambdas) so the demographic arrays
                # come back J-wide and match the model's J income groups
                income_percentiles=np.asarray(p.lambdas).ravel(),
                GraphDiag=False,
                download_path=demographic_data_path,
            )

    def get_dict(self):
        """
        Return the calibrated parameters as a dict. Apply it with
        ``ogjpn.calibrate.update_specs(p, d)``, which also handles the
        parameters OG-Core's validation would reject.
        """
        calibrated = {}
        calibrated.update(self.macro_params)
        calibrated.update(self.tax_params)
        calibrated.update(self.pension_params)
        if self.demographic_params is not None:
            # get_pop_objs returns exactly the demographic parameters that
            # update_specifications accepts, so pass them all through.
            calibrated.update(self.demographic_params)
        return calibrated
