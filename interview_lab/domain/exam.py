"""DOMAIN: rules for building an exam simulation, presenting it without answers, and grading non-code items.

Everything here is pure: the catalog of candidate items and the item resolver are passed in by the caller
(see application.ports), so these rules can be tested without files, a server or a JVM.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
import time
from typing import Callable, Optional

LEVELS = {"jr": 0, "mid": 1, "sr": 2, "staff": 3, "principal": 4, "any": 1}
MODULE_ORDER = ["coding", "java-trivia", "sql", "qa", "microservices", "devops", "architecture", "security", "unix", "mybank"]
TITLES = {
    "coding": {"es": "Código y Big O", "en": "Coding and Big O"},
    "java-trivia": {"es": "Predice la salida (Java)", "en": "Predict the output (Java)"},
    "sql": {"es": "SQL", "en": "SQL"},
    "qa": {"es": "QA: TDD y BDD", "en": "QA: TDD and BDD"},
    "microservices": {"es": "Microservicios", "en": "Microservices"},
    "devops": {"es": "DevOps", "en": "DevOps"},
    "architecture": {"es": "Arquitectura", "en": "Architecture"},
    "security": {"es": "Seguridad", "en": "Security"},
    "unix": {"es": "Unix / Linux", "en": "Unix / Linux"},
    "mybank": {"es": "Mi banco (enlaces y notas)", "en": "My bank (links and notes)"},
}
MIN_PER_ITEM = {"mcq": 1.5, "output": 1.0, "flash": 1.0}          # standard timers; coding uses each problem's own limit
DEFAULT_COUNT = {"coding": {"jr": 2, "mid": 2, "sr": 3, "staff": 3, "principal": 3}, "java-trivia": 10, "mybank": 10, "default": 8}
PACE = {"tight": 0.8, "standard": 1.0, "relaxed": 1.25}
JAVA_ONLY_MODULES = ("coding", "java-trivia")

Resolver = Callable[[dict], Optional[dict]]


def pick(value, lang: str) -> str:
    """Localized text: {"es":..,"en":..,"src":..} -> best match for `lang`."""
    if not isinstance(value, dict):
        return value or ""
    return value.get(lang) or value.get("src") or value.get("es") or value.get("en") or ""


def normalize(text) -> str:
    return "\n".join(" ".join(line.split()) for line in str(text).strip().splitlines())


# ------------------------------------------------------------------ building
def build(config: dict, candidates: list, now: Optional[float] = None) -> dict:
    """Builds an exam definition from user preferences and the available candidate items.

    Each candidate: {"ref", "module", "level", "min_java", "language", "tags", "minutes", ["bank"]}.
    Selection prefers items whose level is closest to the requested seniority; ties are shuffled with a seed
    derived from the exam id, so an exam is reproducible once created.
    """
    level = config.get("seniority") if config.get("seniority") in ("jr", "mid", "sr", "staff", "principal") else "mid"
    language = config.get("language") or "java"
    version = config.get("version")
    version = int(version) if isinstance(version, (int, str)) and str(version).isdigit() else None
    modules = [m for m in MODULE_ORDER if m in (config.get("modules") or [])]
    pace = PACE.get(config.get("pace", "standard"), 1.0)
    banks = set(config.get("banks") or [])
    counts = config.get("counts") or {}
    created = now if now is not None else time.time()
    exam_id = time.strftime("%Y%m%d-%H%M%S", time.localtime(created)) + "-" + hashlib.sha1(
        f"{created}{json.dumps(config, sort_keys=True, default=str)}".encode()).hexdigest()[:4]
    rng = random.Random(exam_id)
    notes, sections = [], []
    for module in modules:
        pool = [c for c in candidates if _eligible(c, module, language, version, banks)]
        if not pool:
            reason = {"es": f"Sin ejercicios disponibles para «{TITLES[module]['es']}» con esos filtros.",
                      "en": f"No exercises available for “{TITLES[module]['en']}” with those filters."}
            if module in JAVA_ONLY_MODULES and language != "java":
                reason = {"es": "Los ejercicios de código y la trivia son solo de Java por ahora.",
                          "en": "Coding exercises and the output quiz are Java-only for now."}
            notes.append({"module": module} | reason)
            continue
        rng.shuffle(pool)
        pool.sort(key=lambda c: abs(LEVELS[c["level"]] - LEVELS[level]))
        n = counts.get(module)
        if not isinstance(n, int) or n < 1:
            d = DEFAULT_COUNT.get(module, DEFAULT_COUNT["default"])
            n = d[level] if isinstance(d, dict) else d
        chosen = pool[:n]
        minutes = max(1, math.ceil(sum(c["minutes"] for c in chosen) * pace))
        sections.append({"module": module, "title": TITLES[module], "minutes": minutes, "items": [c["ref"] for c in chosen]})
    return {"id": exam_id, "created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created)),
            "title": (config.get("title") or "")[:120],
            "config": {"seniority": level, "language": language, "version": version, "modules": modules,
                       "pace": config.get("pace") or "standard", "banks": sorted(banks)},
            "sections": sections, "notes": notes, "total_minutes": sum(s["minutes"] for s in sections)}


def _eligible(c: dict, module: str, language: str, version: Optional[int], banks: set) -> bool:
    if c["module"] != module:
        return False
    if module in JAVA_ONLY_MODULES and language != "java":
        return False
    if language == "java" and version and c.get("min_java", 0) > version:
        return False
    if module == "mybank" and banks and c.get("bank") not in banks:
        return False
    return True


# ------------------------------------------------------------------ presenting
def item_key(ref: dict) -> str:
    return ref["t"] + ":" + str(ref.get("id") or ref.get("q"))


def option_order(exam_id: str, key: str, n: int) -> list:
    """Deterministic option shuffle per exam+item, so the answer position is not predictable but is reproducible when grading."""
    order = list(range(n))
    random.Random(f"{exam_id}:{key}").shuffle(order)
    return order


def public_item(exam_id: str, ref: dict, item: Optional[dict], lang: str) -> Optional[dict]:
    """The item as the candidate sees it: never includes the correct answer (except self-study flashcards)."""
    if item is None:
        return None
    key = item_key(ref)
    t = item["type"]
    if t == "code":
        return {"key": key, "type": "code", "id": item["id"], "title": item["title"], "minutes": item["minutes"]}
    if t == "output":
        topic = item.get("topic_en") if lang == "en" and item.get("topic_en") else item.get("topic", "")
        return {"key": key, "type": "output", "topic": topic, "code": item["code"]}
    if t == "flash":
        return {"key": key, "type": "flash", "q": pick(item["q"], lang), "a": pick(item["a"], lang)}
    order = option_order(exam_id, key, len(item["options"]))
    return {"key": key, "type": "mcq", "q": pick(item["q"], lang), "review": (item.get("review") or {}).get("status", "draft"),
            "options": [pick(item["options"][i], lang) for i in order], "multi": len(item["answer"]) > 1}


def public_exam(exam: dict, resolve: Resolver, lang: str) -> dict:
    sections = []
    for s in exam["sections"]:
        items = [public_item(exam["id"], r, resolve(r), lang) for r in s["items"]]
        sections.append({"module": s["module"], "title": pick(s["title"], lang), "minutes": s["minutes"], "items": [i for i in items if i]})
    return {"id": exam["id"], "created": exam["created"], "title": exam.get("title", ""), "config": exam["config"], "sections": sections,
            "notes": [{"module": n["module"], "text": pick(n, lang)} for n in exam.get("notes", [])], "total_minutes": exam["total_minutes"]}


# ------------------------------------------------------------------ grading
def grade_section(exam: dict, idx: int, answers: dict, resolve: Resolver, lang: str) -> dict:
    section = exam["sections"][idx]
    results, right = [], 0
    for ref in section["items"]:
        if ref["t"] == "code":
            continue                      # code is graded by the JVM grader, not here
        q = resolve(ref)
        if q is None:
            continue
        key, given = item_key(ref), answers.get(item_key(ref))
        if q["type"] == "output":
            ok = normalize(given or "") == normalize(q["expected"])
            expl = q.get("explanation_en") if lang == "en" and q.get("explanation_en") else q["explanation"]
            results.append({"key": key, "correct": ok, "expected": q["expected"], "explanation": expl, "tags": [q.get("topic", "")]})
        elif q["type"] == "flash":
            ok = given == "know"
            results.append({"key": key, "correct": ok, "expected": pick(q["a"], lang), "explanation": "", "tags": q.get("tags", [])})
        else:
            order = option_order(exam["id"], key, len(q["options"]))
            chosen = {order[g] for g in (given if isinstance(given, list) else [given]) if isinstance(g, int) and 0 <= g < len(order)}
            ok = chosen == set(q["answer"])
            results.append({"key": key, "correct": ok, "expected": " / ".join(pick(q["options"][a], lang) for a in q["answer"]),
                            "expected_index": [order.index(a) for a in q["answer"]], "explanation": pick(q["explain"], lang),
                            "tags": q.get("tags", []), "sources": q.get("sources", []), "review": (q.get("review") or {}).get("status", "draft")})
        right += ok
    return {"module": section["module"], "score": right, "max": len(results), "items": results}


ATTEMPT_ID = re.compile(r"^[0-9a-f]{32}$")       # random id the browser mints when an attempt starts


def valid_attempt(attempt) -> bool:
    return isinstance(attempt, str) and bool(ATTEMPT_ID.match(attempt))


def clean_answers(section: dict, answers: dict) -> dict:
    """Autosaved answers reduced to what grading understands: known item keys; ints, short int lists or short text."""
    keys = {item_key(r) for r in section["items"]}
    out = {}
    for k, v in answers.items():
        if k not in keys:
            continue
        if isinstance(v, list):
            v = [x for x in v[:20] if isinstance(x, int) and not isinstance(x, bool)]
        elif isinstance(v, str):
            v = v[:2000]
        elif isinstance(v, bool) or not isinstance(v, int):
            continue
        out[k] = v
    return out


def is_code_section(section: dict) -> bool:
    return bool(section["items"]) and section["items"][0]["t"] == "code"


def code_result(section: dict, best: dict, points: dict) -> dict:
    """Result of a code section from the best graded submission per exercise.

    `best` maps item key -> {"score", "passed"}; `points` maps problem id -> (max points, number of tests).
    Exercises never submitted count as 0, so the section maximum never depends on what the client reports.
    """
    score = top = passed = total = 0
    for ref in section["items"]:
        pts, n = points.get(ref.get("id"), (0, 0))
        top, total = top + pts, total + n
        b = best.get(item_key(ref))
        if b:
            score, passed = score + min(b["score"], pts), passed + min(b["passed"], n)
    return {"score": score, "max": top, "correct": passed, "total": total}


def missed_items(exam: dict, idx: int, report: dict, resolve: Resolver, title: str, lang: str) -> list:
    """Questions answered wrong in a graded section, in the shape the history stores (text, expected answer, tags)."""
    by_key = {item_key(r): r for r in exam["sections"][idx]["items"]}
    out = []
    for r in report["items"]:
        ref = by_key.get(r["key"])
        pub = public_item(exam["id"], ref, resolve(ref), lang) if ref and not r["correct"] else None
        if pub:
            text = pub.get("q") or ((pub["topic"] + ": " if pub.get("topic") else "") + str(pub.get("code", "")).split("\n")[0])
            out.append({"section": title, "q": text, "expected": r["expected"], "explanation": r["explanation"], "tags": r.get("tags", [])})
    return out


def weak_tags(results: list) -> list:
    counts: dict = {}
    for r in results:
        if not r["correct"]:
            for t in r.get("tags", []):
                if t:
                    counts[t] = counts.get(t, 0) + 1
    return sorted(counts, key=lambda t: -counts[t])[:8]
