import pytest


@pytest.fixture
def alembic_config():
    return {"before_revision_data": {"bbbbbbbbbbbb": {"__tablename__": "foo", "id": 9}}}
