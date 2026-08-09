"""
OG-Japan (OG-JPN) calibration.

Phase 0 scope: pull Japan's demographic parameters from the UN World
Population Prospects data (via OG-Core's demographics module, country
code 392) and hand them to an OG-Core Specifications object. Macro,
earnings, and tax calibration are OG-Core defaults for now; they are the
subject of Phases 1 and 2 (see README).
"""

from ogcore import demographics
from ogjpn.constants import UN_COUNTRY_CODE


class Calibration:
    """OG-Japan calibration built on top of an OG-Core Specifications."""

    def __init__(self, p, demographic_data_path=None):
        """
        Args:
            p (ogcore Specifications): model parameters (used for the E,
                S, T, and start_year dimensions)
            demographic_data_path (str): optional path to cache the
                downloaded demographic data
        """
        # Japan demographics from the UN WPP data (country code 392).
        # Requires a UN API token (see README); without one, OG-Core's
        # offline mirror does not currently include Japan.
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
        Return the calibrated parameters as a dict suitable for
        ``Specifications.update_specifications``. Only the demographic
        block is populated in Phase 0.
        """
        calibrated = {}
        # get_pop_objs returns several diagnostic keys that are not model
        # parameters; keep only the ones update_specifications accepts.
        demog_keys = [
            "omega",
            "g_n_ss",
            "omega_SS",
            "surv_rate",
            "rho",
            "g_n",
            "imm_rates",
            "omega_S_preTP",
        ]
        for k in demog_keys:
            if k in self.demographic_params:
                calibrated[k] = self.demographic_params[k]
        return calibrated
