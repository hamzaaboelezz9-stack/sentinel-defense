import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SENTINEL_DEMO"] = "1"
os.environ["DEMO_PASSWORD"] = "fictional-testing-password"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app import main
from backend.app.detection import correlate
from backend.app.lab import evaluate
from backend.app.schemas import Event

main.engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


def event(i=0, **kw):
    return dict(
        id=f"e{i}",
        timestamp=f"2026-01-01T12:00:{i:02d}+00:00",
        device_id="identity-1",
        source_ip="192.0.2.10",
        username="fictional-user",
        **kw,
    )


def normalized(es):
    return [Event(**e).model_dump(mode="json") for e in es]


@pytest.fixture
def client():
    main.meta.drop_all(main.engine)
    main.sessions.clear()
    main.limits.clear()
    with TestClient(main.app) as c:
        yield c


def login(c, role="administrator"):
    assert (
        c.post(
            "/api/v1/login",
            json={"username": role, "password": os.environ["DEMO_PASSWORD"]},
        ).status_code
        == 200
    )


def test_validation():
    for kw in [
        {"source_ip": "8.8.8.8"},
        {"timestamp": "invalid"},
        {"timestamp": "2026-01-01"},
        {"telemetry": 101},
    ]:
        d = event()
        d.update(kw)
        with pytest.raises(ValueError):
            Event(**d)


def test_rule_threshold_and_isolation():
    assert not correlate(normalized([event(i) for i in range(4)]))
    alerts = correlate(normalized([event(i) for i in range(5)]))
    assert len(alerts) == 1
    assert len(alerts[0]["evidence"]) == 5
    es = [event(i) for i in range(4)]
    e = event(4)
    e["source_ip"] = "198.51.100.1"
    assert not correlate(normalized(es + [e]))


def test_spray_and_late_arrival():
    es = []
    for i in range(5):
        e = event(i)
        e["username"] = f"user-{i}"
        es.append(e)
    assert {a["rule"] for a in correlate(normalized(es))} == {
        "brute_force",
        "password_spray",
    }
    assert correlate(normalized(es)) == correlate(normalized(es[::-1]))


def test_auth_and_roles(client):
    assert client.get("/api/v1/events").status_code == 401
    login(client, "viewer")
    assert client.post("/api/v1/events", json=[event()]).status_code == 403
    assert client.get("/api/v1/export/json").status_code == 403
    assert client.get("/api/v1/audit").status_code == 403
    assert client.get("/api/v1/events").status_code == 200
    client.post("/api/v1/logout")
    assert client.get("/api/v1/me").status_code == 401


def test_ingestion_and_history(client):
    login(client)
    batch = [event(i) for i in range(5)]
    assert client.post("/api/v1/events", json=batch).json()["accepted"] == 5
    assert client.post("/api/v1/events", json=batch).json()["duplicates"] == 5
    inc = client.get("/api/v1/incidents").json()
    assert len(inc) == 1
    result = client.patch(
        "/api/v1/incidents/" + inc[0]["id"],
        json={"status": "acknowledged", "note": "<script>untrusted</script>"},
    )
    assert result.status_code == 200
    client.post("/api/v1/events", json=batch)
    saved = client.get("/api/v1/incidents").json()[0]
    assert len(saved["history"]) == 1
    assert saved["status"] == "acknowledged"
    assert client.get("/api/v1/playbook/" + inc[0]["id"]).status_code == 200
    assert client.get("/api/v1/export/pdf").content.startswith(b"%PDF")
    assert client.get("/api/v1/export/csv").text.startswith("id,rule")
    assert client.get("/api/v1/export/json").json()["simulation"] is True
    assert client.post("/api/v1/reset").status_code == 200
    assert client.get("/api/v1/events").json() == []


def test_csrf_and_bad_login(client):
    assert (
        client.post(
            "/api/v1/login", json={"username": "x", "password": "x"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/login", json={}, headers={"Origin": "https://untrusted.example"}
        ).status_code
        == 403
    )


def test_lab_reproducible():
    a = evaluate()
    assert a == evaluate()
    assert sum(map(sum, a["confusion_matrix"])) == 500


@pytest.mark.parametrize(
    "rule,mutate,count",
    [
        ("disabled_account", {"disabled_account": True, "status": "success"}, 1),
        ("unusual_time", {"timestamp": "2026-01-01T23:00:00Z", "status": "success"}, 1),
        ("failure_ratio", {}, 10),
        ("access_denied", {"event_type": "access_denied", "category": "network"}, 5),
        (
            "configuration_change",
            {"event_type": "configuration_change", "category": "device"},
            1,
        ),
        ("device_health", {"telemetry": 95, "category": "device"}, 1),
    ],
)
def test_remaining_rules(rule, mutate, count):
    es = []
    for i in range(count):
        d = event(i)
        d.update(mutate)
        es.append(d)
    assert rule in {a["rule"] for a in correlate(normalized(es))}


def test_outside_window():
    es = [event(i) for i in range(4)]
    last = event(4)
    last["timestamp"] = "2026-01-01T12:03:00Z"
    assert not correlate(normalized(es + [last]))


def test_persistence_restart(tmp_path, monkeypatch):
    eng = create_engine("sqlite:///" + str(tmp_path / "persist.db"))
    monkeypatch.setattr(main, "engine", eng)
    with TestClient(main.app) as c:
        login(c)
        assert c.post("/api/v1/events", json=[event()]).status_code == 200
    eng.dispose()
    monkeypatch.setattr(
        main, "engine", create_engine("sqlite:///" + str(tmp_path / "persist.db"))
    )
    with TestClient(main.app) as c:
        login(c)
        assert len(c.get("/api/v1/events").json()) == 1
