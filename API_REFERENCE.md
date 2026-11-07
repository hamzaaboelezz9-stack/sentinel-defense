# API reference
OpenAPI is available at /docs. Base path /api/v1. Connected browser calls use the HttpOnly session cookie returned by POST /login. Every non-public route has a backend authorization dependency.

| Route | Method | Access / result |
|---|---|---|
| /health, /ready | GET | Public minimal application/database readiness |
| /login | POST | Login-throttled username/password; cookie response |
| /logout | POST | Authenticated session revocation |
| /me | GET | Authenticated username/role |
| /events | GET | Viewer+; validated stored events |
| /events | POST | Analyst+; batch limit, conflict rejection, transactional ingestion/correlation |
| /incidents | GET | Viewer+; evidence and analyst histories |
| /incidents/{id} | PATCH | Analyst+; status, severity, assignment, classification, note |
| /assets | GET | Viewer+; inventory relationships, event/incident counts, telemetry |
| /policy | GET / PUT | Viewer+ read; administrator update of validated rule policy |
| /lab?sensitivity=1 | GET | Viewer+; reproducible held-out evaluation (multiplier .25–3) |
| /anomalies?sensitivity=1 | GET | Viewer+; current incident feature contributions and model/rule separation |
| /playbook/{id} | GET | Viewer+; rule-specific advisory response, no action execution |
| /metrics | GET | Viewer+; measured ingestion and synthetic analyst timings |
| /integrity | GET | Analyst+; local event/audit fingerprint verification |
| /audit | GET | Administrator; persistent chained history |
| /reset | POST | Administrator; scenario records cleared, users/session/audit retained |
| /retention | POST | Administrator; expired unreferenced events removed |
| /export/{pdf,json,csv} | GET | Analyst+; kind=executive/incident/technical, optional incident_id |

Event schema: unique id, timezone-aware UTC-normalized timestamp, device ID, documentation-range source/destination IP, fictional username, category/type/status/severity, fixed synthetic environment, optional related incident and held-out label, disabled-account flag and 0–100 telemetry. Extra fields are forbidden. See schemas.py/OpenAPI for constraints.

Duplicate identical IDs are skipped; conflicting payloads return 409 and roll back the entire batch. Invalid records return safe structured 422 errors. Permissions return 401/403, limits 413/429, unsupported exports 404, and invalid report/policy parameters 422. An anomaly is not proof of malicious intent.
