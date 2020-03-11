def test_migrate_up_to_specific_revision(alembic_runner, alembic_engine):
    alembic_runner.migrate_up_to("aaaaaaaaaaaa")

    alembic_engine.execute("INSERT INTO foo (id) VALUES (100)")

    alembic_runner.roundtrip_next_revision()

    result = alembic_engine.execute("SELECT * FROM foo").fetchall()
    assert len(result) == 0
