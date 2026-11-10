"""P4: with an attempt id the server grades once per section and computes the final result itself (client scores are ignored)."""
import threading
import unittest

from tests.helpers import RunningServer

ATTEMPT = "a" * 32
OTHER = "b" * 32


class FakeClock:
    """The server's clock, moved by hand: timing rules are tested without sleeping."""
    def __init__(self):
        self.now = 1_800_000_000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class ServerSideAttemptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rs = RunningServer()
        cls.c = cls.rs.client
        cls.clock = cls.rs.handlers.exams.clock = FakeClock()

    @classmethod
    def tearDownClass(cls):
        cls.rs.close()

    def setUp(self):
        _, self.exam = self.c.post("/api/exams", {"modules": ["sql", "coding"], "language": "java", "seniority": "mid"})
        self.eid = self.exam["id"]
        self.sql = next(i for i, s in enumerate(self.exam["sections"]) if s["module"] == "sql")
        self.coding = next(i for i, s in enumerate(self.exam["sections"]) if s["module"] == "coding")

    def start(self, idx=None, attempt=ATTEMPT):
        return self.c.post(f"/api/exams/{self.eid}/start", {"section": self.sql if idx is None else idx, "attempt": attempt})

    def section(self, answers, attempt=ATTEMPT, idx=None):
        self.start(idx, attempt)                                      # idempotent: the clock starts once
        return self.c.post(f"/api/exams/{self.eid}/section", {"section": self.sql if idx is None else idx, "answers": answers, "attempt": attempt})

    def finish(self, sections, attempt=ATTEMPT, **extra):
        return self.c.post(f"/api/exams/{self.eid}/finish", {"sections": sections, "attempt": attempt, **extra})

    def runs(self):
        return self.c.get("/api/history")[1]["kpis"]["runs"]

    def test_a_section_is_graded_once_per_attempt(self):
        keys = [i["key"] for i in self.exam["sections"][self.sql]["items"]]
        _, first = self.section({})                                   # empty answers: everything wrong
        self.assertEqual(0, first["score"])
        guessed = {k: 0 for k in keys}
        self.assertEqual(first, self.section(guessed)[1])             # a second attempt at the same section returns the first report
        self.assertEqual(first, self.section({}, attempt=ATTEMPT)[1])
        _, other = self.section(guessed, attempt=OTHER)              # a different attempt is graded on its own
        self.assertEqual(sum(1 for i in other["items"] if i["correct"]), other["score"])

    def test_finish_ignores_the_scores_the_client_reports(self):
        self.section({})                                              # real score: 0 %
        before = self.runs()
        st, rec = self.finish([{"section": self.sql, "module": "sql", "score": 100, "max": 100, "pct": 100.0}])
        self.assertEqual(200, st, rec)
        self.assertEqual({"sql": 0}, {s["module"]: s["score"] for s in rec["sections"]})
        self.assertEqual(before + 1, self.runs())
        self.assertEqual(0.0, self.c.get("/api/history")[1]["kpis"]["last_overall"])

    def test_finishing_twice_stores_the_run_once(self):
        self.section({})
        sections = [{"section": self.sql, "module": "sql"}]
        before = self.runs()
        a, b = self.finish(sections)[1], self.finish(sections)[1]
        self.assertEqual(a, b)
        self.assertEqual(before + 1, self.runs())

    def test_an_ungraded_section_counts_as_nothing_answered(self):
        st, rec = self.finish([{"section": self.sql, "module": "sql", "score": 100, "max": 100}], attempt=OTHER)
        self.assertEqual((200, 0), (st, rec["sections"][0]["score"]))

    def test_missed_questions_come_from_the_server(self):
        self.section({})
        self.finish([{"section": self.sql, "module": "sql"}], missed=[{"section": "x", "q": "forged", "expected": "forged"}])
        _, overview = self.c.get("/api/history")
        run = self.c.get(f"/api/history/runs/{max(r['id'] for r in overview['trend'])}")[1]
        self.assertTrue(run["missed"])
        self.assertNotIn("forged", [m["question"] for m in run["missed"]])

    def test_code_score_is_the_best_graded_submission_of_each_exercise(self):
        problems = [i["id"] for i in self.exam["sections"][self.coding]["items"]]
        self.rs.grader.calls.clear()
        self.start(self.coding)
        for _ in range(2):                                        # FakeGrader always reports 5/10
            st, _ = self.c.post("/api/grade", {"problem": problems[0], "code": "class Solution {}", "exam": self.eid, "attempt": ATTEMPT})
            self.assertEqual(200, st)
        st, rec = self.finish([{"section": self.coding, "module": "coding", "score": 100, "max": 100}])
        self.assertEqual(200, st, rec)
        pct = rec["sections"][0]["score"]
        self.assertTrue(0 < pct < 100, pct)                           # one exercise partly graded, the rest never submitted

    def test_code_for_an_exercise_outside_the_exam_is_refused_before_grading(self):
        calls = len(self.rs.grader.calls)
        self.start(self.coding)
        st, _ = self.c.post("/api/grade", {"problem": "not-in-this-exam", "code": "x", "exam": self.eid, "attempt": ATTEMPT})
        self.assertEqual(400, st)
        self.assertEqual(calls, len(self.rs.grader.calls))

    def test_a_finished_attempt_accepts_nothing_more(self):
        self.section({})
        self.finish([{"section": self.sql, "module": "sql"}])
        self.assertEqual(400, self.section({}, idx=self.sql)[0])
        self.assertEqual(400, self.start(self.sql)[0])
        problem = self.exam["sections"][self.coding]["items"][0]["id"]
        self.assertEqual(400, self.c.post("/api/grade", {"problem": problem, "code": "x", "exam": self.eid, "attempt": ATTEMPT})[0])

    def test_malformed_requests_are_rejected(self):
        for bad in ("short", 123, "G" * 32, ["a" * 32]):
            self.assertEqual(400, self.section({}, attempt=bad)[0], bad)
            self.assertEqual(400, self.finish([{"section": self.sql, "module": "sql"}], attempt=bad)[0], bad)
        for sections in ([], "x", [{"module": "sql"}], [{"section": 99}], [{"section": True}], [{"section": 0}, {"section": 0}], [{"section": 0}] * 31):
            self.assertEqual(400, self.finish(sections)[0], sections)

    def test_the_attempt_id_is_mandatory_for_every_exam_call(self):
        pid = self.exam["sections"][self.coding]["items"][0]["id"]
        base = f"/api/exams/{self.eid}"
        for missing in (None, "", "short", "g" * 32, 5):                    # absent, empty, too short, not hex, not a string
            body = {} if missing is None else {"attempt": missing}
            for path, extra in (("/start", {"section": self.sql}), ("/answers", {"section": self.sql, "answers": {}}),
                                ("/section", {"section": self.sql, "answers": {}, "lang": "en"}), ("/finish", {"sections": [{"section": self.sql}]})):
                self.assertEqual(400, self.c.post(base + path, extra | body)[0], (path, missing))
            self.assertEqual(400, self.c.post("/api/grade", {"problem": pid, "code": "x", "exam": self.eid} | body)[0], missing)
        self.assertEqual(400, self.c.post("/api/grade", {"problem": pid, "code": "x", "attempt": ATTEMPT})[0])   # an attempt without its exam
        self.assertEqual(200, self.c.post("/api/grade", {"problem": pid, "code": "x"})[0])                       # free practice is not an exam


class LocalRobustnessTest(unittest.TestCase):
    """Things that could break a local installation: hand-written content, crashes while saving, a proxy variable."""

    def test_one_malformed_question_does_not_break_every_exam(self):
        import json
        rs = RunningServer()
        try:
            qdir = rs.home / "bank" / "questions"
            qdir.mkdir(parents=True)
            (qdir / "mine.json").write_text(json.dumps([{"module": "sql", "level": "mid"}, "text", {"id": 5}, None]))
            (rs.home / "banks").mkdir()
            (rs.home / "banks" / "b-00000000.json").write_text(json.dumps({"id": "b-00000000", "items": [{"id": "x"}, {"type": "mcq"}, 7]}))
            (rs.home / "banks" / "b-11111111.json").write_text(json.dumps({"items": []}))
            st, exam = rs.client.post("/api/exams", {"modules": ["sql"], "language": "java", "seniority": "mid"})
            self.assertEqual(200, st, exam)
            self.assertEqual(200, rs.client.get("/api/modules")[0])
        finally:
            rs.close()

    def test_saving_replaces_the_file_atomically_and_leaves_no_temporary_files(self):
        import tempfile
        from pathlib import Path
        from interview_lab.adapters.fs_repositories import FsAttemptRepository, FsBankRepository, FsExamRepository
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            FsExamRepository(home).save({"id": "20261110-120000-abcd", "sections": []})
            FsBankRepository(home).save({"id": "b-0123abcd", "items": []})
            FsAttemptRepository(home).save("20261110-120000-abcd", "a" * 32, {"sections": {}})
            files = [p.name for p in home.rglob("*") if p.is_file()]
            self.assertEqual(3, len(files), files)
            self.assertFalse([f for f in files if f.endswith(".tmp")], files)
            self.assertEqual({"id": "20261110-120000-abcd", "sections": []}, FsExamRepository(home).load("20261110-120000-abcd"))

    def test_ollama_requests_never_go_through_a_proxy(self):
        import http.server
        import os
        from unittest import mock
        from interview_lab.adapters import ollama_generator as og

        class Hello(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b'{"models": []}')

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), Hello)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with mock.patch.dict(os.environ, {"http_proxy": "http://127.0.0.1:9", "HTTP_PROXY": "http://127.0.0.1:9", "no_proxy": "", "NO_PROXY": ""}):
                self.assertEqual([], og.installed_models(f"http://127.0.0.1:{srv.server_port}"))   # a dead proxy would make this fail
        finally:
            srv.shutdown()
            srv.server_close()


class ServerClockTest(unittest.TestCase):
    """The time limit is enforced with the server's clock: the browser's timer is only a display."""

    @classmethod
    def setUpClass(cls):
        cls.rs = RunningServer()
        cls.c = cls.rs.client
        cls.clock = cls.rs.handlers.exams.clock = FakeClock()

    @classmethod
    def tearDownClass(cls):
        cls.rs.close()

    def setUp(self):
        _, self.exam = self.c.post("/api/exams", {"modules": ["sql", "coding"], "language": "java", "seniority": "mid"})
        self.eid = self.exam["id"]
        self.sql = next(i for i, s in enumerate(self.exam["sections"]) if s["module"] == "sql")
        self.coding = next(i for i, s in enumerate(self.exam["sections"]) if s["module"] == "coding")
        self.limit = self.exam["sections"][self.sql]["minutes"] * 60
        self.keys = [i["key"] for i in self.exam["sections"][self.sql]["items"]]

    def post(self, path, body):
        return self.c.post(f"/api/exams/{self.eid}/{path}", {"attempt": ATTEMPT, **body})

    def test_the_deadline_is_fixed_when_the_section_starts(self):
        _, a = self.post("start", {"section": self.sql})
        self.assertEqual((self.limit * 1000, False), (a["remaining_ms"], a["expired"]))
        self.clock.advance(60)
        _, b = self.post("start", {"section": self.sql})              # a reload asks again: same deadline, less time left
        self.assertEqual(self.limit * 1000 - 60_000, b["remaining_ms"])
        self.clock.advance(self.limit)
        _, c = self.post("start", {"section": self.sql})
        self.assertEqual((0, True), (c["remaining_ms"], c["expired"]))

    def test_when_time_is_up_the_section_is_graded_with_the_last_saved_answers(self):
        other = lambda path, body: self.c.post(f"/api/exams/{self.eid}/{path}", {"attempt": OTHER, **body})      # noqa: E731
        other("start", {"section": self.sql})
        _, probe = other("section", {"section": self.sql, "answers": {}})
        right = {r["key"]: (r["expected_index"] if len(r["expected_index"]) > 1 else r["expected_index"][0]) for r in probe["items"]}

        self.post("start", {"section": self.sql})
        half = dict(list(right.items())[:len(right) // 2])             # what was marked before the tab was closed
        self.assertEqual(200, self.post("answers", {"section": self.sql, "answers": half})[0])
        self.clock.advance(self.limit + 600)
        self.assertEqual(400, self.post("answers", {"section": self.sql, "answers": right})[0])   # late autosaves are refused
        st, late = self.post("section", {"section": self.sql, "answers": right})                  # late claims are not trusted
        self.assertEqual(200, st)
        self.assertEqual(len(half), late["score"])                     # graded exactly as it was left, not with the full answer sheet
        self.assertLess(late["score"], len(right))

    def test_a_submission_inside_the_grace_period_still_counts(self):
        self.post("start", {"section": self.sql})
        self.clock.advance(self.limit + 5)
        self.assertEqual(200, self.post("section", {"section": self.sql, "answers": {}})[0])

    def test_grading_needs_a_started_section(self):
        self.assertEqual(400, self.post("section", {"section": self.sql, "answers": {}})[0])
        self.assertEqual(400, self.post("answers", {"section": self.sql, "answers": {}})[0])

    def test_code_is_not_graded_after_time_is_up(self):
        self.post("start", {"section": self.coding})
        problem = self.exam["sections"][self.coding]["items"][0]["id"]
        self.assertEqual(200, self.c.post("/api/grade", {"problem": problem, "code": "x", "exam": self.eid, "attempt": ATTEMPT})[0])
        self.clock.advance(self.exam["sections"][self.coding]["minutes"] * 60 + 120)
        calls = len(self.rs.grader.calls)
        self.assertEqual(400, self.c.post("/api/grade", {"problem": problem, "code": "x", "exam": self.eid, "attempt": ATTEMPT})[0])
        self.assertEqual(calls, len(self.rs.grader.calls))

    def test_a_late_report_carries_the_answers_it_was_graded_with(self):
        self.post("start", {"section": self.sql})
        mine = {self.keys[0]: 1, "not-an-item": 5, self.keys[1]: [True, "x", 2]}
        self.post("answers", {"section": self.sql, "answers": mine})
        self.clock.advance(self.limit + 100)
        _, rep = self.post("section", {"section": self.sql, "answers": {self.keys[2]: 0}})
        self.assertEqual({self.keys[0]: 1, self.keys[1]: [2]}, rep["answers"])       # saved ones, cleaned; the late claim is ignored

    def test_starting_a_closed_section_reports_it_as_expired(self):
        self.post("start", {"section": self.sql})
        self.post("section", {"section": self.sql, "answers": {}})
        _, again = self.post("start", {"section": self.sql})
        self.assertEqual((True, True), (again["expired"], again["closed"]))

    def test_finishing_grades_an_unclosed_section_from_the_saved_answers_and_closes_it(self):
        other = lambda path, body: self.c.post(f"/api/exams/{self.eid}/{path}", {"attempt": OTHER, **body})      # noqa: E731
        other("start", {"section": self.sql})
        _, probe = other("section", {"section": self.sql, "answers": {}})
        right = {r["key"]: (r["expected_index"] if len(r["expected_index"]) > 1 else r["expected_index"][0]) for r in probe["items"]}
        self.post("start", {"section": self.sql})
        self.post("answers", {"section": self.sql, "answers": right})
        self.clock.advance(90)
        st, rec = self.post("finish", {"sections": [{"section": self.sql, "module": "sql"}]})      # never sent to /section
        self.assertEqual((200, 100), (st, rec["sections"][0]["score"]))
        detail = self.c.get(f"/api/history/runs/{self.c.get('/api/history')[1]['trend'][-1]['id']}")[1]
        self.assertEqual(1.5, detail["sections"][0]["used_min"])

    def test_a_code_grade_that_lands_after_the_section_closed_is_not_counted(self):
        service = self.rs.handlers.exams
        self.post("start", {"section": self.coding})
        problem = self.exam["sections"][self.coding]["items"][0]["id"]
        target = service.code_target(self.eid, ATTEMPT, problem)             # accepted: the section is running...
        self.post("section", {"section": self.coding, "answers": {}})        # ...then it is closed while the JVM is still grading
        service.record_code(target, {"score": 10, "max": 10, "tests": []})
        _, rec = self.post("finish", {"sections": [{"section": self.coding, "module": "coding"}]})
        self.assertEqual(0, rec["sections"][0]["score"])

    def test_attempt_files_without_timing_data_still_load(self):
        repo = self.rs.handlers.exams.attempts
        repo.save(self.eid, ATTEMPT, {"sections": {}, "code": {}, "finished": None})       # shape written before the clock existed
        st, out = self.post("start", {"section": self.sql})
        self.assertEqual((200, False), (st, out["expired"]))

    def test_time_used_is_measured_by_the_server(self):
        self.post("start", {"section": self.sql})
        self.clock.advance(150)                                       # 2.5 minutes
        self.post("section", {"section": self.sql, "answers": {}})
        self.assertEqual(200, self.post("finish", {"sections": [{"section": self.sql, "module": "sql", "used": 0.1}]})[0])    # the reported 0.1 is ignored
        run = self.c.get("/api/history")[1]["trend"][-1]
        detail = self.c.get(f"/api/history/runs/{run['id']}")[1]
        self.assertEqual(2.5, detail["sections"][0]["used_min"])
        self.assertEqual(self.limit / 60, detail["sections"][0]["allotted_min"])


if __name__ == "__main__":
    unittest.main()
