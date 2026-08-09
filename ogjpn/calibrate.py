"""
OG-Japan (OG-JPN) calibration.

The Calibration class assembles the country-specific pieces (macro
parameters, tax parameters, and demographics) into a single dict that can
be handed to an OG-Core Specifications object via
``update_specifications``. This mirrors the Calibration classes in the
other country models (OG-USA, OG-THA, OG-BRA).

Phase status:
  - macro parameters: provisional first pass (ogjpn.macro_params)
  - tax parameters: consumption tax set; income/payroll deferred
    (ogjpn.tax_params)
  - demographics: live UN data by country code 392, requires a UN API
    token (see README); optional so the pipeline still runs without it
"""

from ogcore import demographics
from ogjpn import macro_params, tax_params
from ogjpn.constants import UN_COUNTRY_CODE

# get_pop_objs returns diagnostic keys that are not model parameters;
# keep only the demographic keys that update_specifications accepts.
_DEMOGRAPHIC_KEYS = (
    "omega",
    "g_n_ss",
    "omega_SS",
    "surv_rate",
    "rho",
    "g_n",
    "imm_rates",
    "omega_S_preTP",
)


class Calibration:
    """OG-Japan calibration built on top of an OG-Core Specifications."""

    def __init__(self, p, use_demographics=True, demographic_data_path=None):
        """
        Args:
            p (ogcore Specifications): model parameters (supplies the E,
                S, T, and start_year dimensions)
            use_demographics (bool): whether to pull live Japan
                demographics (needs a UN API token); if False, only the
                macro and tax blocks are calibrated
            demographic_data_path (str): optional path to cache the
                downloaded demographic data
        """
        self.macro_params = macro_params.get_macro_params()
        self.tax_params = tax_params.get_tax_params()

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
                GraphDiag=False,
                download_path=demographic_data_path,
            )

    def get_dict(self):
        """
        Return the calibrated parameters as a dict for
        ``Specifications.update_specifications``.
        """
        calibrated = {}
        calibrated.update(self.macro_params)
        calibrated.update(self.tax_params)
        if self.demographic_params is not None:
            for key in _DEMOGRAPHIC_KEYS:
                if key in self.demographic_params:
                    calibrated[key] = self.demographic_params[key]
        return calibrated
