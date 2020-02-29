![CircleCI](https://img.shields.io/circleci/build/gh/schireson/pytest-alembic/master) [![codecov](https://codecov.io/gh/schireson/pytest-alembic/branch/master/graph/badge.svg)](https://codecov.io/gh/schireson/pytest-alembic) [![Documentation Status](https://readthedocs.org/projects/pytest-alembic/badge/?version=latest)](https://pytest-alembic.readthedocs.io/en/latest/?badge=latest)


## Introduction


## The pitch


## Built-in Tests

* test_single_head_revision

  Assert that there only exists one head revision.

  We're not sure what realistic scenario involves a diverging history to be desirable. We
  have only seen it be the result of uncaught merge conflicts resulting in a diverged history,
  which lazily breaks during deployment.

* test_upgrade

  Assert that the revision history can be run through from base to head.

* test_model_definitions_match_ddl

  Assert that the state of the migrations matches the state of the models describing the DDL.

  In general, the set of migrations in the history should coalesce into DDL which is described
  by the current set of models. Therefore, a call to `revision --autogenerate` should always
  generate an empty migration (e.g. find no difference between your database (i.e. migrations
  history) and your models).

* test_up_down_consistency

  Assert that all downgrades succeed.

  While downgrading may not be lossless operation data-wise, there’s a theory of database
  migrations that says that the revisions in existence for a database should be able to go
  from an entirely blank schema to the finished product, and back again.

## Installing

```bash
pip install "pytest-alembic"
```
