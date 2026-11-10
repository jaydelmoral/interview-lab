"""ADAPTER: SQLite implementation of the HistoryRepository port (standard library `sqlite3`, no dependencies).

One database file (`<home>/ilab.db`). A connection per call keeps it thread-safe with the threaded HTTP server;
WAL mode lets the dashboard read while a grading result is written. Every table carries `profile_id` so a future
multi-user edition does not need a data migration (see ADR-0017). Schema versioning uses `PRAGMA user_version`.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

DEFAULT_PROFILE = "local"

MIGRATIONS = [
    # --- v1
    """
    CREATE TABLE profiles(id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')));
    CREATE TABLE exam_runs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id TEXT NOT NULL REFERENCES profiles(id),
        exam_id TEXT NOT NULL, finished_at TEXT NOT NULL, title TEXT, seniority TEXT, language TEXT, version INTEGER,
        overall_pct REAL NOT NULL, total_minutes REAL, used_minutes REAL,
        UNIQUE(profile_id, exam_id, finished_at));
    CREATE TABLE section_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL REFERENCES exam_runs(id) ON DELETE CASCADE,
        module TEXT NOT NULL, title TEXT, pct REAL NOT NULL, correct INTEGER, total INTEGER, used_min REAL, allotted_min REAL);
    CREATE TABLE missed_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL REFERENCES exam_runs(id) ON DELETE CASCADE,
        section TEXT, question TEXT, expected TEXT, explanation TEXT, tags TEXT NOT NULL DEFAULT '[]');
    CREATE TABLE code_attempts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id TEXT NOT NULL REFERENCES profiles(id),
        problem_id TEXT NOT NULL, kind TEXT NOT NULL, attempted_at TEXT NOT NULL,
        score INTEGER NOT NULL, max INTEGER NOT NULL, passed INTEGER, total INTEGER,
        UNIQUE(profile_id, problem_id, attempted_at, score));
    CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE INDEX idx_runs_profile ON exam_runs(profile_id, finished_at);
    CREATE INDEX idx_sections_run ON section_results(run_id);
    CREATE INDEX idx_missed_run ON missed_items(run_id);
    CREATE INDEX idx_attempts_profile ON code_attempts(profile_id, attempted_at);
    """,
]


class SqliteHistory:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()       # serialises writers (SQLite allows one anyway); readers do not need it
        with self._conn() as c:
            c.execute("PRAGMA journal_mode=WAL")
        self._migrate()
        self._ensure_profile(DEFAULT_PROFILE, "Local")

    # ------------------------------------------------------------------ plumbing
    @contextmanager
    def _conn(self):
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        try:
            yield c
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            c.close()

    def _migrate(self) -> None:
        with self._lock, self._conn() as c:
            version = c.execute("PRAGMA user_version").fetchone()[0]
            for i in range(version, len(MIGRATIONS)):
                c.executescript(MIGRATIONS[i])            # executescript commits; fine for DDL
                c.execute(f"PRAGMA user_version={i + 1}")

    def schema_version(self) -> int:
        with self._conn() as c:
            return c.execute("PRAGMA user_version").fetchone()[0]

    def _ensure_profile(self, pid: str, name: str) -> None:
        with self._lock, self._conn() as c:
            c.execute("INSERT OR IGNORE INTO profiles(id, name) VALUES (?, ?)", (pid, name))

    # ------------------------------------------------------------------ writes
    def record_run(self, profile_id: str, run: dict) -> int:
        with self._lock, self._conn() as c:
            cur = c.execute(
                "INSERT OR IGNORE INTO exam_runs(profile_id, exam_id, finished_at, title, seniority, language, version, overall_pct, total_minutes, used_minutes)"
                " VALUES (?,?,?,?,?,?,?,?,?,?)",
                (profile_id, run["exam_id"], run["finished_at"], run.get("title"), run.get("seniority"), run.get("language"), run.get("version"),
                 run["overall_pct"], run.get("total_minutes"), run.get("used_minutes")))
            if cur.rowcount == 0:                           # same exam finished in the same second: already stored
                return c.execute("SELECT id FROM exam_runs WHERE profile_id=? AND exam_id=? AND finished_at=?",
                                 (profile_id, run["exam_id"], run["finished_at"])).fetchone()[0]
            rid = cur.lastrowid
            c.executemany("INSERT INTO section_results(run_id, module, title, pct, correct, total, used_min, allotted_min) VALUES (?,?,?,?,?,?,?,?)",
                          [(rid, s["module"], s.get("title"), s["pct"], s.get("correct"), s.get("total"), s.get("used_min"), s.get("allotted_min")) for s in run["sections"]])
            c.executemany("INSERT INTO missed_items(run_id, section, question, expected, explanation, tags) VALUES (?,?,?,?,?,?)",
                          [(rid, q.get("section"), q.get("question"), q.get("expected"), q.get("explanation"), json.dumps(q.get("tags") or [])) for q in run.get("missed", [])])
            return rid

    def record_attempt(self, profile_id: str, a: dict) -> None:
        with self._lock, self._conn() as c:
            c.execute("INSERT OR IGNORE INTO code_attempts(profile_id, problem_id, kind, attempted_at, score, max, passed, total) VALUES (?,?,?,?,?,?,?,?)",
                      (profile_id, a["problem_id"], a["kind"], a["attempted_at"], a["score"], a["max"], a.get("passed"), a.get("total")))

    # ------------------------------------------------------------------ reads
    def runs(self, profile_id: str, with_details: bool = True) -> list:
        """All runs of a profile, oldest first, each with its sections and missed questions."""
        with self._conn() as c:
            rows = [dict(r) for r in c.execute("SELECT * FROM exam_runs WHERE profile_id=? ORDER BY finished_at, id", (profile_id,))]
            by_id = {r["id"]: r for r in rows}
            for r in rows:
                r["sections"], r["missed"] = [], []
            if rows:
                q = ",".join("?" * len(by_id))
                for s in c.execute(f"SELECT * FROM section_results WHERE run_id IN ({q}) ORDER BY id", list(by_id)):
                    by_id[s["run_id"]]["sections"].append({k: s[k] for k in ("module", "title", "pct", "correct", "total", "used_min", "allotted_min")})
                if with_details:
                    for m in c.execute(f"SELECT * FROM missed_items WHERE run_id IN ({q}) ORDER BY id", list(by_id)):
                        by_id[m["run_id"]]["missed"].append({"section": m["section"], "question": m["question"], "expected": m["expected"],
                                                             "explanation": m["explanation"], "tags": json.loads(m["tags"])})
        return rows

    def run(self, profile_id: str, run_id: int) -> Optional[dict]:
        return next((r for r in self.runs(profile_id) if r["id"] == run_id), None)

    def attempts(self, profile_id: str) -> list:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT problem_id, kind, attempted_at, score, max, passed, total FROM code_attempts WHERE profile_id=? ORDER BY attempted_at, id", (profile_id,))]

    # ------------------------------------------------------------------ one-time import of the pre-SQLite JSONL logs
    def import_legacy(self, runs_dir: Path, exams_dir: Path, profile_id: str = DEFAULT_PROFILE) -> dict:
        with self._conn() as c:
            done = c.execute("SELECT value FROM meta WHERE key='legacy_imported'").fetchone()
        if done:
            return {"runs": 0, "attempts": 0, "skipped": True}
        runs = attempts = 0
        f = Path(runs_dir) / "exams.jsonl"
        if f.exists():
            for line in f.read_text().splitlines():
                try:
                    r = json.loads(line)
                    cfg = {}
                    ef = Path(exams_dir) / f"{r['exam']}.json"
                    if ef.exists():
                        cfg = json.loads(ef.read_text())
                    secs = [{"module": s["module"], "title": s["module"], "pct": 100.0 * s["score"] / s["max"] if s["max"] else 0.0} for s in r["sections"]]
                    self.record_run(profile_id, {"exam_id": r["exam"], "finished_at": r["when"], "title": cfg.get("title"),
                                                 "seniority": (cfg.get("config") or {}).get("seniority"), "language": (cfg.get("config") or {}).get("language"),
                                                 "version": (cfg.get("config") or {}).get("version"), "total_minutes": cfg.get("total_minutes"),
                                                 "overall_pct": 100.0 * r["score"] / r["max"] if r["max"] else 0.0, "sections": secs})
                    runs += 1
                except (KeyError, ValueError, TypeError, ZeroDivisionError):
                    continue                                 # a malformed legacy line must not block the import
        f = Path(runs_dir) / "results.jsonl"
        if f.exists():
            for line in f.read_text().splitlines():
                try:
                    r = json.loads(line)
                    self.record_attempt(profile_id, {"problem_id": r["problem"], "kind": "code", "attempted_at": r["timestamp"], "score": r["score"], "max": r["max"]})
                    attempts += 1
                except (KeyError, ValueError, TypeError):
                    continue
        with self._lock, self._conn() as c:
            c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('legacy_imported', datetime('now','localtime'))")
        return {"runs": runs, "attempts": attempts, "skipped": False}
