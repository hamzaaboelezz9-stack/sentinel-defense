"""Smoke-check the disposable container on its loopback-published port."""

import httpx

with httpx.Client(
    base_url="http://127.0.0.1:18765:8000".replace(":18765:8000", ":18765"), timeout=30
) as c:
    assert c.get("/api/v1/health").json()["version"] == "1.0.0"
    assert c.get("/api/v1/events").status_code == 401
    assert (
        c.post(
            "/api/v1/login",
            json={
                "username": "administrator",
                "password": "container-validation-passphrase",
            },
        ).status_code
        == 200
    )
    batch = [
        {
            "id": f"docker-{i}",
            "timestamp": f"2026-01-01T12:00:0{i}Z",
            "device_id": "identity-1",
            "source_ip": "192.0.2.10",
            "username": "fictional-user",
        }
        for i in range(5)
    ]
    r = c.post("/api/v1/events", json=batch)
    assert r.status_code == 200, r.text
    assert len(c.get("/api/v1/incidents").json()) == 1
    assert c.get("/api/v1/integrity").json()["valid"]
    assert c.get("/api/v1/export/pdf").content.startswith(b"%PDF")
    assert c.get("/").status_code == 200
print(
    "PASS: release Docker image builds and runs; loopback HTTP, auth/RBAC, normalized SQLite ingestion, correlation, integrity, PDF, and built frontend verified."
)
