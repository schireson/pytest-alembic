.PHONY: install build test lint format publish
.DEFAULT_GOAL := test

install:
	poetry install

build:
	poetry build

test:
	COVERAGE_PROCESS_START="$(PWD)/pyproject.toml" \
	coverage run -m py.test src tests -vv
	coverage combine
	coverage report -i
	coverage xml

lint:
	flake8 src tests
	isort --check-only --recursive src tests
	pydocstyle src tests
	black --check src tests
	mypy src tests
	bandit -r src

format:
	isort --recursive src tests
	black src tests

publish: build
	poetry publish -u __token__ -p '${PYPI_PASSWORD}' --no-interaction
