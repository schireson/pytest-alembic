import pytest
from pytest_mock_resources import create_postgres_fixture
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine

pg = create_postgres_fixture()


@pytest.fixture
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
    return AsyncEngine(create_engine(url))
