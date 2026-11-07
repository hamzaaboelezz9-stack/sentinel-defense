"""Rebuild all train/calibration/test event windows and derived feature artifacts."""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.lab import FEATURES, evaluate, features, sample_windows

root = Path(__file__).resolve().parents[1] / "datasets"
(root / "synthetic").mkdir(parents=True, exist_ok=True)
for name, seed, n in [
    ("training", 42, 800),
    ("calibration", 43, 300),
    ("evaluation", 44, 500),
]:
    windows, y = sample_windows(seed, n)
    x = np.array([features(w) for w in windows])
    np.savetxt(
        root / (name + ".csv"),
        np.column_stack([x, y]),
        delimiter=",",
        header=",".join(FEATURES + ["label"]),
        comments="",
    )
    (root / "synthetic" / (name + ".events.json")).write_text(
        json.dumps(
            {
                "schema_version": "2.0",
                "seed": seed,
                "windows": windows,
                "labels": y.tolist(),
            }
        )
    )
(root / "evaluation.json").write_text(json.dumps(evaluate(), indent=2))
