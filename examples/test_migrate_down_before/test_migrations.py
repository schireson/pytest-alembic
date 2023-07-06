from sqlalchemy import text


def test_migrate_down_before_specific_revision(alembic_runner, alembic_engine):
    alembic_runner.migrate_up_to("head")

    alembic_runner.migrate_down_before("aaaaaaaaaaaa")
    with alembic_engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM foo")).fetchall()
    assert len(result) == 0
