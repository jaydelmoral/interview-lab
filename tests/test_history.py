"""History and analytics: pure analytics, the SQLite adapter, and the HTTP flow (finish exam -> dashboard data)."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from interview_lab.adapters.sqlite_history import SqliteHistory
from interview_lab.domain import analytics
from tests.helpers import RunningServer


def run(exam_id="e1", when="2026-11-10 10:00:00", overall=50.0, sections=None, missed=None, title="T"):
    return {"exam_id": exam_id, "finished_at": when, "title": title, "seniority": "sr", "language": "java", "version": 21,
            "overall_pct": overall, "total_minutes": 20, "used_minutes": 10,
            "sections": sections if sections is not None else [{"module": "sql", "title": "SQL", "pct": overall, "correct": 2, "total": 5, "used_min": 4, "allotted_min": 6}],
            "missed": missed or []}


class TestAnalytics(unittest.TestCase):
    def test_delta_needs_two_points_and_compares_with_previous_mean(self):
        self.assertIsNone(analytics.delta([50]))
        self.assertEqual(analytics.delta([40, 60]), 20.0)
        self.assertEqual(analytics.delta([30, 50, 70, 80]), 30.0)         # 80 - mean(30,50,70)

    def test_streak_counts_back_from_today_or_yesterday(self):
        days = {"2026-11-08", "2026-11-09", "2026-11-10"}
        self.assertEqual(analytics.streak_days(days, date(2026, 11, 10)), 3)
        self.assertEqual(analytics.streak_days({"2026-11-09"}, date(2026, 11, 10)), 1)      # nothing yet today, but yesterday counts
        self.assertEqual(analytics.streak_days({"2026-11-01"}, date(2026, 11, 10)), 0)

    def test_summarize_orders_weakest_modules_first_and_counts_tags(self):
        runs = [
            dict(run("a", "2026-11-09 09:00:00", 70, [{"module": "sql", "title": "SQL", "pct": 80, "correct": 4, "total": 5, "used_min": 4, "allotted_min": 6},
                                                      {"module": "unix", "title": "Unix", "pct": 40, "correct": 2, "total": 5, "used_min": 6, "allotted_min": 6}],
                      [{"section": "Unix", "question": "q", "expected": "x", "tags": ["permissions"]}]), id=1),
            dict(run("b", "2026-11-10 09:00:00", 60, [{"module": "unix", "title": "Unix", "pct": 60, "correct": 3, "total": 5, "used_min": 5, "allotted_min": 6}],
                      [{"section": "Unix", "question": "q2", "expected": "y", "tags": ["permissions", "pipes"]}]), id=2),
        ]
        out = analytics.summarize(runs, [{"problem_id": "p1", "kind": "code", "attempted_at": "2026-11-10 10:00:00", "score": 5, "max": 10, "passed": 1, "total": 2},
                                         {"problem_id": "p1", "kind": "code", "attempted_at": "2026-11-10 11:00:00", "score": 10, "max": 10, "passed": 2, "total": 2}],
                                date(2026, 11, 10))
        self.assertEqual([m["module"] for m in out["modules"]], ["unix", "sql"])             # weakest first
        self.assertEqual(out["weak_tags"][0], {"tag": "permissions", "count": 2, "last_seen": "2026-11-10"})
        self.assertEqual(out["kpis"]["runs"], 2)
        self.assertEqual(out["kpis"]["streak_days"], 2)
        self.assertEqual(out["code"][0]["improved"], 50.0)
        self.assertEqual(out["recent"][0]["id"], 2)                                          # newest first

    def test_empty_history_is_safe(self):
        out = analytics.summarize([], [])
        self.assertEqual(out["kpis"]["runs"], 0)
        self.assertIsNone(out["kpis"]["avg_overall"])


class TestSqliteHistory(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="ilab-hist-"))
        self.h = SqliteHistory(self.dir / "ilab.db")

    def test_schema_is_versioned_and_reopening_is_safe(self):
        self.assertEqual(self.h.schema_version(), 1)
        self.assertEqual(SqliteHistory(self.dir / "ilab.db").schema_version(), 1)

    def test_records_run_with_sections_and_missed_and_is_idempotent(self):
        rid = self.h.record_run("local", run(missed=[{"section": "SQL", "question": "q", "expected": "x", "explanation": "e", "tags": ["join"]}]))
        self.assertEqual(self.h.record_run("local", run()), rid)                              # same exam, same second
        r = self.h.run("local", rid)
        self.assertEqual(r["sections"][0]["module"], "sql")
        self.assertEqual(r["missed"][0]["tags"], ["join"])
        self.assertEqual(len(self.h.runs("local")), 1)

    def test_profiles_are_isolated(self):
        self.h._ensure_profile("other", "Other")
        self.h.record_run("local", run("a"))
        self.h.record_run("other", run("b", "2026-11-10 11:00:00"))
        self.assertEqual([r["exam_id"] for r in self.h.runs("local")], ["a"])
        self.assertEqual([r["exam_id"] for r in self.h.runs("other")], ["b"])

    def test_legacy_jsonl_is_imported_once_and_bad_lines_are_skipped(self):
        runs_dir, exams_dir = self.dir / "runs", self.dir / "exams"
        runs_dir.mkdir()
        exams_dir.mkdir()
        (exams_dir / "x1.json").write_text(json.dumps({"id": "x1", "title": "Old", "total_minutes": 30, "config": {"seniority": "mid", "language": "java", "version": 17}}))
        (runs_dir / "exams.jsonl").write_text(json.dumps({"exam": "x1", "when": "2026-11-01 10:00:00", "score": 60, "max": 100, "sections": [{"module": "sql", "score": 60, "max": 100}]}) + "\nnot json\n")
        (runs_dir / "results.jsonl").write_text(json.dumps({"timestamp": "2026-11-01 10:05:00", "problem": "p1", "score": 5, "max": 10}) + "\n")
        self.assertEqual(self.h.import_legacy(runs_dir, exams_dir), {"runs": 1, "attempts": 1, "skipped": False})
        self.assertTrue(self.h.import_legacy(runs_dir, exams_dir)["skipped"])
        self.assertEqual(self.h.runs("local")[0]["title"], "Old")
        self.assertEqual(len(self.h.attempts("local")), 1)


class TestHistoryApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = RunningServer()
        cls.c = cls.srv.client

    @classmethod
    def tearDownClass(cls):
        cls.srv.close()

    def test_finishing_an_exam_feeds_the_dashboard(self):
        st, exam = self.c.post("/api/exams", {"seniority": "sr", "language": "java", "version": 21, "pace": "standard", "modules": ["sql"], "banks": [], "lang": "es"})
        self.assertEqual(st, 200)
        sections = [{"module": "sql", "title": "SQL", "score": 60, "max": 100, "pct": 60.0, "correct": 3, "total": 5, "used": 4.5, "allotted": 6},
                    {"module": "unix", "title": "Unix", "score": 40, "max": 100, "pct": 40.0, "correct": 2, "total": 5, "used": 6, "allotted": 6}]
        st, _ = self.c.post(f"/api/exams/{exam['id']}/finish", {"sections": sections, "missed": [{"section": "SQL", "q": "What is a JOIN?", "expected": "x", "explanation": "e", "tags": ["join"]}]})
        self.assertEqual(st, 200)
        st, data = self.c.get("/api/history")
        self.assertEqual(st, 200)
        self.assertEqual(data["kpis"]["runs"], 1)
        self.assertEqual(data["kpis"]["avg_overall"], 50.0)
        self.assertEqual(data["weak_tags"][0]["tag"], "join")
        run_id = data["recent"][0]["id"]
        st, detail = self.c.get(f"/api/history/runs/{run_id}")
        self.assertEqual((st, len(detail["sections"]), detail["missed"][0]["question"]), (200, 2, "What is a JOIN?"))

    def test_legacy_client_payload_and_garbage_do_not_break_finish(self):
        _, exam = self.c.post("/api/exams", {"seniority": "sr", "language": "java", "version": 21, "pace": "standard", "modules": ["sql"], "banks": [], "lang": "es"})
        st, _ = self.c.post(f"/api/exams/{exam['id']}/finish", {"sections": [{"module": "sql", "score": 3, "max": 5}],
                                                                  "missed": ["junk", {"q": 5, "tags": "no"}, {"q": "x" * 5000, "tags": ["a"] * 50}]})
        self.assertEqual(st, 200)

    def test_unknown_run_is_404_and_bad_id_is_not_routed(self):
        self.assertEqual(self.c.get("/api/history/runs/999999")[0], 404)
        self.assertEqual(self.c.get("/api/history/runs/abc")[0], 404)

    def test_code_attempt_is_recorded(self):
        st, _ = self.c.post("/api/grade", {"problem": "001-seat-lookup", "code": "class Solution {}", "lang": "es"})
        self.assertEqual(st, 200)
        _, data = self.c.get("/api/history")
        self.assertTrue(any(p["problem"] == "001-seat-lookup" for p in data["code"]))


if __name__ == "__main__":
    unittest.main()
