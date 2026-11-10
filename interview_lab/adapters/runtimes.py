"""ADAPTER: reads the audited runtime registry (runtimes/*.json) and detects what is installed on this machine.

Detection is read-only (it looks for commands and asks for their version). The web app NEVER installs anything:
installing is a deliberate, confirmed action done with `python3 install.py` at setup time (see ADR-0019).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

CLEAN_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C", "HOME": "/nonexistent"}


def load_registry(root: Path) -> list:
    out = []
    for f in sorted((Path(root) / "runtimes").glob("*.json")):
        try:
            r = json.loads(f.read_text())
            if isinstance(r, dict) and r.get("id") and r.get("detect"):
                out.append(r)
        except ValueError:
            continue
    return out


def detect(runtime: dict, timeout: float = 5) -> dict:
    d = runtime["detect"]
    missing = [c for c in d.get("commands", []) if not shutil.which(c)]
    if missing:
        return {"installed": False, "version": None, "missing": missing}
    version = None
    try:
        r = subprocess.run(d["version_cmd"], capture_output=True, text=True, timeout=timeout, env={**CLEAN_ENV, "PATH": os.environ.get("PATH", CLEAN_ENV["PATH"])}, stdin=subprocess.DEVNULL)
        m = re.search(d["version_regex"], (r.stdout or "") + (r.stderr or ""))
        version = m.group(1) if m else None            # java -version prints to stderr
    except (OSError, subprocess.TimeoutExpired):
        pass
    return {"installed": True, "version": version, "missing": []}


class RuntimeCatalog:
    def __init__(self, root: Path):
        self.root = Path(root)

    def list(self, lang: str = "es") -> list:
        rows = []
        for r in load_registry(self.root):
            st = detect(r)
            rows.append({"id": r["id"], "kind": r.get("kind", "language"), "name": r["name"], "grader": bool(r.get("grader")),
                         "description": (r.get("description") or {}).get("en" if lang == "en" else "es", ""),
                         "installed": st["installed"], "version": st["version"], "install_hint": f"python3 install.py install --lang {r['id']}"})
        return rows
