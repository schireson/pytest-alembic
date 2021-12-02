from typing import Any, Dict, Union

import alembic.config
import pytest
import sqlalchemy

import pytest_alembic
from pytest_alembic.config import Config


def create_alembic_fixture(raw_config=None):
    """Create a new fixture `alembic_runner`-like fixture.

    In many cases, this function should not be strictly necessary. You **can**
    generally rely solely on the :code:`--test-alembic` flag, automatic insertion
    of tests, and the :func:`alembic_runner` fixture.

    However this may be useful in some situations:

    - If you would generally prefer to avoid the :code:`--test-alembic` flag and
      automatic test insertion, this is the function for you!
    - If you have multiple alembic histories and therefore require more than one
      fixture, you will **minimally** need to use this for the 2nd history (if
      not both)

    Examples:
        >>> from pytest_alembic import tests
        >>>
        >>> alembic = create_alembic_fixture()
        >>>
        >>> def test_upgrade_head(alembic):
        ...     tests.test_upgrade_head(alembic)
        >>>
        >>> def test_specific_migration(alembic):
        ...     alembic_runner.migrate_up_to('xxxxxxx')
        ...     assert ...

        Config can also be supplied similarly to the :func:`alembic_config` fixture.

        >>> alembic = create_alembic_fixture({'file': 'migrations.ini'})
    """

    @pytest.fixture
    def _(alembic_engine):
        config = Config.from_raw_config(raw_config)
        with pytest_alembic.runner(config=config, engine=alembic_engine) as runner:
            yield runner

    return _


@pytest.fixture
def alembic_runner(alembic_config, alembic_engine):
    """Produce the primary alembic migration context in which to execute alembic tests.

    This fixture allows authoring custom tests which are specific to your particular
    migration history.

    Examples:
        >>> def test_specific_migration(alembic_runner):
        ...     alembic_runner.migrate_up_to('xxxxxxx')
        ...     assert ...
    """
    config = Config.from_raw_config(alembic_config)
    with pytest_alembic.runner(config=config, engine=alembic_engine) as runner:
        yield runner


@pytest.fixture
def alembic_config() -> Union[Dict[str, Any], alembic.config.Config, Config]:
    """Override this fixture to configure the exact alembic context setup required.

    The return value of this fixture can be one of a few types.

    - If you're only configuring alembic-native configuration, a :class:`alembic.config.Config`
      object is accepted as configuration. This largely leaves pytest-alembic out
      of the setup, so depending on your settings, might be the way to go.

    - If you only have a couple of options to set, you might choose to return
      a ``Dict``.

      The following common alembic config options are accepted as keys.

        - file/config_file_name (commonly alembic.ini)
        - script_location
        - sqlalchemy.url
        - target_metadata
        - process_revision_directives
        - include_schemas

      Additionally you can send a `file` key (akin to `alembic -c`), should your
      `alembic.ini` be otherwise named.

      Note that values here, represent net-additive options on top of what you might
      already have configured in your `env.py`. You should generally prefer to
      configure your `env.py` however you like it and omit such options here.

      You may also use this dict to set pytest-alembic specific features:

        - before_revision_data
        - at_revision_data
        - minimum_downgrade_revision

    - You can also directly return a :ref:`Config` class instance.
      This is your only option if you want to use both pytest-alembic specific features
      **and** construct your own :class:`alembic.config.Config`.

    Examples:
        >>> @pytest.fixture
        ... def alembic_config():
        ...     return {'file': 'migrations.ini'}

        >>> @pytest.fixture
        ... def alembic_config():
        ...     alembic_config = alembic.config.Config()
        ...     alembic_config.set_main_option("script_location", ...)
        ...     return alembic_config
    """
    return {}


@pytest.fixture
def alembic_engine():
    """Override this fixture to provide pytest-alembic powered tests with a database handle."""
    return sqlalchemy.create_engine("sqlite:///")
