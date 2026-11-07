import artifact from "../generated/evaluation.json";
import type { Row } from "../types";
export function eventFeatures(events: Row[]): number[] {
  const failures = events.filter(
    (e) => e.category === "authentication" && e.status === "failure",
  );
  return [
    failures.length,
    failures.length / Math.max(1, events.length),
    new Set(failures.map((e) => e.username)).size,
    events.filter((e) => {
      const h = new Date(e.timestamp).getUTCHours();
      return h < 8 || h >= 18;
    }).length / Math.max(1, events.length),
    Math.max(0, ...events.map((e) => e.telemetry || 0)),
    events.length,
    events.filter((e) => e.disabled_account && e.status === "success").length,
  ];
}
export function explain(events: Row[], sensitivity = 1): Row {
  const x = eventFeatures(events),
    parts = x.map(
      (v, i) =>
        Math.max(0, (v - artifact.center[i]) / artifact.scale[i]) / x.length,
    ),
    score = parts.reduce((a, b) => a + b, 0),
    threshold = artifact.calibrated_threshold * sensitivity;
  return {
    score,
    threshold,
    anomalous: score >= threshold,
    features: x.map((value, i) => ({
      name: artifact.features[i],
      value,
      training_mean: artifact.center[i],
      contribution: parts[i],
    })),
    interpretation: "Statistical deviation is not proof of malicious activity.",
  };
}
export function evaluate(sensitivity = 1): Row {
  const threshold = artifact.calibrated_threshold * sensitivity;
  let tn = 0,
    fp = 0,
    fn = 0,
    tp = 0;
  for (const row of artifact.evaluation_samples) {
    const score = row.features.reduce(
      (sum, v, i) =>
        sum +
        Math.max(0, (v - artifact.center[i]) / artifact.scale[i]) /
          row.features.length,
      0,
    );
    if (score >= threshold) {
      if (row.label) tp++;
      else fp++;
    } else {
      if (row.label) fn++;
      else tn++;
    }
  }
  const precision = tp / Math.max(1, tp + fp),
    recall = tp / Math.max(1, tp + fn);
  return {
    ...artifact,
    threshold,
    precision,
    recall,
    f1: (2 * precision * recall) / Math.max(1e-12, precision + recall),
    specificity: tn / Math.max(1, tn + fp),
    false_positive_rate: fp / Math.max(1, fp + tn),
    confusion_matrix: [
      [tn, fp],
      [fn, tp],
    ],
    evaluation_source:
      "Browser recomputation on packaged held-out event-derived features; Python training/Isolation Forest metadata packaged at build.",
  };
}
