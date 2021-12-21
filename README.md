![CircleCI](https://img.shields.io/circleci/build/gh/schireson/pytest-alembic/master)
[![codecov](https://codecov.io/gh/schireson/pytest-alembic/branch/master/graph/badge.svg)](https://codecov.io/gh/schireson/pytest-alembic)
[![Documentation Status](https://readthedocs.org/projects/pytest-alembic/badge/?version=latest)](https://pytest-alembic.readthedocs.io/en/latest/?badge=latest)

## Introduction

A pytest plugin to test alembic migrations (with default tests) and
which enables you to write tests specific to your migrations.

```bash
$ pip install pytest-alembic
$ pytest --test-alembic

...
::pytest_alembic/tests/model_definitions_match_ddl <- . PASSED           [ 25%]
::pytest_alembic/tests/single_head_revision <- . PASSED                  [ 50%]
::pytest_alembic/tests/up_down_consistency <- . PASSED                   [ 75%]
::pytest_alembic/tests/upgrade <- . PASSED                               [100%]

============================== 4 passed in 2.32s ===============================
```

## The pitch

Have you ever merged a change to your models and you forgot to generate
a migration?

Have you ever written a migration only to realize that it fails when
there’s data in the table?

Have you ever written a **perfect** migration only to merge it and later
find out that someone else merged also merged a migration and your CD is
now broken!?

`pytest-alembic` is meant to (with a little help) solve all these
problems and more. Note, due to a few different factors, there **may**
be some [minimal required
setup](http://pytest-alembic.readthedocs.io/en/latest/setup.html);
however most of it is boilerplate akin to the setup required for alembic
itself.

### Built-in Tests

- **test_single_head_revision**

  Assert that there only exists one head revision.

  We’re not sure what realistic scenario involves a diverging history to
  be desirable. We have only seen it be the result of uncaught merge
  conflicts resulting in a diverged history, which lazily breaks during
  deployment.

- **test_upgrade**

  Assert that the revision history can be run through from base to head.

- **test_model_definitions_match_ddl**

  Assert that the state of the migrations matches the state of the
  models describing the DDL.

  In general, the set of migrations in the history should coalesce into
  DDL which is described by the current set of models. Therefore, a call
  to `revision --autogenerate` should always generate an empty migration
  (e.g. find no difference between your database (i.e. migrations
  history) and your models).

- **test_up_down_consistency**

  Assert that all downgrades succeed.

  While downgrading may not be lossless operation data-wise, there’s a
  theory of database migrations that says that the revisions in
  existence for a database should be able to go from an entirely blank
  schema to the finished product, and back again.

- [Experimental
  tests](http://pytest-alembic.readthedocs.io/en/latest/experimental_tests.html)

  - all_models_register_on_metadata

    Assert that all defined models are imported statically.

    Prevents scenarios in which the minimal import of your models in your `env.py`
    does not import all extant models, leading alembic to not autogenerate all
    your models, or (worse!) suggest the deletion of tables which should still exist.

  - downgrade_leaves_no_trace

    Assert that there is no difference between the state of the database pre/post downgrade.

    In essence this is a much more strict version of `test_up_down_consistency`,
    where the state of a MetaData before and after a downgrade are identical as
    far as alembic (autogenerate) is concerned.

  These tests will need to be enabled manually because their semantics or API are
  not yet guaranteed to stay the same. See the linked docs for more details!

Let us know if you have any ideas for more built-in tests which would be
generally useful for most alembic histories!

### Custom Tests

For more information, see the docs for [custom
tests](http://pytest-alembic.readthedocs.io/en/latest/custom_tests.html)
(example below) or [custom static
data](http://pytest-alembic.readthedocs.io/en/latest/custom_data.html)
(to be inserted automatically before a given revision).

Sometimes when writing a particularly gnarly data migration, it helps to
be able to practice a little timely TDD, since there’s always the
potential you’ll trash your actual production data.

With `pytest-alembic`, you can write tests directly, in the same way
that you would normally, through the use of the `alembic_runner`
fixture.

```python
def test_gnarly_migration_xyz123(alembic_engine, alembic_runner):
    # Migrate up to, but not including this new migration
    alembic_runner.migrate_up_before('xyz123')

    # Perform some very specific data setup, because this migration is sooooo complex.
    # ...
    alembic_engine.execute(table.insert(id=1, name='foo'))

    alembic_runner.migrate_up_one()
```

`alembic_runner` has a number of methods designed to make it convenient
to change the state of your database up, down, and all around.

## Installing

```bash
pip install "pytest-alembic"
```
