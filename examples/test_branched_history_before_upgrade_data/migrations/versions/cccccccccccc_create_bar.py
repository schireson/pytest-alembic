import sqlalchemy as sa
from alembic import op

revision = "cccccccccccc"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bar",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("bar")
