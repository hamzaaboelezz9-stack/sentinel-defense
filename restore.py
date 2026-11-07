"""Offline validated restore. Refuses overwrite unless explicitly requested."""

import argparse
import os
import sqlite3
import tempfile
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("backup")
p.add_argument("destination")
p.add_argument("--replace", action="store_true")
a = p.parse_args()
source = Path(a.backup).resolve()
destination = Path(a.destination).resolve()
if source == destination:
    raise SystemExit("Backup and destination must differ")
if destination.exists() and not a.replace:
    raise SystemExit("Destination exists; stop the app and pass --replace explicitly")
with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as src:
    if src.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise SystemExit("Backup integrity check failed")
    fd, tmp = tempfile.mkstemp(prefix="sentinel-restore-", dir=destination.parent)
    os.close(fd)
    try:
        with sqlite3.connect(tmp) as dst:
            src.backup(dst)
        os.replace(tmp, destination)
    finally:
        if Path(tmp).exists():
            Path(tmp).unlink()
print("Restore completed. Application must have been stopped before replacement.")
