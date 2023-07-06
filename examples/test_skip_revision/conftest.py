import pytest

from pytest_alembic import Config


@pytest.fixture()
def alembic_config():
    return Config(skip_revisions=["bbbbbbbbbbbb"])
