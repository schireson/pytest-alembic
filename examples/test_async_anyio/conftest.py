import pytest
from pytest_mock_resources import create_postgres_fixture
from pytest_alembic import create_async_alembic_fixture
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine

from pytest_alembic.runner import MigrationContext

@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


alembic = create_async_alembic_fixture()
pg = create_postgres_fixture(scope='session')


@pytest.fixture(scope='session')
def alembic_engine(pg):
    creds = pg.pmr_credentials
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=creds.username,
        password=creds.password,
        host=creds.host,
        port=creds.port,
        database=creds.database,
    )
    return create_async_engine(url)


@pytest.mark.anyio
async def test_upgrade(alembic: MigrationContext):
    alembic.migrate_up_to('head')
