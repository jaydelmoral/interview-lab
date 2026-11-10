"""HTTP end-to-end tests: the real server in a thread, a temporary home and a fake grader (no JVM needed)."""
import unittest

from tests.helpers import RunningServer, b64, docx_bytes

JD = "Senior Java 17 developer, 9 years, Spring Boot, Kafka, Docker, SQL, JUnit, Cucumber BDD, Linux"


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rs = RunningServer()
        cls.c = cls.rs.client

    @classmethod
    def tearDownClass(cls):
        cls.rs.close()

    # ---- pages, assets, headers
    def test_pages_and_assets(self):
        for path in ("/", "/practice", "/exam", "/history", "/common.js", "/common.css", "/theme.js", "/editor.js", "/exam.js", "/history.js", "/index.js", "/landing.js", "/brand/logo-full-dark.png", "/api/brand", "/fonts/Outfit-latin-400-600.woff2"):
            self.assertEqual(200, self.c.get(path)[0], path)

    def test_heading_font_is_served_as_woff2_and_brand_declares_the_isotype(self):
        import urllib.request
        with urllib.request.urlopen(self.c.base + "/fonts/Outfit-latin-400-600.woff2") as r:
            body = r.read()
            self.assertEqual("font/woff2", r.headers["Content-Type"])
        self.assertLess(len(body), 40 * 1024)
        status, brand = self.c.get("/api/brand")
        self.assertEqual(200, status)
        self.assertEqual("collaboration-o", brand["isotype"])
        self.assertEqual(404, self.c.get("/fonts/missing.woff2")[0])
        self.assertEqual(404, self.c.get("/fonts/../common.js")[0])

    def test_security_headers_present(self):
        import urllib.request
        with urllib.request.urlopen(self.c.base + "/") as r:
            self.assertIn("default-src 'none'", r.headers["Content-Security-Policy"])
            self.assertEqual("nosniff", r.headers["X-Content-Type-Options"])
            self.assertEqual("DENY", r.headers["X-Frame-Options"])

    # ---- same-origin guard
    def test_guard_rejects_foreign_origin_host_and_content_type(self):
        body = {"text": JD}
        self.assertEqual(403, self.c.post("/api/analyze", body, headers={"Origin": "https://evil.example"})[0])
        self.assertEqual(403, self.c.post("/api/analyze", body, headers={"Origin": "null"})[0])
        self.assertEqual(403, self.c.get("/api/problems", headers={"Host": "evil.example:80"})[0])
        self.assertEqual(415, self.c.post("/api/analyze", raw=b'{"text":"x"}', headers={"Content-Type": "text/plain"})[0])
        self.assertEqual(404, self.c.get("/api/problems/..%2f..%2fetc")[0])
        self.assertEqual(404, self.c.get("/nope")[0])

    def test_request_size_limit(self):
        self.assertEqual(413, self.c.post("/api/grade", {"problem": "001-seat-lookup", "code": "x" * 300_000})[0])

    # ---- profile analysis
    def test_analyze_text_and_docx(self):
        s, d = self.c.post("/api/analyze", {"text": JD})
        self.assertEqual((200, "sr", "java", 17), (s, d["seniority"], d["language"], d["version"]))
        self.assertTrue({"qa", "sql", "devops", "microservices"} <= {m["id"] for m in d["modules"]})
        s, d = self.c.post("/api/analyze", {"filename": "cv.docx", "data": b64(docx_bytes("Junior Python developer, 1 year, Django, PostgreSQL"))})
        self.assertEqual((200, "jr", "python"), (s, d["seniority"], d["language"]))

    def test_analyze_rejects_bad_input(self):
        self.assertEqual(400, self.c.post("/api/analyze", {"filename": "cv.pdf", "data": b64(b"%PDF")})[0])
        self.assertEqual(400, self.c.post("/api/analyze", {"text": "   "})[0])
        self.assertEqual(400, self.c.post("/api/analyze", {"filename": "a.docx", "data": b64(b"not a zip")})[0])

    # ---- exams
    def _exam(self, **cfg):
        base = {"seniority": "mid", "language": "java", "version": 17, "modules": ["sql", "security"], "lang": "en"}
        return self.c.post("/api/exams", base | cfg)

    def test_exam_lifecycle(self):
        s, exam = self._exam()
        self.assertEqual(200, s)
        self.assertEqual(["SQL", "Security"], [x["title"] for x in exam["sections"]])
        self.assertEqual(16, exam["total_minutes"])                       # 2 sections x 5 questions x 1.5 min, rounded up per section
        self.assertNotIn("answer", str(exam))                              # the candidate never receives the answers
        s, again = self.c.get(f"/api/exams/{exam['id']}?lang=en")
        self.assertEqual((200, exam["sections"]), (s, again["sections"]))  # reproducible: same items and same option order
        # answering with the expected options yields a perfect score (grading honors the shuffled order)
        probe, attempt = "c" * 32, "d" * 32                                # a section is graded once per attempt: a probe attempt reveals the answers
        self.c.post(f"/api/exams/{exam['id']}/start", {"section": 0, "attempt": probe})
        s, wrong = self.c.post(f"/api/exams/{exam['id']}/section", {"section": 0, "answers": {i["key"]: 0 for i in exam["sections"][0]["items"]}, "lang": "en", "attempt": probe})
        picks = {r["key"]: r["expected_index"][0] for r in wrong["items"]}
        self.c.post(f"/api/exams/{exam['id']}/start", {"section": 0, "attempt": attempt})
        s, ok = self.c.post(f"/api/exams/{exam['id']}/section", {"section": 0, "answers": picks, "lang": "en", "attempt": attempt})
        self.assertEqual((200, 5, 5), (s, ok["score"], ok["max"]))
        s, fin = self.c.post(f"/api/exams/{exam['id']}/finish", {"sections": [{"section": 0}], "attempt": attempt})
        self.assertEqual((200, 100), (s, fin["score"]))
        s, lst = self.c.get("/api/exams")
        self.assertEqual(100, next(e for e in lst if e["id"] == exam["id"])["last"]["score"])

    def test_exam_errors(self):
        self.assertEqual(400, self._exam(modules=[])[0])
        self.assertEqual(404, self.c.get("/api/exams/20200101-000000-abcd")[0])
        self.assertEqual(404, self.c.get("/api/exams/not-an-id")[0])
        s, d = self._exam(language="python", modules=["coding"])
        self.assertEqual(422, s)
        self.assertIn("Java-only", d["notes"][0]["text"])
        s, exam = self._exam()
        self.assertEqual(400, self.c.post(f"/api/exams/{exam['id']}/section", {"section": 9, "answers": {}})[0])
        self.assertEqual(400, self.c.post(f"/api/exams/{exam['id']}/finish", {"sections": "x", "attempt": "e" * 32})[0])

    # ---- memory banks
    def test_bank_lifecycle_and_exam_with_bank(self):
        notes = ("# Circuit Breaker\nA circuit breaker is a resilience pattern that stops calls to a failing dependency. Resilience4j provides a CircuitBreaker with three states: CLOSED, OPEN and HALF_OPEN.\n"
                 "When the failure rate exceeds the threshold the CircuitBreaker moves to OPEN and rejects calls. After waitDurationInOpenState it becomes HALF_OPEN to test recovery with a few permitted calls.\n"
                 "# Fallbacks\nA fallback method returns a default response while the CircuitBreaker is OPEN. Bulkhead and RateLimiter from Resilience4j complement the pattern.")
        s, bank = self.c.post("/api/banks", {"title": "CB", "notes": notes})
        self.assertEqual((200, "offline"), (s, bank["generator"]))
        self.assertGreaterEqual(bank["items"], 3)
        self.assertIn(bank["id"], [b["id"] for b in self.c.get("/api/banks")[1]])
        s, exam = self.c.post("/api/exams", {"language": "other", "modules": ["mybank"], "banks": [bank["id"]], "lang": "en"})
        self.assertEqual(200, s)
        self.assertEqual(bank["items"], len(exam["sections"][0]["items"]))
        self.assertEqual(200, self.c.delete(f"/api/banks/{bank['id']}")[0])
        self.assertEqual(404, self.c.delete(f"/api/banks/{bank['id']}")[0])

    def test_bank_blocks_private_addresses(self):
        for url in ("http://169.254.169.254/latest/meta-data/", "http://127.0.0.1:8765/", "http://10.0.0.5/", "file:///etc/passwd"):
            s, d = self.c.post("/api/banks", {"urls": [url]})
            self.assertEqual(422, s, url)
            self.assertTrue(d["errors"], url)

    def test_bank_requires_material(self):
        self.assertEqual(400, self.c.post("/api/banks", {"title": "x"})[0])

    # ---- free practice
    def test_practice_flow(self):
        s, lst = self.c.get("/api/problems")
        self.assertEqual(200, s)
        self.assertEqual(15, len(lst))
        s, p = self.c.get("/api/problems/003-gift-card-pair?lang=en")
        self.assertTrue(p["statement_es"] and p["starter"])
        s, rep = self.c.post("/api/grade", {"problem": "003-gift-card-pair", "code": "class Solution {}", "lang": "en"})
        self.assertEqual((200, 5, 10), (s, rep["score"], rep["max"]))
        self.assertEqual("en", self.rs.grader.calls[-1][2])
        self.assertEqual(400, self.c.post("/api/grade", {"problem": "101-predice-la-salida", "code": "x"})[0])      # a quiz is not code
        self.assertEqual(400, self.c.post("/api/grade", {"problem": "nope-nope", "code": "x"})[0])
        s, q = self.c.post("/api/quiz", {"problem": "101-predice-la-salida", "answers": {"q03": "5", "q09": "-2147483648"}, "lang": "en"})
        self.assertEqual(200, s)
        self.assertEqual(2, q["score"])


class FetchDisabledTest(unittest.TestCase):
    def test_links_can_be_disabled(self):
        rs = RunningServer(ILAB_ALLOW_FETCH="0")
        try:
            self.assertEqual(403, rs.client.post("/api/banks", {"urls": ["https://example.com/"]})[0])
            self.assertFalse(rs.client.get("/api/modules")[1]["fetch"])
        finally:
            rs.close()


if __name__ == "__main__":
    unittest.main()
