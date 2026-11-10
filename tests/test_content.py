"""Run with:  python3 -m unittest discover -s tests -v

Needs JDK 21 for the grading tests (they are skipped without it).
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ["ILAB_HOME"] = tempfile.mkdtemp(prefix="ilab-test-")  # never touch a real workspace
sys.path.insert(0, str(ROOT / "grader"))
sys.path.insert(0, str(ROOT / "tools"))
import grade as G  # noqa: E402
import validate as V  # noqa: E402

HAS_JDK = bool(shutil.which("javac") and shutil.which("java"))
PROBLEMS = sorted(d for d in (ROOT / "problems").iterdir() if (d / "meta.json").exists())


class Structure(unittest.TestCase):
    def test_no_errors_or_warnings_in_builtin_content(self):
        for d in PROBLEMS:
            with self.subTest(problem=d.name):
                issues = V.validate(d, run=False)
                self.assertEqual([], issues, issues)

    def test_every_code_problem_is_bilingual(self):
        for d in PROBLEMS:
            m = json.loads((d / "meta.json").read_text())
            if m.get("kind") == "quiz":
                qs = json.loads((d / "quiz.json").read_text())
                self.assertTrue(all(q.get("topic_en") and q.get("explanation_en") for q in qs), d.name)
                continue
            with self.subTest(problem=d.name):
                self.assertTrue((d / "problem.es.md").exists())
                self.assertTrue(all(t.get("fail_why_en") and t.get("fail_how_en") for t in m["tests"]))

    def test_content_is_licensed_and_original(self):
        for d in PROBLEMS:
            m = json.loads((d / "meta.json").read_text())
            self.assertEqual("CC-BY-4.0", m.get("license"), d.name)
            self.assertEqual("original", m.get("origin"), d.name)


@unittest.skipUnless(HAS_JDK, "JDK 21 not installed")
class Grading(unittest.TestCase):
    def test_reference_solutions_score_100_and_starters_do_not(self):
        for d in PROBLEMS:
            m = json.loads((d / "meta.json").read_text())
            if m.get("kind") == "quiz":
                continue
            with self.subTest(problem=d.name):
                ref = sorted((d / "reference").glob("*.java"))[0]
                rep = G.grade(d.name, ref, lang="en")
                self.assertTrue(rep["compile"]["ok"], rep["compile"])
                self.assertEqual(rep["max"], rep["score"], [t for t in rep["tests"] if not t["passed"]])
                self.assertLess(G.grade(d.name, d / "starter.java")["score"], rep["max"])

    def test_submitted_code_does_not_see_your_environment(self):
        os.environ["ILAB_SECRET_PROBE"] = "top-secret"
        code = ('class Solution { static boolean isBooked(int[] s, int k) { '
                'if (System.getenv("ILAB_SECRET_PROBE") != null) throw new RuntimeException("LEAK"); return java.util.Arrays.binarySearch(s, k) >= 0; } }')
        tmp = Path(tempfile.mkdtemp()) / "Solution.java"
        tmp.write_text(code)
        rep = G.grade("001-seat-lookup", tmp)
        self.assertEqual(rep["max"], rep["score"], [t["detail"] for t in rep["tests"] if not t["passed"]])

    def test_infinite_loop_times_out(self):
        tmp = Path(tempfile.mkdtemp()) / "Solution.java"
        tmp.write_text("class Solution { static boolean isBooked(int[] s, int k) { while (true) {} } }")
        rep = G.grade("001-seat-lookup", tmp, lang="en")
        self.assertTrue(any("TIMEOUT" in t["detail"] for t in rep["tests"]))



class TestWebPages(unittest.TestCase):
    """The UI must stay self-contained: the CSP and the local-first promise forbid external assets (ADR-0006, ADR-0015)."""

    PAGES = ("landing.html", "exam.html", "index.html", "history.html")

    def test_pages_load_theme_and_shared_styles_and_nothing_external(self):
        import re
        for name in self.PAGES:
            html = (ROOT / "web" / name).read_text()
            self.assertIn('<script src="/theme.js">', html, name)
            self.assertIn('href="/common.css"', html, name)
            self.assertIsNone(re.search(r'(?:src|href)="https?://', html), f"{name} loads an external resource")
        for asset in ("common.js", "common.css", "theme.js"):
            text = (ROOT / "web" / asset).read_text()
            self.assertIsNone(re.search(r"@import|url\(['\"]?https?://|fetch\(['\"]https?://", text), f"{asset} reaches out to the network")

    def test_both_logo_variants_exist_for_the_theme_switch(self):
        brand = json.loads((ROOT / "web" / "brand" / "brand.json").read_text())
        for key in ("logo_mark", "logo_full"):
            for theme in ("light", "dark"):
                self.assertTrue((ROOT / "web" / "brand" / brand[key][theme]).is_file(), f"{key}/{theme}")


if __name__ == "__main__":
    unittest.main()
