"""Normalized relational persistence with a compatibility adapter for v0.1 API shapes.

All schema changes are mirrored by Alembic migrations. Event hashes preserve original
canonical records; audit hashes are tamper-evident, not a substitute for off-host custody.
"""

import hashlib
import json

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    delete,
    event,
    select,
)
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def sqlite_foreign_keys(dbapi_connection, connection_record):
    if type(dbapi_connection).__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.close()


meta = MetaData()
legacy = Table(
    "records",
    meta,
    Column("kind", String(30), primary_key=True),
    Column("id", String(250), primary_key=True),
    Column("body", Text, nullable=False),
)
users = Table(
    "users",
    meta,
    Column("username", String(60), primary_key=True),
    Column("role", String(30), nullable=False),
    Column("password_hash", Text, nullable=False),
)
assets = Table(
    "assets",
    meta,
    Column("id", String(60), primary_key=True),
    Column("name", String(100), nullable=False),
    Column("ip", String(45), nullable=False),
    Column("parent_id", String(60), ForeignKey("assets.id")),
    Column("kind", String(40), nullable=False),
)
events = Table(
    "events",
    meta,
    Column("id", String(100), primary_key=True),
    Column("timestamp", String(40), nullable=False),
    Column("device_id", String(60), ForeignKey("assets.id"), nullable=False),
    Column("source_ip", String(45), nullable=False),
    Column("destination_ip", String(45)),
    Column("username", String(60), nullable=False),
    Column("category", String(30), nullable=False),
    Column("event_type", String(40), nullable=False),
    Column("status", String(20), nullable=False),
    Column("severity", String(20), nullable=False),
    Column("environment", String(40), nullable=False),
    Column("related_incident_id", String(250)),
    Column("label", Integer),
    Column("disabled_account", Boolean, nullable=False),
    Column("telemetry", Float, nullable=False),
    Column("sha256", String(64), nullable=False),
)
Index(
    "ix_events_source_asset_time",
    events.c.source_ip,
    events.c.device_id,
    events.c.timestamp,
)
incidents = Table(
    "incidents",
    meta,
    Column("id", String(250), primary_key=True),
    Column("rule", String(60), nullable=False),
    Column("rule_version", String(30), nullable=False),
    Column("severity", String(20), nullable=False),
    Column("explanation", Text, nullable=False),
    Column("timestamp", String(40), nullable=False),
    Column("device_id", String(60), ForeignKey("assets.id"), nullable=False),
    Column("status", String(30), nullable=False),
    Column("assignment", String(60), nullable=False),
    Column("classification", String(30), nullable=False),
)
evidence = Table(
    "incident_evidence",
    meta,
    Column(
        "incident_id",
        String(250),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "event_id",
        String(100),
        ForeignKey("events.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)
notes = Table(
    "notes",
    meta,
    Column("id", String(64), primary_key=True),
    Column(
        "incident_id",
        String(250),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("actor", String(60), ForeignKey("users.username")),
    Column("timestamp", String(40), nullable=False),
    Column("status", String(30), nullable=False),
    Column("assignment", String(60), nullable=False),
    Column("note", Text, nullable=False),
    Column("classification", String(30), nullable=False),
    Column("severity", String(20)),
)
sessions = Table(
    "sessions",
    meta,
    Column("id", String(64), primary_key=True),
    Column(
        "username",
        String(60),
        ForeignKey("users.username", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("expires", Float, nullable=False),
)
audits = Table(
    "audit",
    meta,
    Column("sequence", Integer, primary_key=True, autoincrement=True),
    Column("id", String(64), unique=True, nullable=False),
    Column("actor", String(60), nullable=False),
    Column("action", Text, nullable=False),
    Column("timestamp", String(40), nullable=False),
    Column("previous_hash", String(64), nullable=False),
    Column("sha256", String(64), nullable=False),
)
policies = Table(
    "policies",
    meta,
    Column("id", String(30), primary_key=True),
    Column("body", Text, nullable=False),
)
runs = Table(
    "ingestion_runs",
    meta,
    Column("id", String(64), primary_key=True),
    Column("timestamp", String(40), nullable=False),
    Column("accepted", Integer, nullable=False),
    Column("seconds", Float, nullable=False),
)

INVENTORY = [
    ("identity-1", "Identity gateway", "192.0.2.10", None, "identity"),
    ("hq-1", "HQ workstation", "192.0.2.20", "identity-1", "workstation"),
    ("app-1", "Application server", "198.51.100.10", "identity-1", "server"),
    ("db-1", "Database server", "198.51.100.20", "app-1", "database"),
    (
        "monitor-1",
        "Industrial monitoring simulator",
        "203.0.113.10",
        "app-1",
        "monitor",
    ),
    ("network-1", "Network simulator", "203.0.113.20", "identity-1", "network"),
]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def seed(c):
    for id, name, ip, parent, kind in INVENTORY:
        if not c.execute(select(assets.c.id).where(assets.c.id == id)).first():
            c.execute(
                assets.insert().values(
                    id=id, name=name, ip=ip, parent_id=parent, kind=kind
                )
            )


def ensure_asset(c, id, ip):
    if not c.execute(select(assets.c.id).where(assets.c.id == id)).first():
        c.execute(
            assets.insert().values(id=id, name=id, ip=ip, kind="fictional-import")
        )


def read_conn(c, kind):
    table = {
        "users": users,
        "events": events,
        "incidents": incidents,
        "audit": audits,
        "assets": assets,
        "sessions": sessions,
        "runs": runs,
    }.get(kind)
    if table is None:
        return []
    rows = [dict(r) for r in c.execute(select(table)).mappings()]
    if kind == "users":
        return [
            {"username": r["username"], "role": r["role"], "hash": r["password_hash"]}
            for r in rows
        ]
    if kind == "events":
        for r in rows:
            r.pop("sha256")
    if kind == "sessions":
        roles = {r["username"]: r["role"] for r in c.execute(select(users)).mappings()}
        for r in rows:
            r["role"] = roles.get(r["username"], "viewer")
    if kind == "incidents":
        links = {}
        histories = {}
        for r in c.execute(select(evidence)).mappings():
            links.setdefault(r["incident_id"], []).append(r["event_id"])
        for r in c.execute(
            select(notes).order_by(notes.c.timestamp, notes.c.id)
        ).mappings():
            n = dict(r)
            n.pop("id")
            iid = n.pop("incident_id")
            histories.setdefault(iid, []).append(n)
        for r in rows:
            r.update(
                evidence=sorted(links.get(r["id"], [])),
                history=histories.get(r["id"], []),
            )
    return rows


def upsert(c, table, key, values):
    condition = table.c[key] == values[key]
    if c.execute(select(table.c[key]).where(condition)).first():
        c.execute(table.update().where(condition).values(**values))
    else:
        c.execute(table.insert().values(**values))


def put_conn(c, kind, id, body):
    if kind == "users":
        upsert(
            c,
            users,
            "username",
            dict(username=id, role=body["role"], password_hash=body["hash"]),
        )
    elif kind == "events":
        body = {
            **body,
            "telemetry": float(body["telemetry"]),
            "label": None if body.get("label") is None else int(body["label"]),
        }
        ensure_asset(c, body["device_id"], body["source_ip"])
        c.execute(events.insert().values(**body, sha256=digest(body)))
    elif kind == "sessions":
        upsert(
            c,
            sessions,
            "id",
            dict(id=id, username=body["username"], expires=body["expires"]),
        )
    elif kind == "incidents":
        values = {k: body.get(k, "unreviewed") for k in incidents.c.keys()}
        upsert(c, incidents, "id", values)
        for eid in body["evidence"]:
            if not c.execute(
                select(evidence).where(
                    evidence.c.incident_id == id, evidence.c.event_id == eid
                )
            ).first():
                c.execute(evidence.insert().values(incident_id=id, event_id=eid))
        for n in body.get("history", []):
            n = {
                **n,
                "classification": n.get("classification", "unreviewed"),
                "severity": n.get("severity"),
            }
            nid = digest({"incident_id": id, **n})
            if not c.execute(select(notes.c.id).where(notes.c.id == nid)).first():
                c.execute(
                    notes.insert().values(
                        id=nid,
                        incident_id=id,
                        **{k: v for k, v in n.items() if k in notes.c.keys()},
                    )
                )
    elif kind == "audit":
        previous = (
            c.execute(
                select(audits.c.sha256).order_by(audits.c.sequence.desc()).limit(1)
            ).scalar()
            or "0" * 64
        )
        values = {**body, "previous_hash": previous}
        c.execute(audits.insert().values(**values, sha256=digest(values)))
    else:
        raise ValueError("Unsupported record type")


def read(engine, kind):
    with engine.connect() as c:
        return read_conn(c, kind)


def put(engine, kind, id, body):
    with engine.begin() as c:
        put_conn(c, kind, id, body)


def migrate_legacy(c):
    """Retain old records for rollback; migration is repeatable and preserves IDs/history."""
    seed(c)
    if c.execute(
        select(policies.c.id).where(policies.c.id == "legacy_import_complete")
    ).first():
        return
    rows = list(c.execute(select(legacy)).mappings())
    for kind in ["users", "events", "incidents", "audit"]:
        known = {
            r.get("username") if kind == "users" else r["id"]
            for r in read_conn(c, kind)
        }
        for r in rows:
            if r["kind"] == kind and r["id"] not in known:
                put_conn(c, kind, r["id"], json.loads(r["body"]))
    upsert(c, policies, "id", {"id": "legacy_import_complete", "body": "true"})


def reset(c):
    for table in [notes, evidence, incidents, events, runs]:
        c.execute(delete(table))


def verify(c):
    previous = "0" * 64
    for row in c.execute(select(audits).order_by(audits.c.sequence)).mappings():
        r = dict(row)
        r.pop("sequence")
        h = r.pop("sha256")
        if r["previous_hash"] != previous or digest(r) != h:
            return {"valid": False, "kind": "audit", "id": r["id"]}
        previous = h
    for row in c.execute(select(events)).mappings():
        r = dict(row)
        h = r.pop("sha256")
        if digest(r) != h:
            return {"valid": False, "kind": "event", "id": r["id"]}
    return {
        "valid": True,
        "audit_head": previous,
        "note": "Local tamper evidence only; a privileged attacker could rewrite the entire chain.",
    }
