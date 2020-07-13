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


Pytest Marks
------------

Pytest-alembic automatically marks all tests which use the :code:`alembic_runner` fixture
(including all built-in tests) with the :code:`alembic` mark.

This means you can optionally include/exclude migrations tests using the vanilla pytest mark
machinery like so:

.. code:: bash

   pytest -m 'alembic'  # Run *only* alembic tests
   pytest -m 'not alembic'  # Run everything *except* alembic tests
