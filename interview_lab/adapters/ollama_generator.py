"""ADAPTER: question generator backed by a LOCAL Ollama daemon (http://127.0.0.1:11434 by default).

Standard library only (urllib). Nothing leaves the machine unless the user explicitly allows a non-loopback Ollama host.
Implements application.ports.QuestionGenerator; the model output is untrusted and goes through the same strict
validation as every other generator (parse_items).

    export ILAB_AI_PROVIDER=ollama
    export ILAB_AI_MODEL=qwen3.5:9b        # optional: otherwise the first installed model is used
    export ILAB_OLLAMA_URL=http://127.0.0.1:11434
"""
from __future__ import annotations

import ipaddress
import json
import socket
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from ..application.ports import GenerationError
from .anthropic_generator import MAX_INPUT_CHARS, PROMPT, parse_items

ITEMS_PER_REQUEST = 6          # small local models do better (and faster) with fewer questions per call
TIMEOUT_SECONDS = 300          # CPU-only inference of a 7-9B model can take minutes


def is_loopback(url: str) -> bool:
    host = urlsplit(url).hostname or ""
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        try:                                              # a name: every address it resolves to must be loopback
            return all(ipaddress.ip_address(a[4][0]).is_loopback for a in socket.getaddrinfo(host, None))
        except OSError:
            return False


def _http_json(url: str, payload=None, timeout: float = 10):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:      # nosec: scheme and host are validated by the caller
        return json.loads(r.read())


def installed_models(base_url: str, timeout: float = 5) -> list:
    return [m.get("name", "") for m in _http_json(base_url.rstrip("/") + "/api/tags", timeout=timeout).get("models", []) if m.get("name")]


class OllamaQuestionGenerator:
    name = "ollama"

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "", allow_remote: bool = False, post=None, tags=None):
        if urlsplit(base_url).scheme not in ("http", "https"):
            raise GenerationError("Ollama URL must be http(s)")
        if not allow_remote and not is_loopback(base_url):
            raise GenerationError("Ollama host is not loopback; set ILAB_OLLAMA_ALLOW_REMOTE=1 only if you accept sending your text to it")
        self.base = base_url.rstrip("/")
        self._post = post or (lambda path, payload: _http_json(self.base + path, payload, TIMEOUT_SECONDS))
        self._tags = tags or (lambda: installed_models(self.base))
        if not model:
            try:
                models = self._tags()
            except (OSError, ValueError) as e:
                raise GenerationError(f"Ollama is not reachable at {self.base}: {type(e).__name__}") from e
            if not models:
                raise GenerationError("Ollama has no installed models (run: ollama pull <model>)")
            model = models[0]
        self.model = model

    def generate(self, title: str, text: str, headings: list) -> list:
        prompt = PROMPT.format(n=ITEMS_PER_REQUEST, title=title[:120], text=text[:MAX_INPUT_CHARS])
        payload = {"model": self.model, "stream": False, "think": False,
                   "messages": [{"role": "user", "content": prompt}], "options": {"temperature": 0.2, "num_predict": 3000}}
        try:
            resp = self._post("/api/chat", payload)
            raw = (resp.get("message") or {}).get("content") or ""
        except (OSError, ValueError, urllib.error.URLError) as e:
            raise GenerationError(f"Ollama request failed: {type(e).__name__}") from e
        return parse_items(raw, title)
