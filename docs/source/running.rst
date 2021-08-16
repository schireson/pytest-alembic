Running Tests
=============

:code:`Pytest Alembic` automatically adds a flag, :code:`pytest --test-alembic`, which will
automatically invoke the baked-in tests.

Config
------

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


It should be noted, that this obviates the need specify the :code:`pytest_alembic_tests_folder`
config option, as they will be run from the location of your import by pytest automatically.

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
