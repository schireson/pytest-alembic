Setup
=====

:code:`env.py`
--------------

The default :code:`env.py` file that alembic will autogenerate for you includes a snippet like so:

.. code-block:: python

   def run_migrations_online():
       connectable = engine_from_config(
           config.get_section(config.config_ini_section),
           prefix="sqlalchemy.",
           poolclass=pool.NullPool,
       )

This is fine, but :code:`pytest-alembic` needs to provide alembic with a connection at runtime.
So to allow us to produce that connection in a way that :code:`env.py` understands, modify the
above snippet to resemble:

.. code-block:: python

   def run_migrations_online():
       connectable = context.config.attributes.get("connection", None)

       if connectable is None:
           connectable = engine_from_config(
               context.config.get_section(context.config.config_ini_section),
               prefix="sqlalchemy.",
               poolclass=pool.NullPool,
           )


Optional but helpful additions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alembic comes with a number of other options to customize how the autogeneration of revisions
is handled, but most of them are disabled by default. There are many good reasons your particular
migrations might **not** want some of these options enabled; but if they don't apply to your
setup, we think they increase the quality of the safety this library helps to provide.

Further down in your :code:`env.py`, you'll see a configure block.

.. code-block:: python

   with connectable.connect() as connection:
       context.configure(
           connection=connection,
           target_metadata=target_metadata,
           # This is where we want to add more options!
       )

       with context.begin_transaction():
           context.run_migrations()


Consider enabling the following options:

* :code:`compare_type=True`: Indicates type comparison behavior during an autogenerate operation.
* :code:`compare_server_default=True`: Indicates server default comparison behavior during an autogenerate operation.
* :code:`include_schemas=True`: If True, autogenerate will scan across all schemas located by the SQLAlchemy get_schema_names() method, and include all differences in tables found across all those schemas. This may only be useful if you make use of schemas.


Fixtures
--------

We expose 2 explicitly overridable fixtures :code:`alembic_config` and :code:`alembic_engine`.

:code:`alembic_config` is the primary point of entry for configurable options for the
alembic runner. See the API docs for a comprehensive list. For now, you can ignore
this fixture.

:code:`alembic_engine` is where you specify the engine with which the :code:`alembic_runner`
should execute your tests.

If you have a **very** simple database schema, you may be able to get away with the default
fixture implementation, which uses an in-memory SQLite engine. In most cases however,
SQLite will not be able to sufficiently model your migrations.

We generally recommend the below option, but you can also implement your own strategy.


Pytest Mock Resources
~~~~~~~~~~~~~~~~~~~~~
Our recommended approach is to use `pytest-mock-resources <http://www.pytest-mock-resources.readthedocs.io/>`_,
another library we have open sourced which uses Docker to manage the lifecycle of an ephemeral
database instance.

If you use Postgres or Redshift, we can support your usecase today. For other alembic-supported
databases, file an issue!

.. code-block:: python

   from pytest_mock_resources import create_postgres_fixture

   alembic_engine = create_postgres_fixture()
