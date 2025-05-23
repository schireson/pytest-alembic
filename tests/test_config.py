from unittest import mock

import alembic.config
import pytest

from pytest_alembic.config import Config


def mock_patch(*contents):
    m_open = mock.mock_open()
    m_open.side_effect = [(mock.mock_open(read_data=string).return_value) for string in contents]
    return mock.patch("builtins.open", m_open)


def test_default_file():
    config = Config()

    with mock_patch("[alembic]", b""):
        alembic_config = config.make_alembic_config(None)
    assert alembic_config.config_file_name == "alembic.ini"


def test_set_file():
    config = Config(config_options={"file": "foo.ini"})

    with mock_patch("[alembic]", b""):
        alembic_config = config.make_alembic_config(None)
    assert alembic_config.config_file_name == "foo.ini"


def test_set_config_file_name():
    config = Config(config_options={"config_file_name": "foo.ini"})

    with mock_patch("[alembic]", b""):
        alembic_config = config.make_alembic_config(None)
    assert alembic_config.config_file_name == "foo.ini"


def test_set_sqlalchemy_url():
    config = Config(config_options={"sqlalchemy.url": "sqlite:///"})
    alembic_config = config.make_alembic_config(None)
    assert alembic_config.get_main_option("sqlalchemy.url") == "sqlite:///"


def test_set_script_location():
    config = Config(config_options={"script_location": "alembic"})
    alembic_config = config.make_alembic_config(None)
    assert alembic_config.get_main_option("script_location") == "alembic"


@pytest.mark.skipif(
    not hasattr(alembic.config.Config, "get_alembic_option"),
    reason="pyproject.toml is not supported in this version of alembic",
)
def test_pyproject_toml():
    config = Config()

    exists = mock.patch("alembic.config.Config._toml_file_path", return_value=True)
    with exists, mock_patch("[alembic]", b"[tool.alembic]\nscript_location = 'asdf'"):
        alembic_config = config.make_alembic_config(None)
    assert alembic_config.get_main_option("script_location") == "asdf"
