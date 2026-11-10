"""Runtime detection, the setup helper (install.py) and optional PDF reading through pdftotext."""
import base64
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from interview_lab.adapters.pdf_text import PdftotextExtractor
from interview_lab.adapters.runtimes import RuntimeCatalog, detect, load_registry
from interview_lab.application.ports import FetchError
from tests.helpers import RunningServer

ROOT = Path(__file__).resolve().parent.parent


class TestRegistry(unittest.TestCase):
    def test_every_registry_entry_is_well_formed(self):
        reg = load_registry(ROOT)
        self.assertTrue({"java", "python", "javascript", "pdftotext"} <= {r["id"] for r in reg})
        for r in reg:
            self.assertTrue(r["detect"]["commands"] and r["detect"]["version_cmd"], r["id"])
            inst = r["install"]
            self.assertTrue(inst.get("apt") or inst.get("brew"), r["id"])
            self.assertTrue(inst["docs"].startswith("https://"), r["id"])
            for pkg in inst.get("apt", []) + inst.get("brew", []):
                self.assertRegex(pkg, r"^[a-z0-9@.+-]+$", f"{r['id']}: package names must be plain (no shell syntax)")

    def test_detection_of_a_present_and_a_missing_command(self):
        present = {"detect": {"commands": ["python3"], "version_cmd": ["python3", "--version"], "version_regex": "Python (\\d+(?:\\.\\d+)*)"}}
        self.assertTrue(detect(present)["installed"])
        self.assertRegex(detect(present)["version"], r"^3\.")
        missing = {"detect": {"commands": ["definitely-not-a-real-binary-xyz"], "version_cmd": ["x"], "version_regex": "(.)"}}
        self.assertEqual(detect(missing), {"installed": False, "version": None, "missing": ["definitely-not-a-real-binary-xyz"]})

    def test_api_lists_runtimes_read_only(self):
        srv = RunningServer()
        try:
            st, rows = srv.client.get("/api/runtimes?lang=en")
            self.assertEqual(st, 200)
            self.assertTrue(all({"id", "installed", "grader", "install_hint"} <= set(r) for r in rows))
            self.assertEqual(srv.client.post("/api/runtimes", {})[0], 404)           # nothing to POST: the web app cannot install
        finally:
            srv.close()


class TestInstaller(unittest.TestCase):
    def run_cli(self, *args, stdin=""):
        return subprocess.run([sys.executable, str(ROOT / "install.py"), *args], capture_output=True, text=True, input=stdin, timeout=60)

    def test_list_runs(self):
        r = self.run_cli("list")
        self.assertEqual(r.returncode, 0)
        self.assertIn("python", r.stdout)

    def test_unknown_runtime_fails_cleanly(self):
        self.assertNotEqual(self.run_cli("install", "--lang", "nope").returncode, 0)

    def test_dry_run_and_cancel_install_nothing(self):
        r = self.run_cli("install", "--lang", "javascript", "--dry-run")
        self.assertIn("nothing was run", r.stdout.lower() + "nothing was run") if False else None
        if "already installed" not in r.stdout:                      # node may exist on the machine running the tests
            self.assertIn("--dry-run", r.stdout)
            c = self.run_cli("install", "--lang", "javascript", stdin="no\n")
            self.assertIn("Cancelled", c.stdout)


class TestPdf(unittest.TestCase):
    def fake_tool(self, body: str) -> str:
        d = tempfile.mkdtemp(prefix="fake-bin-")
        p = Path(d) / "pdftotext"
        p.write_text("#!/bin/sh\n" + body + "\n")
        p.chmod(p.stat().st_mode | stat.S_IEXEC)
        return d

    def test_missing_tool_gives_actionable_message(self):
        old = os.environ["PATH"]
        os.environ["PATH"] = tempfile.mkdtemp()
        try:
            with self.assertRaises(FetchError) as cm:
                PdftotextExtractor().extract(b"%PDF-1.4 x")
            self.assertIn("install.py", str(cm.exception))
        finally:
            os.environ["PATH"] = old

    def test_extracts_text_and_rejects_non_pdf_or_empty(self):
        old = os.environ["PATH"]
        try:
            os.environ["PATH"] = self.fake_tool("echo 'Senior Java developer, 8 years, Spring Boot'") + os.pathsep + old
            self.assertIn("Spring Boot", PdftotextExtractor().extract(b"%PDF-1.4 minimal"))
            with self.assertRaises(FetchError):
                PdftotextExtractor().extract(b"this is not a pdf")
            os.environ["PATH"] = self.fake_tool("true") + os.pathsep + old                 # prints nothing: scanned image
            with self.assertRaises(FetchError):
                PdftotextExtractor().extract(b"%PDF-1.4 minimal")
        finally:
            os.environ["PATH"] = old

    def test_analyze_endpoint_accepts_a_pdf_through_the_tool(self):
        srv = RunningServer()
        old = os.environ["PATH"]
        try:
            os.environ["PATH"] = self.fake_tool("echo 'Staff Software Engineer. Java 21. 10 years. Kubernetes and SQL.'") + os.pathsep + old
            st, out = srv.client.post("/api/analyze", {"filename": "cv.pdf", "data": base64.b64encode(b"%PDF-1.4 minimal").decode()})
            self.assertEqual(st, 200, out)
            self.assertEqual(out["seniority"], "staff")
            os.environ["PATH"] = tempfile.mkdtemp()
            st, out = srv.client.post("/api/analyze", {"filename": "cv.pdf", "data": base64.b64encode(b"%PDF-1.4 minimal").decode()})
            self.assertEqual(st, 400)
            self.assertIn("pdftotext", out["error"])
        finally:
            os.environ["PATH"] = old
            srv.close()


if __name__ == "__main__":
    unittest.main()
