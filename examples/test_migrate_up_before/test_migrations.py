def test_migrate_up_before_specific_revision(alembic_runner, alembic_engine):
    alembic_runner.migrate_up_before("bbbbbbbbbbbb")

    alembic_runner.insert_into("foo", {"id": 100})

    table = alembic_runner.table_at_revision("foo", revision="aaaaaaaaaaaa")

    with alembic_engine.connect() as conn:
        result = conn.execute(table.select()).fetchall()
    assert len(result) == 1
    assert result[0].id == 100
