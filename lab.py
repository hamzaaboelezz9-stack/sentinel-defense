"""Event-derived synthetic windows, disjoint seeds and calibrated explanations."""

from datetime import UTC, datetime, timedelta
from functools import lru_cache

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from .detection import correlate

FEATURES = [
    "failure_frequency",
    "failure_ratio",
    "unique_targets",
    "off_hours_ratio",
    "telemetry_peak",
    "event_frequency",
    "disabled_successes",
]


def features(events):
    n = len(events)
    fails = [
        e
        for e in events
        if e["category"] == "authentication" and e["status"] == "failure"
    ]
    return [
        len(fails),
        len(fails) / max(1, n),
        len({e["username"] for e in fails}),
        sum(not 8 <= datetime.fromisoformat(e["timestamp"]).hour < 18 for e in events)
        / max(1, n),
        max([e.get("telemetry", 0) for e in events] or [0]),
        n,
        sum(
            bool(e.get("disabled_account")) and e["status"] == "success" for e in events
        ),
    ]


def sample_windows(seed, n):
    rng = np.random.default_rng(seed)
    windows = []
    labels = []
    for i in range(n):
        label = int(rng.random() < 0.25)
        kind = int(rng.integers(0, 5))
        count = int(rng.integers(2, 10)) if not label else int(rng.integers(6, 25))
        hour = 12 if rng.random() > 0.08 else 23
        base = datetime(2026, 1, 1, hour, tzinfo=UTC) + timedelta(days=i)
        rows = []
        for j in range(count):
            failure = rng.random() < (0.15 if not label else 0.95 if kind < 2 else 0.25)
            rows.append(
                dict(
                    id=f"{seed}-{i}-{j}",
                    timestamp=(base + timedelta(seconds=j * 2)).isoformat(),
                    device_id="identity-1",
                    source_ip="192.0.2.10",
                    username=f"fictional-{j if label and kind == 1 else 0}",
                    category="authentication",
                    event_type="login",
                    status="failure" if failure else "success",
                    severity="low",
                    environment="synthetic-lab",
                    disabled_account=bool(label and kind == 2),
                    telemetry=float(
                        rng.uniform(92, 100)
                        if label and kind == 3
                        else rng.uniform(5, 55)
                    ),
                    label=label,
                    destination_ip=None,
                    related_incident_id=None,
                )
            )
        windows.append(rows)
        labels.append(label)
    return windows, np.array(labels)


def dataset(seed, n):
    windows, y = sample_windows(seed, n)
    return np.array([features(w) for w in windows], dtype=float), y


def metrics(y, scores, threshold):
    pred = np.asarray(scores) >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return dict(
        precision=float(precision_score(y, pred, zero_division=0)),
        recall=float(recall_score(y, pred, zero_division=0)),
        f1=float(f1_score(y, pred, zero_division=0)),
        specificity=float(tn / max(1, tn + fp)),
        false_positive_rate=float(fp / max(1, fp + tn)),
        roc_auc=float(roc_auc_score(y, scores)),
        confusion_matrix=[[int(tn), int(fp)], [int(fn), int(tp)]],
    )


@lru_cache(maxsize=4)
def fit(seed=42):
    tx, ty = dataset(seed, 800)
    cx, cy = dataset(seed + 1, 300)
    ex, ey = dataset(seed + 2, 500)
    normal = tx[ty == 0]
    center = normal.mean(axis=0)
    scale = np.maximum(normal.std(axis=0), [1, 0.1, 1, 0.1, 5, 1, 1])

    def score(x):
        return np.maximum(0, (x - center) / scale).mean(axis=1)

    cs = score(cx)
    threshold = float(
        max(
            np.linspace(0.1, 6, 80),
            key=lambda t: f1_score(cy, cs >= t, zero_division=0),
        )
    )
    model = IsolationForest(n_estimators=80, random_state=seed, n_jobs=1).fit(normal)
    ifcal = -model.score_samples(cx)
    ifth = float(
        max(
            np.linspace(ifcal.min(), ifcal.max(), 80),
            key=lambda t: f1_score(cy, ifcal >= t, zero_division=0),
        )
    )
    return center, scale, threshold, ex, ey, model, ifth


def explain(events, seed=42, sensitivity=1.0):
    center, scale, threshold, *_ = fit(seed)
    x = np.asarray(features(events))
    contrib = np.maximum(0, (x - center) / scale) / len(FEATURES)
    score = float(sum(contrib))
    t = threshold * sensitivity
    return {
        "score": score,
        "threshold": t,
        "anomalous": score >= t,
        "features": [
            {
                "name": name,
                "value": float(v),
                "training_mean": float(m),
                "contribution": float(c),
            }
            for name, v, m, c in zip(FEATURES, x, center, contrib, strict=True)
        ],
        "interpretation": "Statistical deviation is not proof of malicious activity.",
    }


def evaluate(seed=42, sensitivity=1.0):
    center, scale, threshold, x, y, model, ifth = fit(seed)
    scores = np.maximum(0, (x - center) / scale).mean(axis=1)
    t = threshold * sensitivity
    fpr, tpr, roc_thresholds = roc_curve(y, scores)
    precision, recall, pr_thresholds = precision_recall_curve(y, scores)
    test_windows, _ = sample_windows(seed + 2, 500)
    rules = np.array([bool(correlate(w)) for w in test_windows], dtype=int)
    return {
        "seed": seed,
        "schema_version": "2.0",
        "splits": {"training": 800, "calibration": 300, "evaluation": 500},
        "split_seeds": [seed, seed + 1, seed + 2],
        "threshold": t,
        "calibrated_threshold": threshold,
        **metrics(y, scores, t),
        "features": FEATURES,
        "center": center.tolist(),
        "scale": scale.tolist(),
        "isolation_forest": {
            "threshold": ifth,
            **metrics(y, -model.score_samples(x), ifth),
        },
        "rule_baseline": metrics(y, rules, 0.5),
        "roc": [
            {"fpr": float(a), "tpr": float(b)} for a, b in zip(fpr, tpr, strict=True)
        ],
        "precision_recall": [
            {"precision": float(a), "recall": float(b)}
            for a, b in zip(precision[::10], recall[::10], strict=True)
        ],
        "threshold_comparison": [
            {"threshold": float(v), **metrics(y, scores, float(v))}
            for v in [t * 0.75, t, t * 1.25]
        ],
        "evaluation_samples": [
            {"features": a.tolist(), "label": int(b), "rule_prediction": int(r)}
            for a, b, r in zip(x, y, rules, strict=True)
        ],
        "limitations": "Independent synthetic event windows only; training uses normal training windows. Labels never enter feature extraction. No operational network validation. An anomaly is not proof of malicious activity.",
    }
