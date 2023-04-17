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
	flake8 src tests || exit 1
	isort --check-only src tests || exit 1
	pydocstyle src tests || exit 1
	black --check src tests || exit 1
	mypy src tests || exit 1
	bandit -r src --skip B101 || exit 11

format:
	isort src tests
	black src tests

publish: build
	poetry publish -u __token__ -p '${PYPI_PASSWORD}' --no-interaction

changelog:
	# https://convco.github.io/
	convco changelog > CHANGELOG.md
