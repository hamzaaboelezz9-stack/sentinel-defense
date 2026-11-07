import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "records",
        sa.Column("kind", sa.String(30), primary_key=True),
        sa.Column("id", sa.String(250), primary_key=True),
        sa.Column("body", sa.Text(), nullable=False),
    )


def downgrade():
    op.drop_table("records")
