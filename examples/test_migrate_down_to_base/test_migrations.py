def test_migrate_down_to_base(alembic_runner, alembic_engine):
    alembic_runner.migrate_up_to("head")

    alembic_runner.migrate_down_to("base")
    result = alembic_engine.execute("SELECT * FROM pg_namespace where nspname = 'foo'").fetchall()
    assert len(result) == 0
