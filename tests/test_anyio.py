import pytest
from pytest_alembic import tests
from pytest_alembic import create_alembic_fixture

from pytest_mock_resources import create_postgres_fixture
from sqlalchemy import Column, MetaData, Table, types

metadata = MetaData()

table = Table("t", metadata, Column("name", types.Unicode(), primary_key=True))

alembic = create_alembic_fixture()
alembic_engine = create_postgres_fixture(metadata)


@pytest.mark.anyio(scope='session')
async def test_upgrade(alembic):
    return tests.test_upgrade(alembic)
