#!/usr/bin/env python3
"""Validate multiple-choice question banks. MUST-HAVE rule: every question cites official sources and has a review status.
Valida bancos de preguntas de opción múltiple. REGLA OBLIGATORIA: toda pregunta cita fuentes oficiales y tiene estado de revisión.

    python3 tools/validate_bank.py                 # bank/questions, packs/*/questions and $ILAB_HOME/bank/questions
    python3 tools/validate_bank.py --path DIR      # just the *.json files in DIR (for example a pack's questions/)
    python3 tools/validate_bank.py --online        # also check that every source URL answers (needs curl)
    python3 tools/validate_bank.py --strict-review # unreviewed (draft) questions fail instead of just being counted
    python3 tools/validate_bank.py --strict-quality # a file whose answers can be guessed by length fails (see GUESSABLE_SHARE)
    python3 tools/validate_bank.py --quality-details # list every question whose right answer stands out by its length

Exit code 1 on any ERROR.

Quality rule (audit of 2026-11-13): if the right option is much longer than the wrong ones, a candidate scores without knowing
the subject, so the result measures nothing. Per file, the share of single-answer questions whose right option is the longest
should stay near chance (25 % with four options). Regla de calidad: la opción correcta no debe delatarse por su largo.
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


LENGTH_RATIO = 1.5        # a right option this many times longer than the average wrong one stands out
GUESSABLE_SHARE = 0.35    # per file: at most this share of single-answer questions may have the right option as the longest


def length_bias(q: dict):
    """(right option is the longest, right length / average wrong length) for a single-answer question; None otherwise.
    Lengths add the English and Spanish texts, so a bias in either language shows."""
    opts, ans = q.get("options"), q.get("answer")
    if not (isinstance(opts, list) and len(opts) >= 2 and all(pair_ok(o) for o in opts) and isinstance(ans, list) and len(ans) == 1
            and isinstance(ans[0], int) and 0 <= ans[0] < len(opts)):
        return None
    size = [len(o["en"].strip()) + len(o["es"].strip()) for o in opts]
    wrong = [s for i, s in enumerate(size) if i != ans[0]]
    return size[ans[0]] > max(wrong), size[ans[0]] / (sum(wrong) / len(wrong))


def quality_report(files: dict) -> tuple:
    """files: {where: [questions]} -> (lines to print, files over GUESSABLE_SHARE, questions over LENGTH_RATIO)."""
    lines, over, standout = [], [], []
    for where, items in files.items():
        rows = [(q.get("id", "?"), b) for q in items if isinstance(q, dict) for b in [length_bias(q)] if b]
        if not rows:
            continue
        share = sum(1 for _, (longest, _r) in rows if longest) / len(rows)
        standout += [f"{where}: {qid}: right option is {ratio:.1f}x the average wrong one" for qid, (_l, ratio) in rows if ratio > LENGTH_RATIO]
        mark = "  <-- guessable by length" if share > GUESSABLE_SHARE else ""
        lines.append(f"  quality  {where}: right option is the longest in {share:.0%} of {len(rows)} single-answer questions{mark}")
        if share > GUESSABLE_SHARE:
            over.append(f"{where}: right option is the longest in {share:.0%} of its questions (limit {GUESSABLE_SHARE:.0%}): rewrite the wrong options so they are as long and as plausible")
    return lines, over, standout


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
    by_module, by_file = {}, {}
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
            by_file[where] = items
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
    lines, over, standout = quality_report(by_file)
    for line in lines:
        print(line)
    if "--quality-details" in argv:
        for s in standout:
            print("  ·", s)
    elif standout:
        print(f"  quality  {len(standout)} question(s) whose right option stands out by its length (--quality-details lists them)")
    if "--strict-quality" in argv:
        errors += over
    for e in errors:
        print("  ✗", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
