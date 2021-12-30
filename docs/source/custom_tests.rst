Writing Custom Tests
====================

Honestly, there's not much to it by this point!

.. code-block:: python

   from sqlalchemy import text

   def test_gnarly_migration_xyz123(alembic_runner, alembic_engine):
       # Migrate up to, but not including this new migration
       alembic_runner.migrate_up_before('xyz123')

       # Perform some very specific data setup, because this migration is sooooo complex.
       # ...
       alembic_runner.insert_into(dict(id=1, name='foo'), tablename='tablename'))
       # Or you can optionally accept the `alembic_engine` fixture, which is a
       # sqlalchemy engine object, with which you can do whatever setup you'd like.

       alembic_runner.migrate_up_one()

       with alembic_engine.connect() as conn:
           rows = conn.execute(text("SELECT id from foo")).fetchall()

       assert rows == [(1,)]

:class:`alembic_runner <pytest_alembic.MigrationContext>` has all sorts of convenience methods
for altering the state of the database for your test:

.. autoclass:: pytest_alembic.runner.MigrationContext
    :members:
    :noindex:
