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
def alembic_config() -> Union[Dict[str, Any], alembic.config.Config]:
    """Override this fixture to configure the exact alembic context setup required.

    The return value of this fixture can be a literal :class:`alembic.config.Config`
    object. If you, have a lot of options to set, or feel more comfortable setting
    alembic config, this might be the way to go.

    It can also be a `Dict` containing the common set of kwargs one might use
    to configure an alembic Config object, such as:

        - script_location
        - target_metadata
        - process_revision_directives
        - include_schemas

    Note that values here, represent net-additive options on top of what you might
    already have configured in your `env.py`. You should generally prefer to
    configure your `env.py` however you like it and omit such options here.

    Additionally you can send a `file` key (akin to `alembic -c`), should your
    `alembic.ini` be otherwise named.

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
