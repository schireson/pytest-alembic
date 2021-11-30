import sqlalchemy as sa
from alembic import op

revision = "dddddddddddd"
down_revision = "cccccccccccc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("foo", sa.Column("bar_id", sa.Integer(), server_default="9"))


def downgrade():
    op.drop_column("foo", "bar_id")
