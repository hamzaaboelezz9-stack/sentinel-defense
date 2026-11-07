"""Consistent SQLite backup; restore only with application stopped."""

import argparse
import sqlite3

p = argparse.ArgumentParser()
p.add_argument("source")
p.add_argument("destination")
a = p.parse_args()
with sqlite3.connect(a.source) as src, sqlite3.connect(a.destination) as dst:
    src.backup(dst)
print("Backup completed. Stop the app before replacing its database with this backup.")
