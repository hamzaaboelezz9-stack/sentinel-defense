import hashlib
import json
import logging
import os
import secrets
import threading
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, delete, select

from .core import settings
from .database import store
from .detection import Policy, correlate
from .lab import evaluate, explain
from .playbooks import playbook
from .schemas import Event, Login, Update

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("sentinel")
cfg = settings()

ROOT = Path(__file__).resolve().parents[2]
engine = create_engine(os.getenv("DATABASE_URL", f"sqlite:///{ROOT}/sentinel.db"))
meta = store.meta
records = store.legacy
lock = threading.RLock()
ph = PasswordHasher()
sessions = {}
limits = {}


def read(kind):
    with lock:
        return store.read(engine, kind)


def put(kind, id, body):
    with lock:
        return store.put(engine, kind, id, body)


def audit(actor, action):
    id = secrets.token_hex(12)
    with lock:
        put(
            "audit",
            id,
            {
                "id": id,
                "actor": actor,
                "action": action,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )


@asynccontextmanager
async def lifespan(app):
    meta.create_all(engine)
    with engine.begin() as c:
        store.migrate_legacy(c)
    if os.getenv("SENTINEL_DEMO") == "1" and not read("users"):
        password = os.getenv("DEMO_PASSWORD")
        if not password or len(password) < 12:
            raise RuntimeError("DEMO_PASSWORD of at least 12 characters is required")
        for role in ["administrator", "analyst", "viewer"]:
            put(
                "users",
                role,
                {"username": role, "role": role, "hash": ph.hash(password)},
            )
    yield


app = FastAPI(title="SENTINEL DEFENSE", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def security(request, call_next):
    started = time.perf_counter()
    if int(request.headers.get("content-length", "0")) > 5_000_000:
        return JSONResponse(status_code=413, content={"detail": "Request too large"})
    if request.url.path.startswith("/api/v1/"):
        key = "api:" + request.client.host
        now = time.time()
        with lock:
            bucket = [t for t in limits.get(key, []) if now - t < 60]
            if len(bucket) >= cfg.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Request rate limit exceeded"},
                    headers={"Retry-After": "60"},
                )
            limits[key] = bucket + [now]
    if request.method not in ["GET", "HEAD", "OPTIONS"]:
        origin = request.headers.get("origin")
        if origin and origin != str(request.base_url).rstrip("/"):
            return Response("Origin not allowed", 403)
    response = await call_next(request)
    response.headers.update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Cache-Control": "no-store",
        }
    )
    log.info(
        json.dumps(
            {
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "seconds": round(time.perf_counter() - started, 6),
            }
        )
    )
    return response


def user(request: Request):
    token = request.cookies.get("sentinel_session", "")
    s = next(
        (
            x
            for x in read("sessions")
            if x["id"] == hashlib.sha256(token.encode()).hexdigest()
        ),
        None,
    )
    if not s or s["expires"] < time.time():
        raise HTTPException(401, "Authentication required")
    return s


def writer(u=Depends(user)):
    if u["role"] == "viewer":
        raise HTTPException(403, "Analyst role required")
    return u


def admin(u=Depends(user)):
    if u["role"] != "administrator":
        raise HTTPException(403, "Administrator required")
    return u


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "simulation": True, "version": "1.0.0"}


@app.get("/api/v1/ready")
def ready():
    with engine.connect() as c:
        c.execute(select(records.c.id).limit(1))
    return {"database": "ready"}


@app.post("/api/v1/login")
def login(body: Login, request: Request, response: Response):
    key = request.client.host
    now = time.time()
    attempts = [t for t in limits.get(key, []) if now - t < 60]
    limits[key] = attempts + [now]
    if len(attempts) >= 10:
        raise HTTPException(429, "Try again later")
    match = next((x for x in read("users") if x["username"] == body.username), None)
    try:
        if not match:
            ph.verify(ph.hash("dummy-verification-value"), body.password)
            raise ValueError()
        ph.verify(match["hash"], body.password)
    except (VerificationError, InvalidHashError, ValueError):
        raise HTTPException(401, "Invalid credentials") from None
    token = secrets.token_urlsafe(32)
    put(
        "sessions",
        hashlib.sha256(token.encode()).hexdigest(),
        {"username": body.username, "expires": now + cfg.session_seconds},
    )
    response.set_cookie(
        "sentinel_session",
        token,
        httponly=True,
        samesite="strict",
        secure=os.getenv("SECURE_COOKIES") == "1",
        max_age=cfg.session_seconds,
    )
    audit(body.username, "login")
    return {"username": body.username, "role": match["role"]}


@app.post("/api/v1/logout")
def logout(request: Request, response: Response, u=Depends(user)):
    with engine.begin() as c:
        c.execute(
            delete(store.sessions).where(
                store.sessions.c.id
                == hashlib.sha256(
                    request.cookies.get("sentinel_session", "").encode()
                ).hexdigest()
            )
        )
    response.delete_cookie("sentinel_session")
    return {"ok": True}


@app.get("/api/v1/me")
def me(u=Depends(user)):
    return {"username": u["username"], "role": u["role"]}


@app.get("/api/v1/events")
def events(u=Depends(user)):
    return read("events")


@app.post("/api/v1/events")
def ingest(batch: list[Event], u=Depends(writer)):
    if len(batch) > cfg.max_batch:
        raise HTTPException(413, "Batch limit exceeded")
    started = time.perf_counter()
    accepted = 0
    with lock, engine.begin() as c:
        incoming = {}
        for event in batch:
            body = event.model_dump(mode="json")
            if event.id in incoming and incoming[event.id] != body:
                raise HTTPException(409, "Conflicting duplicate event ID")
            incoming[event.id] = body
        for id, body in incoming.items():
            old = (
                c.execute(select(store.events).where(store.events.c.id == id))
                .mappings()
                .first()
            )
            if old:
                old = dict(old)
                old.pop("sha256")
                if old != body:
                    raise HTTPException(409, "Conflicting duplicate event ID")
            else:
                store.put_conn(c, "events", id, body)
                accepted += 1
        groups = {(e["source_ip"], e["device_id"]) for e in incoming.values()}
        prior = store.read_conn(c, "incidents")
        for source, device in groups:
            group = [
                dict(r)
                for r in c.execute(
                    select(store.events).where(
                        store.events.c.source_ip == source,
                        store.events.c.device_id == device,
                    )
                ).mappings()
            ]
            for e in group:
                e.pop("sha256")
            for incident in correlate(group, current_policy(c)):
                candidates = [
                    i
                    for i in prior
                    if i["rule"] == incident["rule"]
                    and set(i["evidence"]) & set(incident["evidence"])
                ]
                saved = next(
                    (i for i in candidates if i["id"] == incident["id"]), None
                ) or (candidates[0] if candidates else None)
                if saved:
                    saved["evidence"] = sorted(
                        set(saved["evidence"]) | set(incident["evidence"])
                    )
                    for other in candidates:
                        if other["id"] == saved["id"]:
                            continue
                        saved["evidence"] = sorted(
                            set(saved["evidence"]) | set(other["evidence"])
                        )
                        known = {store.digest(h) for h in saved["history"]}
                        saved["history"].extend(
                            h for h in other["history"] if store.digest(h) not in known
                        )
                        for table in [store.notes, store.evidence]:
                            c.execute(
                                delete(table).where(table.c.incident_id == other["id"])
                            )
                        c.execute(
                            delete(store.incidents).where(
                                store.incidents.c.id == other["id"]
                            )
                        )
                        prior = [i for i in prior if i["id"] != other["id"]]
                        aid = secrets.token_hex(12)
                        store.put_conn(
                            c,
                            "audit",
                            aid,
                            {
                                "id": aid,
                                "actor": u["username"],
                                "action": "incident_coalesced:"
                                + other["id"]
                                + "->"
                                + saved["id"],
                                "timestamp": datetime.now(UTC).isoformat(),
                            },
                        )
                    incident = saved
                else:
                    incident.update(status="open", assignment="", history=[])
                store.put_conn(c, "incidents", incident["id"], incident)
        elapsed = time.perf_counter() - started
        c.execute(
            store.runs.insert().values(
                id=secrets.token_hex(12),
                timestamp=datetime.now(UTC).isoformat(),
                accepted=accepted,
                seconds=elapsed,
            )
        )
    audit(u["username"], f"ingest:{accepted}")
    return {
        "accepted": accepted,
        "duplicates": len(batch) - accepted,
        "processing_seconds": elapsed,
    }


@app.get("/api/v1/incidents")
def incidents(u=Depends(user)):
    return read("incidents")


@app.patch("/api/v1/incidents/{id:path}")
def update(id: str, body: Update, u=Depends(writer)):
    with lock:
        incident = next((i for i in read("incidents") if i["id"] == id), None)
        if not incident:
            raise HTTPException(404, "Incident not found")
        incident.update(
            status=body.status,
            assignment=body.assignment,
            classification=body.classification,
        )
        if body.severity is not None:
            incident["severity"] = body.severity
        incident["history"].append(
            {
                "actor": u["username"],
                "timestamp": datetime.now(UTC).isoformat(),
                **body.model_dump(),
            }
        )
        put("incidents", id, incident)
        audit(u["username"], f"incident_update:{id}")
    return incident


@app.get("/api/v1/playbook/{id:path}")
def response_plan(id: str, u=Depends(user)):
    incident = next((i for i in read("incidents") if i["id"] == id), None)
    if not incident:
        raise HTTPException(404, "Incident not found")
    return playbook(incident)


@app.get("/api/v1/lab")
def lab(sensitivity: float = 1.0, u=Depends(user)):
    if not 0.25 <= sensitivity <= 3:
        raise HTTPException(422, "Sensitivity must be between .25 and 3")
    return evaluate(sensitivity=sensitivity)


@app.get("/api/v1/audit")
def audits(u=Depends(admin)):
    return read("audit")


@app.post("/api/v1/reset")
def reset(u=Depends(admin)):
    with lock, engine.begin() as c:
        store.reset(c)
    audit(u["username"], "demo_reset")
    return {"ok": True}


@app.get("/api/v1/export/{format}")
def export(
    format: str,
    kind: str = "executive",
    incident_id: str | None = None,
    u=Depends(writer),
):
    from .reporting import build_data, csv_export, pdf

    with engine.connect() as c:
        check = store.verify(c)
    performance = metrics(u)
    if kind == "technical":
        model = evaluate()
        performance = {
            "runtime": performance,
            "model": {
                k: model[k]
                for k in [
                    "seed",
                    "splits",
                    "precision",
                    "recall",
                    "f1",
                    "specificity",
                    "false_positive_rate",
                    "confusion_matrix",
                ]
            },
        }
        evidence = ROOT / "reports/validation.json"
        performance["release_validation"] = (
            json.loads(evidence.read_text())
            if evidence.exists()
            else {"status": "Execution manifest not packaged"}
        )
    try:
        data = build_data(
            read("events"),
            read("incidents"),
            read("assets"),
            kind,
            incident_id,
            performance,
            check,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    audit(u["username"], "export:" + format + ":" + kind)
    if format == "json":
        body = json.dumps(data, indent=2)
        mime = "application/json"
    elif format == "csv":
        body = csv_export(data)
        mime = "text/csv"
    elif format == "pdf":
        body = pdf(data)
        mime = "application/pdf"
    else:
        raise HTTPException(404, "Unknown export format")
    return Response(
        body,
        media_type=mime,
        headers={
            "Content-Disposition": f"attachment; filename=sentinel-{kind}.{format}"
        },
    )


def current_policy(c=None):
    if c is None:
        with engine.connect() as conn:
            return current_policy(conn)
    raw = c.execute(
        select(store.policies.c.body).where(store.policies.c.id == "detection")
    ).scalar()
    return Policy.model_validate_json(raw) if raw else Policy()


@app.get("/api/v1/policy")
def get_policy(u=Depends(user)):
    return current_policy().model_dump()


@app.put("/api/v1/policy")
def set_policy(body: Policy, u=Depends(admin)):
    with lock, engine.begin() as c:
        store.upsert(
            c, store.policies, "id", {"id": "detection", "body": body.model_dump_json()}
        )
    audit(u["username"], "policy_update:" + body.model_dump_json())
    return body.model_dump()


@app.get("/api/v1/assets")
def inventory(u=Depends(user)):
    es = read("events")
    active = [
        i
        for i in read("incidents")
        if i["status"] not in ["resolved", "false_positive"]
    ]
    return [
        {
            **a,
            "event_count": sum(e["device_id"] == a["id"] for e in es),
            "active_incidents": sum(i["device_id"] == a["id"] for i in active),
            "telemetry": [
                {"timestamp": e["timestamp"], "value": e["telemetry"]}
                for e in es
                if e["device_id"] == a["id"] and e["event_type"] == "telemetry"
            ],
        }
        for a in read("assets")
    ]


@app.get("/api/v1/anomalies")
def anomalies(sensitivity: float = 1.0, u=Depends(user)):
    if not 0.25 <= sensitivity <= 3:
        raise HTTPException(422, "Sensitivity must be between .25 and 3")
    es = {e["id"]: e for e in read("events")}
    return [
        {
            "incident_id": i["id"],
            **explain(
                [es[id] for id in i["evidence"] if id in es], sensitivity=sensitivity
            ),
        }
        for i in read("incidents")
    ]


@app.get("/api/v1/integrity")
def integrity(u=Depends(writer)):
    with engine.connect() as c:
        return store.verify(c)


@app.get("/api/v1/metrics")
def metrics(u=Depends(user)):
    incidents = read("incidents")
    ack = []
    resolved = []
    for i in incidents:
        for status, out in [("acknowledged", ack), ("resolved", resolved)]:
            h = next((h for h in i["history"] if h["status"] == status), None)
            if h:
                out.append(
                    max(
                        0,
                        (
                            datetime.fromisoformat(h["timestamp"])
                            - datetime.fromisoformat(i["timestamp"])
                        ).total_seconds(),
                    )
                )
    runs = read("runs")
    seconds = sum(r["seconds"] for r in runs)
    count = sum(r["accepted"] for r in runs)
    return {
        "ingested_events": count,
        "processing_seconds": seconds,
        "events_per_second": count / seconds if seconds else None,
        "mean_time_to_acknowledge_seconds": sum(ack) / len(ack) if ack else None,
        "mean_time_to_resolve_seconds": sum(resolved) / len(resolved)
        if resolved
        else None,
        "acknowledged_samples": len(ack),
        "resolved_samples": len(resolved),
        "note": "Synthetic event-to-analyst elapsed time, not operational response performance.",
    }


@app.post("/api/v1/retention")
def retain(u=Depends(admin)):
    from datetime import timedelta

    cutoff = (datetime.now(UTC) - timedelta(days=cfg.retention_days)).isoformat()
    with lock, engine.begin() as c:
        referenced = select(store.evidence.c.event_id)
        result = c.execute(
            delete(store.events).where(
                store.events.c.timestamp < cutoff, ~store.events.c.id.in_(referenced)
            )
        )
    audit(u["username"], f"retention_removed:{result.rowcount}")
    return {"removed": result.rowcount, "cutoff": cutoff, "evidence_preserved": True}


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "errors": [
                {"location": list(e["loc"]), "message": e["msg"]} for e in exc.errors()
            ],
        },
    )


@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    log.error(
        json.dumps(
            {
                "event": "unhandled_error",
                "path": request.url.path,
                "exception_type": type(exc).__name__,
            }
        )
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal application error; consult local server logs."},
    )


if (ROOT / "demo").exists():
    app.mount("/demo", StaticFiles(directory=ROOT / "demo", html=True), name="demo")
if (ROOT / "frontend/dist").exists():
    app.mount(
        "/", StaticFiles(directory=ROOT / "frontend/dist", html=True), name="frontend"
    )
