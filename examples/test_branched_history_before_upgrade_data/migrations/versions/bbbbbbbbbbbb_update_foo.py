import sqlalchemy as sa
from alembic import op

revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "foo",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("'2020-01-01'"),
            nullable=False,
        ),
    )


def downgrade():
    pass
