Custom Tests
============

Honestly, there's not much to it by this point!

.. code-block:: python

   def test_knarly_migration_xyz123(alembic_runner):
       # Migrate up to, but not including this new migration
       alembic_runner.migrate_up_before('xyz123')

       # Perform some very specific data setup, because this migration is sooooo complex.
       # ...
       alembic_runner.insert_into(dict(id=1, name='foo'), tablename='tablename'))
       # Or you can optionally accept the `alembic_engine` fixture, which is a
       # sqlalchemy engine object, with which you can do whatever setup you'd like.

       alembic_runner.migrate_up_one()

:class:`alembic_runner <pytest_alembic.MigrationContext>` has all sorts of convenience methods
for altering the state of the database for your test:

.. autoclass:: pytest_alembic.runner.MigrationContext
    :members:
