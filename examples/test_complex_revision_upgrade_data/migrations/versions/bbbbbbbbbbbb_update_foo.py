from alembic import op
import sqlalchemy as sa

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("bar", sa.Column("foo_id", sa.Integer(), server_default="9"))
    op.alter_column("bar", "foo_id", server_default=None, nullable=False)


def downgrade():
    pass
