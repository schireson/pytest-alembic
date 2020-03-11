def test_migrate_down_before_specific_revision(alembic_runner, alembic_engine):
    alembic_runner.migrate_up_to("head")

    alembic_runner.migrate_down_before("aaaaaaaaaaaa")
    result = alembic_engine.execute("SELECT * FROM foo").fetchall()
    assert len(result) == 0
