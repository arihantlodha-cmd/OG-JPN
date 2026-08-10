"""
OG-Japan (OG-JPN) calibration.

The Calibration class assembles the country-specific pieces into a single dict
that can be handed to an OG-Core Specifications object via
``update_specifications``. This mirrors the Calibration classes in the other
country models (OG-USA, OG-THA, OG-BRA).

A country model is a thin layer on top of OG-Core, and the thing that makes it a
*country* model is how much of OG-Core's parameter surface it actually
overrides. Anything not set here silently keeps OG-Core's United States value,
so each block below states what it covers.

Blocks:
  - macro parameters   (ogjpn.macro_params)  growth, capital share, debt, the
                       sovereign rate wedge, openness, spending shares
  - tax parameters     (ogjpn.tax_params)    payroll, consumption, corporate,
                       property, bequest, and a progressive income tax
  - pension parameters (ogjpn.pension_params) a defined-benefit system and the
                       yen income anchor
  - demographics       live UN data by country code 392

Still on OG-Core's US defaults, and documented as such rather than presented as
calibrated:
  - ``chi_n``, the disutility-of-labour profile. This is the family-wide norm --
    no country repo has recalibrated it -- but it must be described as borrowed,
    never as calibrated.
  - the ``e`` earnings-ability matrix, which has no Japan tilt yet. The family
    method is a single-scalar exponential tilt on OG-USA's matrix solved so the
    model Gini matches the country's. See docs/CALIBRATION_AUDIT.md.
"""

import numpy as np

from ogcore import demographics
from ogjpn import macro_params, pension_params, tax_params
from ogjpn.constants import UN_COUNTRY_CODE


class Calibration:
    """OG-Japan calibration built on top of an OG-Core Specifications."""

    def __init__(self, p, use_demographics=True, demographic_data_path=None):
        """
        Args:
            p (ogcore Specifications): model parameters (supplies the E,
                S, T, and start_year dimensions)
            use_demographics (bool): whether to pull live Japan
                demographics (needs a UN API token); if False, only the
                macro, tax, and pension blocks are calibrated
            demographic_data_path (str): optional path to cache the
                downloaded demographic data
        """
        self.macro_params = macro_params.get_macro_params()
        self.tax_params = tax_params.get_tax_params()
        self.pension_params = pension_params.get_pension_params()

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
        Return the calibrated parameters as a dict for
        ``Specifications.update_specifications``.
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
