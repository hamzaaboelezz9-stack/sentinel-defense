"""Provision an operator on a local installation without demo accounts."""

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.main import audit, engine, meta, ph, put, read

p = argparse.ArgumentParser()
p.add_argument("username")
p.add_argument(
    "--role", choices=["administrator", "analyst", "viewer"], default="viewer"
)
a = p.parse_args()
if not 1 <= len(a.username) <= 60:
    raise SystemExit("Username must be 1–60 characters")
meta.create_all(engine)
if any(u["username"] == a.username for u in read("users")):
    raise SystemExit("User already exists; refusing to replace credentials")
password = getpass.getpass("Password (12+ characters): ")
if len(password) < 12 or getpass.getpass("Confirm password: ") != password:
    raise SystemExit("Password invalid or confirmation mismatch")
put("users", a.username, {"role": a.role, "hash": ph.hash(password)})
audit("local-provisioner", "create_user:" + a.username + ":" + a.role)
print("User created. No password was stored in plaintext.")
