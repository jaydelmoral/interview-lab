"""Local AI adapter (Ollama): loopback-only by default, strict validation of model output, graceful failures."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from interview_lab.adapters.ollama_generator import OllamaQuestionGenerator, is_loopback
from interview_lab.application.ports import GenerationError

GOOD = [{"q": "What does an open circuit breaker do with new calls?", "options": ["Fails them immediately", "Retries forever", "Queues them for a year", "Doubles the timeout"], "answer": 0, "explain": "It fails fast."},
        {"q": "short", "options": ["a", "b", "c", "d"], "answer": 0},                                   # too short: dropped
        {"q": "Which state lets a few trial calls through?", "options": ["Half-open", "Closed", "Open", "Broken"], "answer": 9}]   # bad answer: dropped


class FakeOllama(BaseHTTPRequestHandler):
    content = json.dumps(GOOD)
    seen = []

    def log_message(self, *a):
        pass

    def _send(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send({"models": [{"name": "fake-model:1b"}]})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeOllama.seen.append(body)
        self._send({"message": {"role": "assistant", "content": FakeOllama.content}})


class TestOllama(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", 0), FakeOllama)
        cls.url = f"http://127.0.0.1:{cls.httpd.server_address[1]}"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        FakeOllama.content = json.dumps(GOOD)
        FakeOllama.seen.clear()

    def test_loopback_detection(self):
        for ok in ("http://127.0.0.1:11434", "http://localhost:11434", "http://[::1]:11434"):
            self.assertTrue(is_loopback(ok), ok)
        for bad in ("http://10.0.0.5:11434", "http://192.168.1.9:11434", "http://8.8.8.8:11434", "http://169.254.169.254"):
            self.assertFalse(is_loopback(bad), bad)

    def test_remote_hosts_are_refused_unless_explicitly_allowed(self):
        with self.assertRaises(GenerationError):
            OllamaQuestionGenerator("http://10.0.0.5:11434", "m")
        OllamaQuestionGenerator("http://10.0.0.5:11434", "m", allow_remote=True)
        with self.assertRaises(GenerationError):
            OllamaQuestionGenerator("file:///etc/passwd", "m")

    def test_end_to_end_against_a_fake_daemon_uses_first_installed_model_and_validates(self):
        g = OllamaQuestionGenerator(self.url)                       # no model given: discovered through /api/tags
        self.assertEqual(g.model, "fake-model:1b")
        items = g.generate("Circuit breaker", "A breaker opens after failures...", [])
        self.assertEqual(len(items), 1)                              # the two invalid items were dropped
        self.assertEqual(items[0]["q"]["src"][:10], "What does ")
        sent = FakeOllama.seen[0]
        self.assertEqual((sent["model"], sent["stream"]), ("fake-model:1b", False))
        self.assertIn("Circuit breaker", sent["messages"][0]["content"])

    def test_garbage_and_prose_from_the_model_are_rejected(self):
        g = OllamaQuestionGenerator(self.url, "m")
        for bad in ("I cannot do that", "[]", "[{\"q\": 1}]", "{not json"):
            FakeOllama.content = bad
            with self.assertRaises(GenerationError, msg=bad):
                g.generate("t", "text", [])

    def test_model_wrapping_json_in_prose_still_works(self):
        FakeOllama.content = "Sure! Here you go:\n" + json.dumps(GOOD[:1]) + "\nHope it helps."
        self.assertEqual(len(OllamaQuestionGenerator(self.url, "m").generate("t", "text", [])), 1)

    def test_unreachable_daemon_is_a_clean_error(self):
        with self.assertRaises(GenerationError):
            OllamaQuestionGenerator("http://127.0.0.1:9", "")        # discovery fails
        g = OllamaQuestionGenerator("http://127.0.0.1:9", "m")
        with self.assertRaises(GenerationError):
            g.generate("t", "text", [])


if __name__ == "__main__":
    unittest.main()
