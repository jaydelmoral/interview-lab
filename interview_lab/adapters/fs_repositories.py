"""ADAPTER: JSON-file persistence under $ILAB_HOME (exams/, banks/, runs/). Human-readable and easy to back up."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

EXAM_ID = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}$")
BANK_ID = re.compile(r"^b-[0-9a-f]{8}$")


class FsExamRepository:
    def __init__(self, home: Path):
        self.dir, self.runs = Path(home) / "exams", Path(home) / "runs"

    def save(self, exam: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / f"{exam['id']}.json").write_text(json.dumps(exam, ensure_ascii=False, indent=1))

    def load(self, exam_id: str) -> Optional[dict]:
        f = self.dir / f"{exam_id}.json"
        return json.loads(f.read_text()) if EXAM_ID.match(str(exam_id)) and f.exists() else None

    def list(self) -> list:
        out = []
        for f in sorted(self.dir.glob("*.json"), reverse=True)[:50] if self.dir.is_dir() else []:
            try:
                out.append(json.loads(f.read_text()))
            except Exception:
                continue
        return out

    def record_result(self, record: dict) -> None:
        self.runs.mkdir(parents=True, exist_ok=True)
        with open(self.runs / "exams.jsonl", "a") as f:
            f.write(json.dumps(record) + "\n")

    def last_results(self) -> dict:
        out, f = {}, self.runs / "exams.jsonl"
        if f.exists():
            for line in f.read_text().splitlines():
                try:
                    r = json.loads(line)
                    out[r["exam"]] = r
                except Exception:
                    continue
        return out


class FsBankRepository:
    def __init__(self, home: Path):
        self.dir = Path(home) / "banks"

    def save(self, bank: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / f"{bank['id']}.json").write_text(json.dumps(bank, ensure_ascii=False, indent=1))

    def list(self) -> list:
        out = []
        for f in sorted(self.dir.glob("*.json")) if self.dir.is_dir() else []:
            try:
                out.append(json.loads(f.read_text()))
            except Exception:
                continue
        return out

    def delete(self, bank_id: str) -> bool:
        f = self.dir / f"{bank_id}.json"
        if BANK_ID.match(str(bank_id)) and f.exists():
            f.unlink()
            return True
        return False


class JsonlLog:
    """Append-only results log (runs/results.jsonl)."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def append(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
