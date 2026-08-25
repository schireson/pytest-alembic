import io
from contextlib import AbstractContextManager
from typing import Any
from unittest import mock

import alembic.config
import pytest

from pytest_alembic.config import Config


def mock_patch(*contents: str | bytes) -> AbstractContextManager[Any]:
    m_open = mock.mock_open()
    m_open.side_effect = [(mock.mock_open(read_data=string).return_value) for string in contents]
    return mock.patch("builtins.open", m_open)


def test_default_file() -> None:
    config = Config()

    with mock_patch("[alembic]", b""):
        alembic_config = config.make_alembic_config(io.StringIO())
    assert alembic_config.config_file_name == "alembic.ini"


def test_set_file() -> None:
    config = Config(config_options={"file": "foo.ini"})

    with mock_patch("[alembic]", b""):
        alembic_config = config.make_alembic_config(io.StringIO())
    assert alembic_config.config_file_name == "foo.ini"


def test_set_config_file_name() -> None:
    config = Config(config_options={"config_file_name": "foo.ini"})

    with mock_patch("[alembic]", b""):
        alembic_config = config.make_alembic_config(io.StringIO())
    assert alembic_config.config_file_name == "foo.ini"


def test_set_sqlalchemy_url() -> None:
    config = Config(config_options={"sqlalchemy.url": "sqlite:///"})
    alembic_config = config.make_alembic_config(io.StringIO())
    assert alembic_config.get_main_option("sqlalchemy.url") == "sqlite:///"


def test_set_script_location() -> None:
    config = Config(config_options={"script_location": "alembic"})
    alembic_config = config.make_alembic_config(io.StringIO())
    assert alembic_config.get_main_option("script_location") == "alembic"


@pytest.mark.skipif(
    not hasattr(alembic.config.Config, "get_alembic_option"),
    reason="pyproject.toml is not supported in this version of alembic",
)
def test_pyproject_toml() -> None:
    config = Config()

    exists = mock.patch("alembic.config.Config._toml_file_path", return_value=True)
    with exists, mock_patch("[alembic]", b"[tool.alembic]\nscript_location = 'asdf'"):
        alembic_config = config.make_alembic_config(io.StringIO())
    assert alembic_config.get_main_option("script_location") == "asdf"


def test_legacy_alembic_without_toml_support() -> None:
    """Assert the pre-`pyproject.toml` alembic path still builds a config.

    `_supports_toml` gates two branches, and only one of them is reachable in any given
    environment -- the installed alembic either has `get_alembic_option` or it does not.
    Patching it is what lets the legacy branch be exercised on a modern alembic.
    """
    config = Config(config_options={"file": "foo.ini"})

    supports_toml = mock.patch("pytest_alembic.config._supports_toml", return_value=False)
    with supports_toml, mock_patch("[alembic]"):
        alembic_config = config.make_alembic_config(io.StringIO())

    assert alembic_config.config_file_name == "foo.ini"


def test_legacy_alembic_reads_script_location_from_main_option() -> None:
    """Assert `_get_option` falls back to `get_main_option` without toml support."""
    config = Config()

    supports_toml = mock.patch("pytest_alembic.config._supports_toml", return_value=False)
    with supports_toml, mock_patch("[alembic]\nscript_location = legacy"):
        alembic_config = config.make_alembic_config(io.StringIO())

    assert alembic_config.get_main_option("script_location") == "legacy"
