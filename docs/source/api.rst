API
===

Fixtures
--------

alembic_runner
~~~~~~~~~~~~~~
.. autofunction:: pytest_alembic.plugin.fixtures.alembic_runner

alembic_config
~~~~~~~~~~~~~~
.. autofunction:: pytest_alembic.plugin.fixtures.alembic_config

Config
++++++
.. autoclass:: pytest_alembic.config.Config
   :members: from_raw_config

alembic_engine
~~~~~~~~~~~~~~
.. autofunction:: pytest_alembic.plugin.fixtures.alembic_engine

create_alembic_fixture
~~~~~~~~~~~~~~~~~~~~~~
.. autofunction:: pytest_alembic.plugin.fixtures.create_alembic_fixture


Alembic Runner
--------------

The object yielded into a test from an `alembic_runner` fixture is the :class:`MigrationContext`

.. automodule:: pytest_alembic.runner
    :members: MigrationContext

.. automodule:: pytest_alembic.history
    :members: AlembicHistory

.. automodule:: pytest_alembic.revision_data
    :members: RevisionData, RevisionSpec
