# SENTINEL DEFENSE 1.0 — acceptance and execution evidence
PASS is scoped to the behavior described below. Portfolio-release acceptance is not operational approval. No unknown-platform result is invented.

| Criterion | Status | Actual evidence / boundary |
|---|---|---|
| Browser demonstration opens | PASS | Embedded bundle served over localhost in Chromium with API calls blocked |
| Direct local-file opening | NOT TESTED | Attempted file:// navigation was blocked by administrator policy |
| Connected dashboard launches | PASS | Built React with local Uvicorn; browser workflows |
| FastAPI endpoints work | PASS | Backend integration tests, browser and Docker smoke checks |
| Events persist after restart | PASS | File-backed SQLite engine recreation |
| Synthetic incident generation | PASS | Connected and offline browser generation |
| Brute force and password spray | PASS | Threshold, isolation, event-time, and parity fixtures |
| All eight detection rules | PASS | Parameterized backend tests and generated browser parity fixtures |
| Duplicate incident suppression | PASS | Repeat batch, conflicts, rolling boundary, concurrent duplicate requests, late-bridge coalescing |
| Unauthorized requests rejected | PASS | 401/403 tests and Docker smoke check |
| Role restrictions enforced | PASS | Viewer/analyst/admin mutation, export, policy, audit and retention checks |
| Investigations saved | PASS | Status, severity, classification, assignment and notes through API/browser |
| History survives repeat processing | PASS | Duplicate replay, late coalescing, normalized persistence and migration tests |
| AI uses generated datasets | PASS | Raw event-window pipeline; event-derived features; independent split seeds |
| Metrics are reproducible | PASS | Held-out metrics and feature provenance tests; 500 evaluation rows |
| Rule-specific response playbooks | PASS | Eight generated versioned playbooks; response component and browser check |
| PDF generation | PASS | Actual backend PDF bytes in SQLite/PostgreSQL/Docker; technical/incident/executive templates |
| CSV and JSON exports | PASS | Real data, schema/evidence manifests, findings, CSV formula safety |
| Demonstration reset | PASS | API and offline browser test; users/audit retained |
| Frontend/backend integration | PASS | Auth, events, saved findings, model lab, advisory response, integrity, export |
| Automated backend tests | PASS | 25 pytest tests, reports/backend-tests.txt and pytest.xml |
| Frontend tests and build | PASS | 27 Vitest tests; strict TypeScript/Vite build |
| Browser regression | PASS | Connected and offline Chromium script, reload/reset and mobile-width checks |
| Normalized schema/migration | PASS | Foreign keys, legacy import, upgrade/downgrade/re-upgrade preserving original data |
| Backup and restore | PASS | Consistent SQLite backup, integrity-checked restore and restored row verification |
| Integrity and retention | PASS | Tampered event rejected by verification; referenced evidence survives retention |
| PostgreSQL | PASS | Real PostgreSQL 17 container schema/API/deduplication/integrity/PDF checks |
| Docker release runtime | PASS | Actual image build and loopback runtime with non-root file access corrected |
| Compose configuration | PASS | Both SQLite/PostgreSQL configurations validate with required variables |
| Full Compose orchestration | NOT TESTED | Individual Docker and PostgreSQL runtime paths were tested separately |
| 10,000-event benchmark | PASS | Ten 1,000-event batches and ten query samples; reports/benchmark.json |
| Dependency scans | PASS | npm audit and locked Python pip-audit completed; no known advisories reported at scan time |
| Ruff | PASS | Backend/scripts checks pass |
| Windows launcher execution | NOT TESTED | Batch file supplied; no Windows host available locally |
| Remote GitHub Actions | NOT TESTED | Linux/frontend/Windows jobs configured; no remote run or passing badge claimed |
| Independent new-user README trial | NOT TESTED | Launch/build/test paths exercised by implementer, not an independent evaluator |

Optional Arabic/RTL, light theme, and external LLM integration were not selected. Real-world deployment validation is outside this educational release. Read LIMITATIONS.md for scaling, custody, synthetic-model, platform, and security boundaries. Initial test failures were corrected; only the final executed outputs are summarized in the release manifest.
