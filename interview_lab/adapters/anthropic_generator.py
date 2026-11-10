"""ADAPTER (optional): AI question generator using the Anthropic API with the *user's own* key.

Off by default. Enable it by installing the SDK and setting your own key in your environment:

    pip install anthropic
    export ANTHROPIC_API_KEY=...        # YOUR key; this project never ships or stores one
    export ILAB_AI_PROVIDER=anthropic   # optional: ILAB_AI_MODEL (default claude-haiku-5-5)

Privacy: when enabled, the text you add to "My bank" is sent to the provider to generate questions. Cost is billed to your account.
Privacidad: si lo activas, el texto que agregues a "Mi banco" se envía al proveedor; el costo es de tu cuenta, nunca del autor del proyecto.
"""
from __future__ import annotations

import hashlib
import json

from ..application.ports import GenerationError

MAX_INPUT_CHARS = 12_000
MAX_ITEMS = 12
PROMPT = """You are writing study questions for a software engineer preparing for a technical interview.
From the TEXT below, write up to {n} multiple-choice questions that test understanding of the technical concepts in it.
Rules:
- Use ONLY facts stated in the text. Do not invent facts.
- Each question has exactly 4 options and exactly one correct option.
- Write in the same language as the text.
- Reply with ONLY a JSON array, no prose, where each element is:
  {{"q": "question", "options": ["a", "b", "c", "d"], "answer": 0, "explain": "one sentence"}}
  ("answer" is the 0-based index of the correct option.)

TITLE: {title}
TEXT:
{text}
"""


def parse_items(raw: str, title: str) -> list:
    """Extracts and validates the JSON array returned by the model. Untrusted input: validate everything."""
    try:
        data = json.loads(raw[raw.index("["): raw.rindex("]") + 1])
    except ValueError as e:
        raise GenerationError("the model did not return a JSON array") from e
    items = []
    for d in data[:MAX_ITEMS] if isinstance(data, list) else []:
        try:
            q, opts, ans, ex = str(d["q"]).strip(), [str(o).strip() for o in d["options"]], int(d["answer"]), str(d.get("explain", "")).strip()
        except (KeyError, TypeError, ValueError):
            continue
        if not (10 <= len(q) <= 400) or len(opts) != 4 or not 0 <= ans < 4 or any(not (1 <= len(o) <= 300) for o in opts) or len(set(opts)) != 4:
            continue
        iid = "a" + hashlib.sha1((q + opts[ans]).encode()).hexdigest()[:8]
        items.append({"id": iid, "type": "mcq", "module": "mybank", "level": "any", "tags": [title[:40]] if title else [],
                      "q": {"src": q}, "options": [{"src": o} for o in opts], "answer": [ans], "explain": {"src": ex[:400]}})
    if not items:
        raise GenerationError("the model returned no valid questions")
    return items


class AnthropicQuestionGenerator:
    """Implements application.ports.QuestionGenerator. The SDK is imported lazily so it stays an optional dependency."""
    name = "anthropic"

    def __init__(self, model: str, client=None):
        self.model = model
        if client is None:
            try:
                import anthropic                      # noqa: PLC0415 (optional dependency)
            except ImportError as e:
                raise GenerationError("install the SDK first: pip install anthropic") from e
            client = anthropic.Anthropic()            # reads ANTHROPIC_API_KEY from the environment
        self.client = client

    def generate(self, title: str, text: str, headings: list) -> list:
        prompt = PROMPT.format(n=MAX_ITEMS, title=title[:120], text=text[:MAX_INPUT_CHARS])
        try:
            resp = self.client.messages.create(model=self.model, max_tokens=4000, messages=[{"role": "user", "content": prompt}])
            raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        except Exception as e:                         # network, auth, quota...: never leak details of the key
            raise GenerationError(f"AI provider error: {type(e).__name__}") from e
        return parse_items(raw, title)
