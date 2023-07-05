from alembic import op
from sqlalchemy import text

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    conn = op.get_bind()
    conn.execute(text("DELETE FROM foo"))
