# Security model
Synthetic educational inputs only. All ingestion source/destination addresses must be documentation IPv4 ranges. No scans, exploitation, credential theft, operational-device interaction, network blocking, account disabling, or executable AI output is implemented.

Argon2 hashes protect passwords. Random session tokens are stored only as SHA-256 keys with username relationships and expiry in the database. Cookies are HttpOnly and SameSite=Strict. Use SECURE_COOKIES=1 only with HTTPS; local HTTP needs the default false. Restart does not invalidate unexpired database sessions. Logout deletes the server-side session.

Viewer: read events, incidents, assets, policy, metrics, laboratory, and playbooks. Analyst: additionally ingest, investigate, verify evidence, and export. Administrator: additionally configure rules, view audit, reset, and apply retention. Every protected endpoint uses API dependencies, regardless of UI controls. Default demo accounts exist only with SENTINEL_DEMO=1 and an explicit 12+ character password. `scripts/create_user.py` provisions non-demo local users through an interactive hidden password prompt.

Same-origin write checks, no enabled cross-origin access, Pydantic validation, a 5 MB request bound, per-process API/login rate limits, security headers, escaped React text, escaped PDF text, formula-neutralized CSV cells, and parameterized SQLAlchemy queries address common training-application hazards. Unhandled responses avoid database or credential details. Structured logs omit request bodies, passwords, cookies, and tokens.

Event hashes and chained audit hashes provide local tamper evidence. They do not defeat a privileged attacker who can rewrite all records and hashes; independent custody is needed for that threat. Browser localStorage is fully controlled by its user and is not an authentication boundary. Do not store real secrets in the offline demo.

Retention deletes only expired, unreferenced events and preserves evidence. Restore is an offline operation: stop the app, validate the backup, and explicitly authorize replacement. Keep database backups private. No secrets, databases, session files, or environment files are included in the source ZIP.
