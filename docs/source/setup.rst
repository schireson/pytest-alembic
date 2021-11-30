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


Caplog Issues
~~~~~~~~~~~~~

The default :code:`env.py` file that alembic will autogenerate for you also includes a call to
:func:`logging.config.fileConfig`. Given that alembic tests invoke the :code:`env.py`, and
:func:`logging.config.fileConfig` has a default argument of :code:`disable_existing_loggers=True`,
this can inadvertantly break tests which use pytest's :code:`caplog` fixture.

To fix this, simply provide :code:`disable_existing_loggers=False` to :code:`fileConfig`.

.. warning::
   Additionally, if you are a user of :func:`logging.basicConfig`, note that :func:`logging.basicConfig`
   "does nothing if the root logger already has handlers configured", (which is why we generally
   try to avoid :code:`basicConfig`) and may cause issues for similar reasons.

.. note::
   Python 3.8 added a :code:`force=True` keyword to :func:`logging.basicConfig`, which makes
   it somewhat less hazardous to use.

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

Overridding the fixtures
~~~~~~~~~~~~~~~~~~~~~~~~

One should generally put the implementations of :ref:`alembic_config` and :ref:`alembic_engine`
in a :code:`conftest.py` (a special file recognized by pytest) at the root of your tests folder,
typically :code:`tests/conftest.py`.

If your tests are located elsewhere, you should use the :ref:`pytest config <Pytest Config>` to specify
:code:`pytest_alembic_tests_folder`, to point at your tests folder root.

Then you can define your own implementations of these fixtures:

:ref:`alembic_config` is the primary point of entry for configurable options for the
alembic runner. See the API docs for a comprehensive list. This can often be omitted, as
alembic does not typically require configuration. The default implementation is:

.. code:: python

   @pytest.fixture
   def alembic_config():
       """Override this fixture to configure the exact alembic context setup required.
       """
       return {}


:ref:`alembic_engine` is where you specify the engine with which the :ref:`alembic_runner`
should execute your tests.

.. code:: python

   @pytest.fixture
   def alembic_engine():
       """Override this fixture to provide pytest-alembic powered tests with a database handle.
       """
       return sqlalchemy.create_engine("sqlite:///")

If you have a **very** simple database schema, you may be able to get away with the default
fixture implementation, which uses an in-memory SQLite engine. In most cases however,
SQLite will not be able to sufficiently model your migrations.


Pytest Mock Resources
~~~~~~~~~~~~~~~~~~~~~

Though you can, of course, implement whatever strategy you want, our recommended approach is to use
`pytest-mock-resources <http://www.pytest-mock-resources.readthedocs.io/>`_,
another library we have open sourced which uses Docker to manage the lifecycle of an ephemeral
database instance.

If you use Postgres or Redshift, we can support your usecase today. For other alembic-supported
databases, file an issue!

.. code-block:: python

   from pytest_mock_resources import create_postgres_fixture

   alembic_engine = create_postgres_fixture()


Git(hub) Settings
-----------------

.. image:: _static/github_setting.png

We highly recommend you enable "Require branches to be up to date before merging" on repos
which have alembic migrations!

While this will require that people merging PRs to rebase on top of master before merging
(which we think is ideal for ensuring your build is always green anyways), it guarantees that
**our** tests are running against a known up-to-date migration history.

Without this option it is trivially easy to end up with an alembic version history with
2 or more heads which needs to be manually resolved.

Provider support

* Only GitLab EE supports an approximate option to GitHub's.
* Only Bitbucket EE supports an approximate option to GitHub's.
