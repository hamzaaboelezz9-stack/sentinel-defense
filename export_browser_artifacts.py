import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.detection import Policy
from backend.app.lab import evaluate
from backend.app.playbooks import BOOKS

root = Path(__file__).resolve().parents[1] / "frontend/src/generated"
root.mkdir(parents=True, exist_ok=True)
(root / "evaluation.json").write_text(json.dumps(evaluate(), indent=2))
(root / "playbooks.json").write_text(json.dumps(BOOKS, indent=2))
(root / "policy.json").write_text(Policy().model_dump_json(indent=2))
