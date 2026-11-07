import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.detection import correlate
from backend.app.lab import features, sample_windows

windows, _ = sample_windows(1234, 25)
fixtures = []
for rows in windows:
    predicted = correlate(rows)
    fixtures.append(
        {
            "events": rows,
            "features": features(rows),
            "incidents": [
                {k: i[k] for k in ["id", "rule", "severity", "evidence"]}
                for i in predicted
            ],
        }
    )
(Path(__file__).resolve().parents[1] / "frontend/src/generated/parity.json").write_text(
    json.dumps(fixtures)
)
