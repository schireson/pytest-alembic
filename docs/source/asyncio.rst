Asyncio
=======

Support for asyncio is largely built on top of the `Alembic Cookbook`_ example,
inlined here for posterity:

.. code-block:: python

   import asyncio

   # ... no change required to the rest of the code
   
   def do_run_migrations(connection):
       context.configure(connection=connection, target_metadata=target_metadata)
   
       with context.begin_transaction():
           context.run_migrations()
   
   
   async def run_migrations_online():
       """Run migrations in 'online' mode.
   
       In this scenario we need to create an Engine
       and associate a connection with the context.
   
       """
       connectable = AsyncEngine(
           engine_from_config(
               config.get_section(config.config_ini_section),
               prefix="sqlalchemy.",
               poolclass=pool.NullPool,
               future=True,
           )
       )
   
       async with connectable.connect() as connection:
           await connection.run_sync(do_run_migrations)

       await connectable.dispose()
   
   
   if context.is_offline_mode():
       run_migrations_offline()
   else:
       asyncio.run(run_migrations_online())

Note that this is a prerequisite for how one gets **alembic itself** to run with an async
connection, when running ``alembic`` commands interatively yourself.

At this point, you just need to make sure the ``alembic_engine`` fixture is producing a async engine.
something like

.. code-block:: python

   from sqlalchemy import create_engine
   from sqlalchemy.ext.asyncio import create_engine_async, AsyncEngine

   @pytest.fixture
   def alembic_engine(...):
       return create_async_engine(URL(...))


   @pytest.fixture
   def alembic_engine(...):
       engine = create_engine(URL(...))
       return AsyncEngine(engine)


   # or, for example, with pytest-mock-resources
   from pytest_mock_resources import create_postgres_fixture

   alembic_engine = create_postgres_fixture(async_=True)


A slightly more versatile setup
-------------------------------
The above ``env.py`` setup comes with a caveat. It assumes execution of the migrations
solely through async. Due to the way sqlalchemy/alembic async works (as evidenced by
even their suggested use of ``run_sync``), this can be a problem.

For pytest-alembic the only such built in test is :ref:`test_downgrade_leaves_no_trace`.
For compatibility with (majority) sync alembic use, it's implemented sychronously, and internally
requires performing transaction manipulation which would otherwise require re-entrant use of
``asyncio.run``.

If you don't use this test, and haven't implemented any of your own which encounter this issue,
then feel free to stick with the official alembic suggestion. However a slight reorganization of
their suggested setup allows for both sychronous and asynchronous execution of migrations, and
thus fixes :ref:`test_downgrade_leaves_no_trace`.

.. code-block:: python

   from sqlalchemy.ext.asyncio.engine import AsyncEngine

   def run_migrations_online():
       connectable = context.config.attributes.get("connection", None)
   
       if connectable is None:
           connectable = AsyncEngine(
               engine_from_config(
                   context.config.get_section(context.config.config_ini_section),
                   prefix="sqlalchemy.",
                   poolclass=pool.NullPool,
                   future=True,
               )
           )
   
       # Note, we decide whether to run asynchronously based on the kind of engine we're dealing with.
       if isinstance(connectable, AsyncEngine):
           asyncio.run(run_async_migrations(connectable))
       else:
           with connectable.connect() as connection:
               do_run_migrations(connection)
   
   
   # Then use their setup for async connection/running of the migration
   async def run_async_migrations(connectable):
       async with connectable.connect() as connection:
           await connection.run_sync(do_run_migrations)
   
       await connectable.dispose()
   
   
   def do_run_migrations(connection):
       context.configure(connection=connection, target_metadata=target_metadata)
   
       with context.begin_transaction():
           context.run_migrations()
   
   
   # But the outer layer still allows sychronous execution also.
   run_migrations_online()


.. _`Alembic Cookbook`: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
