Contributing
============

Prerequisites
-------------

This project is managed with uv_, so you'll need that first. See the `uv installation
docs`_ for the available options.

The test suite provisions a real postgres instance through pytest-mock-resources_, so
you will also need Docker running locally.

Getting Setup
-------------
``pytest-alembic`` supports Python 3.10 and above (see ``requires-python`` in
``pyproject.toml``). CI exercises 3.10 through 3.13 against a matrix of ``pytest``,
``pytest-asyncio`` and ``sqlalchemy`` versions.

Run :code:`make help` to list the common commands, but for some basic setup:

.. code-block:: bash

    # Installs the package along with its dev dependencies
    make install

And you'll want to make sure you can run the tests and linters successfully:

.. code-block:: bash

    # Runs CI-level tests, with coverage reports
    make test

    # Runs ruff (lint and format check) and mypy
    make lint

Both of these are the same entry points CI uses, so a green :code:`make test lint`
locally should mean a green build.

If :code:`make lint` reports formatting differences or fixable lint errors,
:code:`make format` applies them in place.

Building the docs
-----------------

The docs dependencies live in a non-default group, so :code:`make install` does not
include them:

.. code-block:: bash

    uv sync --group docs
    uv run sphinx-autobuild docs/source docs/build

Need help
---------

Submit an issue!

.. _uv: https://docs.astral.sh/uv/
.. _uv installation docs: https://docs.astral.sh/uv/getting-started/installation/
.. _pytest-mock-resources: https://github.com/schireson/pytest-mock-resources
