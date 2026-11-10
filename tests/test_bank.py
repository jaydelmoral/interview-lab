"""Question bank: the MUST-HAVE source/review rules, content packs, and Staff/Principal levels."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from interview_lab.domain import exam as rules
from interview_lab.domain import profile
from tests.helpers import RunningServer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import validate_bank as VB  # noqa: E402


def good_question(qid="sql-900", **over):
    q = {"id": qid, "type": "mcq", "module": "sql", "level": "sr", "lang": "any", "tags": ["x"],
         "q": {"en": "Q?", "es": "¿Q?"}, "options": [{"en": f"o{i}", "es": f"o{i}"} for i in range(4)], "answer": [0],
         "explain": {"en": "e", "es": "e"}, "sources": [{"title": "Docs", "url": "https://example.com/docs"}],
         "review": {"status": "draft", "author": "tester", "date": "2026-11-10"}}
    q.update(over)
    return q


class TestBankValidator(unittest.TestCase):
    def errors(self, q):
        out = []
        VB.check_question(q, "t.json", out)
        return out

    def test_valid_question_passes(self):
        self.assertEqual(self.errors(good_question()), [])

    def test_must_have_sources(self):
        for bad in ({"sources": []}, {"sources": [{"title": "x", "url": "http://insecure.example"}]}, {"sources": [{"url": "https://x.y"}]}):
            self.assertTrue(any("source" in e for e in self.errors(good_question(**bad))), bad)
        q = good_question()
        del q["sources"]
        self.assertTrue(self.errors(q))

    def test_must_have_review_status_and_reviewer_when_reviewed(self):
        self.assertTrue(self.errors(good_question(review={"status": "maybe", "author": "a", "date": "d"})))
        self.assertTrue(self.errors(good_question(review={"status": "reviewed", "author": "a", "date": "d"})))          # no reviewer
        self.assertEqual(self.errors(good_question(review={"status": "reviewed", "author": "a", "date": "d", "reviewer": "Ana"})), [])

    def test_structure_rules(self):
        self.assertTrue(self.errors(good_question(answer=[5])))
        self.assertTrue(self.errors(good_question(options=[{"en": "a", "es": "a"}] * 4)))        # not distinct
        self.assertTrue(self.errors(good_question(module="cooking")))
        self.assertTrue(self.errors(good_question(q={"en": "only english"})))

    def test_every_builtin_question_satisfies_the_rules(self):
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "validate_bank.py"), "--path", str(ROOT / "bank" / "questions")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


class TestPacksAndLevels(unittest.TestCase):
    def make_pack(self, root: Path, name="demo", count=2):
        pack = root / name
        (pack / "questions").mkdir(parents=True)
        (pack / "pack.json").write_text(json.dumps({"name": name, "version": "1", "license": "proprietary"}))
        (pack / "questions" / "sql.json").write_text(json.dumps([good_question(f"{name}-sql-{i}", level="principal") for i in range(count)]))
        return pack

    def test_catalog_loads_pack_questions_and_ignores_folders_without_manifest(self):
        srv = RunningServer()
        try:
            packs = srv.home / "no-packs"
            self.make_pack(packs, "demo", 3)
            (packs / "stray" / "questions").mkdir(parents=True)
            (packs / "stray" / "questions" / "sql.json").write_text(json.dumps([good_question("stray-1")]))   # no pack.json: ignored
            cat = srv.handlers.exams.catalog
            ids = {c["ref"]["id"] for c in cat.candidates() if c["ref"]["t"] == "mcq"}
            self.assertTrue({"demo-sql-0", "demo-sql-1", "demo-sql-2"} <= ids)
            self.assertNotIn("stray-1", ids)
            item = cat.resolve({"t": "mcq", "id": "demo-sql-1"})
            self.assertEqual(item["level"], "principal")
            self.assertEqual(item["sources"][0]["url"], "https://example.com/docs")
        finally:
            srv.close()

    def test_staff_and_principal_exams_pick_the_closest_level_first(self):
        cands = [{"ref": {"t": "mcq", "id": f"{lv}-{i}"}, "module": "sql", "level": lv, "min_java": 0, "language": "any", "tags": [], "minutes": 1.5}
                 for lv in ("jr", "mid", "sr", "staff", "principal") for i in range(3)]
        for want in ("staff", "principal"):
            exam = rules.build({"seniority": want, "language": "java", "version": 21, "modules": ["sql"], "counts": {"sql": 3}}, cands, now=1.0)
            self.assertEqual(exam["config"]["seniority"], want)
            self.assertTrue(all(r["id"].startswith(want) for r in exam["sections"][0]["items"]))

    def test_graded_items_expose_sources_and_review_status(self):
        srv = RunningServer()
        try:
            self.make_pack(srv.home / "no-packs", "demo", 5)
            c = srv.client
            st, ex = c.post("/api/exams", {"seniority": "principal", "language": "java", "version": 21, "pace": "standard", "modules": ["sql"], "banks": [], "lang": "en"})
            self.assertEqual(st, 200, ex)
            item = ex["sections"][0]["items"][0]
            self.assertEqual(item["review"], "draft")
            self.assertNotIn("answer", item)
            c.post(f"/api/exams/{ex['id']}/start", {"section": 0, "attempt": "f" * 32})
            st, rep = c.post(f"/api/exams/{ex['id']}/section", {"section": 0, "answers": {}, "lang": "en", "attempt": "f" * 32})
            self.assertEqual(st, 200)
            self.assertTrue(rep["items"][0]["sources"])
        finally:
            srv.close()


class TestSeniorityDetection(unittest.TestCase):
    def test_staff_and_principal_titles(self):
        self.assertEqual(profile.analyze("Staff Software Engineer, 10 years of Java")["seniority"], "staff")
        self.assertEqual(profile.analyze("Principal Engineer, Java 21, microservices")["seniority"], "principal")
        self.assertEqual(profile.analyze("Ingeniero Principal con Java")["seniority"], "principal")

    def test_plain_words_do_not_trigger_it(self):
        self.assertEqual(profile.analyze("Senior Java developer, 6 years. We offer staff augmentation services.")["seniority"], "sr")
        self.assertEqual(profile.analyze("our principal goal is speed; 3 years of Java")["seniority"], "mid")


if __name__ == "__main__":
    unittest.main()
