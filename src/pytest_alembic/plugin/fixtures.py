from typing import Any, Dict, Union

import alembic.config
import pytest
import sqlalchemy

from pytest_alembic.config import Config


@pytest.fixture
def alembic_runner(alembic_config, alembic_engine):
    """Produce an alembic migration context in which to execute alembic tests."""
    import pytest_alembic

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
