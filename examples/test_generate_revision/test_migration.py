import pytest
from sqlalchemy import text

from pytest_alembic.runner import MigrationContext


def test_generate_revision(alembic_runner: MigrationContext, alembic_engine):
    with pytest.raises(Exception, match=r".*no such table.*"), alembic_engine.connect() as conn:
        conn.execute(text("SELECT * FROM foo")).fetchall()

    alembic_runner.generate_revision(autogenerate=True, prevent_file_generation=False)
    alembic_runner.migrate_up_one()

    with alembic_engine.begin() as conn:
        conn.execute(text("INSERT INTO foo (id) VALUES (100)"))

    with alembic_engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM foo")).fetchall()
    assert len(result) == 1
