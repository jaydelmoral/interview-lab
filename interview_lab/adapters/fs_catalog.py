"""ADAPTER: the catalog of exam items, read from files.

Sources: coding problems (problems/), output-quiz questions (problems/*/quiz.json),
multiple-choice banks (bank/questions/*.json and $ILAB_HOME/bank/questions/*.json) and the user's memory banks ($ILAB_HOME/banks/*.json).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..domain.exam import MIN_PER_ITEM
from .fs_problems import FsProblems


class FsCatalog:
    def __init__(self, root: Path, home: Path, problems: FsProblems):
        self.root, self.home, self.problems = Path(root), Path(home), problems

    def _json_files(self, *parts):
        for base in (self.root, self.home):
            d = base.joinpath(*parts)
            if d.is_dir():
                for f in sorted(d.glob("*.json")):
                    try:
                        yield json.loads(f.read_text())
                    except Exception:
                        continue

    def candidates(self) -> list:
        out = []
        for d, _ in self.problems.folders():
            try:
                m = json.loads((d / "meta.json").read_text())
            except Exception:
                continue
            if m.get("kind") == "quiz":
                try:
                    qs = json.loads((d / "quiz.json").read_text())
                except Exception:
                    continue
                for q in qs:
                    out.append({"ref": {"t": "output", "p": d.name, "q": q["id"]}, "module": m.get("module", "java-trivia"),
                                "level": q.get("level", "mid"), "min_java": q.get("min_java", 8), "language": "java",
                                "tags": [q.get("topic", "")], "minutes": MIN_PER_ITEM["output"]})
            else:
                out.append({"ref": {"t": "code", "id": d.name}, "module": m.get("module", "coding"), "level": m.get("level", "mid"),
                            "min_java": m.get("min_java", 8), "language": m.get("language", "java"), "tags": m.get("tags", []),
                            "minutes": m.get("time_limit_min", 20)})
        for lst in self._json_files("bank", "questions"):
            for q in lst if isinstance(lst, list) else []:
                out.append({"ref": {"t": "mcq", "id": q["id"]}, "module": q.get("module", "unknown"), "level": q.get("level", "mid"),
                            "min_java": 0, "language": q.get("lang", "any"), "tags": q.get("tags", []), "minutes": MIN_PER_ITEM["mcq"]})
        for bank in self._json_files("banks"):
            for q in bank.get("items", []):
                out.append({"ref": {"t": "bank", "b": bank["id"], "q": q["id"]}, "module": "mybank", "level": "any", "min_java": 0,
                            "language": "any", "tags": q.get("tags", []), "bank": bank["id"],
                            "minutes": MIN_PER_ITEM["flash" if q["type"] == "flash" else "mcq"]})
        return out

    def counts(self) -> dict:
        c: dict = {}
        for it in self.candidates():
            c[it["module"]] = c.get(it["module"], 0) + 1
        return c

    def resolve(self, ref: dict) -> Optional[dict]:
        t = ref.get("t")
        if t == "code":
            m = self.problems.meta(ref["id"])
            return {"type": "code", "id": ref["id"], "title": m["title"], "minutes": m["time_limit_min"]} if m else None
        if t == "mcq":
            for lst in self._json_files("bank", "questions"):
                for q in lst if isinstance(lst, list) else []:
                    if q["id"] == ref["id"]:
                        return q | {"type": "mcq"}
        elif t == "bank":
            for bank in self._json_files("banks"):
                if bank["id"] == ref["b"]:
                    return next((q for q in bank["items"] if q["id"] == ref["q"]), None)
        elif t == "output":
            return next((q | {"type": "output"} for q in self.problems.quiz_questions(ref["p"]) if q["id"] == ref["q"]), None)
        return None
