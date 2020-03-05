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
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "bar", sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    )


def downgrade():
    op.drop_table("bar")
    op.drop_table("foo")
