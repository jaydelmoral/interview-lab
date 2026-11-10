"""WEB: route handlers. Thin translation between HTTP (paths, JSON) and application services."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from ..application.errors import NotFound

STATIC_TYPES = {".png": "image/png", ".json": "application/json; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".ttf": "font/ttf", ".woff2": "font/woff2", ".svg": "image/svg+xml", ".map": "application/json"}
PAGES = {"/": "landing.html", "/index.html": "landing.html", "/practice": "index.html", "/exam": "exam.html", "/history": "history.html"}
ASSETS = {"/common.js", "/common.css", "/theme.js", "/editor.js", "/exam.js", "/history.js", "/index.js", "/landing.js", "/fonts/Outfit-latin-400-600.woff2"}
BRAND_FILE = re.compile(r"^/brand/([a-z0-9._-]+\.(?:png|json))$")


@dataclass
class Request:
    method: str
    path: str
    query: dict
    headers: object
    body: Optional[dict] = None
    lang: str = "es"
    params: dict = field(default_factory=dict)


@dataclass
class Response:
    status: int = 200
    body: object = None
    content_type: str = "application/json; charset=utf-8"

    def payload(self) -> bytes:
        if isinstance(self.body, bytes):
            return self.body
        if isinstance(self.body, str):
            return self.body.encode()
        return json.dumps(self.body, ensure_ascii=False).encode()


def lang_of(value) -> str:
    return "en" if value == "en" else "es"


class Handlers:
    """Holds the services (injected by the composition root) and exposes one method per endpoint."""

    def __init__(self, settings, analysis, exams, banks, practice, ai_enabled: bool, generator_name: str, history=None, runtimes=None):
        self.s, self.analysis, self.exams, self.banks, self.practice, self.history, self.runtimes = settings, analysis, exams, banks, practice, history, runtimes
        self.ai_enabled, self.generator_name = ai_enabled, generator_name
        self.web = settings.root / "web"

    # ---- pages and static files
    def page(self, req: Request) -> Response:
        return Response(200, (self.web / PAGES[req.path]).read_bytes(), "text/html; charset=utf-8")

    def asset(self, req: Request) -> Response:
        return Response(200, (self.web / req.path[1:]).read_bytes(), STATIC_TYPES[Path(req.path).suffix])

    def vendor_file(self, req: Request) -> Response:
        """Optional vendored Monaco editor (installed by tools/fetch_monaco.py, git-ignored). Read-only, confined to its folder."""
        base = (self.web / "vendor" / "monaco").resolve()
        rel = req.params["path"]
        f = (base / rel).resolve()
        if ".." in rel.split("/") or base not in f.parents or not f.is_file() or f.suffix not in STATIC_TYPES:
            raise NotFound("not found")
        return Response(200, f.read_bytes(), STATIC_TYPES[f.suffix])

    def brand_file(self, req: Request) -> Response:
        f = self.web / "brand" / req.params["file"]
        if not f.is_file():
            raise NotFound("not found")
        return Response(200, f.read_bytes(), STATIC_TYPES[f.suffix])

    def brand(self, req: Request):
        return json.loads((self.web / "brand" / "brand.json").read_text())

    # ---- profile / catalog
    def analyze(self, req: Request):
        b = req.body
        return self.analysis.analyze(text=b.get("text"), filename=str(b.get("filename", "")), data_b64=b.get("data"))

    def modules(self, req: Request):
        return self.exams.modules(req.lang, self.s.allow_fetch, self.ai_enabled) | {"generator": self.generator_name}

    # ---- exams
    def exams_list(self, req: Request):
        return self.exams.list()

    def exam_create(self, req: Request):
        cfg = {k: req.body.get(k) for k in ("seniority", "language", "version", "modules", "pace", "banks", "counts", "title")}
        return self.exams.create(cfg, req.lang)

    def exam_get(self, req: Request):
        return self.exams.get_public(req.params["id"], req.lang)

    def exam_section(self, req: Request):
        return self.exams.grade_section(req.params["id"], req.body.get("section"), req.body.get("answers"), req.lang, req.body.get("attempt"))

    def exam_start(self, req: Request):
        return self.exams.start_section(req.params["id"], req.body.get("section"), req.body.get("attempt"))

    def exam_answers(self, req: Request):
        return self.exams.save_answers(req.params["id"], req.body.get("section"), req.body.get("answers"), req.body.get("attempt"))

    def exam_finish(self, req: Request):
        return self.exams.finish(req.params["id"], req.body.get("sections"), req.body.get("attempt"), req.lang)

    # ---- memory banks
    def banks_list(self, req: Request):
        return self.banks.list()

    def bank_create(self, req: Request):
        b = req.body
        urls = [u for u in (b.get("urls") or []) if isinstance(u, str) and u.strip()]
        notes = b.get("notes") if isinstance(b.get("notes"), str) else ""
        return self.banks.create(str(b.get("title", ""))[:80], urls, notes)

    def bank_delete(self, req: Request):
        self.banks.delete(req.params["id"])
        return {"deleted": req.params["id"]}

    # ---- installed runtimes (read-only: the app never installs anything, see ADR-0019)
    def runtimes_list(self, req: Request):
        return self.runtimes.list(req.lang)

    # ---- history and analytics
    def history_overview(self, req: Request):
        return self.history.overview()

    def history_run(self, req: Request):
        return self.history.run(int(req.params["id"]))

    # ---- free practice
    def problems_list(self, req: Request):
        return self.practice.list()

    def problem_get(self, req: Request):
        return self.practice.get(req.params["id"], req.lang)

    def grade_code(self, req: Request):
        b = req.body
        target = self.exams.code_target(b.get("exam"), b.get("attempt"), b.get("problem"))    # None: plain free practice
        report = self.practice.grade_code(b.get("problem"), b.get("code"), req.lang)
        if target:
            self.exams.record_code(target, report)
        return report

    def grade_quiz(self, req: Request):
        return self.practice.grade_quiz(req.body.get("problem"), req.body.get("answers"), req.lang)


def build_routes(h: Handlers) -> list:
    """(method, compiled path regex, handler, max JSON body bytes). The table IS the API surface (see docs/API.md)."""
    big, small = 4_500_000, 100_000
    r = lambda m, p, fn, limit=small: (m, re.compile("^" + p + "$"), fn, limit)   # noqa: E731
    return [
        *[r("GET", re.escape(p), h.page) for p in PAGES],
        *[r("GET", re.escape(p), h.asset) for p in ASSETS],
        r("GET", r"/brand/(?P<file>[a-z0-9._-]+\.(?:png|json))", h.brand_file),
    r("GET", r"/vendor/monaco/(?P<path>vs(?:/[A-Za-z0-9_.@-]+)+)", h.vendor_file),
        r("GET", "/api/brand", h.brand),
        r("GET", "/api/modules", h.modules),
        r("GET", "/api/problems", h.problems_list),
        r("GET", r"/api/problems/(?P<id>[^/]+)", h.problem_get),
        r("GET", "/api/exams", h.exams_list),
        r("GET", r"/api/exams/(?P<id>[^/]+)", h.exam_get),
        r("GET", "/api/banks", h.banks_list),
    r("GET", "/api/runtimes", h.runtimes_list),
    r("GET", "/api/history", h.history_overview),
    r("GET", r"/api/history/runs/(?P<id>\d{1,12})", h.history_run),
        r("POST", "/api/analyze", h.analyze, big),
        r("POST", "/api/exams", h.exam_create),
        r("POST", r"/api/exams/(?P<id>[^/]+)/section", h.exam_section),
        r("POST", r"/api/exams/(?P<id>[^/]+)/start", h.exam_start),
        r("POST", r"/api/exams/(?P<id>[^/]+)/answers", h.exam_answers),
        r("POST", r"/api/exams/(?P<id>[^/]+)/finish", h.exam_finish),
        r("POST", "/api/banks", h.bank_create),
        r("POST", "/api/grade", h.grade_code),
        r("POST", "/api/quiz", h.grade_quiz),
        r("DELETE", r"/api/banks/(?P<id>[^/]+)", h.bank_delete),
    ]
