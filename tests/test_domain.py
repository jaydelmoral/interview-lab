"""Unit tests of the pure domain rules (no files, no server, no JVM)."""
import unittest

from interview_lab.domain import exam as ex
from interview_lab.domain import profile


def cand(ref_id, module="sql", level="mid", **kw):
    return {"ref": {"t": "mcq", "id": ref_id}, "module": module, "level": level, "min_java": kw.pop("min_java", 0),
            "language": "any", "tags": [], "minutes": kw.pop("minutes", 1.5), **kw}


class ProfileTest(unittest.TestCase):
    def test_seniority_from_years_and_keywords(self):
        self.assertEqual("jr", profile.analyze("1 year of Java")["seniority"])
        self.assertEqual("mid", profile.analyze("4 years with Java")["seniority"])
        self.assertEqual("sr", profile.analyze("8+ years of Java")["seniority"])
        self.assertEqual("sr", profile.analyze("Senior Java engineer")["seniority"])
        self.assertEqual("jr", profile.analyze("Junior Java developer")["seniority"])
        self.assertEqual("mid", profile.analyze("a developer")["seniority"])

    def test_language_and_version(self):
        a = profile.analyze("Java 1.8 and Java 11 and JDK 17; some Python")
        self.assertEqual(("java", 17), (a["language"], a["version"]))
        a = profile.analyze("Python 3.12, Django, FastAPI, pandas")
        self.assertEqual(("python", 12), (a["language"], a["version"]))

    def test_modules_detected_with_word_boundaries(self):
        ids = {m["id"] for m in profile.analyze("Kubernetes and Docker. We love Cucumber and OWASP.")["modules"]}
        self.assertTrue({"devops", "qa", "security", "coding"} <= ids)
        self.assertNotIn("sql", ids)                                       # "mysql" must not match inside other words
        self.assertIn("sql", {m["id"] for m in profile.analyze("PostgreSQL and MySQL")["modules"]})

    def test_ai_is_reported_as_coming_soon(self):
        self.assertEqual("ai", profile.analyze("LLM and RAG experience")["coming"][0]["id"])

    def test_text_is_bounded(self):
        self.assertLessEqual(profile.analyze("java " * 100_000)["chars"], profile.MAX_TEXT)


class BuildTest(unittest.TestCase):
    def pool(self):
        return [cand(f"s{i}", "sql", lv) for i, lv in enumerate(["jr"] * 4 + ["mid"] * 4 + ["sr"] * 4)] + \
               [cand("j1", "java-trivia", "mid", min_java=8), cand("j2", "java-trivia", "sr", min_java=21)]

    def test_closest_level_first_and_count(self):
        e = ex.build({"seniority": "sr", "modules": ["sql"], "counts": {"sql": 4}}, self.pool(), now=1_700_000_000)
        picked = {r["id"] for r in e["sections"][0]["items"]}
        self.assertEqual({"s8", "s9", "s10", "s11"}, picked)

    def test_reproducible_for_same_inputs(self):
        a = ex.build({"modules": ["sql"]}, self.pool(), now=1_700_000_000)
        b = ex.build({"modules": ["sql"]}, self.pool(), now=1_700_000_000)
        self.assertEqual(a, b)

    def test_java_version_filter(self):
        e = ex.build({"language": "java", "version": 17, "modules": ["java-trivia"]}, self.pool(), now=1)
        self.assertEqual(["j1"], [r["q"] if "q" in r else r["id"] for r in e["sections"][0]["items"]])

    def test_java_only_modules_skipped_for_other_languages(self):
        e = ex.build({"language": "python", "modules": ["java-trivia", "sql"]}, self.pool(), now=1)
        self.assertEqual(["sql"], [s["module"] for s in e["sections"]])
        self.assertIn("Java-only", ex.pick(e["notes"][0], "en"))

    def test_pace_scales_minutes(self):
        base = ex.build({"modules": ["sql"], "pace": "standard", "counts": {"sql": 4}}, self.pool(), now=1)["sections"][0]["minutes"]
        tight = ex.build({"modules": ["sql"], "pace": "tight", "counts": {"sql": 4}}, self.pool(), now=1)["sections"][0]["minutes"]
        relaxed = ex.build({"modules": ["sql"], "pace": "relaxed", "counts": {"sql": 4}}, self.pool(), now=1)["sections"][0]["minutes"]
        self.assertEqual((6, 5, 8), (base, tight, relaxed))

    def test_bank_filter(self):
        pool = [cand("a", "mybank", "any", bank="b-1"), cand("b", "mybank", "any", bank="b-2")]
        pool[0]["ref"] = {"t": "bank", "b": "b-1", "q": "a"}
        pool[1]["ref"] = {"t": "bank", "b": "b-2", "q": "b"}
        e = ex.build({"modules": ["mybank"], "banks": ["b-2"]}, pool, now=1)
        self.assertEqual([{"t": "bank", "b": "b-2", "q": "b"}], e["sections"][0]["items"])

    def test_unknown_modules_and_levels_are_ignored(self):
        e = ex.build({"modules": ["nope", "sql"], "seniority": "wizard"}, self.pool(), now=1)
        self.assertEqual(("mid", ["sql"]), (e["config"]["seniority"], e["config"]["modules"]))


class GradingTest(unittest.TestCase):
    Q = {"type": "mcq", "id": "q", "q": {"en": "?"}, "options": [{"en": c} for c in "abcd"], "answer": [2], "explain": {"en": "because"}, "tags": ["t"]}
    EXAM = {"id": "20260101-000000-abcd", "sections": [{"module": "sql", "title": {}, "minutes": 1, "items": [{"t": "mcq", "id": "q"}]}]}

    def resolve(self, ref):
        return dict(self.Q)

    def test_public_item_hides_answer_and_shuffles_deterministically(self):
        a = ex.public_item(self.EXAM["id"], {"t": "mcq", "id": "q"}, self.Q, "en")
        b = ex.public_item(self.EXAM["id"], {"t": "mcq", "id": "q"}, self.Q, "en")
        self.assertEqual(a, b)
        self.assertNotIn("answer", a)
        self.assertEqual(sorted("abcd"), sorted(a["options"]))

    def test_grading_uses_the_displayed_order(self):
        shown = ex.public_item(self.EXAM["id"], {"t": "mcq", "id": "q"}, self.Q, "en")["options"]
        right_idx = shown.index("c")
        good = ex.grade_section(self.EXAM, 0, {"mcq:q": right_idx}, self.resolve, "en")
        bad = ex.grade_section(self.EXAM, 0, {"mcq:q": (right_idx + 1) % 4}, self.resolve, "en")
        self.assertEqual((1, 1), (good["score"], good["max"]))
        self.assertEqual(0, bad["score"])
        self.assertEqual(["t"], ex.weak_tags(bad["items"]))

    def test_garbage_answers_never_crash(self):
        for given in (None, "x", [], [99], [-1], {"a": 1}, 3.5):
            self.assertEqual(0, ex.grade_section(self.EXAM, 0, {"mcq:q": given}, self.resolve, "es")["score"])

    def test_output_quiz_normalizes_whitespace(self):
        exam = {"id": "20260101-000000-abcd", "sections": [{"module": "java-trivia", "title": {}, "minutes": 1, "items": [{"t": "output", "p": "p", "q": "q1"}]}]}
        item = {"type": "output", "id": "q1", "expected": "a b\nc", "explanation": "e", "topic": "T"}
        self.assertEqual(1, ex.grade_section(exam, 0, {"output:q1": "  a   b \n c "}, lambda r: item, "es")["score"])

    def test_flashcards_are_self_rated(self):
        exam = {"id": "20260101-000000-abcd", "sections": [{"module": "mybank", "title": {}, "minutes": 1, "items": [{"t": "bank", "b": "b-1", "q": "f1"}]}]}
        item = {"type": "flash", "id": "f1", "q": {"src": "?"}, "a": {"src": "!"}, "tags": []}
        self.assertEqual(1, ex.grade_section(exam, 0, {"bank:f1": "know"}, lambda r: item, "es")["score"])
        self.assertEqual(0, ex.grade_section(exam, 0, {"bank:f1": "dont"}, lambda r: item, "es")["score"])


if __name__ == "__main__":
    unittest.main()
