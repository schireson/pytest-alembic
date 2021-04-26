import pytest
import sqlalchemy


@pytest.fixture
def alembic_runner(alembic_config, alembic_engine):
    """Produce an alembic migration context in which to execute alembic tests."""
    import pytest_alembic

    with pytest_alembic.runner(config=alembic_config, engine=alembic_engine) as runner:
        yield runner


@pytest.fixture
def alembic_config():
    """Override this fixture to configure the exact alembic context setup required."""
    return {}


@pytest.fixture
def alembic_engine():
    """Override this fixture to provide pytest-alembic powered tests with a database handle."""
    return sqlalchemy.create_engine("sqlite:///")
