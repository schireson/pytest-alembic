import pytest
from pytest_mock_resources import create_postgres_fixture

alembic_engine = create_postgres_fixture()


@pytest.fixture()
def alembic_config():
    return {"minimum_downgrade_revision": "cccccccccccc"}
