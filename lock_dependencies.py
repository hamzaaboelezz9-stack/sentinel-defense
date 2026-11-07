"""Capture the dependency closure actually exercised by local validation."""

from importlib.metadata import distribution
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

root = Path(__file__).resolve().parents[1]
queue = [
    Requirement(line)
    for line in (root / "backend/requirements.txt").read_text().splitlines()
    if line and not line.startswith("#")
]
seen = set()
versions = {}
while queue:
    r = queue.pop()
    key = (canonicalize_name(r.name), tuple(sorted(r.extras)))
    if key in seen:
        continue
    seen.add(key)
    d = distribution(r.name)
    versions[d.metadata["Name"]] = d.version
    for value in d.requires or []:
        req = Requirement(value)
        if req.marker is None or any(
            req.marker.evaluate({"extra": extra}) for extra in (list(r.extras) + [""])
        ):
            queue.append(req)
(root / "backend/requirements.lock").write_text(
    "\n".join(
        f"{name}=={version}"
        for name, version in sorted(versions.items(), key=lambda p: p[0].lower())
    )
    + "\n"
)
print("Locked", len(versions), "tested dependencies")
