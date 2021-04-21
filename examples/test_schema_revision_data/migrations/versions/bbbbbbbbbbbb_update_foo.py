from alembic import op

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    result = conn.execute("SELECT * FROM meow.foo").fetchall()
    assert len(result) == 1
    assert result[0].id == 9, f"{result[0].id} == 9"


def downgrade():
    pass
