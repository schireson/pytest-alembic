.PHONY: install build test lint format deps docs docs-coverage audit audit-all publish changelog
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

deps:  ## Check dependency hygiene (deptry)
	# No flags: every exception lives in [tool.deptry] in pyproject.toml, so a local
	# run and CI measure the same thing. `--group docs` so deptry can introspect the
	# docs packages too, rather than guessing their module names.
	uv run --group docs deptry src

docs:  ## Build the HTML documentation (sphinx)
	# `--group docs` because `make install` runs a bare `uv sync`, which does not
	# include that group. `-W` holds the build at zero warnings: a broken
	# cross-reference or an unlexable code block fails here rather than quietly
	# degrading a rendered page on readthedocs after the merge.
	uv run --group docs sphinx-build -W -b html docs/source docs/build/html

docs-coverage:  ## Check docstring coverage (interrogate)
	# No flags: every threshold and exclusion lives in [tool.interrogate] in
	# pyproject.toml, so a local run and CI measure the same thing.
	uv run interrogate

audit:  ## Audit runtime dependencies for known vulnerabilities
	uv export --frozen --no-emit-project --no-dev --no-hashes --format requirements-txt \
		| uvx pip-audit --no-deps -r /dev/stdin

audit-all:  ## Audit every dependency group, including dev and docs
	uv export --frozen --no-emit-project --all-groups --no-hashes --format requirements-txt \
		| uvx pip-audit --no-deps -r /dev/stdin

publish: build  ## Build and publish to PyPI
	uv publish --token '${PYPI_TOKEN}'

changelog:  ## Regenerate CHANGELOG.md via convco
	# https://convco.github.io/
	convco changelog > CHANGELOG.md
