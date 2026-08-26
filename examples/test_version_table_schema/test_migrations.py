from sqlalchemy import text


def test_version_table_lives_in_the_configured_schema(alembic_runner, alembic_engine):
    """Assert alembic's bookkeeping table landed where `env.py` asked for it.

    Every other check in this example passes whether or not `version_table_schema` was
    honoured -- the migrations touch `foo`, not the version table, so ignoring the
    option entirely would still leave a green run. This is the one assertion that
    actually looks at where the version table went.
    """
    alembic_runner.migrate_up_to("heads")

    query = text(
        "SELECT table_schema FROM information_schema.tables WHERE table_name = 'alembic_version'"
    )
    with alembic_engine.connect() as conn:
        schemas = sorted(row.table_schema for row in conn.execute(query))

    assert schemas == ["version_table_schema"]
