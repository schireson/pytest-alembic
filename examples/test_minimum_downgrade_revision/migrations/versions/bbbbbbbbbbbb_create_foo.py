import sqlalchemy as sa
from alembic import op

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind()
    op.execute("DELETE FROM foo")


def downgrade():
    raise ValueError("Cannot downgrade here!")
