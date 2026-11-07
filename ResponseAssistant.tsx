import { useState, useEffect } from "react";
import { api } from "../services/api";
import type { Row } from "../types";
export function ResponseAssistant({
  incident,
  onRecord,
}: {
  incident?: Row;
  onRecord: () => void;
}) {
  const [plan, setPlan] = useState<Row | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    setPlan(null);
    if (incident)
      api("/playbook/" + encodeURIComponent(incident.id))
        .then(setPlan)
        .catch((e) => setError(String(e)));
  }, [incident?.id]);
  return (
    <article className="panel">
      <div className="eyebrow">
        DETERMINISTIC ADVISORY PLAYBOOK · NO COMMAND EXECUTION
      </div>
      <h2>Human-supervised response</h2>
      {error && <p role="alert">{error}</p>}
      {!incident ? (
        <p>Select an incident from Investigations.</p>
      ) : !plan ? (
        <p>Loading playbook…</p>
      ) : (
        <>
          <h3>{plan.summary}</h3>
          <p>{plan.confidence}</p>
          {[
            "benign_explanations",
            "investigate",
            "containment",
            "impact",
            "recovery",
            "verify",
            "closure",
          ].map((k) => (
            <section className="timeline" key={k}>
              <h3>{k.replaceAll("_", " ").toUpperCase()}</h3>
              <ul>
                {plan[k].map((text: string) => (
                  <li key={text}>{text}</li>
                ))}
              </ul>
            </section>
          ))}
          <p>
            Playbook v{plan.version} · No disruptive action can execute from
            this interface.
          </p>
          <button className="primary" onClick={onRecord}>
            Record analyst decision →
          </button>
        </>
      )}
    </article>
  );
}
