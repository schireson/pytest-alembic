import pytest
from pytest_mock_resources import create_postgres_fixture

alembic_engine = create_postgres_fixture()


@pytest.fixture
def alembic_config():
    return {"before_revision_data": {"bbbbbbbbbbbb": {"__tablename__": "meow.foo", "id": 9}}}
