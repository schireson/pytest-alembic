# Changelog

### [v0.12.1](https://github.com/schireson/pytest-alembic/compare/v0.12.0...v0.12.1) (2025-05-22)

#### Fixes

* Handle pyproject.toml based alembic config.
([82d9d62](https://github.com/schireson/pytest-alembic/commit/82d9d62024ccb86b655272a70e0d94374b5675a5))

## [v0.12.0](https://github.com/schireson/pytest-alembic/compare/v0.11.1...v0.12.0) (2025-05-16)

### Fixes

* Release 0.12.0
([4baee1e](https://github.com/schireson/pytest-alembic/commit/4baee1e85abe3733e6aa785c7704248f4fbb59b0))
* Failing tests.
([1dc5b43](https://github.com/schireson/pytest-alembic/commit/1dc5b43d7e5b7530181808490cb31386631990a9))
* Linting.
([0c32cb2](https://github.com/schireson/pytest-alembic/commit/0c32cb23a32e711e633df3af9124f713b9bfa475))
* Bump minimum python version on package to 3.7, stop testing 3.7.
([32b8f62](https://github.com/schireson/pytest-alembic/commit/32b8f629f99efad07bcc2bd3ba4ff8981c399b13))
* Ensure branched revisions are upgraded individually once.
([853b116](https://github.com/schireson/pytest-alembic/commit/853b1164af9d03cb71504895c63e4962cc14ab84))
* Updated pyproject.toml to be more flexible with poetry_core versioning.
([c7f25c3](https://github.com/schireson/pytest-alembic/commit/c7f25c39a795591a794f1ab89203f4a992012319))

### [v0.11.1](https://github.com/schireson/pytest-alembic/compare/v0.11.0...v0.11.1) (2024-03-27)

#### Fixes

* Ensure branched revisions are upgraded individually once.
([25b03a3](https://github.com/schireson/pytest-alembic/commit/25b03a3cac04258bbf3725f00e4794663808581a))

## [v0.11.0](https://github.com/schireson/pytest-alembic/compare/v0.10.7...v0.11.0) (2024-03-04)

### Fixes

* fixture definition incompatibility with 8.x.x series pytest.
([637f28c](https://github.com/schireson/pytest-alembic/commit/637f28c6649c9e2fa139b8c766923b9d077f9353))

### [v0.10.7](https://github.com/schireson/pytest-alembic/compare/v0.10.6...v0.10.7) (2023-07-06)

#### Fixes

* Add testing for sqlalchemy 2.0 compatibility.
([6ef0f3c](https://github.com/schireson/pytest-alembic/commit/6ef0f3cf5c7f1d0d88453a6b28c4d77ea2f0dc60))

### [v0.10.6](https://github.com/schireson/pytest-alembic/compare/v0.10.5...v0.10.6) (2023-06-27)

#### Fixes

* Issue with runtime version_table_schema option.
([8e417a3](https://github.com/schireson/pytest-alembic/commit/8e417a3220234d16bad8661733faf0f5edd356c0))

### [v0.10.5](https://github.com/schireson/pytest-alembic/compare/v0.10.4...v0.10.5) (2023-05-23)

### [v0.10.4](https://github.com/schireson/pytest-alembic/compare/v0.10.2...v0.10.4) (2023-04-18)

#### Fixes

* Over-eager cli option default for alembic-tests-path.
([367fa50](https://github.com/schireson/pytest-alembic/commit/367fa501c705f462cc44ece4243258dd1c1b0289))

### [v0.10.2](https://github.com/schireson/pytest-alembic/compare/v0.10.1...v0.10.2) (2023-04-17)

#### Fixes

* Ensure parity of behavior between testing with/without `--test-alembic`.
([5f93d08](https://github.com/schireson/pytest-alembic/commit/5f93d081716b1252331a259d3feaf97feda4f8e5))
* Remove dangling references to pytest_alembic_tests_folder.
([ef11751](https://github.com/schireson/pytest-alembic/commit/ef117516e545da30d7fefc7665a71835d5cdc2ae))

### [v0.10.1](https://github.com/schireson/pytest-alembic/compare/v0.10.0...v0.10.1) (2023-02-21)

#### Fixes

* Add an option to configure the default test registration path.
([cc6076d](https://github.com/schireson/pytest-alembic/commit/cc6076d0834e6cef633e1cc69c47ee01823d1244))

## [v0.10.0](https://github.com/schireson/pytest-alembic/compare/v0.9.1...v0.10.0) (2023-02-03)

### Features

* Add config option to skip specific sets of revisions.
([0848c38](https://github.com/schireson/pytest-alembic/commit/0848c38674dcb3aab5740a77a8a0dcb9a7f57e4b))

### [v0.9.1](https://github.com/schireson/pytest-alembic/compare/v0.9.0...v0.9.1) (2022-11-01)

#### Fixes

* Refresh alembic history to enable tests generate new revisions to be aware
of those revisions.
([a255f81](https://github.com/schireson/pytest-alembic/commit/a255f81ba1bddf4be806c7ddc0558bfc45955b4b))

## [v0.9.0](https://github.com/schireson/pytest-alembic/compare/v0.8.4...v0.9.0) (2022-11-01)

### Fixes

* Compatibility with newer versions of pytest and pytest-asyncio.
([4ed809b](https://github.com/schireson/pytest-alembic/commit/4ed809b8b059091cbd55aa68d57d398c129a7d3f))

### [v0.8.4](https://github.com/schireson/pytest-alembic/compare/v0.8.3...v0.8.4) (2022-08-03)

#### Fixes

* Correctly insert the root package during metaadata detection.
([b89e604](https://github.com/schireson/pytest-alembic/commit/b89e604a15052c3e23a9a19049497b0040759a75))
* Correctly insert the root package during metaadata detection.
([d719608](https://github.com/schireson/pytest-alembic/commit/d71960884a6e47176d21e64e14d987bdc09715f0))

### [v0.8.3](https://github.com/schireson/pytest-alembic/compare/v0.8.2...v0.8.3) (2022-07-20)

### [v0.8.2](https://github.com/schireson/pytest-alembic/compare/v0.8.1...v0.8.2) (2022-04-10)

#### Fixes

* Add missing connection param to table_at_revision.
([a20d16e](https://github.com/schireson/pytest-alembic/commit/a20d16e42c9cec5f1062e2b7d3072eae42ef5534))
* Improve test options for all_models_register_on_metadata.
([28b7f59](https://github.com/schireson/pytest-alembic/commit/28b7f5950e5239f81c6b46a0b4265b0ed73fcb10))

### [v0.8.1](https://github.com/schireson/pytest-alembic/compare/v0.8.0...v0.8.1) (2022-03-12)

#### Fixes

* Add missing explicit reexports.
([d5375ad](https://github.com/schireson/pytest-alembic/commit/d5375ad3cba6066826c2ac4df3220d20433d381e))

## [v0.8.0](https://github.com/schireson/pytest-alembic/compare/v0.7.0...v0.8.0) (2022-02-08)

### Fixes

* (Huge speed optimization) Avoid the use of the high-level alembic command
interface in most cases.
([d616ffa](https://github.com/schireson/pytest-alembic/commit/d616ffaacc83acdd48b6ace0b517ceb35aaf0172))

## [v0.7.0](https://github.com/schireson/pytest-alembic/compare/v0.6.1...v0.7.0) (2021-12-21)

### ⚠ BREAKING CHANGE

* Starting with this release, python 3.6 will no longer be tested or officially supported. In this specific release, only the new official support for asyncio-based engine with alembic and pytest-alembic is incompatible with 3.6. Any existing usage should remain at least provisionally compatible until later releases which may or may not further break compatibility.


### Features

* Enable in-test insertion of data in async contexts.
([e9f8d97](https://github.com/schireson/pytest-alembic/commit/e9f8d9726e1a6a9032aa773db8dc1b69cc81cc5a))

### Fixes

* asynchronous engine tests which perform transaction manipulation.
([245f9ef](https://github.com/schireson/pytest-alembic/commit/245f9ef4e94f82d5d7742407451bcd0ad12762ac))

### [v0.6.1](https://github.com/schireson/pytest-alembic/compare/v0.6.0...v0.6.1) (2021-12-02)

#### Fixes

* Add missing alembic Config options.
([c3cab87](https://github.com/schireson/pytest-alembic/commit/c3cab870677ebe690fb2e82170f2af3981e2ebeb))

## [v0.6.0](https://github.com/schireson/pytest-alembic/compare/v0.5.1...v0.6.0) (2021-11-30)

### Features

* Add ability to set a minimum bound downgrade migration
([cda6937](https://github.com/schireson/pytest-alembic/commit/cda69378272a70efc40535e13546f50b5fdc7d74))
* Add new test which asserts parity between upgrade and downgrade detectable
effects.
([ab9b645](https://github.com/schireson/pytest-alembic/commit/ab9b6450988ff000899ff8ee193a309a3ff6c9a3))
* Add new test for roundtrip downgrade isolation.
([2fb20d0](https://github.com/schireson/pytest-alembic/commit/2fb20d0b8d17a70d84252832ee36fad020b06a68))

### Fixes

* Run pytest tests inline (faster and easier coverage).
([ea9b59d](https://github.com/schireson/pytest-alembic/commit/ea9b59dc61ac537fa5648273878c628094dbae71))

### [v0.5.1](https://github.com/schireson/pytest-alembic/compare/v0.5.0...v0.5.1) (2021-11-23)

#### Fixes

* Increase minimum python version to 3.6+ (this was already true!).
([e6bdfe6](https://github.com/schireson/pytest-alembic/commit/e6bdfe67f7d0bf8e675eeefa38cd44a06847799f))
* Incompatibility of branched history downgrade strategy with alembic 1.6+.
([192686b](https://github.com/schireson/pytest-alembic/commit/192686b9f3eaf43e8109c9376b9a806352f3a8c7))
* ensure the up-down consistency test actually verifies migrations
([a2e9d13](https://github.com/schireson/pytest-alembic/commit/a2e9d1321b378036e19af8e9525d78eddac09a37))

## [v0.5.0](https://github.com/schireson/pytest-alembic/compare/v0.4.0...v0.5.0) (2021-09-03)

### Features

* Add experimental test to identify tables which alembic will not recognize.
([d12e342](https://github.com/schireson/pytest-alembic/commit/d12e3422f2123eb0395e3b4a4535fdf9d2676f4a))

### Fixes

* Add back missing lint job.
([80242f3](https://github.com/schireson/pytest-alembic/commit/80242f3e4c4fc7e0120b44a4a03a4eecead2c51e))

## [v0.4.0](https://github.com/schireson/pytest-alembic/compare/v0.3.3...v0.4.0) (2021-08-16)

### Features

* Create a mechanism in which to create multiple alembic runner fixtures.
([ef1d5da](https://github.com/schireson/pytest-alembic/commit/ef1d5daec9d66e256a4b1b8a742d6889fbbbc44d))
* Allow alembic Config to be used directly in alembic_config fixture.
([3b00103](https://github.com/schireson/pytest-alembic/commit/3b0010398fd245a44e6ce16f9765a2e4c0c45c66))

### Fixes

* Run covtest on all branches.
([f1bd6ac](https://github.com/schireson/pytest-alembic/commit/f1bd6aca6196cbea4674f4b6d1c1eee204cee387))

### [v0.3.3](https://github.com/schireson/pytest-alembic/compare/v0.3.2...v0.3.3) (2021-08-04)

#### Fixes

* Conditionally set script_location.
([a26f59b](https://github.com/schireson/pytest-alembic/commit/a26f59b8b737eff8e77e663f23623024377e5371))

### [v0.3.2](https://github.com/schireson/pytest-alembic/compare/v0.3.1...v0.3.2) (2021-08-04)

### [v0.3.1](https://github.com/schireson/pytest-alembic/compare/v0.3.0...v0.3.1) (2021-05-10)

## [v0.3.0](https://github.com/schireson/pytest-alembic/compare/v0.2.6...v0.3.0) (2021-05-10)

### [v0.2.6](https://github.com/schireson/pytest-alembic/compare/v0.2.5...v0.2.6) (2021-04-26)

### [v0.2.5](https://github.com/schireson/pytest-alembic/compare/v0.2.4...v0.2.5) (2020-07-13)

#### Features

* Allow the customization of the location at which the built in tests are
executed.
([255c95c](https://github.com/schireson/pytest-alembic/commit/255c95c8edf0055f9d97aa671590449600b3e2a4))

### [v0.2.4](https://github.com/schireson/pytest-alembic/compare/v0.2.3...v0.2.4) (2020-07-01)

#### Fixes

* Require dataclasses only below 3.7, as it is included in stdlib 3.7 onward.
([0b30fb4](https://github.com/schireson/pytest-alembic/commit/0b30fb41bebf702102b09c55bba18931158d94ef))

### [v0.2.3](https://github.com/schireson/pytest-alembic/compare/v0.2.2...v0.2.3) (2020-06-26)

#### Features

* Reduce the multiple pages of traceback output to a few lines of context that
are actually meaningful to a failed test.
([d9bcfcc](https://github.com/schireson/pytest-alembic/commit/d9bcfcc709421734e14f3d034bfa77f74c15729e))

### [v0.2.2](https://github.com/schireson/pytest-alembic/compare/v0.2.1...v0.2.2) (2020-06-25)

#### Features

* Add rendered migration body to failed model-sync test.
([108db31](https://github.com/schireson/pytest-alembic/commit/108db31b874cc199418a012f314daa47d87b310a))

### [v0.2.1](https://github.com/schireson/pytest-alembic/compare/v0.1.1...v0.2.1) (2020-03-23)

#### Fixes

* Fix deprecation pytest warning in 3.4.
([f15a86b](https://github.com/schireson/pytest-alembic/commit/f15a86bd0620606203732a3f13d454b786d21a50))

### [v0.1.1](https://github.com/schireson/pytest-alembic/compare/v0.1.0...v0.1.1) (2020-03-09)

## v0.1.0 (2020-03-09)
