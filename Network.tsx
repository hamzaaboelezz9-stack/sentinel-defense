import { useState } from "react";
import type { Row } from "../types";
export function Network({
  assets,
  onMonitor,
}: {
  assets: Row[];
  onMonitor: (id: string) => void;
}) {
  const [selected, setSelected] = useState<Row | null>(null);
  const positions = new Map(
    assets.map((a, i) => [
      a.id,
      {
        x: i === 0 ? 450 : 100 + ((i - 1) % 4) * 230,
        y: i === 0 ? 70 : 220 + Math.floor((i - 1) / 4) * 160,
      },
    ]),
  );
  return (
    <article className="panel">
      <h2>Fictional infrastructure topology</h2>
      <p>
        Relationships come from the configured asset records. Event counts,
        telemetry, and incident indicators derive from ingested fictional
        records. “No telemetry” is not a healthy-device assertion.
      </p>
      <div className="tableWrap">
        <svg
          viewBox={`0 0 950 ${Math.max(460, Math.ceil(assets.length / 4) * 170 + 150)}`}
          style={{ minWidth: 580, width: "100%" }}
          role="img"
          aria-label="Interactive fictional network topology"
        >
          {assets
            .filter((a) => a.parent_id && positions.has(a.parent_id))
            .map((a) => {
              const p = positions.get(a.parent_id)!,
                c = positions.get(a.id)!;
              return (
                <line
                  key={a.id}
                  x1={p.x}
                  y1={p.y}
                  x2={c.x}
                  y2={c.y}
                  stroke="#356579"
                  strokeWidth="2"
                />
              );
            })}
          {assets.map((a) => {
            const p = positions.get(a.id)!;
            return (
              <g
                role="button"
                tabIndex={0}
                aria-label={a.name}
                key={a.id}
                transform={`translate(${p.x},${p.y})`}
                onClick={() => setSelected(a)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    setSelected(a);
                  }
                }}
                style={{ cursor: "pointer" }}
              >
                <rect
                  x="-95"
                  y="-35"
                  width="190"
                  height="90"
                  rx="10"
                  fill="#11283a"
                  stroke={a.active_incidents ? "#e9ab60" : "#418c9f"}
                  strokeWidth="2"
                />
                <text textAnchor="middle" fill="#d7e6f3" y="-8" fontSize="12">
                  {a.name.slice(0, 25)}
                </text>
                <text textAnchor="middle" fill="#74d0d9" y="13" fontSize="11">
                  {a.ip}
                </text>
                <text textAnchor="middle" fill="#a3b5c5" y="34" fontSize="10">
                  {a.event_count} events · {a.active_incidents} incidents
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      {selected && (
        <section className="timeline">
          <h3>{selected.name}</h3>
          <p>
            {selected.kind} · {selected.ip} ·{" "}
            {selected.telemetry.length
              ? "Latest synthetic telemetry: " + selected.telemetry.at(-1).value
              : "No telemetry recorded"}
          </p>
          <button onClick={() => onMonitor(selected.id)}>
            Inspect asset events →
          </button>
        </section>
      )}
    </article>
  );
}
