# Changelog

## 0.13

### 0.13.0 (Unreleased)

- breaking: drop Python 3.9, minimum now 3.10
- feat: add type hints to exposed tests
- fix: commit async migrations via `engine.begin()`, not `connection.commit()`
- fix: spawn `sys.executable` for the collection subprocess, not PATH's python
- fix: incorrect execution of the min revision downgrade in "leaves-no-trace" test
- fix: honour the `default` argument of `collect_test_definitions`
- fix: readthedocs build

## 0.12

### 0.12.1

- fix: handle pyproject.toml based alembic config

### 0.12.0

- fix: ensure branched revisions are upgraded individually once
- fix: bump minimum Python version on package to 3.7

## 0.11

### 0.11.1

- fix: ensure branched revisions are upgraded individually once

### 0.11.0

- fix: fixture definition incompatibility with pytest 8.x

## 0.10

### 0.10.7

- fix: add testing for SQLAlchemy 2.0 compatibility

### 0.10.6

- fix: issue with runtime `version_table_schema` option

### 0.10.4

- fix: over-eager CLI option default for `--alembic-tests-path`

### 0.10.2

- fix: ensure parity of behavior between testing with/without `--test-alembic`
- fix: remove dangling references to `pytest_alembic_tests_folder`

### 0.10.1

- fix: add option to configure the default test registration path

### 0.10.0

- feat: add config option to skip specific sets of revisions

## 0.9

### 0.9.1

- fix: refresh alembic history to make tests aware of newly generated revisions

### 0.9.0

- fix: compatibility with newer versions of pytest and pytest-asyncio

## 0.8

### 0.8.4

- fix: correctly insert the root package during metadata detection

### 0.8.2

- fix: add missing `connection` param to `table_at_revision`
- fix: improve test options for `all_models_register_on_metadata`

### 0.8.1

- fix: add missing explicit re-exports

### 0.8.0

- fix: avoid the high-level alembic command interface in most cases (large speed improvement)

## 0.7

### 0.7.0

- breaking: drop Python 3.6
- feat: enable in-test insertion of data in async contexts
- fix: asynchronous engine tests which perform transaction manipulation

## 0.6

### 0.6.1

- fix: add missing alembic Config options

### 0.6.0

- feat: add ability to set a minimum bound downgrade migration
- feat: add test asserting parity between upgrade and downgrade detectable effects
- feat: add test for roundtrip downgrade isolation

## 0.5

### 0.5.1

- fix: increase minimum Python version to 3.6+
- fix: incompatibility of branched history downgrade strategy with alembic 1.6+
- fix: ensure the up-down consistency test actually verifies migrations

### 0.5.0

- feat: add experimental test to identify tables alembic will not recognize

## 0.4

### 0.4.0

- feat: create a mechanism for multiple alembic runner fixtures
- feat: allow alembic `Config` to be used directly in `alembic_config` fixture

## 0.3

### 0.3.0

- (no user-facing changes recorded)

## 0.2

### 0.2.5

- feat: allow customization of the location at which built-in tests are executed

### 0.2.4

- fix: require `dataclasses` only below 3.7 (included in stdlib from 3.7 onward)

### 0.2.3

- feat: reduce multiple pages of traceback output to a few lines of meaningful context

### 0.2.2

- feat: add rendered migration body to failed model-sync test

### 0.2.1

- fix: fix deprecation pytest warning in 3.4

## 0.1

### 0.1.0

- Initial release
