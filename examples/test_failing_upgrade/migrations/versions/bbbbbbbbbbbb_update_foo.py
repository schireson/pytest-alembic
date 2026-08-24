revision = "bbbbbbbbbbbb"
down_revision = "aaaaaaaaaaaa"
branch_labels = None
depends_on = None


def upgrade():
    msg = "Something went wrong upgrading"
    raise ValueError(msg)


def downgrade():
    pass
