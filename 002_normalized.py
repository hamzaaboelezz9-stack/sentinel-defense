"""Normalize preview data without dropping its rollback copy."""

from alembic import op

from backend.app.database.store import meta, migrate_legacy

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    c = op.get_bind()
    for table in meta.sorted_tables:
        if table.name != "records":
            table.create(c, checkfirst=True)
    migrate_legacy(c)


def downgrade():
    c = op.get_bind()
    for table in reversed(meta.sorted_tables):
        if table.name != "records":
            table.drop(c, checkfirst=True)
