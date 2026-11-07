# Verification and reproducibility
Backend: `python -m pytest backend/tests --cov=backend.app --junitxml=reports/pytest.xml`. Frontend: `cd frontend && npm ci && npm run build && npm test`. Style: `ruff check backend scripts`. Security: `pip-audit --disable-pip --no-deps -r backend/requirements.lock` and `npm audit`. Scans represent known advisories at execution time, not proof of security.

Browser setup: install Python Playwright and Chromium. scripts/browser_test.py uses /usr/bin/chromium; adjust the executable on another OS. Start a disposable test app:
```
SENTINEL_DEMO=1 DEMO_PASSWORD=local-validation-passphrase DATABASE_URL=sqlite:////absolute/path/disposable.db python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8767
SENTINEL_TEST_URL=http://127.0.0.1:8767 python scripts/browser_test.py
```
The browser test resets that instance's scenario data. Never point it at valued investigations. It validates login, events, severity/classification, saved notes, AI evaluation, response, integrity, PDF, offline generation/evaluation/persistence/reset, mobile width and JS errors. Offline API requests are blocked during testing. Direct file navigation was attempted and blocked by browser administrator policy.

Backend tests cover all eight rules, threshold negatives, source isolation, rolling boundaries, conflict rollback, concurrent deduplication, late-bridge coalescing/history, DB sessions, auth/RBAC, origin rejection, validation, reports, hashing/tamper detection, retention, feature provenance, seeded evaluation, file-backed persistence, Alembic upgrade/downgrade, backup and restore. Coverage does not establish universal correctness.

Twenty-five Python-generated fixtures compare browser detection IDs/rules/severity/evidence and feature extraction. Additional Vitest tests verify held-out metric recomputation and the response-assistant component. Rebuild fixtures with scripts/generate_parity.py after intentional rule changes; review changes before accepting new fixtures.

scripts/benchmark.py measures ten 1,000-event batches and ten query samples in a local TestClient/SQLite harness. scripts/validate_postgres.py and validate_docker.py are destructive only to their specifically named disposable test instances; inspect scripts before reuse. Test output files and a validation manifest are included in reports. Remote CI/Windows execution is not claimed.
