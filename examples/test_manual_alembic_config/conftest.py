import alembic.config
import pytest


@pytest.fixture()
def alembic_config():
    config = alembic.config.Config("alembic.ini")
    config.set_main_option("script_location", "alembic")
    return config
