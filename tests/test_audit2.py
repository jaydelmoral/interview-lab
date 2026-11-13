"""Regression tests for the 2026-11-13 audit: wrong types never cause a 500, one malformed hand-written entry
never breaks an exam, and what a section stores is only what grading understands."""
import json
import unittest

from tests.helpers import ROOT, RunningServer

ATTEMPT = "c" * 32
GOOD = {"id": "u-good", "module": "sql", "level": "sr", "q": {"es": "p", "en": "q"}, "options": [{"es": "a"}, {"es": "b"}], "answer": [1],
        "explain": {"es": "e"}, "tags": ["joins"]}
BAD = [
    {"id": "u-no-fields", "module": "sql"},                                                   # only an id
    GOOD | {"id": "u-options-text", "options": "abc"},                                        # options is not a list
    GOOD | {"id": "u-answer-out", "answer": [7]},                                             # answer points outside the options
    GOOD | {"id": "u-answer-bool", "answer": [True]},
    GOOD | {"id": "u-tags-number", "tags": 5},
    GOOD | {"id": "u-review-text", "review": "yes"},
    GOOD | {"id": 12},                                                                        # id is not a text
    "not a question",
]


class WrongTypesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = RunningServer()
        cls.c = cls.srv.client

    @classmethod
    def tearDownClass(cls):
        cls.srv.close()

    def test_a_problem_id_that_is_not_a_text_is_not_a_500(self):
        for bad in (100000000000, 1.5, True, [1], {"a": 1}):
            self.assertEqual(400, self.c.post("/api/grade", {"problem": bad, "code": "class A {}"})[0], bad)
            self.assertEqual(400, self.c.post("/api/quiz", {"problem": bad, "answers": {}})[0], bad)

    def test_bank_links_that_are_not_a_list_are_ignored(self):
        for bad in (1, 1.5, True, {"a": 1}, "https://example.org"):
            status, body = self.c.post("/api/banks", {"title": "x", "urls": bad, "notes": ""})
            self.assertEqual(400, status, (bad, body))                                        # nothing to build from: a clean refusal

    def test_a_section_index_must_be_a_real_number(self):
        _, exam = self.c.post("/api/exams", {"modules": ["sql", "unix"]})
        self.c.post(f"/api/exams/{exam['id']}/start", {"section": 1, "attempt": ATTEMPT})
        status, _ = self.c.post(f"/api/exams/{exam['id']}/section", {"section": True, "answers": {}, "attempt": ATTEMPT})
        self.assertEqual(400, status)

    def test_grading_a_section_stores_only_cleaned_answers(self):
        _, exam = self.c.post("/api/exams", {"modules": ["sql"]})
        eid, keys = exam["id"], [i["key"] for i in exam["sections"][0]["items"]]
        self.c.post(f"/api/exams/{eid}/start", {"section": 0, "attempt": ATTEMPT})
        junk = {"x" * 50: "y" * 60000, "nested": {"a": [1, [2]]}, keys[0]: 0, keys[1]: {"not": "an answer"}}
        status, report = self.c.post(f"/api/exams/{eid}/section", {"section": 0, "answers": junk, "attempt": ATTEMPT})
        self.assertEqual(200, status, report)
        self.assertEqual({keys[0]: 0}, report["answers"])                                     # only known items with a usable value
        stored = self.srv.home / "exam-attempts" / f"{eid}-{ATTEMPT}.json"
        self.assertLess(stored.stat().st_size, 30_000)


class MalformedUserQuestionsTest(unittest.TestCase):
    """A question file the user wrote by hand: the readable entries are used, the rest are skipped, nothing breaks."""

    def setUp(self):
        self.srv = RunningServer()
        self.c = self.srv.client
        folder = self.srv.home / "bank" / "questions"
        folder.mkdir(parents=True)
        (folder / "mine.json").write_text(json.dumps(BAD + [GOOD, GOOD | {"id": "u-odd-level", "level": "wizard", "module": ["sql"]}]), encoding="utf-8")

    def tearDown(self):
        self.srv.close()

    def test_bad_entries_are_skipped_and_the_exam_still_works(self):
        self.assertEqual(200, self.c.get("/api/modules")[0])                                  # counting must not trip on an odd module
        status, exam = self.c.post("/api/exams", {"modules": ["sql"], "counts": {"sql": 200}})
        self.assertEqual(200, status, exam)
        keys = {i["key"] for i in exam["sections"][0]["items"]}
        self.assertIn("mcq:u-good", keys)
        self.assertFalse({k for k in keys if k.split(":")[1] in {b["id"] for b in BAD if isinstance(b, dict) and isinstance(b.get("id"), str)}})
        eid = exam["id"]
        self.assertEqual(200, self.c.get(f"/api/exams/{eid}")[0])
        self.c.post(f"/api/exams/{eid}/start", {"section": 0, "attempt": ATTEMPT})
        status, report = self.c.post(f"/api/exams/{eid}/section", {"section": 0, "answers": {}, "attempt": ATTEMPT})
        self.assertEqual(200, status, report)
        self.assertEqual(200, self.c.post(f"/api/exams/{eid}/finish", {"sections": [{"section": 0}], "attempt": ATTEMPT})[0])

    def test_the_built_in_bank_loses_nothing_to_the_stricter_reader(self):
        raw = sum(len(json.loads(f.read_text(encoding="utf-8"))) for f in sorted((ROOT / "bank" / "questions").glob("*.json")))
        counts = self.c.get("/api/modules")[1]["modules"]
        served = sum(m["count"] for m in counts if m["id"] not in ("coding", "java-trivia", "mybank"))
        self.assertEqual(raw + 1, served)                                                     # every built-in question, plus the one good entry above


if __name__ == "__main__":
    unittest.main()
