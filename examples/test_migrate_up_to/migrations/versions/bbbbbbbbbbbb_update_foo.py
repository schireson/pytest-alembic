from alembic import op

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    conn = op.get_bind()
    conn.execute("DELETE FROM foo")
