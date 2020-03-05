import pytest
from pytest_mock_resources import create_postgres_fixture

alembic_engine = create_postgres_fixture()


@pytest.fixture
def alembic_config():
    return {
        "revision_upgrade_data": {
            "bbbbbbbbbbbb": [
                {"__tablename__": "foo", "id": 9},
                {"__tablename__": "foo", "id": 10},
                {"__tablename__": "bar", "id": 1},
            ],
            "cccccccccccc": [{"__tablename__": "bar", "id": 2, "foo_id": 10}],
        }
    }
