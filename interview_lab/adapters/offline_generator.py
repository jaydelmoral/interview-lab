"""ADAPTER: offline question generator (QuestionGenerator port). No AI, no network.
Generador local de preguntas: llena huecos con términos técnicos y crea tarjetas a partir de los títulos.
"""
import hashlib
import random
import re

STOP = set("""the and for with that this from are was were has have had not but you your can will would should could into onto over under
than then them they their there here when where what which who whom whose how why also such more most many much some any each other
use used using uses based may might must just like only very about after before between both either neither been being does did
los las del una uno unos unas con por para que como pero sus sus este esta estos estas ese esa cuando donde cual quien cómo también
más muy son ser fue sido está están hay puede pueden debe deben entre sobre desde hasta cada otro otra todo toda todos todas""".split())
TOKEN = re.compile(r"[A-Za-z@][A-Za-z0-9_.@#+-]{2,}")
SENT = re.compile(r"(?<=[.!?:;])\s+|\n+")
DEFN = re.compile(r"\b(is a|is an|are|means|es un|es una|son|permite|allows|used to|se usa|sirve|consists|consiste|provides|proporciona|defines|define)\b", re.I)


def _terms(text):
    freq = {}
    for tok in TOKEN.findall(text):
        t = tok.strip(".-#+")
        if len(t) < 3 or t.lower() in STOP or t.isdigit():
            continue
        freq[t] = freq.get(t, 0) + 1
    return freq


def _is_technical(tok, freq):
    strong = (any(c.isupper() for c in tok[1:]) or tok.startswith("@") or any(c.isdigit() for c in tok)
              or "_" in tok or "." in tok or tok.isupper() or (tok[0].isupper() and len(tok) > 5))
    return strong or freq.get(tok, 0) >= 3


def make_items(title, text, headings, lang_hint="src", limit=30, seed=None):
    """Builds multiple-choice 'fill the blank' items and flashcards from text. Deterministic for a given seed."""
    rng = random.Random(seed or hashlib.sha1(text[:2000].encode()).hexdigest())
    freq = _terms(text)
    techs = sorted({t for t in freq if _is_technical(t, freq)}, key=lambda t: (-freq[t], t))
    sentences = [s.strip() for s in SENT.split(text) if 50 <= len(s.strip()) <= 240]
    scored = []
    for s in sentences:
        cand = [t for t in TOKEN.findall(s) if t.strip(".-#+") in techs and len(t) >= 4]
        if not cand:
            continue
        score = (2 if DEFN.search(s) else 0) + min(len(cand), 3) + (1 if 70 <= len(s) <= 180 else 0)
        scored.append((score, s, cand))
    scored.sort(key=lambda x: -x[0])
    items, used = [], set()
    for score, s, cand in scored:
        if len(items) >= limit - min(len(headings), 6):
            break
        answer = max(cand, key=lambda t: (freq.get(t.strip(".-#+"), 0), len(t))).strip(".-#+")
        if answer in used:
            continue
        pool = [t for t in techs if t != answer and t not in s and abs(len(t) - len(answer)) <= 8]
        if len(pool) < 3:
            continue
        distract = rng.sample(pool[:30], 3)
        opts = distract + [answer]
        rng.shuffle(opts)
        used.add(answer)
        blank = re.sub(re.escape(answer), "_____", s, count=1)
        iid = "c" + hashlib.sha1((s + answer).encode()).hexdigest()[:8]
        items.append({"id": iid, "type": "mcq", "module": "mybank", "level": "any", "tags": [title[:40]] if title else [],
                      "q": {"src": blank}, "options": [{"src": o} for o in opts], "answer": [opts.index(answer)],
                      "explain": {"src": s}})
    # flashcards from headings: "Explain: <heading>" + the first sentences after it
    for h in headings[:6]:
        pos = text.find(h)
        if pos < 0:
            continue
        after = " ".join(text[pos + len(h): pos + len(h) + 400].split())
        if len(after) < 60:
            continue
        iid = "f" + hashlib.sha1((h + after[:40]).encode()).hexdigest()[:8]
        items.append({"id": iid, "type": "flash", "module": "mybank", "level": "any", "tags": [title[:40]] if title else [],
                      "q": {"src": h}, "a": {"src": after[:360]}})
    return items


class OfflineQuestionGenerator:
    """Implements application.ports.QuestionGenerator with deterministic heuristics."""
    name = "offline"

    def generate(self, title: str, text: str, headings: list) -> list:
        return make_items(title, text, headings)
