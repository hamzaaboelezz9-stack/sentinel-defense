"""Local demo provisioning; generates a password at launch, never in source."""

import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SENTINEL_DEMO", "1")
if not os.environ.get("DEMO_PASSWORD"):
    os.environ["DEMO_PASSWORD"] = secrets.token_urlsafe(18)
    print(
        "New database demo password (administrator / analyst / viewer):",
        os.environ["DEMO_PASSWORD"],
        flush=True,
    )
    print(
        "On an existing database, use the password from its first launch.", flush=True
    )
import uvicorn

uvicorn.run(
    "backend.app.main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000"))
)
