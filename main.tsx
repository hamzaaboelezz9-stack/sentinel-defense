import logo from "./logo.svg";
import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter, useLocation, useNavigate } from "react-router-dom";
import "./style.css";
import type { Row } from "./types";
import {
  api,
  offline,
  inventory,
  generate,
  download,
  localRead,
  hash,
} from "./services/api";
import { Analytics } from "./components/Analytics";
import { Laboratory } from "./components/Laboratory";
import { ResponseAssistant } from "./components/ResponseAssistant";
import { Administration } from "./components/Administration";
import { Network } from "./components/Network";
const pages = [
  "Overview",
  "Monitoring",
  "Investigations",
  "Network",
  "AI Laboratory",
  "Response assistant",
  "Reports",
  "Engineering demo",
  "Knowledge",
  "Administration",
];
function App() {
  const route = useLocation(),
    navigate = useNavigate();
  const page = decodeURIComponent(route.pathname.slice(1)) || "Overview";
  const setPage = (p: string) => navigate("/" + encodeURIComponent(p));
  const [user, setUser] = useState<Row | null>(
      offline ? { role: "administrator", username: "offline-presenter" } : null,
    ),
    [events, setEvents] = useState<Row[]>([]),
    [incidents, setIncidents] = useState<Row[]>([]),
    [selected, setSelected] = useState<string>(""),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false),
    [query, setQuery] = useState(""),
    [lab, setLab] = useState<Row | null>(null),
    [stage, setStage] = useState(0),
    [status, setStatus] = useState("open"),
    [note, setNote] = useState(""),
    [assignment, setAssignment] = useState("");
  const [assetRows, setAssetRows] = useState<Row[]>([]),
    [metrics, setMetrics] = useState<Row>({}),
    [health, setHealth] = useState("Checking"),
    [live, setLive] = useState(false),
    [range, setRange] = useState(0),
    [category, setCategory] = useState("all"),
    [severity, setSeverity] = useState("all"),
    [reportKind, setReportKind] = useState("executive");
  const [incidentSeverity, setIncidentSeverity] = useState("medium"),
    [classification, setClassification] = useState("unreviewed");
  const incident = incidents.find((i) => i.id === selected) || incidents[0],
    canWrite = user?.role !== "viewer";
  useEffect(() => {
    if (incident) {
      setStatus(incident.status);
      setIncidentSeverity(incident.severity);
      setClassification(incident.classification || "unreviewed");
      setAssignment(incident.assignment || "");
    }
  }, [
    incident?.id,
    incident?.status,
    incident?.assignment,
    incident?.severity,
    incident?.classification,
  ]);
  async function refresh() {
    const [e, i, a, m, h] = await Promise.all([
      api("/events"),
      api("/incidents"),
      api("/assets"),
      api("/metrics"),
      api("/ready"),
    ]);
    setEvents(e);
    setIncidents(i);
    setAssetRows(a);
    setMetrics(m);
    setHealth(h.database || h.status);
  }
  async function action(fn: () => Promise<any>) {
    setError("");
    setLoading(true);
    try {
      await fn();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    if (offline) refresh();
    else
      api("/me")
        .then((u) => {
          setUser(u);
          refresh();
        })
        .catch(() => {});
  }, []);
  useEffect(() => {
    if (!live || !user) return;
    const id = setInterval(
      () => refresh().catch((e) => setError(String(e))),
      5000,
    );
    return () => clearInterval(id);
  }, [live, user]);
  async function simulate(kind: string) {
    await api("/events", "POST", generate(kind));
    await refresh();
  }
  async function report(format: string) {
    if (offline) {
      const d = localRead();
      if (format === "pdf") {
        window.print();
        return;
      }
      const selected =
        reportKind === "incident" && incident
          ? d.incidents.filter((i: Row) => i.id === incident.id)
          : d.incidents;
      const data = {
        schema_version: "2.0",
        kind: reportKind,
        simulation: true,
        timestamp: new Date().toISOString(),
        events: d.events,
        incidents: selected,
        assets: assetRows,
        metrics,
        evidence_manifest: await Promise.all(
          d.events.map(async (e: Row) => ({ id: e.id, sha256: await hash(e) })),
        ),
        limitations: [
          "Synthetic educational data only",
          "Browser-local data is user controlled",
          "No operational validation",
        ],
      };
      const safe = (x: string) => (/^[=+@\t\r-]/.test(x) ? "'" + x : x);
      const body =
        format === "json"
          ? JSON.stringify(data, null, 2)
          : "id,rule,severity,status,findings\n" +
            selected
              .map((i: Row) =>
                [
                  i.id,
                  i.rule,
                  i.severity,
                  i.status,
                  i.history.map((h: Row) => h.note).join(" | "),
                ]
                  .map((x) => JSON.stringify(safe(x)))
                  .join(","),
              )
              .join("\n");
      download(
        "sentinel-" + reportKind + "." + format,
        body,
        format === "json" ? "application/json" : "text/csv",
      );
    } else {
      const r = await fetch(
        "/api/v1/export/" +
          format +
          "?kind=" +
          reportKind +
          (reportKind === "incident" && incident
            ? "&incident_id=" + encodeURIComponent(incident.id)
            : ""),
      );
      if (!r.ok) throw Error("Report generation denied");
      const blob = await r.blob();
      const url = URL.createObjectURL(blob),
        a = document.createElement("a");
      a.href = url;
      a.download = "sentinel-" + reportKind + "." + format;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  }
  const active = incidents.filter(
    (i) => !["resolved", "false_positive"].includes(i.status),
  );
  const latest = Math.max(0, ...events.map((e) => Date.parse(e.timestamp)));
  const filtered = events.filter(
    (e) =>
      JSON.stringify(e).toLowerCase().includes(query.toLowerCase()) &&
      (!range || latest - Date.parse(e.timestamp) <= range) &&
      (category === "all" || e.category === category) &&
      (severity === "all" || e.severity === severity),
  );
  return (
    <>
      <aside className="sidebar">
        <div className="brand">
          <img src={logo} alt="" width="38" height="45" />
          <span>
            SENTINEL<small>DEFENSE</small>
          </span>
        </div>
        <div className="sectionLabel">SECURITY OPERATIONS</div>
        <nav>
          {pages.map((p, i) => (
            <button
              key={p}
              className={p === page ? "active" : ""}
              onClick={() => setPage(p)}
            >
              <span>
                {["◈", "≋", "▣", "⌘", "◇", "⊞", "▤", "▷", "ⓘ", "⚙"][i]}
              </span>
              {p}
            </button>
          ))}
        </nav>
        <div className="sideFoot">
          <span className="dot" /> Synthetic lab environment
          <br />
          <small>Engineering release · v1.0.0</small>
        </div>
      </aside>
      <main>
        <header>
          <div>
            Workspace <span>/</span> {page}
          </div>
          <div className="account">
            <span className="badge">
              {offline ? "OFFLINE SIMULATION" : "CONNECTED LAB"}
            </span>
            {user?.username}
            {user && !offline && (
              <button
                onClick={() =>
                  action(async () => {
                    await api("/logout", "POST");
                    setUser(null);
                  })
                }
              >
                Sign out
              </button>
            )}
          </div>
        </header>
        <div className="banner">
          Defensive Engineering Demonstration — Synthetic Data Only{" "}
          <span>No operational systems connected</span>
        </div>
        <section className="content">
          <div className="title">
            <div>
              <div className="eyebrow">
                INTELLIGENT CYBER DEFENSE & SECURITY OPERATIONS PLATFORM
              </div>
              <h1>{page === "Overview" ? "Security overview" : page}</h1>
              <p>
                Understand the signal. Investigate the evidence. Keep the human
                in control.
              </p>
            </div>
            {user && (
              <button disabled={loading} onClick={() => action(refresh)}>
                ↻ Refresh data
              </button>
            )}
          </div>
          {error && (
            <div role="alert" className="error">
              {error}
            </div>
          )}
          {loading && <div role="status">Processing…</div>}
          {!user ? (
            <form
              className="panel login"
              onSubmit={(e) => {
                e.preventDefault();
                const f = new FormData(e.currentTarget);
                action(async () => {
                  const u = await api("/login", "POST", {
                    username: f.get("username"),
                    password: f.get("password"),
                  });
                  setUser(u);
                  await refresh();
                });
              }}
            >
              <h2>Sign in to the training lab</h2>
              <p>
                Use the development account provisioned by your local
                administrator. No credentials are embedded in this application.
              </p>
              <label>
                Username
                <input name="username" autoComplete="username" required />
              </label>
              <label>
                Password
                <input
                  type="password"
                  name="password"
                  autoComplete="current-password"
                  required
                />
              </label>
              <button className="primary">Sign in</button>
              <p>
                Want an installation-free demonstration?{" "}
                <a href="?demo=1">Open browser-local simulation</a>
              </p>
            </form>
          ) : (
            <>
              {(page === "Overview" || page === "Monitoring") && (
                <>
                  <div className="metrics">
                    {[
                      [
                        "Security events",
                        events.length,
                        "Validated fictional records",
                      ],
                      [
                        "Active incidents",
                        active.length,
                        "Awaiting analyst disposition",
                      ],
                      [
                        "Critical incidents",
                        active.filter((i) => i.severity === "critical").length,
                        "Immediate review recommended",
                      ],
                      [
                        "Monitored fictional assets",
                        assetRows.length,
                        "Fictional training inventory",
                      ],
                    ].map(([name, v, sub]) => (
                      <article className="panel metric" key={name}>
                        <small>{name}</small>
                        <strong>{v}</strong>
                        <span>{sub}</span>
                      </article>
                    ))}
                  </div>
                  <div className="grid">
                    <article className="panel">
                      <div className="panelHead">
                        <h2>Detection distribution</h2>
                        <span className="badge">ACTUAL RECORDS</span>
                      </div>
                      {["critical", "high", "medium", "low"].map((level) => (
                        <div className="barRow" key={level}>
                          <span>{level}</span>
                          <div>
                            <i
                              className={level}
                              style={{
                                width: `${incidents.length ? (incidents.filter((i) => i.severity === level).length / incidents.length) * 100 : 0}%`,
                              }}
                            />
                          </div>
                          <b>
                            {
                              incidents.filter((i) => i.severity === level)
                                .length
                            }
                          </b>
                        </div>
                      ))}
                      <p>
                        Rule matches indicate investigation priority, not proof
                        of malicious activity.
                      </p>
                    </article>
                    <article className="panel">
                      <h2>Controlled scenario generator</h2>
                      <p>
                        Generate fictional logs and run the same detection
                        pipeline used for ingestion.
                      </p>
                      <div className="buttons">
                        {[
                          ["normal", "Normal activity"],
                          ["brute", "Brute force"],
                          ["spray", "Password spray"],
                          ["disabled", "Disabled account"],
                          ["health", "Device anomaly"],
                          ["config", "Configuration change"],
                          ["denied", "Access denials"],
                          ["ratio", "Failure ratio"],
                          ["unusual", "Off-hours login"],
                        ].map(([k, n]) => (
                          <button
                            disabled={!canWrite || loading}
                            key={k}
                            onClick={() => action(() => simulate(k))}
                          >
                            {n}
                          </button>
                        ))}
                      </div>
                    </article>
                  </div>
                  <Analytics
                    events={events}
                    incidents={incidents}
                    metrics={metrics}
                  />
                  <article className="panel">
                    <div className="panelHead">
                      <h2>Security event stream</h2>
                      <input
                        aria-label="Search events"
                        placeholder="Search source, device, account…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                      />
                    </div>
                    <div className="buttons filters">
                      <label>
                        Event-time range
                        <select
                          value={range}
                          onChange={(e) => setRange(Number(e.target.value))}
                        >
                          <option value="0">All recorded time</option>
                          <option value="60000">Latest recorded minute</option>
                          <option value="3600000">Latest recorded hour</option>
                          <option value="86400000">Latest recorded day</option>
                        </select>
                      </label>
                      <label>
                        Category
                        <select
                          value={category}
                          onChange={(e) => setCategory(e.target.value)}
                        >
                          {["all", "authentication", "network", "device"].map(
                            (x) => (
                              <option key={x}>{x}</option>
                            ),
                          )}
                        </select>
                      </label>
                      <label>
                        Severity
                        <select
                          value={severity}
                          onChange={(e) => setSeverity(e.target.value)}
                        >
                          {["all", "low", "medium", "high", "critical"].map(
                            (x) => (
                              <option key={x}>{x}</option>
                            ),
                          )}
                        </select>
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={live}
                          onChange={(e) => setLive(e.target.checked)}
                        />{" "}
                        Refresh every 5 seconds
                      </label>
                      <span className="badge">
                        {health === "ready" ? "DATABASE READY" : health} ·{" "}
                        {filtered.length} matching records
                      </span>
                    </div>
                    <div className="tableWrap">
                      <table>
                        <thead>
                          <tr>
                            {[
                              "UTC timestamp",
                              "Asset",
                              "Source IP",
                              "Account",
                              "Type",
                              "Outcome",
                            ].map((x) => (
                              <th key={x}>{x}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {filtered
                            .slice(-100)
                            .reverse()
                            .map((e) => (
                              <tr key={e.id}>
                                <td>{e.timestamp}</td>
                                <td>{e.device_id}</td>
                                <td className="mono">{e.source_ip}</td>
                                <td>{e.username}</td>
                                <td>{e.event_type}</td>
                                <td>
                                  <span
                                    className={
                                      "pill " +
                                      (e.status === "failure" ? "high" : "low")
                                    }
                                  >
                                    {e.status}
                                  </span>
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                      {!filtered.length && (
                        <p className="empty">
                          No events yet. Generate a controlled scenario to
                          begin.
                        </p>
                      )}
                    </div>
                  </article>
                </>
              )}
              {page === "Investigations" && (
                <div className="investigation">
                  <article className="panel">
                    <h2>
                      Incident queue{" "}
                      <span className="badge">{incidents.length}</span>
                    </h2>
                    {incidents.map((i) => (
                      <button
                        className={
                          "incident " + (incident?.id === i.id ? "chosen" : "")
                        }
                        key={i.id}
                        onClick={() => {
                          setSelected(i.id);
                          setStatus(i.status);
                          setAssignment(i.assignment || "");
                        }}
                      >
                        <span className={"pill " + i.severity}>
                          {i.severity}
                        </span>
                        <b>{i.rule.replaceAll("_", " ")}</b>
                        <small>
                          {i.device_id} · {i.status}
                        </small>
                      </button>
                    ))}
                    {!incidents.length && (
                      <p>No incidents. Generate a scenario from Overview.</p>
                    )}
                  </article>
                  <article className="panel">
                    {incident ? (
                      <>
                        <div className="eyebrow">INCIDENT INVESTIGATION</div>
                        <h2>{incident.rule.replaceAll("_", " ")}</h2>
                        <p>{incident.explanation}</p>
                        <code>{incident.id}</code>
                        <h3>
                          Evidence timeline · {incident.evidence.length} records
                        </h3>
                        {events
                          .filter((e) => incident.evidence.includes(e.id))
                          .map((e) => (
                            <div className="timeline" key={e.id}>
                              <b>{e.timestamp}</b>
                              <p>
                                {e.username} · {e.source_ip} · {e.status}
                              </p>
                              <small>{e.id}</small>
                            </div>
                          ))}
                        <label>
                          Status
                          <select
                            value={status}
                            onChange={(e) => setStatus(e.target.value)}
                          >
                            {[
                              "open",
                              "acknowledged",
                              "resolved",
                              "false_positive",
                            ].map((s) => (
                              <option key={s}>{s}</option>
                            ))}
                          </select>
                        </label>
                        <label>
                          Assignment
                          <input
                            value={assignment}
                            maxLength={60}
                            onChange={(e) => setAssignment(e.target.value)}
                          />
                        </label>
                        <label>
                          Incident severity
                          <select
                            aria-label="Incident severity"
                            value={incidentSeverity}
                            onChange={(e) =>
                              setIncidentSeverity(e.target.value)
                            }
                          >
                            {["low", "medium", "high", "critical"].map((s) => (
                              <option key={s}>{s}</option>
                            ))}
                          </select>
                        </label>
                        <label>
                          Classification
                          <select
                            aria-label="Classification"
                            value={classification}
                            onChange={(e) => setClassification(e.target.value)}
                          >
                            {["unreviewed", "confirmed", "false_positive"].map(
                              (s) => (
                                <option key={s}>{s}</option>
                              ),
                            )}
                          </select>
                        </label>
                        <label>
                          Analyst findings
                          <textarea
                            maxLength={2000}
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                          />
                        </label>
                        <button
                          className="primary"
                          disabled={!canWrite || loading}
                          onClick={() =>
                            action(async () => {
                              await api(
                                "/incidents/" + encodeURIComponent(incident.id),
                                "PATCH",
                                {
                                  status,
                                  assignment,
                                  note,
                                  severity: incidentSeverity,
                                  classification,
                                },
                              );
                              setNote("");
                              await refresh();
                            })
                          }
                        >
                          Save investigation
                        </button>
                        <h3>Analyst history</h3>
                        {incident.history.map((h: Row, i: number) => (
                          <p className="timeline" key={i}>
                            {h.timestamp} · {h.actor}
                            <br />
                            {h.status} · {h.note}
                          </p>
                        ))}
                      </>
                    ) : (
                      <p>Select an incident to begin.</p>
                    )}
                  </article>
                </div>
              )}
              {page === "Network" && (
                <Network
                  assets={assetRows}
                  onMonitor={(id) => {
                    setQuery(id);
                    setPage("Monitoring");
                  }}
                />
              )}
              {page === "AI Laboratory" && <Laboratory incidents={incidents} />}
              {page === "Response assistant" && (
                <>
                  <label>
                    Incident
                    <select
                      value={incident?.id || ""}
                      onChange={(e) => setSelected(e.target.value)}
                    >
                      {incidents.map((i) => (
                        <option key={i.id} value={i.id}>
                          {i.rule} · {i.device_id}
                        </option>
                      ))}
                    </select>
                  </label>
                  <ResponseAssistant
                    incident={incident}
                    onRecord={() => setPage("Investigations")}
                  />
                </>
              )}
              {page === "Reports" && (
                <article className="panel">
                  <div className="eyebrow">EVIDENCE & REPORTING</div>
                  <h2>Simulated security briefing</h2>
                  <label>
                    Report type
                    <select
                      value={reportKind}
                      onChange={(e) => setReportKind(e.target.value)}
                    >
                      <option value="executive">
                        Executive security briefing
                      </option>
                      <option value="incident">Selected incident report</option>
                      <option value="technical">
                        Technical performance report
                      </option>
                    </select>
                  </label>
                  <p>Selected case: {incident?.id || "No incident selected"}</p>
                  <p>Generated {new Date().toISOString()} · Schema 2.0</p>
                  <p>
                    {events.length} security events · {incidents.length}{" "}
                    incidents · {active.length} active investigations
                  </p>
                  <h3>Current findings</h3>
                  <p>
                    Ingestion:{" "}
                    {metrics.events_per_second == null
                      ? "No backend throughput measurement"
                      : Number(metrics.events_per_second).toFixed(1) +
                        " events/s"}{" "}
                    · Analyst-classified false positives:{" "}
                    {
                      incidents.filter(
                        (i) =>
                          i.status === "false_positive" ||
                          i.classification === "false_positive",
                      ).length
                    }
                  </p>
                  {incidents.map((i) => (
                    <p key={i.id}>
                      <span className={"pill " + i.severity}>{i.severity}</span>{" "}
                      {i.rule} — {i.explanation} ({i.evidence.length} evidence
                      records)
                    </p>
                  ))}
                  {incidents
                    .filter(
                      (i) => reportKind !== "incident" || i.id === incident?.id,
                    )
                    .map((i) => (
                      <section className="timeline" key={"findings-" + i.id}>
                        <h3>
                          {i.rule} · {i.classification || "unreviewed"}
                        </h3>
                        {i.history.map((h: Row, index: number) => (
                          <p key={index}>
                            {h.timestamp} · {h.actor} · {h.status}
                            <br />
                            {h.note}
                          </p>
                        ))}
                      </section>
                    ))}
                  <p>
                    Limitations: fictional inputs, experimental anomaly model,
                    no operational validation, no institutional endorsement.
                  </p>
                  <div className="buttons">
                    {["pdf", "json", "csv"].map((f) => (
                      <button
                        className="primary"
                        disabled={!canWrite}
                        key={f}
                        onClick={() => action(() => report(f))}
                      >
                        {f === "pdf" && offline
                          ? "Print / Save as PDF"
                          : "Export " + f.toUpperCase()}
                      </button>
                    ))}
                  </div>
                  {offline && (
                    <p>
                      Offline PDF uses your browser’s print dialog. Connected
                      mode generates PDF bytes on the backend.
                    </p>
                  )}
                </article>
              )}
              {page === "Engineering demo" && (
                <article className="panel">
                  <div className="eyebrow">
                    SEVEN-MINUTE PRESENTER WALKTHROUGH
                  </div>
                  <h2>
                    Stage {stage + 1} / 7 —{" "}
                    {
                      [
                        "System overview",
                        "Simulated incident",
                        "Detection",
                        "AI analysis",
                        "Investigation",
                        "Human response",
                        "Final report",
                      ][stage]
                    }
                  </h2>
                  <p>
                    {
                      [
                        "Show the configured fictional asset inventory and explain the event schema.",
                        "Generate a fictional authentication sequence. These are records, not attacks.",
                        "Explain five failures within sixty seconds, evidence references, and deduplication.",
                        "Show actual held-out metrics in connected mode. Explain that anomalies are not proof.",
                        "Open the incident, inspect its evidence, and save analyst findings.",
                        "Review the deterministic response checklist. Explain why disruption remains a human decision.",
                        "Export the briefing and discuss engineering limitations.",
                      ][stage]
                    }
                  </p>
                  <div className="buttons">
                    <button
                      disabled={stage === 0}
                      onClick={() => setStage(stage - 1)}
                    >
                      ← Previous
                    </button>
                    <button
                      disabled={stage === 6}
                      onClick={() => setStage(stage + 1)}
                    >
                      Next stage →
                    </button>
                    <button
                      className="primary"
                      onClick={() => {
                        if (stage === 1) action(() => simulate("brute"));
                        else
                          setPage(
                            [
                              "Network",
                              "Overview",
                              "Investigations",
                              "AI Laboratory",
                              "Investigations",
                              "Response assistant",
                              "Reports",
                            ][stage],
                          );
                      }}
                    >
                      Open stage activity
                    </button>
                    <button
                      disabled={user.role !== "administrator"}
                      onClick={() => {
                        if (
                          confirm(
                            "Delete all scenario events and investigations? Audit history is retained in connected mode.",
                          )
                        )
                          action(async () => {
                            await api("/reset", "POST");
                            setStage(0);
                            await refresh();
                          });
                      }}
                    >
                      Reset demonstration
                    </button>
                  </div>
                </article>
              )}
              {page === "Knowledge" && (
                <article className="panel">
                  <h2>Engineering knowledge panel</h2>
                  {[
                    [
                      "FastAPI",
                      "Typed validation and OpenAPI make event contracts inspectable and testable.",
                    ],
                    [
                      "Relational persistence",
                      "Transactions preserve data across restarts. SQLAlchemy links users, assets, events, incidents, evidence, notes, sessions, and audit records. Alembic preserves legacy investigations during upgrade.",
                    ],
                    [
                      "Correlation",
                      "Sort by event time, group by source and asset, and evaluate bounded windows. Late arrivals are handled by replay.",
                    ],
                    [
                      "Deduplication",
                      "Event IDs prevent repeated ingestion. Rolling cooldowns suppress repeated rule/source/device alerts. Event-time replay and evidence overlap preserve analyst history on late arrival.",
                    ],
                    [
                      "Machine learning",
                      "Features are extracted from generated event windows. Training, calibration, and held-out evaluation are separate; synthetic results do not establish operational detection performance.",
                    ],
                    [
                      "RBAC",
                      "Backend dependencies enforce viewer, analyst, and administrator permissions independently of the interface.",
                    ],
                    [
                      "Tests",
                      "Automated tests establish specific behaviors for controlled inputs, not universal correctness or security certification.",
                    ],
                    [
                      "Before operational deployment",
                      "Independent security review, TLS and secret rotation, approved retention, privacy review, representative operational validation, and deployment-specific reliability testing are still required.",
                    ],
                  ].map(([h, t]) => (
                    <div className="timeline" key={h}>
                      <h3>{h}</h3>
                      <p>{t}</p>
                    </div>
                  ))}
                </article>
              )}
              {page === "Administration" && <Administration role={user.role} />}
            </>
          )}
          <footer>
            SENTINEL DEFENSE · Educational engineering release · No military
            affiliation or endorsement
          </footer>
        </section>
      </main>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <HashRouter>
    <App />
  </HashRouter>,
);
