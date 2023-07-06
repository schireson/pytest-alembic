from sqlalchemy import text


def test_migrate_up_to_specific_revision(alembic_runner, alembic_engine):
    alembic_runner.migrate_up_to("aaaaaaaaaaaa")

    with alembic_engine.begin() as conn:
        conn.execute(text("INSERT INTO foo (id) VALUES (100)"))

    alembic_runner.migrate_up_to("head")

    with alembic_engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM foo")).fetchall()
        assert len(result) == 1

        result = conn.execute(text("SELECT * FROM bar")).fetchall()
        assert len(result) == 0
