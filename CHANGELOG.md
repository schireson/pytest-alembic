# Changelog

## [Unreleased](https://github.com/schireson/pytest-alembic/compare/v0.8.3...HEAD) (2022-10-31)

### Fixes

* Refresh alembic history to enable tests generate new revisions to be aware of  
those revisions.
  ([a81b5f8](https://github.com/schireson/pytest-alembic/commit/a81b5f82cbf0243f045cc41263a56bb788fc260d))
* Compatibility with newer versions of pytest and pytest-asyncio.
  ([4ed809b](https://github.com/schireson/pytest-alembic/commit/4ed809b8b059091cbd55aa68d57d398c129a7d3f))
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

* Starting with this release, python 3.6 will no longer be tested or officiallysupported. In this specific release, only the new official support forasyncio-based engine with alembic and pytest-alembic is incompatible with 3.6.Any existing usage should remain at least provisionally compatible until laterreleases which may or may not further break compatibility.

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

* Reduce the multiple pages of traceback output to a few lines of context that are  
actually meaningful to a failed test.
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
