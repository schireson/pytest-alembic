import sqlalchemy as sa
from alembic import op

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("foo", sa.Column("foo_id", sa.Integer(), server_default="0"))


def downgrade():
    op.drop_column("foo", "foo_id")
