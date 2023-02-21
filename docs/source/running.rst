Running Tests
=============

You have two primary options for running the configured set of tests:

1. Automatically at the command-line via ``--test-alembic``

   :code:`Pytest Alembic` automatically adds a flag, :code:`pytest --test-alembic`, which will
   automatically invoke the baked-in tests.

   This can be convenient if you want to exclude migrations tests most of the time, but include
   them for e.g. CI. By default, ``pytest tests`` would then, **not** run migrations tests.

   Additionally, it means you don't need to manually include the tests in a test file somewhere
   in your project.

   If your tests dont generally reside at/below a ``tests/`` directory with a ``tests/conftest.py``
   file, you can/should set the :code:`pytest_alembic_tests_path` option, described
   below.

2. You can directly import the tests you want to include at any point in your project.

   .. code-block:: python
      :caption: tests/test_migrations.py
   
      from pytest_alembic.tests import (
          test_model_definitions_match_ddl,
          test_single_head_revision,
          test_up_down_consistency,
          test_upgrade,
      )

   This can be convenient if you always want the migrations tests to run, or else want a reference
   to the tests' existence somewhere in your source code. Pytest would automatically include
   the tests every time you run i.e. :code:`pytest tests`.

In either case, you can exclude migrations tests using pytest's "marker" system, i.e.
``pytest -m "not alembic"``.




Configuration
-------------

Pytest Config
~~~~~~~~~~~~~
In any of the pytest config locations (``pytest.ini``, ``setup.cfg``, ``pyproject.toml``),
you can set any of the following configuration options to alter global pytest-alembic
behavior.

* :code:`pytest_alembic_include`

  List of built-in tests to include. If specified, 'pytest_alembic_exclude' is ignored.
  If both are omitted, all tests are included. The tests should be listed as a comma delimited string
  containing the tests' names.

* :code:`pytest_alembic_exclude`

  List of built-in tests to exclude. Ignored if 'pytest_alembic_include' is specified.
  The tests should be listed as a comma delimited string containing the tests' names.

* :code:`pytest_alembic_tests_folder`

  The location under which the built-in tests will be bound. This defaults to 'tests/'
  (the tests themselves then being executed from tests/pytest_alembic/), the typical test
  location. However this can be customized if pytest is, for example, invoked from a parent
  directory like :code:`pytest folder/tests`, or the tests are otherwise located at a different
  location, relative to the :code:`pytest` invocation.

  .. note::

     As of pytest-alembic version 0.8.5, this option is ignored. Instead, if you require customizing
     the registration location, you should use :code:`pytest_alembic_tests_path` instead.

* :code:`pytest_alembic_tests_path`

  .. note::

     Introduced in v0.10.1.

  The location at which the built-in tests will be bound. This defaults to 'tests/conftest.py'.
  Typically, you would want this to coincide with the path at which your `alembic_engine` is being
  defined/registered. Note that this path must be the full path, relative to the root location
  at which pytest is being invoked.

  This option has replaced :code:`pytest_alembic_tests_folder` due to changes in how pytest test collection
  needed to be performed in around pytest ~7.0.

  Additionally, this option is only required if you are using the :code:`--test-alembic` flag.


Alembic Config
~~~~~~~~~~~~~~
See the :ref:`Config` fixture for more detail.


Alternative to :code:`--test-alembic`
-------------------------------------

There is **some** magic to the automatic inclusion of the built-in tests. It's not obvious, from
looking at any of the test code, that these tests (sometimes) magically be included.

Also, one may want to include the built-in tests automatically, every time, without needing to
specify :code:`--test-alembic`, or by doing so conditionally in-code.

Whatever the reason, it is possible to simply import the test implementations from
:code:`pytest_alembic` directly.

Simply import the tests at whatever location you want tests to be included:

.. code-block:: python
   :caption: tests/test_migrations.py

   from pytest_alembic.tests import test_single_head_revision
   from pytest_alembic.tests import test_upgrade
   from pytest_alembic.tests import test_model_definitions_match_ddl
   from pytest_alembic.tests import test_up_down_consistency


Furthermore, doing this as well as using :code:`--test-alembic` will cause the tests to be
run twice (since they'd be considered unique tests with different paths). So generally, these
methods should be considered mutually exclusive.


Multiple Alembic Histories
--------------------------

It may be the case that you have the histories for two separate databases (or schemas)
in a single project. How should you structure your tests?

This is likely one of the times you want to avoid the use of the :code:`--test-alembic`
flag and the automatic insertion of tests.

Instead, you'll likely want to want to make use of :func:`create_alembic_fixture`.

.. code-block:: python

  from pytest_alembic import tests, create_alembic_fixture

  # The argument here represents the equivalent to `alembic_config`. Depending
  # on your setup, this may be configuring the "file" argument, "script_location",
  # or some other way of configuring one or the other of your histories.
  history_1 = create_alembic_fixture({"file": "alembic.ini"})

  def test_single_head_revision_history_1(history_1):
      tests.test_single_head_revision(history_1)

  def test_upgrade_history_1(history_1):
      tests.test_upgrade(history_1)

  def test_model_definitions_match_ddl_history_1(history_1):
      tests.test_model_definitions_match_ddl(history_1)

  def test_up_down_consistency_history_1(history_1):
      tests.test_up_down_consistency(history_1)

  # The 2nd fixture, and the 2nd set of tests.
  history_2 = create_alembic_fixture({"file": "history_2.ini"})

  def test_single_head_revision_history_2(history_2):
      tests.test_single_head_revision(history_2)

  def test_upgrade_history_2(history_2):
      tests.test_upgrade(history_2)

  def test_model_definitions_match_ddl_history_2(history_2):
      tests.test_model_definitions_match_ddl(history_2)

  def test_up_down_consistency_history_2(history_2):
      tests.test_up_down_consistency(history_2)


Due to limitations of how pytest test collection occurs, there's currently no
obvious way to automatically set up and define these tests to occur against
different fixtures.


Pytest Marks
------------

Pytest-alembic automatically marks all tests which use the :code:`alembic_runner` fixture
(including all built-in tests) with the :code:`alembic` mark.

This means you can optionally include/exclude migrations tests using the vanilla pytest mark
machinery like so:

.. code:: bash

   pytest -m 'alembic'  # Run *only* alembic tests
   pytest -m 'not alembic'  # Run everything *except* alembic tests
