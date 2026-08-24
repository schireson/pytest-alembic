.PHONY: help install build test lint format publish changelog
.DEFAULT_GOAL := test

help:  ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package and its dev dependencies
	uv sync

build:  ## Build the sdist and wheel
	uv build

test:  ## Run the test suite with coverage reports
	SQLALCHEMY_WARN_20=1 COVERAGE_PROCESS_START="$(PWD)/pyproject.toml" \
	uv run coverage run -m pytest src tests -vv
	uv run coverage combine
	uv run coverage report -i
	uv run coverage xml

lint:  ## Check lint, formatting and types (ruff, mypy)
	uv run ruff check src tests examples || exit 1
	uv run ruff format --check src tests examples || exit 1
	uv run mypy src tests || exit 1

format:  ## Apply ruff fixes and formatting in place
	uv run ruff check --fix src tests examples
	uv run ruff format src tests examples

publish: build  ## Build and publish to PyPI
	uv publish --token '${PYPI_TOKEN}'

changelog:  ## Regenerate CHANGELOG.md via convco
	# https://convco.github.io/
	convco changelog > CHANGELOG.md
