import pytest


@pytest.fixture
def alembic_config():
    return {"revision_upgrade_data": {"bbbbbbbbbbbb": {"__tablename__": "foo", "id": 9}}}
