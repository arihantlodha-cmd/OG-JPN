(Chap_Intro)=
# OG-JPN

| | |
| --- | --- |
| Org | [![OG-Core](https://img.shields.io/badge/built%20on-OG--Core-1f6feb)](https://pslmodels.github.io/OG-Core/) [![OS License: CC0-1.0](https://img.shields.io/badge/OS%20License-CC0%201.0-yellow)](https://github.com/arihantlodha-cmd/OG-JPN/blob/main/LICENSE) [![Jupyter Book Badge](https://raw.githubusercontent.com/jupyter-book/jupyter-book/next/docs/media/images/badge.svg)](https://arihantlodha-cmd.github.io/OG-JPN/) |
| Package | [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/) [![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/) [![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff) |
| Testing | ![Build and test](https://github.com/arihantlodha-cmd/OG-JPN/actions/workflows/build_and_test.yml/badge.svg?branch=main) ![Docs](https://github.com/arihantlodha-cmd/OG-JPN/actions/workflows/deploy_docs.yml/badge.svg?branch=main) ![Ruff](https://github.com/arihantlodha-cmd/OG-JPN/actions/workflows/check_ruff.yml/badge.svg?branch=main) |

[`OG-JPN`](https://github.com/arihantlodha-cmd/OG-JPN) is a package that provides the code and data to calibrate an overlapping-generations (OG) model to the economy of Japan. It uses [`OG-Core`](https://pslmodels.github.io/OG-Core/) as a dependency, which contains the core theory, logic, and solution methods of a general OG model. `OG-JPN` supplies the country-specific layer: Japan's demographics, macro and fiscal parameters, a progressive income tax fitted to administrative tax data, Japan's two-tier public pension in yen, and the initial distribution of household wealth. Together they make a dynamic general equilibrium model of fiscal policy in Japan, in the same family as [`OG-USA`](https://github.com/PSLmodels/OG-USA), [`OG-UK`](https://github.com/PSLmodels/OG-UK), and [`OG-ZAF`](https://github.com/EAPD-DRB/OG-ZAF). To our knowledge it is the first open-source OG model of Japan.

Japan is an unusually important case for this class of model. It has the oldest population of any large economy and gross public debt of about 215 percent of GDP, beyond the range OG-Core's default parameters anticipate. Those are exactly the fiscal-demographic dynamics overlapping-generations models are built to study.

```{figure} ../../../japan_aging.png
:name: FigJapanAging
:width: 90%

Japan's population by age, 1990 and 2030 (UN World Population Prospects).
```

Fed Japan's demographics, its two-tier pension formula, and its tax data, the model's public pension outlays in its first year are 10.1 percent of GDP, against 10.4 percent in Japan, and they rise by about two points over the next two decades. See {ref}`Chap_Validation` for what matches, what does not yet, and why.

This documentation contains the following sections:

* **Getting started**: installing and running the model, and contributing.
* **Calibration**: where each part of the Japan calibration comes from.
* **Policy results**: three fiscal reforms Japan is debating, each solved in the long run and on the transition path.
* **Reference**: the Python API, the roadmap, and data sources.


(Sec_CoreMaintainers)=
## Core maintainer

Ari Lodha (GitHub handle [@arihantlodha-cmd](https://github.com/arihantlodha-cmd)) is the core maintainer of `OG-JPN`. Questions, bug reports, and contributions are welcome as GitHub [issues](https://github.com/arihantlodha-cmd/OG-JPN/issues) and [pull requests](https://github.com/arihantlodha-cmd/OG-JPN/pulls); see {ref}`Chap_ContribGuide`.


(Sec_Disclaimer)=
## Disclaimer

The model is under continuous development and its components can change. Parts of the calibration are first-pass and are labeled as such throughout these pages; read results for their direction and rough size rather than their last digit. Changes are recorded in the [commit history](https://github.com/arihantlodha-cmd/OG-JPN/commits/main) and in closed pull requests.


(Sec_Citing)=
## Citing OG-JPN

OG-JPN (Version #.#.#)[Source code], https://github.com/arihantlodha-cmd/OG-JPN
