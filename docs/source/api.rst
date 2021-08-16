API
===

Fixture Functions
-----------------

.. automodule:: pytest_alembic.plugin.fixtures
    :members: alembic_runner, alembic_config, alembic_engine, create_alembic_fixture


Alembic Runner
--------------

The object yielded into a test from an `alembic_runner` fixture is the :class:`MigrationContext`

.. automodule:: pytest_alembic.runner
    :members: MigrationContext

.. automodule:: pytest_alembic.history
    :members: AlembicHistory

.. automodule:: pytest_alembic.revision_data
    :members: RevisionData, RevisionSpec
