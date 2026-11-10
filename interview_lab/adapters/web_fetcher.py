"""ADAPTER: SSRF-safe URL fetcher + HTML text extractor (UrlFetcher port).
Lectura segura de enlaces (protección SSRF) y extracción de texto.

Safety: http/https only, ports 80/443, every resolved address must be a public one, redirects are re-validated,
size/time limits, text content only, and the connection is pinned to the validated IP (no DNS rebinding between check and use).
"""
import hashlib
import http.client
import ipaddress
import random
import re
import socket
import ssl
import urllib.parse
from html.parser import HTMLParser

MAX_BYTES = 1_500_000
TIMEOUT = 8
MAX_REDIRECTS = 3
USER_AGENT = "interview-lab/1.0 (personal study tool)"


from ..application.ports import FetchError


def resolve_public(host: str):
    """Returns a public IP for `host` or raises FetchError."""
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise FetchError(f"cannot resolve {host}") from e
    ips = {i[4][0] for i in infos}
    if not ips:
        raise FetchError("no address")
    for ip in ips:
        if not ipaddress.ip_address(ip.split("%")[0]).is_global:
            raise FetchError("address not allowed (private or local network)")
    return sorted(ips)[0]


def validate_url(url: str):
    u = urllib.parse.urlsplit(url.strip())
    if u.scheme not in ("http", "https") or not u.hostname:
        raise FetchError("only http(s) links are allowed")
    if u.username or u.password:
        raise FetchError("links with credentials are not allowed")
    port = u.port or (443 if u.scheme == "https" else 80)
    if port not in (80, 443):
        raise FetchError("only ports 80/443")
    return u, port


def _connection(u, port, ip):
    if u.scheme == "https":
        ctx = ssl.create_default_context()

        class Pinned(http.client.HTTPSConnection):
            def connect(self):
                sock = socket.create_connection((ip, port), self.timeout)
                self.sock = ctx.wrap_socket(sock, server_hostname=u.hostname)
        return Pinned(u.hostname, port, timeout=TIMEOUT, context=ctx)

    class PinnedHTTP(http.client.HTTPConnection):
        def connect(self):
            self.sock = socket.create_connection((ip, port), self.timeout)
    return PinnedHTTP(u.hostname, port, timeout=TIMEOUT)


def fetch(url: str, resolver=resolve_public) -> tuple[str, str]:
    """Returns (final_url, html_or_text). Raises FetchError."""
    for _ in range(MAX_REDIRECTS + 1):
        u, port = validate_url(url)
        ip = resolver(u.hostname)
        conn = _connection(u, port, ip)
        try:
            path = (u.path or "/") + ("?" + u.query if u.query else "")
            conn.request("GET", path, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain;q=0.9", "Accept-Encoding": "identity"})
            resp = conn.getresponse()
            if resp.status in (301, 302, 303, 307, 308) and resp.getheader("Location"):
                url = urllib.parse.urljoin(url, resp.getheader("Location"))
                continue
            if resp.status != 200:
                raise FetchError(f"HTTP {resp.status}")
            ctype = (resp.getheader("Content-Type") or "").lower()
            if not (ctype.startswith("text/html") or ctype.startswith("text/plain") or ctype.startswith("application/xhtml")):
                raise FetchError("only HTML or plain text pages are supported (not PDF or other formats)")
            data = resp.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise FetchError("page too large")
            m = re.search(r"charset=([\w-]+)", ctype)
            return url, data.decode(m.group(1) if m else "utf-8", "replace")
        except (OSError, http.client.HTTPException) as e:
            raise FetchError(f"network error: {e}") from e
        finally:
            conn.close()
    raise FetchError("too many redirects")


class _Text(HTMLParser):
    SKIP = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg"}
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "td", "th", "pre", "blockquote", "dd", "dt", "tr", "div", "br", "section", "article"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts, self.heads, self.title = [], [], ""
        self._in_title, self._head = False, None

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2", "h3"):
            self._head = []
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3") and self._head is not None:
            h = " ".join("".join(self._head).split())
            if 3 <= len(h) <= 120:
                self.heads.append((len("".join(self.parts)), h))
            self._head = None
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.skip:
            return
        self.parts.append(data)
        if self._head is not None:
            self._head.append(data)


def extract(html_or_text: str, is_html=True):
    """Returns (title, text, headings)."""
    if not is_html:
        return "", html_or_text, []
    p = _Text()
    p.feed(html_or_text)
    text = "".join(p.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return " ".join(p.title.split())[:160], text, [h for _, h in p.heads]




class SafeUrlFetcher:
    """Implements application.ports.UrlFetcher."""

    def __init__(self, resolver=resolve_public):
        self.resolver = resolver

    def fetch_text(self, url: str) -> tuple:
        final, body = fetch(url, self.resolver)
        return extract(body, is_html=True)[:3]
