"""Optional Monaco editor: pinned-hash installer, safe extraction and the confined vendor route."""
import base64
import hashlib
import io
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

from tests.helpers import RunningServer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import fetch_monaco as FM  # noqa: E402


def make_tgz(members: dict) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


class TestFetchMonaco(unittest.TestCase):
    def test_hash_verification(self):
        data = b"hello"
        good = "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()
        self.assertTrue(FM.verify(data, good))
        self.assertFalse(FM.verify(b"tampered", good))
        self.assertFalse(FM.verify(data))                      # the real pinned hash does not match arbitrary bytes

    def test_pinned_version_and_hash_are_present(self):
        self.assertRegex(FM.VERSION, r"^\d+\.\d+\.\d+$")
        self.assertTrue(FM.INTEGRITY.startswith("sha512-") and len(FM.INTEGRITY) > 80)
        self.assertTrue(FM.URL.startswith("https://registry.npmjs.org/"))

    def test_extracts_only_wanted_files(self):
        tgz = make_tgz({"package/min/vs/loader.js": b"L", "package/min/vs/editor/editor.main.js": b"E", "package/LICENSE": b"MIT",
                        "package/esm/vs/huge.js": b"NO", "package/README.md": b"NO"})
        dest = Path(tempfile.mkdtemp())
        self.assertEqual(FM.extract(tgz, dest), 3)
        self.assertTrue((dest / "vs" / "loader.js").is_file() and (dest / "LICENSE").is_file())
        self.assertFalse((dest / "esm").exists() or (dest / "README.md").exists())

    def test_path_traversal_in_archive_is_refused(self):
        tgz = make_tgz({"package/min/vs/../../../../evil.js": b"X"})
        with self.assertRaises(SystemExit):
            FM.extract(tgz, Path(tempfile.mkdtemp()))


class TestVendorRoute(unittest.TestCase):
    def test_serves_installed_files_and_blocks_everything_else(self):
        vend = ROOT / "web" / "vendor" / "monaco" / "vs"
        existed = vend.exists()
        probe = vend / "test-probe.js"
        vend.mkdir(parents=True, exist_ok=True)
        probe.write_text("//probe")
        srv = RunningServer()
        try:
            c = srv.client
            st, body = c.get("/vendor/monaco/vs/test-probe.js")
            self.assertEqual((st, body), (200, b"//probe"))
            for bad in ("/vendor/monaco/vs/missing.js", "/vendor/monaco/vs/../../../../etc/passwd", "/vendor/monaco/other/x.js", "/vendor/monaco/vs/test-probe.js%2e%2e"):
                self.assertEqual(c.get(bad)[0], 404, bad)
            self.assertEqual(c.post("/vendor/monaco/vs/test-probe.js", {})[0], 404)
        finally:
            srv.close()
            probe.unlink()
            if not existed:
                vend.rmdir()
                vend.parent.rmdir()

    def test_csp_allows_the_editor_assets_but_nothing_external(self):
        srv = RunningServer()
        try:
            import urllib.request
            r = urllib.request.urlopen(srv.client.base + "/")
            csp = r.headers["Content-Security-Policy"]
            r.close()
            self.assertIn("font-src 'self' data:", csp)
            self.assertIn("worker-src 'self' blob:", csp)
            self.assertIn("default-src 'none'", csp)
            self.assertNotIn("http", csp.replace("http://", ""))   # no external origins listed
        finally:
            srv.close()


if __name__ == "__main__":
    unittest.main()
