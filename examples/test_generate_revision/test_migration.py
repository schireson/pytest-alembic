import pytest

from pytest_alembic.runner import MigrationContext


def test_generate_revision(alembic_runner: MigrationContext, alembic_engine):
    with pytest.raises(Exception):
        alembic_engine.execute("SELECT * FROM foo").fetchall()

    alembic_runner.generate_revision(autogenerate=True, prevent_file_generation=False)
    alembic_runner.migrate_up_one()

    alembic_engine.execute("INSERT INTO foo (id) VALUES (100)")

    result = alembic_engine.execute("SELECT * FROM foo").fetchall()
    assert len(result) == 1
