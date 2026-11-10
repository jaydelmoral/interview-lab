#!/usr/bin/env python3
"""Validate multiple-choice question banks. MUST-HAVE rule: every question cites official sources and has a review status.
Valida bancos de preguntas de opción múltiple. REGLA OBLIGATORIA: toda pregunta cita fuentes oficiales y tiene estado de revisión.

    python3 tools/validate_bank.py                 # bank/questions, packs/*/questions and $ILAB_HOME/bank/questions
    python3 tools/validate_bank.py --path DIR      # just the *.json files in DIR (for example a pack's questions/)
    python3 tools/validate_bank.py --online        # also check that every source URL answers (needs curl)
    python3 tools/validate_bank.py --strict-review # unreviewed (draft) questions fail instead of just being counted

Exit code 1 on any ERROR.
"""
import concurrent.futures as cf
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = {"sql", "qa", "microservices", "devops", "architecture", "security", "unix"}
LEVELS = {"jr", "mid", "sr", "staff", "principal", "any"}
REVIEW_STATUS = {"draft", "reviewed"}


def pair_ok(x) -> bool:
    return isinstance(x, dict) and all(isinstance(x.get(k), str) and x[k].strip() for k in ("en", "es"))


def check_question(q: dict, where: str, errors: list) -> None:
    def err(msg):
        errors.append(f"{where}: {q.get('id', '?')}: {msg}")
    for k in ("id", "type", "module", "level", "tags", "q", "options", "answer", "explain", "sources", "review"):
        if k not in q:
            err(f"missing '{k}'")
    if q.get("type") != "mcq":
        err("type must be 'mcq'")
    if q.get("module") not in MODULES:
        err(f"unknown module {q.get('module')!r}")
    if q.get("level") not in LEVELS:
        err(f"unknown level {q.get('level')!r}")
    if not (isinstance(q.get("tags"), list) and q["tags"] and all(isinstance(t, str) and t for t in q["tags"])):
        err("tags must be a non-empty list of strings")
    if not pair_ok(q.get("q")):
        err("q must have non-empty 'en' and 'es'")
    opts = q.get("options")
    if not (isinstance(opts, list) and len(opts) == 4 and all(pair_ok(o) for o in opts)):
        err("options must be exactly 4 items, each with 'en' and 'es'")
    else:
        if len({o["en"].strip().lower() for o in opts}) != 4:
            err("options are not distinct")
    ans = q.get("answer")
    if not (isinstance(ans, list) and ans and all(isinstance(a, int) and 0 <= a < 4 for a in ans) and len(set(ans)) == len(ans)):
        err("answer must be a non-empty list of distinct indexes 0..3")
    if not pair_ok(q.get("explain")):
        err("explain must have non-empty 'en' and 'es'")
    # ---- MUST-HAVE: sources
    src = q.get("sources")
    if not (isinstance(src, list) and src):
        err("MUST-HAVE: needs at least one source (official documentation)")
    else:
        for s in src:
            if not (isinstance(s, dict) and isinstance(s.get("title"), str) and s["title"].strip()
                    and isinstance(s.get("url"), str) and s["url"].startswith("https://")):
                err(f"bad source entry {s!r}: needs 'title' and an https 'url'")
    # ---- MUST-HAVE: review status
    rv = q.get("review")
    if not (isinstance(rv, dict) and rv.get("status") in REVIEW_STATUS and rv.get("author") and rv.get("date")):
        err("MUST-HAVE: review needs status (draft|reviewed), author and date")
    elif rv["status"] == "reviewed" and not rv.get("reviewer"):
        err("a 'reviewed' question must name its reviewer")


def question_dirs(only: Path = None) -> list:
    if only:
        return [Path(only)]
    dirs = [ROOT / "bank" / "questions"]
    dirs += sorted((ROOT / "packs").glob("*/questions")) if (ROOT / "packs").is_dir() else []
    home = Path(os.environ.get("ILAB_HOME", ROOT / "workspace"))
    dirs.append(home / "bank" / "questions")
    return [d for d in dirs if d.is_dir()]


def probe(url: str):
    for method in (["-I"], []):
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "-m", "20", "-w", "%{http_code}", "-A", "Mozilla/5.0 (source-check)", *method, url], capture_output=True, text=True)
        if r.stdout.strip().isdigit() and int(r.stdout) < 400:
            return url, int(r.stdout)
    return url, int(r.stdout) if r.stdout.strip().isdigit() else 0


def main(argv: list) -> int:
    only = Path(argv[argv.index("--path") + 1]) if "--path" in argv else None
    errors, seen, total, drafts, urls = [], {}, 0, 0, set()
    by_module = {}
    for d in question_dirs(only):
        for f in sorted(d.glob("*.json")):
            try:
                where = str(f.resolve().relative_to(ROOT))
            except ValueError:
                where = str(f)
            try:
                items = json.loads(f.read_text())
            except ValueError as e:
                errors.append(f"{where}: invalid JSON ({e})")
                continue
            if not isinstance(items, list):
                errors.append(f"{where}: expected a JSON list")
                continue
            for q in items:
                total += 1
                check_question(q, where, errors)
                qid = q.get("id")
                if qid in seen:
                    errors.append(f"{where}: duplicate id {qid} (also in {seen[qid]})")
                seen[qid] = where
                by_module[q.get("module")] = by_module.get(q.get("module"), 0) + 1
                if (q.get("review") or {}).get("status") != "reviewed":
                    drafts += 1
                for s in q.get("sources") or []:
                    if isinstance(s, dict) and isinstance(s.get("url"), str):
                        urls.add(s["url"])
    if "--online" in argv:
        with cf.ThreadPoolExecutor(8) as ex:
            for url, code in ex.map(probe, sorted(urls)):
                if code == 0 or code >= 400:
                    errors.append(f"source URL does not answer (HTTP {code}): {url}")
    if "--strict-review" in argv and drafts:
        errors.append(f"{drafts} question(s) are still 'draft' (strict review mode)")
    print(f"{total} questions, {len(urls)} distinct sources, {total - drafts} reviewed / {drafts} draft; by module: {dict(sorted(by_module.items()))}")
    for e in errors:
        print("  ✗", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
