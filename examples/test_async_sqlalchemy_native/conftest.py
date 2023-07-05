import pytest
from pytest_mock_resources import create_postgres_fixture

alembic_engine = create_postgres_fixture(async_=True)


@pytest.fixture()
def alembic_config():
    return {"before_revision_data": {"bbbbbbbbbbbb": {"__tablename__": "foo", "id": 9}}}
