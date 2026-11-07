import type { Row } from "../types";
import defaults from "../generated/policy.json";
export function localCorrelate(events: Row[], p: Row = defaults): Row[] {
  const alerts: Row[] = [];
  const windows = new Map<string, Row[]>();
  const episodes = new Map<string, { last: number; incident: Row }>();
  for (const e of [...events].sort(
    (a, b) =>
      Date.parse(a.timestamp) - Date.parse(b.timestamp) ||
      a.id.localeCompare(b.id),
  )) {
    const now = Date.parse(e.timestamp),
      key = e.source_ip + ":" + e.device_id;
    const group = (windows.get(key) || []).filter(
      (x) => now - Date.parse(x.timestamp) <= p.window_seconds * 1000,
    );
    group.push(e);
    windows.set(key, group);
    const fails = group.filter(
        (x) => x.status === "failure" && x.category === "authentication",
      ),
      recent = fails.filter(
        (x) => now - Date.parse(x.timestamp) <= p.brute_seconds * 1000,
      ),
      denied = group.filter((x) => x.event_type === "access_denied");
    const checks: [string, boolean, Row[], string, string][] = [
      [
        "brute_force",
        recent.length >= p.brute_count,
        recent,
        "high",
        `At least ${p.brute_count} authentication failures within ${p.brute_seconds} seconds.`,
      ],
      [
        "password_spray",
        new Set(fails.map((x) => x.username)).size >= p.spray_accounts,
        fails,
        "high",
        `At least ${p.spray_accounts} distinct accounts targeted within ${p.window_seconds} seconds.`,
      ],
      [
        "disabled_account",
        e.category === "authentication" &&
          e.status === "success" &&
          e.disabled_account,
        [e],
        "critical",
        "Successful authentication to a disabled fictional account.",
      ],
      [
        "unusual_time",
        e.category === "authentication" &&
          e.status === "success" &&
          !(
            new Date(now).getUTCHours() >= p.working_start &&
            new Date(now).getUTCHours() < p.working_end
          ),
        [e],
        "medium",
        `Authentication outside ${String(p.working_start).padStart(2, "0")}:00–${String(p.working_end).padStart(2, "0")}:00 UTC.`,
      ],
      [
        "failure_ratio",
        group.length >= p.failure_minimum &&
          fails.length / group.length > p.failure_ratio,
        fails,
        "medium",
        `Failure ratio exceeds ${Math.round(p.failure_ratio * 100)}% across at least ${p.failure_minimum} events.`,
      ],
      [
        "access_denied",
        denied.length >= p.denied_count,
        denied,
        "medium",
        "Repeated access-denied events in the configured window.",
      ],
      [
        "configuration_change",
        e.event_type === "configuration_change",
        [e],
        "high",
        "Unexpected simulated device configuration change.",
      ],
      [
        "device_health",
        e.telemetry > p.telemetry_threshold,
        [e],
        "high",
        `Synthetic telemetry exceeds ${p.telemetry_threshold} units.`,
      ],
    ];
    for (const [rule, match, evidence, severity, explanation] of checks) {
      if (!match) continue;
      const episodeKey = rule + ":" + key;
      let episode = episodes.get(episodeKey);
      if (!episode || now - episode.last > p.cooldown_seconds * 1000) {
        const incident = {
          id: `${rule}:${e.source_ip}:${e.device_id}:${e.id}`,
          rule,
          rule_version: "2.0",
          severity,
          explanation,
          evidence: [],
          timestamp: e.timestamp,
          device_id: e.device_id,
          status: "open",
          assignment: "",
          history: [],
        };
        episode = { last: now, incident };
        episodes.set(episodeKey, episode);
        alerts.push(incident);
      }
      episode.last = now;
      episode.incident.evidence = [
        ...new Set([
          ...episode.incident.evidence,
          ...evidence.map((x) => x.id),
        ]),
      ].sort();
    }
  }
  return alerts;
}
