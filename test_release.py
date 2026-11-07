"""Regression tests for the full-release upgrades."""

import json
import os
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from sqlalchemy import update

from backend.app import main
from backend.app.database import store
from backend.app.detection import Policy, correlate
from backend.app.lab import evaluate, explain, features, sample_windows
from backend.tests.test_system import client as client
from backend.tests.test_system import event, login, normalized


def test_rolling_cooldown_boundary():
    es = []
    for i in range(6):
        e = event(i)
        e["timestamp"] = (
            f"2026-01-01T12:{1 if i < 3 else 2:02d}:{57 + i if i < 3 else i - 3:02d}Z"
        )
        es.append(e)
    alerts = correlate(normalized(es))
    assert len(alerts) == 1
    assert len(alerts[0]["evidence"]) == 6
    assert not correlate(normalized(es), Policy(brute_count=8))
    with pytest.raises(ValueError):
        Policy(working_start=20, working_end=8)


def test_duplicate_conflict_is_atomic(client):
    login(client)
    assert client.post("/api/v1/events", json=[event()]).status_code == 200
    changed = event()
    changed["username"] = "different"
    assert client.post("/api/v1/events", json=[event(1), changed]).status_code == 409
    assert len(client.get("/api/v1/events").json()) == 1


def test_durable_session_and_integrity(client):
    login(client)
    client.post("/api/v1/events", json=[event()])
    main.sessions.clear()
    assert client.get("/api/v1/me").status_code == 200
    assert client.get("/api/v1/integrity").json()["valid"]
    with main.engine.begin() as c:
        c.execute(update(store.events).values(username="tampered"))
    assert not client.get("/api/v1/integrity").json()["valid"]


def test_policy_roles_retention_and_classification(client):
    login(client)
    p = client.get("/api/v1/policy").json()
    p["brute_count"] = 6
    assert client.put("/api/v1/policy", json=p).status_code == 200
    client.post("/api/v1/events", json=[event(i) for i in range(6)])
    i = client.get("/api/v1/incidents").json()[0]
    r = client.patch(
        "/api/v1/incidents/" + i["id"],
        json={
            "status": "acknowledged",
            "classification": "confirmed",
            "severity": "critical",
            "note": "Validated fictional case",
        },
    )
    assert r.json()["classification"] == "confirmed"
    assert r.json()["severity"] == "critical"
    assert client.get("/api/v1/playbook/" + i["id"]).json()["rule"] == "brute_force"
    assert client.post("/api/v1/retention").json()["evidence_preserved"]
    assert len(client.get("/api/v1/events").json()) == 6
    client.post("/api/v1/logout")
    login(client, "viewer")
    assert client.put("/api/v1/policy", json=p).status_code == 403
    assert client.post("/api/v1/retention").status_code == 403


def test_rich_reports(client):
    login(client)
    client.post("/api/v1/events", json=[event(i) for i in range(5)])
    i = client.get("/api/v1/incidents").json()[0]
    client.patch(
        "/api/v1/incidents/" + i["id"],
        json={"note": "=FORMULA()", "assignment": "+untrusted"},
    )
    data = client.get(
        "/api/v1/export/json", params={"kind": "incident", "incident_id": i["id"]}
    ).json()
    assert data["evidence_manifest"]
    assert data["incidents"][0]["history"][0]["note"] == "=FORMULA()"
    assert "'+untrusted" in client.get("/api/v1/export/csv").text
    assert client.get("/api/v1/export/pdf?kind=technical").content.startswith(b"%PDF")
    assert client.get("/api/v1/export/pdf?kind=invalid").status_code == 422
    assert client.get("/api/v1/metrics").json()["ingested_events"] == 5


def test_concurrent_idempotent_ingestion(client):
    login(client)
    batch = [event(i) for i in range(5)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(
            pool.map(lambda _: client.post("/api/v1/events", json=batch), range(4))
        )
    assert all(r.status_code == 200 for r in responses)
    assert sum(r.json()["accepted"] for r in responses) == 5
    assert len(client.get("/api/v1/incidents").json()) == 1


def test_event_feature_provenance():
    windows, y = sample_windows(44, 10)
    x = features(windows[0])
    assert x[5] == len(windows[0])
    assert x[0] == sum(e["status"] == "failure" for e in windows[0])
    altered = [{**e, "label": 1 - e["label"]} for e in windows[0]]
    assert features(altered) == x
    model = evaluate()
    assert model["split_seeds"] == [42, 43, 44]
    assert "isolation_forest" in model
    assert sum(
        f["contribution"] for f in explain(windows[0])["features"]
    ) == pytest.approx(explain(windows[0])["score"])


def test_normalized_migration_and_backup(tmp_path):
    root = Path(__file__).resolve().parents[2]
    db = tmp_path / "legacy.db"
    env = {**os.environ, "DATABASE_URL": "sqlite:///" + str(db)}

    def migration(target):
        subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                "backend/alembic.ini",
                "upgrade",
                target,
            ],
            cwd=root,
            env=env,
            check=True,
            capture_output=True,
        )

    migration("001")
    from argon2 import PasswordHasher

    e = normalized([event()])[0]
    with sqlite3.connect(db) as c:
        c.execute(
            "INSERT INTO records VALUES(?,?,?)",
            (
                "users",
                "administrator",
                json.dumps(
                    {
                        "username": "administrator",
                        "role": "administrator",
                        "hash": PasswordHasher().hash("migration-only-passphrase"),
                    }
                ),
            ),
        )
        c.execute(
            "INSERT INTO records VALUES(?,?,?)", ("events", e["id"], json.dumps(e))
        )
    migration("head")
    with sqlite3.connect(db) as c:
        assert c.execute("select count(*) from events").fetchone()[0] == 1
        assert c.execute("select count(*) from assets").fetchone()[0] >= 6
    backup = tmp_path / "backup.db"
    subprocess.run(
        [sys.executable, "scripts/backup.py", str(db), str(backup)],
        cwd=root,
        check=True,
        capture_output=True,
    )
    with sqlite3.connect(backup) as c:
        assert c.execute("select count(*) from events").fetchone()[0] == 1
    restored = tmp_path / "restored.db"
    subprocess.run(
        [sys.executable, "scripts/restore.py", str(backup), str(restored)],
        cwd=root,
        check=True,
        capture_output=True,
    )
    with sqlite3.connect(restored) as c:
        assert c.execute("select count(*) from events").fetchone()[0] == 1
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            "backend/alembic.ini",
            "downgrade",
            "001",
        ],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
    )
    migration("head")
    with sqlite3.connect(db) as c:
        assert c.execute("select count(*) from events").fetchone()[0] == 1


def test_validation_size_and_role_matrix(client):
    login(client, "analyst")
    assert client.get("/api/v1/audit").status_code == 403
    assert client.post("/api/v1/reset").status_code == 403
    assert client.get("/api/v1/export/json").status_code == 200
    assert client.post("/api/v1/events", json=[{"id": "bad"}]).status_code == 422
    assert (
        client.post(
            "/api/v1/events", json=[event(i % 50) for i in range(1001)]
        ).status_code
        == 413
    )
    assert client.get("/api/v1/health").headers["x-content-type-options"] == "nosniff"


def test_late_bridge_merges_incidents_and_preserves_notes(client):
    from datetime import UTC, datetime, timedelta

    login(client)
    base = datetime(2026, 1, 1, 12, tzinfo=UTC)

    def e(id, seconds):
        d = event()
        d.update(id=id, timestamp=(base + timedelta(seconds=seconds)).isoformat())
        return d

    bursts = [e("first-" + str(i), i) for i in range(6)] + [
        e("second-" + str(i), 180 + i) for i in range(6)
    ]
    assert client.post("/api/v1/events", json=bursts).status_code == 200
    initial = client.get("/api/v1/incidents").json()
    assert len(initial) == 2
    for i in initial:
        client.patch(
            "/api/v1/incidents/" + i["id"], json={"note": "Preserve " + i["id"]}
        )
    bridge = [
        e("bridge-" + str(i), seconds) for i, seconds in enumerate(range(10, 180, 10))
    ]
    assert client.post("/api/v1/events", json=bridge).status_code == 200
    merged = [
        i for i in client.get("/api/v1/incidents").json() if i["rule"] == "brute_force"
    ]
    assert len(merged) == 1
    assert len(merged[0]["history"]) == 2
