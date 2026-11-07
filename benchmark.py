import json
import os
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import UTC
from tempfile import TemporaryDirectory

with TemporaryDirectory() as d:
    os.environ.update(
        DATABASE_URL="sqlite:///" + d + "/benchmark.db",
        SENTINEL_DEMO="1",
        DEMO_PASSWORD="benchmark-only-passphrase",
    )
    from datetime import datetime, timedelta

    from fastapi.testclient import TestClient

    from backend.app.main import app

    with TestClient(app) as c:
        c.post(
            "/api/v1/login",
            json={"username": "administrator", "password": os.environ["DEMO_PASSWORD"]},
        )
        start = datetime(2026, 1, 1, 12, tzinfo=UTC)
        batch = [
            {
                "id": f"bench-{i}",
                "timestamp": (start + timedelta(seconds=i)).isoformat(),
                "device_id": "identity-1",
                "source_ip": f"192.0.2.{i % 200 + 1}",
                "username": "fictional-operator",
                "status": "success",
            }
            for i in range(10000)
        ]
        t = time.perf_counter()
        for offset in range(0, len(batch), 1000):
            r = c.post("/api/v1/events", json=batch[offset : offset + 1000])
            assert r.status_code == 200, r.text
        elapsed = time.perf_counter() - t
        assert r.status_code == 200
        lat = []
        for _ in range(10):
            t = time.perf_counter()
            assert len(c.get("/api/v1/events").json()) == 10000
            lat.append(time.perf_counter() - t)
        result = {
            "environment": "FastAPI TestClient, local SQLite, single process; not a network/load test",
            "batch_size": 1000,
            "total_events": 10000,
            "ingestion_seconds": elapsed,
            "events_per_second": 10000 / elapsed,
            "query_median_seconds": statistics.median(lat),
            "query_samples": 10,
        }
        Path("reports/benchmark.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
