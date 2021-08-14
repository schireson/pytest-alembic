import pytest
import alembic.config


@pytest.fixture
def alembic_config():
    config = alembic.config.Config("alembic.ini")
    config.set_main_option("script_location", "alembic")
    return config
