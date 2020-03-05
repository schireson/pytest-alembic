from alembic import op

revision = "cccccccccccc"
down_revision = "bbbbbbbbbbbb"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    result = conn.execute("SELECT * FROM foo").fetchall()
    assert len(result) == 2
    assert result[0].id == 9, f"{result[0].id} == 9"
    assert result[1].id == 10, f"{result[1].id} == 10"

    result = conn.execute("SELECT * FROM bar").fetchall()
    assert len(result) == 2
    assert result[0].id == 1, f"{result[0].id} == 1"
    assert result[0].foo_id == 9, f"{result[0].foo_id} == 9"
    assert result[1].id == 2, f"{result[1].id} == 2"
    assert result[1].foo_id == 10, f"{result[1].foo_id} == 10"


def downgrade():
    pass
