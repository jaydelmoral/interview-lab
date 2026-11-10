"""ADAPTER: problems stored as folders (built-in under problems/, yours under $ILAB_HOME/problems/)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")


class FsProblems:
    def __init__(self, root: Path, home: Path):
        self.sources = ((Path(root) / "problems", "builtin"), (Path(home) / "problems", "user"))

    def folders(self):
        for base, source in self.sources:
            if base.is_dir():
                for d in sorted(base.iterdir()):
                    if (d / "meta.json").exists() and ID_RE.match(d.name):
                        yield d, source

    def find(self, pid: str) -> Optional[tuple]:
        """Built-in problems win over user problems with the same id."""
        if not ID_RE.match(str(pid)):
            return None
        for base, source in self.sources:
            d = base / pid
            if (d / "meta.json").exists():
                return d, source
        return None

    def meta(self, pid: str) -> Optional[dict]:
        found = self.find(pid)
        return json.loads((found[0] / "meta.json").read_text()) if found else None

    def list_summaries(self) -> list:
        out = []
        for d, source in self.folders():
            try:
                m = json.loads((d / "meta.json").read_text())
                out.append({"id": m["id"], "title": m["title"], "time_limit_min": m["time_limit_min"], "tags": m["tags"],
                            "kind": m.get("kind", "code"), "domain": m.get("domain", ""), "source": source,
                            "has_es": (d / "problem.es.md").exists() or m.get("kind") == "quiz"})
            except Exception:
                continue                  # a malformed user problem must not break the list
        return out

    def quiz_questions(self, pid: str) -> list:
        found = self.find(pid)
        return json.loads((found[0] / "quiz.json").read_text()) if found else []

    def public(self, pid: str, lang: str) -> Optional[dict]:
        found = self.find(pid)
        if not found:
            return None
        d, source = found
        m = json.loads((d / "meta.json").read_text())
        base = {"id": m["id"], "title": m["title"], "time_limit_min": m["time_limit_min"], "tags": m["tags"],
                "domain": m.get("domain", ""), "source": source, "license": m.get("license", "")}
        if m.get("kind") == "quiz":
            qs = json.loads((d / "quiz.json").read_text())
            return base | {"kind": "quiz", "questions": [
                {"id": q["id"], "topic": q.get("topic_en") if lang == "en" and q.get("topic_en") else q["topic"], "code": q["code"]} for q in qs]}
        es = d / "problem.es.md"
        return base | {"kind": "code", "statement": (d / "problem.md").read_text(),
                       "statement_es": es.read_text() if es.exists() else None, "starter": (d / "starter.java").read_text(),
                       "tests": [{"title": t["title"], "category": t["category"], "points": t["points"]} for t in m["tests"]]}
