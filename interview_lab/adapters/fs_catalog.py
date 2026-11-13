"""ADAPTER: the catalog of exam items, read from files.

Sources: coding problems (problems/), output-quiz questions (problems/*/quiz.json),
multiple-choice banks (bank/questions/*.json and $ILAB_HOME/bank/questions/*.json) and the user's memory banks ($ILAB_HOME/banks/*.json).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..domain.exam import LEVELS, MIN_PER_ITEM
from .fs_problems import FsProblems


def _text(v) -> bool:
    """A text as the bank stores it: a string, or {"es": ..., "en": ...}."""
    return isinstance(v, str) or (isinstance(v, dict) and any(isinstance(x, str) for x in v.values()))


def _readable(q, kind: str) -> bool:
    """True when every later step (building, showing and grading an exam) can read this entry."""
    if not isinstance(q, dict) or not isinstance(q.get("id"), str):
        return False
    if not isinstance(q.get("tags", []), list) or not isinstance(q.get("review") or {}, dict):
        return False
    if kind == "output":
        return all(isinstance(q.get(k), str) for k in ("code", "expected", "explanation"))
    t = q.get("type") if kind == "bank" else "mcq"
    if t == "flash":
        return _text(q.get("q")) and _text(q.get("a"))
    if t != "mcq":
        return False
    opts, ans = q.get("options"), q.get("answer")
    return (_text(q.get("q")) and _text(q.get("explain")) and isinstance(opts, list) and len(opts) >= 2 and all(_text(o) for o in opts)
            and isinstance(ans, list) and bool(ans) and all(isinstance(a, int) and not isinstance(a, bool) and 0 <= a < len(opts) for a in ans))


def _level(v, default: str = "mid") -> str:
    return v if isinstance(v, str) and v in LEVELS else default


def _int(v, default: int) -> int:
    return v if isinstance(v, int) and not isinstance(v, bool) else default


def _tags(v) -> list:
    return [t for t in v if isinstance(t, str)] if isinstance(v, list) else []


class FsCatalog:
    def __init__(self, root: Path, home: Path, problems: FsProblems, packs_dir: Path = None):
        self.root, self.home, self.problems = Path(root), Path(home), problems
        self.packs_dir = Path(packs_dir) if packs_dir else self.root / "packs"

    def _json_files(self, *parts):
        for base in (self.root, self.home):
            d = base.joinpath(*parts)
            if d.is_dir():
                for f in sorted(d.glob("*.json")):
                    try:
                        yield json.loads(f.read_text())
                    except Exception:
                        continue

    @staticmethod
    def _valid(items, *, kind: str = "mcq") -> list:
        """Entries a user can write by hand may be malformed: keep only the ones with a text id and the fields their kind needs
        ("mcq" question lists, "bank" items of the memory banks, "output" quiz questions). A bad entry is skipped, never fatal."""
        return [q for q in (items if isinstance(items, list) else []) if _readable(q, kind)]

    def _question_lists(self):
        """Question files from the built-in bank, the user's workspace and every content pack (packs/<name>/questions)."""
        yield from self._json_files("bank", "questions")
        if self.packs_dir.is_dir():
            for pack in sorted(self.packs_dir.iterdir()):
                if (pack / "pack.json").is_file():
                    for f in sorted((pack / "questions").glob("*.json")):
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
                for q in self._valid(qs, kind="output"):
                    out.append({"ref": {"t": "output", "p": d.name, "q": q["id"]}, "module": str(m.get("module", "java-trivia")),
                                "level": _level(q.get("level")), "min_java": _int(q.get("min_java"), 8), "language": "java",
                                "tags": _tags([q.get("topic", "")]), "minutes": MIN_PER_ITEM["output"]})
            else:
                out.append({"ref": {"t": "code", "id": d.name}, "module": str(m.get("module", "coding")), "level": _level(m.get("level")),
                            "min_java": _int(m.get("min_java"), 8), "language": m.get("language", "java"), "tags": _tags(m.get("tags")),
                            "minutes": _int(m.get("time_limit_min"), 20)})
        for lst in self._question_lists():
            for q in self._valid(lst):
                out.append({"ref": {"t": "mcq", "id": q["id"]}, "module": str(q.get("module", "unknown")), "level": _level(q.get("level")),
                            "min_java": 0, "language": q.get("lang", "any"), "tags": _tags(q.get("tags")), "minutes": MIN_PER_ITEM["mcq"]})
        for bank in self._json_files("banks"):
            if not isinstance(bank, dict) or not isinstance(bank.get("id"), str):
                continue
            for q in self._valid(bank.get("items"), kind="bank"):
                out.append({"ref": {"t": "bank", "b": bank["id"], "q": q["id"]}, "module": "mybank", "level": "any", "min_java": 0,
                            "language": "any", "tags": _tags(q.get("tags")), "bank": bank["id"],
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
            for lst in self._question_lists():
                for q in self._valid(lst):
                    if q["id"] == ref["id"]:
                        return q | {"type": "mcq"}
        elif t == "bank":
            for bank in self._json_files("banks"):
                if isinstance(bank, dict) and bank.get("id") == ref.get("b"):
                    return next((q for q in self._valid(bank.get("items"), kind="bank") if q["id"] == ref.get("q")), None)
        elif t == "output":
            return next((q | {"type": "output"} for q in self._valid(self.problems.quiz_questions(ref["p"]), kind="output") if q["id"] == ref["q"]), None)
        return None
