from alembic import context

from backend.app.main import engine, meta

with engine.connect() as conn:
    context.configure(connection=conn, target_metadata=meta)
    with context.begin_transaction():
        context.run_migrations()
