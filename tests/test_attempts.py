"""P4: with an attempt id the server grades once per section and computes the final result itself (client scores are ignored)."""
import unittest

from tests.helpers import RunningServer

ATTEMPT = "a" * 32
OTHER = "b" * 32


class ServerSideAttemptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rs = RunningServer()
        cls.c = cls.rs.client

    @classmethod
    def tearDownClass(cls):
        cls.rs.close()

    def setUp(self):
        _, self.exam = self.c.post("/api/exams", {"modules": ["sql", "coding"], "language": "java", "seniority": "mid"})
        self.eid = self.exam["id"]
        self.sql = next(i for i, s in enumerate(self.exam["sections"]) if s["module"] == "sql")
        self.coding = next(i for i, s in enumerate(self.exam["sections"]) if s["module"] == "coding")

    def section(self, answers, attempt=ATTEMPT, idx=None):
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
        for _ in range(2):                                        # FakeGrader always reports 5/10
            st, _ = self.c.post("/api/grade", {"problem": problems[0], "code": "class Solution {}", "exam": self.eid, "attempt": ATTEMPT})
            self.assertEqual(200, st)
        st, rec = self.finish([{"section": self.coding, "module": "coding", "score": 100, "max": 100}])
        self.assertEqual(200, st, rec)
        pct = rec["sections"][0]["score"]
        self.assertTrue(0 < pct < 100, pct)                           # one exercise partly graded, the rest never submitted

    def test_code_for_an_exercise_outside_the_exam_is_refused_before_grading(self):
        calls = len(self.rs.grader.calls)
        st, _ = self.c.post("/api/grade", {"problem": "not-in-this-exam", "code": "x", "exam": self.eid, "attempt": ATTEMPT})
        self.assertEqual(400, st)
        self.assertEqual(calls, len(self.rs.grader.calls))

    def test_a_finished_attempt_accepts_nothing_more(self):
        self.section({})
        self.finish([{"section": self.sql, "module": "sql"}])
        self.assertEqual(400, self.section({}, idx=self.sql)[0])
        problem = self.exam["sections"][self.coding]["items"][0]["id"]
        self.assertEqual(400, self.c.post("/api/grade", {"problem": problem, "code": "x", "exam": self.eid, "attempt": ATTEMPT})[0])

    def test_malformed_requests_are_rejected(self):
        for bad in ("short", 123, "G" * 32, ["a" * 32]):
            self.assertEqual(400, self.section({}, attempt=bad)[0], bad)
            self.assertEqual(400, self.finish([{"section": self.sql, "module": "sql"}], attempt=bad)[0], bad)
        for sections in ([], "x", [{"module": "sql"}], [{"section": 99}], [{"section": True}], [{"section": 0}, {"section": 0}], [{"section": 0}] * 31):
            self.assertEqual(400, self.finish(sections)[0], sections)

    def test_without_an_attempt_id_the_old_client_trusted_mode_still_works(self):
        st, rec = self.c.post(f"/api/exams/{self.eid}/finish", {"sections": [{"module": "sql", "score": 70, "max": 100}]})
        self.assertEqual((200, 70), (st, rec["sections"][0]["score"]))
        self.assertEqual(200, self.c.post("/api/grade", {"problem": self.exam["sections"][self.coding]["items"][0]["id"], "code": "x"})[0])


if __name__ == "__main__":
    unittest.main()
