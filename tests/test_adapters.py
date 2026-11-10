"""Unit tests of adapters that need no network and no JVM."""
import json
import unittest
from types import SimpleNamespace

from interview_lab.adapters import anthropic_generator as ag
from interview_lab.adapters import offline_generator as og
from interview_lab.adapters import web_fetcher as wf
from interview_lab.application.ports import FetchError, GenerationError

HTML = """<html><head><title>Circuit Breaker</title></head><body><nav>menu</nav><h1>Circuit Breaker</h1>
<p>A circuit breaker is a resilience pattern that stops calls to a failing dependency. Resilience4j provides a CircuitBreaker with three states: CLOSED, OPEN and HALF_OPEN.</p>
<p>When the failure rate exceeds the threshold the CircuitBreaker moves to OPEN and rejects calls. After waitDurationInOpenState it becomes HALF_OPEN to test recovery with a few permitted calls.</p>
<h2>Fallbacks</h2><p>A fallback method returns a default response while the CircuitBreaker is OPEN. Bulkhead and RateLimiter from Resilience4j complement the pattern.</p>
<script>evil()</script></body></html>"""


class FetcherTest(unittest.TestCase):
    def test_blocked_urls(self):
        for url in ("ftp://example.com/", "https://user:pw@example.com/", "http://example.com:8080/", "http://localhost:8765/", "//example.com", "javascript:alert(1)"):
            with self.assertRaises(FetchError, msg=url):
                wf.validate_url(url)

    def test_private_and_special_addresses_are_not_public(self):
        for host in ("127.0.0.1", "10.1.2.3", "169.254.169.254", "192.168.0.1", "172.16.0.9", "::1", "0.0.0.0"):
            with self.assertRaises(FetchError, msg=host):
                wf.resolve_public(host)

    def test_redirect_to_private_address_is_blocked(self):
        calls = []

        def resolver(host):
            calls.append(host)
            return wf.resolve_public("127.0.0.1")        # simulates a redirect target resolving to loopback
        with self.assertRaises(FetchError):
            wf.fetch("http://example.com/", resolver=resolver)

    def test_extract_strips_scripts_and_navigation(self):
        title, text, heads = wf.extract(HTML)
        self.assertEqual(("Circuit Breaker", ["Circuit Breaker", "Fallbacks"]), (title, heads))
        self.assertIn("resilience pattern", text)
        self.assertNotIn("evil()", text)
        self.assertNotIn("menu", text)


class OfflineGeneratorTest(unittest.TestCase):
    def test_generates_valid_mcq_and_flashcards(self):
        title, text, heads = wf.extract(HTML)
        items = og.OfflineQuestionGenerator().generate(title, text, heads)
        mcq = [i for i in items if i["type"] == "mcq"]
        self.assertTrue(mcq)
        for q in mcq:
            self.assertEqual(4, len(q["options"]))
            self.assertIn("_____", q["q"]["src"])
            self.assertEqual(4, len({o["src"] for o in q["options"]}))
            self.assertLess(q["answer"][0], 4)
        self.assertTrue([i for i in items if i["type"] == "flash"])

    def test_deterministic(self):
        title, text, heads = wf.extract(HTML)
        g = og.OfflineQuestionGenerator()
        self.assertEqual(g.generate(title, text, heads), g.generate(title, text, heads))


class AnthropicGeneratorTest(unittest.TestCase):
    GOOD = json.dumps([{"q": "Which state lets trial calls through?", "options": ["Open", "Closed", "Half-open", "Idle"], "answer": 2, "explain": "Half-open tests recovery."}])

    def client(self, text=None, exc=None):
        def create(**kw):
            if exc:
                raise exc
            return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])
        return SimpleNamespace(messages=SimpleNamespace(create=create))

    def test_valid_response_becomes_items(self):
        g = ag.AnthropicQuestionGenerator("m", client=self.client("Here you go:\n" + self.GOOD))
        items = g.generate("T", "text", [])
        self.assertEqual((1, [2]), (len(items), items[0]["answer"]))

    def test_invalid_responses_are_rejected(self):
        for bad in ("not json", "[]", json.dumps([{"q": "short", "options": ["a", "b", "c", "d"], "answer": 0}]),
                    json.dumps([{"q": "A long enough question?", "options": ["a", "a", "b", "c"], "answer": 0}]),
                    json.dumps([{"q": "A long enough question?", "options": ["a", "b", "c", "d"], "answer": 7}])):
            with self.assertRaises(GenerationError, msg=bad):
                ag.AnthropicQuestionGenerator("m", client=self.client(bad)).generate("T", "x", [])

    def test_provider_errors_do_not_leak_details(self):
        g = ag.AnthropicQuestionGenerator("m", client=self.client(exc=RuntimeError("sk-secret-key leaked?")))
        with self.assertRaises(GenerationError) as cm:
            g.generate("T", "x", [])
        self.assertNotIn("sk-secret", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
