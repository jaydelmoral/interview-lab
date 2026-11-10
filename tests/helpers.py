"""Shared test helpers: an in-process server on a free port with a temporary home and a fake grader (no JVM needed)."""
import base64
import io
import json
import tempfile
import threading
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from interview_lab.config import Settings
from interview_lab.web.app import compose, make_server

ROOT = Path(__file__).resolve().parent.parent


class FakeGrader:
    def __init__(self):
        self.calls = []

    def grade(self, pid, path, lang="es"):
        self.calls.append((pid, Path(path).read_text(), lang))
        return {"problem": pid, "title": pid, "lang": lang, "timestamp": "t", "compile": {"ok": True, "message": ""}, "tests": [], "score": 5, "max": 10}


class Client:
    def __init__(self, base, port):
        self.base, self.port = base, port

    def call(self, method, path, body=None, headers=None, raw=None):
        h = {"Origin": f"http://localhost:{self.port}"}
        data = raw
        if body is not None:
            data, h["Content-Type"] = json.dumps(body).encode(), "application/json"
        h.update(headers or {})
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req) as r:
                payload = r.read()
                return r.status, (json.loads(payload) if "json" in r.headers.get("Content-Type", "") else payload)
        except urllib.error.HTTPError as e:
            payload = e.read()
            e.close()
            try:
                return e.code, json.loads(payload)
            except ValueError:
                return e.code, payload

    def get(self, path, **kw): return self.call("GET", path, **kw)
    def post(self, path, body=None, **kw): return self.call("POST", path, body, **kw)
    def delete(self, path, **kw): return self.call("DELETE", path, **kw)


class RunningServer:
    def __init__(self, **overrides):
        self.home = Path(tempfile.mkdtemp(prefix="ilab-api-"))
        s = Settings.from_env(ROOT, {"ILAB_HOME": str(self.home), "ILAB_PORT": "0", **overrides})
        self.grader = FakeGrader()
        self.handlers = compose(s, grader=self.grader)
        self.server = make_server(s, self.handlers)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = Client(f"http://127.0.0.1:{self.port}", self.port)

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def docx_bytes(text):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("word/document.xml", f"<w:document><w:p><w:t>{text}</w:t></w:p></w:document>")
    return b.getvalue()


def b64(data):
    return base64.b64encode(data).decode()
