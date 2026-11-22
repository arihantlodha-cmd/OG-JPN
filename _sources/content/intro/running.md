(Chap_Running)=
# Installing and running OG-JPN

## Installation

`OG-JPN` needs Python 3.12 or 3.13 and [`OG-Core`](https://pypi.org/project/ogcore/) 0.24.6 or later.

With [`uv`](https://docs.astral.sh/uv/):

```
git clone https://github.com/arihantlodha-cmd/OG-JPN.git
cd OG-JPN
uv sync --extra dev
```

Or with `pip`:

```
git clone https://github.com/arihantlodha-cmd/OG-JPN.git
cd OG-JPN
pip install -e ".[dev]"
```

## Demographic data

Japan's fertility, mortality, and population come from the UN World Population Prospects (country code 392). No setup is needed: Japan is in OG-Core's offline data mirror, [EAPD-DRB/Population-Data](https://github.com/EAPD-DRB/Population-Data), so the model runs without a UN API token. A free [UN Data Portal](https://population.un.org/dataportal/about/dataapi) token, saved as `~/.config/og/un_api_token.txt`, makes OG-Core pull the live data instead.

## Running the model

| Command | What it does | Time (Apple-silicon laptop) |
|---|---|---|
| `python examples/run_ogjpn_ss.py` | solve and validate the steady state | ~10 seconds |
| `python examples/run_ogjpn_tpi.py` | solve the baseline transition path | ~4-6 minutes |
| `python examples/analysis_consumption_tax.py` | consumption-tax reform, steady state | under a minute |
| `python examples/analysis_consumption_tax_tpi.py` | consumption-tax reform, transition | ~15-25 minutes |
| `python -m pytest tests/` | calibration tests (no network, no solve) | seconds |

The pension-age (`analysis_retirement_age*.py`) and replacement-rate (`analysis_replacement_rate*.py`) reforms follow the same pattern.

`run_ogjpn_tpi.py` takes `--initial-wealth data` (the default: Japan's observed wealth-by-age profile, see {ref}`Chap_Wealth`) or `--initial-wealth ss` (OG-Core's steady-state proxy).

Transition-path runs use [Dask](https://www.dask.org/) for parallel computation and are memory hungry. On a laptop, run them one at a time.

## Using the calibration in your own scripts

```python
from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogjpn.calibrate import Calibration
from ogjpn.constants import START_YEAR

p = Specifications(baseline=True)
p.update_specifications({"start_year": START_YEAR})
p.update_specifications(Calibration(p).get_dict())
p.baseline_dir = p.output_base = "./OUTPUT_BASELINE"
runner(p, time_path=False)
```
