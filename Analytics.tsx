import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
} from "recharts";
import type { Row } from "../types";
export function Analytics({
  events,
  incidents,
  metrics,
}: {
  events: Row[];
  incidents: Row[];
  metrics: Row;
}) {
  const times = new Map<string, Row>();
  for (const e of events) {
    const k = e.timestamp.slice(0, 16);
    const row = times.get(k) || { time: k.slice(11), events: 0, failures: 0 };
    row.events++;
    if (e.status === "failure") row.failures++;
    times.set(k, row);
  }
  for (const i of incidents) {
    const k = i.timestamp.slice(0, 16),
      row = times.get(k) || { time: k.slice(11), events: 0, failures: 0 };
    row.incidents = (row.incidents || 0) + 1;
    times.set(k, row);
  }
  const trend = [...times.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-40)
    .map(([, v]) => v);
  const category = ["authentication", "network", "device"].map((name) => ({
    name,
    count: events.filter((e) => e.category === name).length,
  }));
  return (
    <>
      <div className="grid">
        <article className="panel">
          <h2>Event activity · event time (UTC)</h2>
          {trend.length ? (
            <div aria-label="Event activity chart" style={{ height: 220 }}>
              <ResponsiveContainer>
                <AreaChart data={trend}>
                  <CartesianGrid stroke="#23374b" />
                  <XAxis dataKey="time" stroke="#8aabc3" />
                  <YAxis allowDecimals={false} stroke="#8aabc3" />
                  <Tooltip
                    contentStyle={{
                      background: "#132338",
                      borderColor: "#3b526d",
                    }}
                  />
                  <Area dataKey="events" stroke="#59d2e1" fill="#1a6878" />
                  <Area dataKey="failures" stroke="#e3a650" fill="#654625" />
                  <Area dataKey="incidents" stroke="#fa7f9a" fill="#612b45" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p>No recorded events yet.</p>
          )}
        </article>
        <article className="panel">
          <h2>Event categories</h2>
          <div style={{ height: 220 }}>
            <ResponsiveContainer>
              <BarChart data={category}>
                <XAxis dataKey="name" stroke="#8aabc3" />
                <YAxis allowDecimals={false} stroke="#8aabc3" />
                <Tooltip contentStyle={{ background: "#132338" }} />
                <Bar dataKey="count" fill="#54c4ce" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </div>
      <div className="metrics">
        {[
          [
            "Mean time to acknowledge",
            metrics.mean_time_to_acknowledge_seconds,
            metrics.acknowledged_samples,
          ],
          [
            "Mean time to resolve",
            metrics.mean_time_to_resolve_seconds,
            metrics.resolved_samples,
          ],
        ].map(([name, value, n]) => (
          <article className="panel metric" key={name}>
            <small>{name}</small>
            <strong>
              {value == null ? "—" : (Number(value) / 3600).toFixed(1) + " h"}
            </strong>
            <span>
              {n || 0} measured synthetic cases · event-to-analyst time
            </span>
          </article>
        ))}
        <article className="panel metric">
          <small>Classified false positives</small>
          <strong>
            {incidents.filter((i) => i.status === "false_positive").length}
          </strong>
          <span>Analyst decisions, not inferred ground truth</span>
        </article>
        <article className="panel metric">
          <small>Measured ingestion</small>
          <strong>
            {metrics.events_per_second == null
              ? "—"
              : Number(metrics.events_per_second).toFixed(0)}
          </strong>
          <span>
            {metrics.events_per_second == null
              ? "No backend measurement in browser-local mode"
              : "events/s · cumulative server processing"}
          </span>
        </article>
      </div>
    </>
  );
}
