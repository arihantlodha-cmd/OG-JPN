# Common development tasks for OG-JPN. Requires uv (https://docs.astral.sh/uv/).
# USAGE: make [TARGET]

.PHONY: help install test lint format documentation clean
help:
	@echo "install       : create .venv and install ogjpn with dev deps"
	@echo "test          : run the test suite"
	@echo "lint          : check formatting and lint with ruff (no changes)"
	@echo "format        : format with ruff and auto-fix lint"
	@echo "documentation : build the Jupyter Book documentation"
	@echo "clean         : remove caches and build outputs"

install:
	uv sync --extra dev

test:
	uv run python -m pytest --cov=ogjpn --cov-report=xml

lint:
	uv run ruff format --check .
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check . --fix

documentation:
	cd docs/book && uv run jupyter-book build .

clean:
	@find . -name '__pycache__' -type d -exec rm -r {} +
	@rm -rf .pytest_cache .ruff_cache build dist *.egg-info docs/book/_build coverage.xml
