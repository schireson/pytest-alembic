from alembic import op
import sqlalchemy as sa

revision = "aaaaaaaaaaaa"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "foo",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
