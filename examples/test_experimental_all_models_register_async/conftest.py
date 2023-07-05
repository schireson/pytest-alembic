import pytest
from pytest_mock_resources import create_postgres_fixture

import pytest_alembic.tests.experimental

alembic_engine = create_postgres_fixture(async_=True)


@pytest.fixture()
def alembic_config():
    return {"before_revision_data": {"bbbbbbbbbbbb": {"__tablename__": "foo", "id": 9}}}


def test_all_models_register_on_metadata(alembic_runner):
    pytest_alembic.tests.experimental.test_all_models_register_on_metadata(
        alembic_runner, "models", async_=True
    )
