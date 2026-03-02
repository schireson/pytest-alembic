import pytest
from pytest_mock_resources import create_postgres_fixture, PostgresConfig
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine

from pytest_alembic import tests

pg = create_postgres_fixture(async_=True)


@pytest.fixture(scope="session")
def pmr_postgres_config():
    return PostgresConfig(drivername="postgresql+asyncpg")


@pytest.fixture
def alembic_engine(pg):
    creds = pg.engine.url
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
async def test_upgrade(alembic_runner):
    tests.test_upgrade(alembic_runner)


@pytest.mark.anyio
async def test_single_head_revision(alembic_runner):
    tests.test_single_head_revision(alembic_runner)


@pytest.mark.anyio
async def test_up_down_consistency(alembic_runner):
    tests.test_up_down_consistency(alembic_runner)


@pytest.mark.anyio
async def test_model_definitions_match_ddl(alembic_runner):
    tests.test_model_definitions_match_ddl(alembic_runner)
