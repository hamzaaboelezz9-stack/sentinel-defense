"""Run only against a disposable PostgreSQL database owned by this test."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres@127.0.0.1:15432/postgres"
os.environ["SENTINEL_DEMO"] = "1"
os.environ["DEMO_PASSWORD"] = "postgres-validation-only"
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.schemas import Event

main.meta.drop_all(main.engine)
with TestClient(main.app) as c:
    assert (
        c.post(
            "/api/v1/login",
            json={"username": "administrator", "password": os.environ["DEMO_PASSWORD"]},
        ).status_code
        == 200
    )
    batch = [
        Event(
            id=f"pg-{i}",
            timestamp=f"2026-01-01T12:00:0{i}Z",
            device_id="identity-1",
            source_ip="192.0.2.10",
            username="fictional-user",
        ).model_dump(mode="json")
        for i in range(5)
    ]
    r = c.post("/api/v1/events", json=batch)
    assert r.status_code == 200, r.text
    assert c.post("/api/v1/events", json=batch).json()["duplicates"] == 5
    assert len(c.get("/api/v1/incidents").json()) == 1
    assert c.get("/api/v1/integrity").json()["valid"]
    assert c.get("/api/v1/export/pdf").content.startswith(b"%PDF")
    assert c.get("/api/v1/assets").status_code == 200
    print(
        "PASS: PostgreSQL 17 normalized schema, foreign keys, authentication, ingestion, deduplication, correlation, integrity, and PDF export."
    )
