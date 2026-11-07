import { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { api, offline, download } from "../services/api";
import type { Row } from "../types";
export function Laboratory({ incidents }: { incidents: Row[] }) {
  const [lab, setLab] = useState<Row | null>(null),
    [sensitivity, setSensitivity] = useState(1),
    [anomalies, setAnomalies] = useState<Row[]>([]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  async function run() {
    setBusy(true);
    setError("");
    try {
      setLab(await api("/lab?sensitivity=" + sensitivity));
      setAnomalies(await api("/anomalies?sensitivity=" + sensitivity));
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <article className="panel">
      <div className="eyebrow">
        EXPERIMENTAL · EVENT-DERIVED SYNTHETIC FEATURES
      </div>
      <h2>Explainable anomaly laboratory</h2>
      <p>
        Fit on normal training windows, select a threshold on a separate
        calibration split, then evaluate independent held-out windows. Labels
        are never features.{" "}
        {offline
          ? "The browser recomputes statistics from packaged held-out samples; Python-trained comparison metadata is included."
          : "The Python service trains and evaluates the statistical baseline and Isolation Forest."}
      </p>
      <label>
        Sensitivity threshold multiplier: {sensitivity.toFixed(2)}
        <input
          aria-label="Sensitivity threshold multiplier"
          type="range"
          min="0.25"
          max="3"
          step="0.05"
          value={sensitivity}
          onChange={(e) => setSensitivity(Number(e.target.value))}
        />
      </label>
      <button className="primary" disabled={busy} onClick={run}>
        {busy ? "Evaluating…" : "Run reproducible evaluation"}
      </button>
      {error && <p role="alert">{error}</p>}
      {lab && (
        <>
          <div className="metrics">
            {["precision", "recall", "f1", "roc_auc"].map((k) => (
              <div className="metric panel" key={k}>
                <small>{k}</small>
                <strong>{(lab[k] * 100).toFixed(1)}%</strong>
              </div>
            ))}
          </div>
          <div className="grid">
            <section>
              <h3>Confusion matrix [TN, FP; FN, TP]</h3>
              <table>
                <thead>
                  <tr>
                    <th>Actual / predicted</th>
                    <th>Normal</th>
                    <th>Anomaly</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th>Normal</th>
                    <td>{lab.confusion_matrix[0][0]}</td>
                    <td>{lab.confusion_matrix[0][1]}</td>
                  </tr>
                  <tr>
                    <th>Anomaly</th>
                    <td>{lab.confusion_matrix[1][0]}</td>
                    <td>{lab.confusion_matrix[1][1]}</td>
                  </tr>
                </tbody>
              </table>
              <p>
                Specificity {(lab.specificity * 100).toFixed(1)}% ·
                False-positive rate {(lab.false_positive_rate * 100).toFixed(1)}
                %
              </p>
              <p>
                Seed {lab.seed} · Training {lab.splits.training} · Calibration{" "}
                {lab.splits.calibration} · Evaluation {lab.splits.evaluation}
              </p>
            </section>
            <section>
              <h3>ROC curve · held-out data</h3>
              <div style={{ height: 230 }}>
                <ResponsiveContainer>
                  <LineChart data={lab.roc}>
                    <CartesianGrid stroke="#23374b" />
                    <XAxis
                      dataKey="fpr"
                      type="number"
                      domain={[0, 1]}
                      stroke="#89a6bf"
                    />
                    <YAxis type="number" domain={[0, 1]} stroke="#89a6bf" />
                    <Tooltip contentStyle={{ background: "#132338" }} />
                    <Line dataKey="tpr" stroke="#5ed8df" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
          <h3>Detection method comparison</h3>
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["Statistical baseline", lab],
                ["Isolation Forest", lab.isolation_forest],
                ["Rule engine", lab.rule_baseline],
              ].map(([name, m]: any) => (
                <tr key={name}>
                  <td>{name}</td>
                  {["precision", "recall", "f1"].map((k) => (
                    <td key={k}>{(m[k] * 100).toFixed(1)}%</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <h3>Threshold comparisons</h3>
          <table>
            <thead>
              <tr>
                <th>Threshold</th>
                <th>Precision</th>
                <th>Recall</th>
              </tr>
            </thead>
            <tbody>
              {lab.threshold_comparison.map((r: Row) => (
                <tr key={r.threshold}>
                  <td>{r.threshold.toFixed(3)}</td>
                  <td>{(r.precision * 100).toFixed(1)}%</td>
                  <td>{(r.recall * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          <h3>Current incident explanations</h3>
          {anomalies.length ? (
            anomalies.map((a) => (
              <section className="timeline" key={a.incident_id}>
                <b>
                  {incidents.find((i) => i.id === a.incident_id)?.rule} · Score{" "}
                  {a.score.toFixed(3)} / threshold {a.threshold.toFixed(3)}
                </b>
                <p>
                  {a.anomalous ? "Model anomaly" : "Model below threshold"} ·
                  Rule match is a separate result
                </p>
                {a.features.map((f: Row) => (
                  <p key={f.name}>
                    {f.name}: {f.value.toFixed(2)} · contribution{" "}
                    {f.contribution.toFixed(3)}
                  </p>
                ))}
              </section>
            ))
          ) : (
            <p>No incident evidence is available for scoring.</p>
          )}
          <p>{lab.limitations}</p>
          <button
            onClick={() =>
              download(
                "model-metadata.json",
                JSON.stringify(lab, null, 2),
                "application/json",
              )
            }
          >
            Download model and evaluation metadata
          </button>
        </>
      )}
    </article>
  );
}
