# Installation, deployment, migrations and recovery
## Local connected mode
Use README commands or the Windows launcher. Initial dependency installation needs network access. Prebuilt frontend assets are in frontend/dist. Node 24 is required only for source frontend builds. Run from a writable extracted directory.

The launcher calls scripts/run.py, creates demo users only for a new database, prints a generated password, and binds 127.0.0.1. Existing user credentials are never changed by setting DEMO_PASSWORD again. Preserve your original password. For non-demo provisioning use `python scripts/create_user.py operator --role administrator` and set SENTINEL_DEMO=0 before serving.

## SQLite Compose
Export a unique DEMO_PASSWORD of 12+ characters, then `docker compose up --build`. Only 127.0.0.1:8000 is published. The release Dockerfile consumes the validated prebuilt frontend and locked Python dependencies, runs as a non-root user, and includes a readiness health check. Rebuild frontend assets before building an image from modified source.

## PostgreSQL Compose
Export DEMO_PASSWORD and a URL-safe POSTGRES_PASSWORD, then `docker compose -f docker-compose.postgres.yml up --build`. The database is private to the Compose network and uses a persistent volume. Only the app is loopback-published. A separate PostgreSQL 17 container was used for real schema/API validation; the production-like orchestration file is not a public deployment authorization.

## Managed Cloud builds
The session proxy may need its CA supplied: `docker build --secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt -t sentinel-defense:1.0.0 .`. The optional BuildKit secret is consumed only for pip trust and is not copied into the final image. Do not disable TLS verification.

## Migrations
Fresh explicit migration: `python -m alembic -c backend/alembic.ini upgrade head` before startup. Version 001 creates the old record table; 002 creates normalized tables and imports users/events/incidents/evidence/notes/audits while preserving legacy IDs and history. Startup also creates missing tables and imports an unmarked legacy database for easy preview upgrades. For an unversioned legacy database, back it up, inspect its schema, stamp 001 deliberately, then upgrade; do not run migration 001 over its existing table blindly. The downgrade restores the original legacy snapshot, not new work made after normalization; always back up first.

## Backup and restore
`python scripts/backup.py sentinel.db backup.db` uses SQLite's consistent backup API. Stop the app before restore. `python scripts/restore.py backup.db restored.db` validates SQLite integrity and refuses an existing destination. To replace an existing stopped database explicitly, add --replace. Tests verify migration, rollback, re-upgrade, backup and restored records.

## Troubleshooting
Python not found: install Python 3.12+ with PATH enabled and reopen the terminal. PowerShell restrictions: the batch launcher invokes .venv\Scripts\python.exe directly, so activation scripts are unnecessary. Dependency errors: read pip's actual message, check network/disk space, and use requirements.lock. Port conflict: set PORT to an unused port. Login failure on an existing DB: use its original password, not the newly generated value. To discard a disposable lab, stop the app and back up/remove its database; never delete valued investigations to fix a login error. Browser file policy: serve the demo at /demo/?demo=1 using the local app, or use its private hosted version.
