from unittest import mock

from pytest_alembic.config import Config


def mock_open(*args, **kargs):
    f_open = mock.mock_open(*args, **kargs)
    f_open.return_value.__iter__ = lambda self: iter(self.readline, "")
    return f_open


def test_default_file():
    config = Config()

    with mock.patch("builtins.open", mock_open(read_data="[alembic]")):
        alembic_config = config.make_alembic_config(None)
    assert alembic_config.config_file_name == "alembic.ini"


def test_set_file():
    config = Config(config_options={"file": "foo.ini"})

    with mock.patch("builtins.open", mock_open(read_data="[alembic]")):
        alembic_config = config.make_alembic_config(None)
    assert alembic_config.config_file_name == "foo.ini"


def test_set_config_file_name():
    config = Config(config_options={"config_file_name": "foo.ini"})

    with mock.patch("builtins.open", mock_open(read_data="[alembic]")):
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
