import { useState, useEffect } from "react";
import { api, offline } from "../services/api";
import type { Row } from "../types";
export function Administration({ role }: { role: string }) {
  const [policy, setPolicy] = useState<Row>({}),
    [audit, setAudit] = useState<Row[]>([]),
    [integrity, setIntegrity] = useState<Row | null>(null),
    [message, setMessage] = useState("");
  useEffect(() => {
    api("/policy")
      .then(setPolicy)
      .catch((e) => setMessage(String(e)));
    if (role === "administrator")
      api("/audit")
        .then(setAudit)
        .catch((e) => setMessage(String(e)));
  }, [role]);
  async function run(fn: () => Promise<any>) {
    try {
      await fn();
    } catch (e) {
      setMessage(String(e));
    }
  }
  return (
    <>
      <article className="panel">
        <h2>Detection policy</h2>
        <p>
          Policy changes apply to subsequent ingestion. Stored incident history
          is preserved. Working hours use UTC.
        </p>
        <div className="policyGrid">
          {Object.entries(policy).map(([k, v]) => (
            <label key={k}>
              {k.replaceAll("_", " ")}
              <input
                type="number"
                value={v}
                step={k === "failure_ratio" ? 0.05 : 1}
                disabled={role !== "administrator"}
                onChange={(e) =>
                  setPolicy({ ...policy, [k]: Number(e.target.value) })
                }
              />
            </label>
          ))}
        </div>
        <button
          className="primary"
          disabled={role !== "administrator"}
          onClick={() =>
            run(async () => {
              setPolicy(await api("/policy", "PUT", policy));
              setMessage("Policy saved and audited.");
            })
          }
        >
          Save detection policy
        </button>
        {message && <p role="status">{message}</p>}
      </article>
      <article className="panel">
        <h2>Evidence integrity & retention</h2>
        <p>
          Event fingerprints detect local modifications. Connected audit records
          form a hash chain. Privileged full-database rewriting requires
          independent evidence custody to detect.
        </p>
        <div className="buttons">
          <button
            disabled={role === "viewer"}
            onClick={() =>
              run(async () => setIntegrity(await api("/integrity")))
            }
          >
            Verify evidence integrity
          </button>
          <button
            disabled={role !== "administrator" || offline}
            onClick={() => {
              if (
                confirm(
                  "Remove expired events that are not referenced as incident evidence?",
                )
              )
                run(async () =>
                  setMessage(JSON.stringify(await api("/retention", "POST"))),
                );
            }}
          >
            Apply configured retention
          </button>
        </div>
        {integrity && (
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {JSON.stringify(integrity, null, 2)}
          </pre>
        )}
        {offline && (
          <p>
            Browser-local storage provides no security boundary. Automated
            retention is a connected administration operation.
          </p>
        )}
      </article>
      {role === "administrator" && (
        <article className="panel">
          <h2>Audit history</h2>
          <button
            onClick={() => run(async () => setAudit(await api("/audit")))}
          >
            Refresh audit history
          </button>
          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>UTC</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Hash</th>
                </tr>
              </thead>
              <tbody>
                {audit
                  .slice(-100)
                  .reverse()
                  .map((r) => (
                    <tr key={r.id}>
                      <td>{r.timestamp}</td>
                      <td>{r.actor}</td>
                      <td>{r.action}</td>
                      <td className="mono">
                        {r.sha256?.slice(0, 16) || "Browser log"}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </article>
      )}
    </>
  );
}
