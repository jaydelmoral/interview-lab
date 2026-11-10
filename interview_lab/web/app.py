"""WEB: composition root + HTTP server. Wires adapters into services and services into handlers."""
from __future__ import annotations

import json
import logging
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from ..adapters.anthropic_generator import AnthropicQuestionGenerator
from ..adapters.fs_catalog import FsCatalog
from ..adapters.fs_problems import FsProblems
from ..adapters.fs_repositories import FsBankRepository, FsExamRepository, JsonlLog
from ..adapters.java_grader import JavaCodeGrader
from ..adapters.offline_generator import OfflineQuestionGenerator
from ..adapters.sqlite_history import SqliteHistory
from ..adapters.web_fetcher import SafeUrlFetcher
from ..application.errors import AppError, Forbidden, InvalidRequest, NotFound, Unprocessable
from ..application.ports import GenerationError
from ..application.services import AnalysisService, BankService, ExamService, HistoryService, PracticeService
from ..config import Settings
from .handlers import Handlers, Request, Response, build_routes, lang_of
from .security import SECURITY_HEADERS, RequestGuard

log = logging.getLogger("interview_lab")
STATUS = {NotFound: 404, InvalidRequest: 400, Forbidden: 403, Unprocessable: 422}


def compose(settings: Settings, grader=None) -> Handlers:
    """Composition root: the only place that knows which concrete adapter implements each port."""
    problems = FsProblems(settings.root, settings.home)
    catalog = FsCatalog(settings.root, settings.home, problems)
    offline = OfflineQuestionGenerator()
    generator, ai_enabled = offline, False
    if settings.ai_provider == "anthropic":
        try:
            generator, ai_enabled = AnthropicQuestionGenerator(settings.ai_model), True
        except GenerationError as e:
            log.warning("AI generator disabled: %s", e)
    history = SqliteHistory(settings.home / "ilab.db")
    history.import_legacy(settings.home / "runs", settings.home / "exams")      # one-time, idempotent
    practice = PracticeService(problems, grader or JavaCodeGrader(settings.root, settings.home), JsonlLog(settings.home / "runs" / "results.jsonl"),
                               settings.home / "runs" / "attempts", settings.max_code_bytes, history)
    return Handlers(settings, AnalysisService(), ExamService(catalog, FsExamRepository(settings.home), history),
                    BankService(FsBankRepository(settings.home), SafeUrlFetcher(), generator, offline, settings.allow_fetch),
                    practice, ai_enabled, generator.name, HistoryService(history))


def make_server(settings: Settings, handlers: Handlers = None) -> ThreadingHTTPServer:
    h = handlers or compose(settings)
    routes = build_routes(h)
    guard = RequestGuard(settings.allowed_hosts)

    class RequestHandler(BaseHTTPRequestHandler):
        server_version = "interview-lab"

        def log_message(self, fmt, *args):
            pass

        def _send(self, resp: Response):
            data = resp.payload()
            self.send_response(resp.status)
            self.send_header("Content-Type", resp.content_type)
            self.send_header("Content-Length", str(len(data)))
            for k, v in SECURITY_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _error(self, status, message, details=None):
            body = {"error": message}
            if details:
                body.update(details)
            self._send(Response(status, body))

        def _dispatch(self, method: str):
            if not guard.host_ok(self.headers) or (method != "GET" and not guard.origin_ok(self.headers)):
                return self._error(403, "origin not allowed")
            parts = urlsplit(self.path)
            query = {k: v[0] for k, v in parse_qs(parts.query).items()}
            for m, rx, fn, limit in routes:
                match = rx.match(parts.path)
                if m != method or not match:
                    continue
                req = Request(method, parts.path, query, self.headers, None, lang_of(query.get("lang")), match.groupdict())
                if method == "POST":
                    if not guard.is_json(self.headers):
                        return self._error(415, "application/json required")
                    try:
                        length = int(self.headers.get("Content-Length", "0"))
                        if length > limit:
                            return self._error(413, "request too large")
                        req.body = json.loads(self.rfile.read(length))
                        assert isinstance(req.body, dict)
                    except Exception:
                        return self._error(400, "invalid request")
                    req.lang = lang_of(req.body.get("lang", query.get("lang")))
                try:
                    out = fn(req)
                    return self._send(out if isinstance(out, Response) else Response(200, out))
                except AppError as e:
                    return self._error(STATUS.get(type(e), 400), e.message, e.details)
                except Exception:                              # last resort: never take the server down
                    log.exception("unhandled error on %s %s", method, parts.path)
                    return self._error(500, "internal error")
            self._error(404, "not found")

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def do_DELETE(self):
            self._dispatch("DELETE")

    return ThreadingHTTPServer((settings.host, settings.port), RequestHandler)


def main(root) -> None:
    settings = Settings.from_env(root)
    (settings.home / "problems").mkdir(parents=True, exist_ok=True)
    (settings.home / "runs" / "attempts").mkdir(parents=True, exist_ok=True)
    server = make_server(settings)
    print(f"interview-lab on http://{'localhost' if settings.host in ('127.0.0.1', '0.0.0.0') else settings.host}:{settings.port}  (Ctrl+C to quit)")
    print(f"your data: {settings.home}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
