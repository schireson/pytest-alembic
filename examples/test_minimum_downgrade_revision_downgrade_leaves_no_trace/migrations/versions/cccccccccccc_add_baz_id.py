import sqlalchemy as sa
from alembic import op

revision = "cccccccccccc"
down_revision = "bbbbbbbbbbbb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("foo", sa.Column("baz_id", sa.Integer(), server_default="0"))


def downgrade():
    # Intentionally broken: does not undo the upgrade.
    # minimum_downgrade_revision must be set to "cccccccccccc" to skip this.
    pass
