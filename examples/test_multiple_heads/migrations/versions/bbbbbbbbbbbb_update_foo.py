import sqlalchemy as sa
from alembic import op

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("foo", sa.Column("name", sa.Unicode(), nullable=True))


def downgrade():
    op.drop_column("foo", "name")
