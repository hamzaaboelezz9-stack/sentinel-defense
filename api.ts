import type { Row } from "../types";
import { localCorrelate } from "./detection";
import { evaluate, explain } from "./laboratory";
import defaults from "../generated/policy.json";
import books from "../generated/playbooks.json";
export const offline =
  location.protocol === "file:" ||
  new URLSearchParams(location.search).has("demo");
export const inventory = [
  ["identity-1", "Identity gateway", "192.0.2.10"],
  ["hq-1", "HQ workstation", "192.0.2.20"],
  ["app-1", "Application server", "198.51.100.10"],
  ["db-1", "Database server", "198.51.100.20"],
  ["monitor-1", "Industrial monitor simulator", "203.0.113.10"],
  ["network-1", "Network simulator", "203.0.113.20"],
];
export function localRead(): Row {
  const raw = localStorage.getItem("sentinel-v1");
  if (!raw)
    return {
      events: [],
      incidents: [],
      audit: [],
      hashes: {},
      policy: defaults,
    };
  try {
    const d = JSON.parse(raw);
    if (!Array.isArray(d.events) || !Array.isArray(d.incidents)) throw Error();
    return { audit: [], hashes: {}, policy: defaults, ...d };
  } catch {
    throw Error(
      "Browser storage is corrupted. Export or clear this site’s storage before continuing.",
    );
  }
}
export function validateEvent(e: Row) {
  if (
    !e ||
    typeof e !== "object" ||
    typeof e.id !== "string" ||
    !/^\w[\w-]{0,99}$/.test(e.id) ||
    typeof e.timestamp !== "string" ||
    !/(Z|[+-]\d\d:\d\d)$/.test(e.timestamp) ||
    !Number.isFinite(Date.parse(e.timestamp))
  )
    throw Error("Invalid event ID or timezone-aware timestamp");
  for (const field of ["device_id", "username"])
    if (
      typeof e[field] !== "string" ||
      !e[field].length ||
      e[field].length > 60
    )
      throw Error("Invalid " + field);
  for (const field of ["source_ip", "destination_ip"])
    if (
      e[field] != null &&
      !/^(192\.0\.2|198\.51\.100|203\.0\.113)\.(\d{1,3})$/.test(e[field])
    )
      throw Error("Documentation IPv4 addresses only");
    else if (e[field] != null && Number(e[field].split(".").at(-1)) > 255)
      throw Error("Invalid IP");
  for (const [field, values] of Object.entries({
    category: ["authentication", "network", "device"],
    event_type: ["login", "access_denied", "configuration_change", "telemetry"],
    status: ["success", "failure"],
    severity: ["low", "medium", "high", "critical"],
    environment: ["synthetic-lab"],
  }))
    if (!values.includes(e[field])) throw Error("Invalid " + field);
  if (
    !Number.isFinite(e.telemetry) ||
    e.telemetry < 0 ||
    e.telemetry > 100 ||
    typeof e.disabled_account !== "boolean"
  )
    throw Error("Invalid telemetry/account flag");
}
export async function hash(value: any) {
  const stable = (v: any): any =>
    Array.isArray(v)
      ? v.map(stable)
      : v && typeof v === "object"
        ? Object.fromEntries(
            Object.keys(v)
              .sort()
              .map((k) => [k, stable(v[k])]),
          )
        : v;
  const buffer = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(JSON.stringify(stable(value))),
  );
  return Array.from(new Uint8Array(buffer))
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
}
export async function api(
  path: string,
  method = "GET",
  body?: any,
): Promise<any> {
  if (!offline) {
    const r = await fetch("/api/v1" + path, {
      method,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (!r.ok) {
      const e = await r.json().catch(() => ({ detail: "Request failed" }));
      throw Error(e.detail || "Request failed");
    }
    return r.json();
  }
  let d = localRead(),
    out: any;
  const route = path.split("?")[0];
  if (route === "/events" && method === "POST") {
    if (!Array.isArray(body) || body.length > 1000)
      throw Error("Maximum 1000 records per batch");
    const ids = new Map(d.events.map((e: Row) => [e.id, e]));
    let accepted = 0;
    for (const e of body) {
      validateEvent(e);
      if (ids.has(e.id) && JSON.stringify(ids.get(e.id)) !== JSON.stringify(e))
        throw Error("Conflicting duplicate event ID");
      if (!ids.has(e.id)) {
        d.events.push(e);
        ids.set(e.id, e);
        d.hashes[e.id] = await hash(e);
        accepted++;
      }
    }
    const old = d.incidents;
    d.incidents = localCorrelate(d.events, d.policy).map((i) => {
      const matches = old.filter(
        (o: Row) =>
          o.rule === i.rule &&
          o.evidence.some((id: string) => i.evidence.includes(id)),
      );
      const saved = matches.find((o: Row) => o.id === i.id) || matches[0];
      if (!saved) return i;
      const histories = matches.flatMap((o: Row) => o.history);
      const unique = new Map(histories.map((h: Row) => [JSON.stringify(h), h]));
      return {
        ...saved,
        evidence: [
          ...new Set([
            ...i.evidence,
            ...matches.flatMap((o: Row) => o.evidence),
          ]),
        ].sort(),
        history: [...unique.values()],
      };
    });
    out = { accepted, duplicates: body.length - accepted };
  } else if (route === "/reset") {
    d = {
      events: [],
      incidents: [],
      audit: d.audit,
      hashes: {},
      policy: d.policy,
    };
    out = { ok: true };
  } else if (route.startsWith("/incidents/") && method === "PATCH") {
    const i = d.incidents.find(
      (i: Row) => i.id === decodeURIComponent(route.slice(11)),
    );
    if (!i) throw Error("Incident not found");
    if (
      !["open", "acknowledged", "resolved", "false_positive"].includes(
        body.status,
      ) ||
      body.note.length > 2000 ||
      body.assignment.length > 60
    )
      throw Error("Invalid investigation");
    Object.assign(i, {
      status: body.status,
      assignment: body.assignment,
      severity: body.severity || i.severity,
      classification: body.classification || i.classification || "unreviewed",
    });
    i.history.push({
      ...body,
      actor: "offline-presenter",
      timestamp: new Date().toISOString(),
    });
    out = i;
  } else if (route === "/events") out = d.events;
  else if (route === "/incidents") out = d.incidents;
  else if (route === "/lab")
    out = evaluate(
      Number(new URLSearchParams(path.split("?")[1]).get("sensitivity") || 1),
    );
  else if (route === "/anomalies")
    out = d.incidents.map((i: Row) => ({
      incident_id: i.id,
      ...explain(
        d.events.filter((e: Row) => i.evidence.includes(e.id)),
        Number(new URLSearchParams(path.split("?")[1]).get("sensitivity") || 1),
      ),
    }));
  else if (route === "/policy") {
    if (method === "PUT") {
      for (const k of Object.keys(defaults))
        if (!Number.isFinite(body[k]) || body[k] < 0)
          throw Error("Invalid policy value");
      if (
        body.working_start >= body.working_end ||
        body.brute_seconds > body.window_seconds ||
        body.cooldown_seconds < 1
      )
        throw Error("Inconsistent policy");
      d.policy = body;
    }
    out = d.policy;
  } else if (route === "/audit") out = d.audit;
  else if (route === "/assets")
    out = inventory.map(([id, name, ip], i) => ({
      id,
      name,
      ip,
      parent_id: i === 0 ? null : i === 3 ? "app-1" : "identity-1",
      kind: "configured-simulator",
      event_count: d.events.filter((e: Row) => e.device_id === id).length,
      active_incidents: d.incidents.filter(
        (x: Row) =>
          x.device_id === id &&
          !["resolved", "false_positive"].includes(x.status),
      ).length,
      telemetry: d.events
        .filter((e: Row) => e.device_id === id && e.event_type === "telemetry")
        .map((e: Row) => ({ timestamp: e.timestamp, value: e.telemetry })),
    }));
  else if (route.startsWith("/playbook/")) {
    const i = d.incidents.find(
      (i: Row) => i.id === decodeURIComponent(route.slice(10)),
    );
    if (!i) throw Error("Incident not found");
    const b = (books as Row)[i.rule];
    out = {
      version: "2.0",
      summary: b[0] + ": " + i.explanation,
      confidence: "Rule match; malicious intent unproven.",
      benign_explanations: [b[1]],
      investigate: b[2],
      containment: b[3],
      impact: [
        "Changes may interrupt legitimate services. Human approval required.",
      ],
      recovery: ["Apply reviewed changes in the fictional lab."],
      verify: ["Inspect new events and preserve findings."],
      closure: ["Record classification and follow-up owner."],
      executes_actions: false,
    };
  } else if (route === "/integrity") {
    let valid = true;
    for (const e of d.events)
      if (d.hashes[e.id] && d.hashes[e.id] !== (await hash(e))) valid = false;
    out = {
      valid,
      note: "Browser-local fingerprints; browser owners can rewrite storage. Legacy unhashed records are not verified.",
      verified_records: Object.keys(d.hashes).length,
    };
  } else if (route === "/metrics") {
    const times = (status: string) =>
      d.incidents
        .map((i: Row) => {
          const h = i.history.find((h: Row) => h.status === status);
          return h
            ? Math.max(
                0,
                (Date.parse(h.timestamp) - Date.parse(i.timestamp)) / 1000,
              )
            : null;
        })
        .filter((v: any) => v !== null);
    const a = times("acknowledged"),
      r = times("resolved");
    out = {
      ingested_events: d.events.length,
      events_per_second: null,
      mean_time_to_acknowledge_seconds: a.length
        ? a.reduce((a: number, b: number) => a + b, 0) / a.length
        : null,
      mean_time_to_resolve_seconds: r.length
        ? r.reduce((a: number, b: number) => a + b, 0) / r.length
        : null,
      acknowledged_samples: a.length,
      resolved_samples: r.length,
      note: "Synthetic event-to-analyst elapsed time; not operational response performance.",
    };
  } else if (route === "/ready") out = { database: "Browser storage ready" };
  else if (route === "/health")
    out = { status: "Browser-local simulation ready", version: "1.0.0" };
  else throw Error("Endpoint unavailable in browser-local mode");
  if (method !== "GET")
    d.audit.push({
      id: crypto.randomUUID(),
      actor: "offline-presenter",
      action: method + " " + route,
      timestamp: new Date().toISOString(),
    });
  localStorage.setItem("sentinel-v1", JSON.stringify(d));
  return out;
}
export function download(name: string, body: string, type: string) {
  const url = URL.createObjectURL(new Blob([body], { type })),
    a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function generate(kind: string): Row[] {
  const base = Date.parse("2026-01-01T12:00:00Z"),
    prefix = crypto.randomUUID();
  return Array.from(
    { length: kind === "normal" ? 12 : kind === "ratio" ? 12 : 6 },
    (_, i) => ({
      id: `${prefix}-${i}`,
      timestamp: new Date(
        base + i * 5000 + (kind === "unusual" ? 11 * 3600000 : 0),
      ).toISOString(),
      device_id:
        kind === "health"
          ? "monitor-1"
          : kind === "config"
            ? "network-1"
            : "identity-1",
      source_ip: kind === "normal" ? `192.0.2.${20 + i}` : "192.0.2.10",
      destination_ip: null,
      username: kind === "spray" ? `fictional-${i}` : "fictional-operator",
      category: ["health", "config"].includes(kind)
        ? "device"
        : kind === "denied"
          ? "network"
          : "authentication",
      event_type:
        kind === "health"
          ? "telemetry"
          : kind === "config"
            ? "configuration_change"
            : kind === "denied"
              ? "access_denied"
              : "login",
      status: ["normal", "disabled", "unusual"].includes(kind)
        ? "success"
        : "failure",
      severity: "low",
      environment: "synthetic-lab",
      disabled_account: kind === "disabled",
      telemetry: kind === "health" ? 96 : 0,
      label: kind === "normal" ? 0 : 1,
      related_incident_id: null,
    }),
  );
}
