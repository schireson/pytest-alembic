import pytest
import pytest_asyncio
from pytest_mock_resources import create_postgres_fixture
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine

pg = create_postgres_fixture()


try:
    fixture = pytest_asyncio.fixture
except AttributeError:
    fixture = pytest.fixture


@fixture
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
