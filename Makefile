.PHONY: install build test lint format publish
.DEFAULT_GOAL := test

install:
	poetry install

build:
	poetry build

test:
	COVERAGE_PROCESS_START="$(PWD)/pyproject.toml" \
	coverage run -m pytest src tests -vv
	coverage combine
	coverage report -i
	coverage xml

lint:
	ruff src tests || exit 1
	black --check src tests || exit 1
	mypy src tests || exit 1

format:
	ruff --fix src tests
	black src tests

publish: build
	poetry publish -u __token__ -p '${PYPI_TOKEN}' --no-interaction

changelog:
	# https://convco.github.io/
	convco changelog > CHANGELOG.md
