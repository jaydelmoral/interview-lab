"""WEB: same-origin guard. Defends the local server against DNS rebinding and cross-site request forgery.

A web page open in another browser tab can send requests to http://localhost:PORT. Because this server compiles and
runs code, every request must prove it comes from our own pages: Host and Origin are checked, and state-changing
requests must be application/json (which browsers refuse to send cross-origin without a CORS preflight we never answer).
"""
from __future__ import annotations

import re

ORIGIN_RE = re.compile(r"^https?://([^/:]+|\[[^\]]+\])(:\d+)?$")


class RequestGuard:
    def __init__(self, allowed_hosts):
        self.allowed = set(allowed_hosts)

    def host_ok(self, headers) -> bool:
        host = headers.get("Host") or ""
        host = host[:host.index("]") + 1] if host.startswith("[") and "]" in host else host.split(":")[0]
        return host in self.allowed

    def origin_ok(self, headers) -> bool:
        origin = headers.get("Origin")
        if origin is None:
            return True          # non-browser clients (curl) send no Origin; browsers always do on cross-origin POST
        m = ORIGIN_RE.match(origin)
        return bool(m) and m.group(1) in self.allowed

    @staticmethod
    def is_json(headers) -> bool:
        return (headers.get("Content-Type") or "").lower().startswith("application/json")


SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": ("default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                                "img-src 'self' data:; font-src 'self' data:; worker-src 'self' blob:; connect-src 'self'; base-uri 'none'; form-action 'none'"),
}
