from alembic import op

revision = "aaaaaaaaaaaa"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("create schema foo")


def downgrade():
    op.execute("drop schema foo")
