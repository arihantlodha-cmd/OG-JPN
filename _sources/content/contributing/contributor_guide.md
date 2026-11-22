(Chap_ContribGuide)=
# Contributor guide

Contributions are welcome, from fixing a typo to replacing a first-pass part of the calibration with better Japanese data. The {ref}`Chap_Roadmap` lists the open items.

(Sec_GitHubIssue)=
## Opening an issue

Open a GitHub [issue](https://github.com/arihantlodha-cmd/OG-JPN/issues) to report a bug, question a calibration choice, or point to a better data source. For a data source, include the publisher, table or series name, year, and URL.

(Sec_GitHubPR)=
## Submitting a pull request

1. Fork the repository and create a branch from `main`.
2. Install the development dependencies: `uv sync --extra dev` (or `pip install -e ".[dev]"`).
3. Make the change. Every calibrated number needs a source: put the publisher, series, and year in a comment next to it, as the existing modules do.
4. Run the checks locally:
   ```
   make lint     # ruff format --check and ruff check
   make test     # pytest
   ```
5. If the change affects model results, rerun the affected example scripts and update the result pages in `docs/`.
6. Open a pull request describing what changed and why.

## Calibration principles

* **Source every number.** Calibrated values come from published Japanese or international statistics. Documented placeholders are acceptable while clearly labeled; unlabeled guesses are not.
* **Don't tune to hit targets.** If a moment misses (for example `C/Y`), work out why before changing a parameter. {ref}`Chap_Validation` explains why the capital-output ratio is not a free parameter.
* **Report what does not work.** Limitations stay in the documentation until they are fixed.

## Upstream contributions

Problems that belong in OG-Core itself should be fixed there. OG-JPN's work so far has produced several upstream changes; see {ref}`Chap_Roadmap`.
