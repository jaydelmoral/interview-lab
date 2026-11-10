"""Regression tests for the 2026-11-10 audit: input handling, client-reported scores, grader resource limits, history storage."""
import importlib.util
import os
import shutil
import socket
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from interview_lab.adapters.sqlite_history import SqliteHistory
from interview_lab.adapters.web_fetcher import fetch
from interview_lab.application.services import PracticeService
from tests.helpers import ROOT, FakeGrader, RunningServer


def _grade_module():
    spec = importlib.util.spec_from_file_location("ilab_grade_under_test", ROOT / "grader" / "grade.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class RequestHandlingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = RunningServer()
        cls.c = cls.srv.client

    @classmethod
    def tearDownClass(cls):
        cls.srv.close()

    def test_negative_content_length_is_rejected_instead_of_blocking(self):
        with socket.create_connection(("127.0.0.1", self.srv.port), timeout=5) as s:
            s.sendall(b"POST /api/quiz HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: -1\r\n\r\n{}")
            self.assertIn(b" 400 ", s.recv(200).split(b"\r\n")[0])

    def test_exam_preferences_with_wrong_types_never_cause_a_500(self):
        for extra in ({"title": 123}, {"counts": "x"}, {"counts": {"sql": "many"}}, {"banks": [{"a": 1}]}, {"banks": "b-1"},
                      {"language": {"a": 1}}, {"pace": 7}, {"version": True}, {"seniority": ["sr"]}):
            st, out = self.c.post("/api/exams", {"modules": ["sql"], **extra})
            self.assertEqual(200, st, f"{extra} -> {out}")

    def test_missing_language_defaults_to_java(self):
        st, exam = self.c.post("/api/exams", {"modules": ["coding"]})
        self.assertEqual(200, st, exam)
        self.assertEqual("java", exam["config"]["language"])

    def test_finish_rejects_malformed_requests_and_never_trusts_client_scores(self):
        _, exam = self.c.post("/api/exams", {"modules": ["sql"]})
        url, att = f"/api/exams/{exam['id']}/finish", "9" * 32
        self.assertEqual(400, self.c.post(url, {"sections": [{"section": 0}]})[0])                       # the attempt id is mandatory
        for bad in ([], "x", [1], [{"section": 5}], [{"section": True}], [{"section": 0}, {"section": 0}], [{"section": 0}] * 31):
            self.assertEqual(400, self.c.post(url, {"sections": bad, "attempt": att})[0], bad)
        self.assertEqual(0, self.c.get("/api/history")[1]["kpis"]["runs"])
        # scores sent by the client are ignored: a forged 100 % for a section nobody answered is stored as 0 %
        self.assertEqual(200, self.c.post(url, {"sections": [{"section": 0, "score": 500, "max": 100, "pct": 100}], "attempt": att})[0])
        kpis = self.c.get("/api/history")[1]["kpis"]
        self.assertEqual((1, 0.0), (kpis["runs"], kpis["best_overall"]))


class AttemptFilesTest(unittest.TestCase):
    def test_two_submissions_in_the_same_second_keep_separate_files(self):
        class Problems:
            def meta(self, pid):
                return {"kind": "code"}

        class Log:
            def append(self, record):
                pass

        with tempfile.TemporaryDirectory() as tmp:
            grader = FakeGrader()
            svc = PracticeService(Problems(), grader, Log(), Path(tmp), 50_000)
            threads = [threading.Thread(target=svc.grade_code, args=("p-one", f"class A{i} {{}}", "es")) for i in range(6)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            files = sorted((Path(tmp) / "p-one").glob("*.java"))
            self.assertEqual(6, len(files))
            self.assertEqual({f"class A{i} {{}}" for i in range(6)}, {f.read_text() for f in files})
            self.assertEqual({f"class A{i} {{}}" for i in range(6)}, {code for _, code, _ in grader.calls})   # each graded with its own code


class GraderProcessLimitsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = _grade_module()
        cls.env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}

    def test_endless_output_is_capped_in_memory(self):
        code = "import sys\nwhile True: sys.stdout.write('x' * 65536)"
        rc, out, err, timed_out = self.g.run_capped([sys.executable, "-c", code], 1.0, Path(tempfile.gettempdir()), self.env)
        self.assertTrue(timed_out)
        self.assertLessEqual(len(out), self.g.MAX_OUTPUT)

    def test_normal_output_and_exit_code_are_returned(self):
        rc, out, err, timed_out = self.g.run_capped([sys.executable, "-c", "import sys; print('hi'); sys.stderr.write('warn'); sys.exit(3)"],
                                                    10, Path(tempfile.gettempdir()), self.env)
        self.assertEqual((3, "hi", "warn", False), (rc, out.strip(), err.strip(), timed_out))

    @unittest.skipUnless(os.name == "posix", "process groups are POSIX-only")
    def test_child_processes_do_not_outlive_the_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = Path(tmp) / "child.pid"
            code = ("import subprocess, sys, time\n"
                    "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
                    f"open({str(pidfile)!r}, 'w').write(str(p.pid))\n"
                    "time.sleep(60)\n")
            _, _, _, timed_out = self.g.run_capped([sys.executable, "-c", code], 1.5, Path(tmp), self.env)
            self.assertTrue(timed_out)
            child = int(pidfile.read_text())
            for _ in range(40):                                  # the kill is asynchronous: give the kernel a moment
                if not _alive(child):
                    break
                time.sleep(0.05)
            self.assertFalse(_alive(child), "a process started by the code under test survived the test")

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"), "needs a JDK")
    def test_compile_message_does_not_show_our_own_jvm_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "Solution.java").write_text("class Solution { int f() { return nope; } }")
            ok, msg = self.g.compile_java(Path(tmp))
            self.assertFalse(ok)
            self.assertIn("cannot find symbol", msg)
            self.assertNotIn("JAVA_TOOL_OPTIONS", msg)
            self.assertNotIn(tmp, msg)


def _alive(pid: int) -> bool:
    try:
        with open(f"/proc/{pid}/stat") as f:                    # a killed child of a dead parent may linger as a zombie: not alive
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        try:
            os.kill(pid, 0)
            return not os.path.isdir("/proc")
        except OSError:
            return False


class HistoryStorageTest(unittest.TestCase):
    def test_migration_is_atomic_and_reopening_is_harmless(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "ilab.db"
            self.assertEqual(1, SqliteHistory(db).schema_version())
            self.assertEqual(1, SqliteHistory(db).schema_version())                 # second start: nothing to do, no "table exists"
            with sqlite3.connect(db) as c:
                self.assertEqual(1, c.execute("SELECT count(*) FROM profiles").fetchone()[0])

    def test_single_run_lookup_respects_profile_and_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            h = SqliteHistory(Path(tmp) / "ilab.db")
            ids = [h.record_run("local", {"exam_id": f"e{i}", "finished_at": f"2026-11-10 10:00:0{i}", "overall_pct": 10.0 * i,
                                          "sections": [{"module": "sql", "title": "SQL", "pct": 10.0 * i}],
                                          "missed": [{"section": "SQL", "question": f"q{i}", "tags": ["joins"]}]}) for i in range(3)]
            run = h.run("local", ids[1])
            self.assertEqual(("e1", 10.0, "q1"), (run["exam_id"], run["sections"][0]["pct"], run["missed"][0]["question"]))
            self.assertIsNone(h.run("local", 9999))
            self.assertIsNone(h.run("someone-else", ids[1]))


class FetcherCharsetTest(unittest.TestCase):
    def test_unknown_charset_falls_back_to_utf8(self):
        import http.server

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = "<h1>título</h1>".encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=not-a-real-charset")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            import interview_lab.adapters.web_fetcher as wf
            port = srv.server_address[1]
            original = wf.validate_url
            wf.validate_url = lambda url: (wf.urllib.parse.urlsplit(url), port)       # the real one only allows ports 80/443
            try:
                _, text = fetch(f"http://test.invalid:{port}/", resolver=lambda host: "127.0.0.1")
            finally:
                wf.validate_url = original
            self.assertIn("título", text)
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
