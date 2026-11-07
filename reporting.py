"""Reports derived from records, with escaped content and evidence fingerprints."""

import csv
import io
import json
from datetime import UTC, datetime
from html import escape

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .database.store import digest
from .playbooks import playbook


def build_data(
    events,
    incidents,
    assets,
    kind="executive",
    incident_id=None,
    performance=None,
    integrity=None,
):
    if kind not in ["executive", "incident", "technical"]:
        raise ValueError("Unknown report kind")
    selected = (
        [i for i in incidents if i["id"] == incident_id] if incident_id else incidents
    )
    if kind == "incident" and not selected:
        raise ValueError("Incident not found")
    refs = {id for i in selected for id in i["evidence"]}
    ev = [e for e in events if e["id"] in refs] if kind == "incident" else events
    return {
        "schema_version": "2.0",
        "simulation": True,
        "kind": kind,
        "timestamp": datetime.now(UTC).isoformat(),
        "events": ev,
        "incidents": selected,
        "assets": assets,
        "evidence_manifest": [{"id": e["id"], "sha256": digest(e)} for e in ev],
        "summary": {
            "events": len(ev),
            "incidents": len(selected),
            "active": sum(
                i["status"] not in ["resolved", "false_positive"] for i in selected
            ),
            "severity": {
                s: sum(i["severity"] == s for i in selected)
                for s in ["critical", "high", "medium", "low"]
            },
            "false_positive_classifications": sum(
                i["status"] == "false_positive" for i in selected
            ),
        },
        "performance": performance or {},
        "integrity": integrity or {},
        "limitations": [
            "Fictional synthetic environment; not operationally validated.",
            "Anomaly scores are not proof of malicious activity.",
            "Local hashes require independent custody to resist a privileged database rewrite.",
        ],
    }


def pdf(data):
    out = io.BytesIO()
    doc = SimpleDocTemplate(
        out,
        title="SENTINEL DEFENSE — " + data["kind"],
        author="SENTINEL DEFENSE",
        topMargin=35,
        bottomMargin=35,
    )
    styles = getSampleStyleSheet()
    story = []

    def text(value, style="BodyText"):
        story.append(
            Paragraph(escape(str(value)).replace("\n", "<br/>"), styles[style])
        )
        story.append(Spacer(1, 7))

    text("SENTINEL DEFENSE", "Title")
    text(data["kind"].upper() + " SECURITY BRIEFING", "Heading1")
    text("Defensive Engineering Demonstration — Synthetic Data Only")
    text(data["timestamp"] + " | Schema " + data["schema_version"])
    text("Executive summary", "Heading2")
    text(json.dumps(data["summary"]))
    text(
        "Priority: review critical and high-severity open cases, validate evidence, and document supervised decisions."
    )
    for limit in data["limitations"]:
        text(limit)
    if data["kind"] == "technical":
        text("Measured application performance", "Heading2")
        text(json.dumps(data["performance"]))
        text("Integrity verification: " + json.dumps(data["integrity"]))
        text(
            "Eight configured rules: brute force, password spray, disabled-account success, off-hours login, failure ratio, denied access, configuration change, and telemetry health."
        )
    for i in data["incidents"]:
        text(i["rule"].replace("_", " ").title(), "Heading2")
        text(i["id"])
        text(
            f"Severity {i['severity']} | Status {i['status']} | Assignment {i['assignment'] or 'Unassigned'}"
        )
        text(i["explanation"])
        text("First occurrence: " + i["timestamp"] + " | Asset: " + i["device_id"])
        text("Evidence identifiers: " + ", ".join(i["evidence"]))
        text("Analyst findings and decision history", "Heading3")
        for h in i["history"]:
            text(f"{h['timestamp']} | {h['actor']} | {h['status']} | {h['note']}")
        plan = playbook(i)
        text("Recommended investigation and mitigation", "Heading3")
        for step in plan["investigate"] + plan["containment"] + plan["verify"]:
            text("• " + step)
    text("Evidence manifest", "Heading2")
    for ev in data["evidence_manifest"]:
        text(ev["id"] + " | SHA-256 " + ev["sha256"])
    if data["kind"] == "incident":
        text("Event timeline", "Heading2")
        for e in sorted(data["events"], key=lambda e: e["timestamp"]):
            text(
                f"{e['timestamp']} | {e['id']} | {e['username']} | {e['source_ip']} | {e['event_type']} | {e['status']}"
            )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            36, 20, f"Synthetic data only | SENTINEL DEFENSE | Page {doc.page}"
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()


def csv_export(data):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(
        [
            "id",
            "rule",
            "severity",
            "status",
            "assignment",
            "evidence",
            "analyst_findings",
        ]
    )

    def safe(v):
        s = str(v)
        return "'" + s if s.startswith(("=", "+", "-", "@", "\t", "\r")) else s

    for i in data["incidents"]:
        w.writerow(
            [
                safe(v)
                for v in [
                    i["id"],
                    i["rule"],
                    i["severity"],
                    i["status"],
                    i["assignment"],
                    ";".join(i["evidence"]),
                    " | ".join(h["note"] for h in i["history"]),
                ]
            ]
        )
    return out.getvalue()
