.PHONY: install build test lint format publish audit audit-all
.DEFAULT_GOAL := test

install:
	uv sync

build:
	uv build

test:
	SQLALCHEMY_WARN_20=1 COVERAGE_PROCESS_START="$(PWD)/pyproject.toml" \
	uv run coverage run -m pytest src tests -vv
	uv run coverage combine
	uv run coverage report -i
	uv run coverage xml

lint:
	uv run ruff check src tests examples || exit 1
	uv run ruff format --check src tests examples || exit 1
	uv run mypy src tests || exit 1

format:
	uv run ruff check --fix src tests examples
	uv run ruff format src tests examples

audit:  ## Audit runtime dependencies for known vulnerabilities
	uv export --frozen --no-emit-project --no-dev --no-hashes --format requirements-txt \
		| uvx pip-audit --no-deps -r /dev/stdin

audit-all:  ## Audit every dependency group, including dev and docs
	uv export --frozen --no-emit-project --all-groups --no-hashes --format requirements-txt \
		| uvx pip-audit --no-deps -r /dev/stdin

publish: build
	uv publish --token '${PYPI_TOKEN}'

changelog:
	# https://convco.github.io/
	convco changelog > CHANGELOG.md
