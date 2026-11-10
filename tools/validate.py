#!/usr/bin/env python3
"""Validate problems: structure, bilingual statements, content lint, and (optionally) run the reference solution.
Valida problemas: estructura, enunciados bilingües, lint de contenido y ejecución de la solución de referencia.

    python3 tools/validate.py                     # every built-in problem + your workspace problems
    python3 tools/validate.py my-problem-id       # just one
    python3 tools/validate.py --no-run            # skip the JVM (structure + lint only)

Exit code 1 if there is any ERROR. WARNINGS (brands, missing translation) do not fail the run.
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "grader"))
import grade as G  # noqa: E402

BRANDS = json.loads((ROOT / "tools" / "brands.json").read_text())
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?<!\d)\+?\d[\d\s().-]{8,}\d(?!\d)")
REQUIRED = ["id", "title", "time_limit_min", "tags"]
CODE_REQUIRED = ["tests"]
TEST_KEYS = ["id", "category", "title", "points", "fail_why", "fail_how"]


def blocks(md: str):
    """Top-level blocks of a statement: code fences count as one block; the rest is split on blank lines."""
    out, cur, fence = [], [], False
    for line in md.splitlines():
        if line.startswith("```"):
            cur.append(line)
            if fence:
                out.append("\n".join(cur)); cur = []
            fence = not fence
            continue
        if fence:
            cur.append(line)
        elif line.strip() == "":
            if cur:
                out.append("\n".join(cur)); cur = []
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return out


def lint_text(name, text, allow, problems):
    low = text.lower()
    for brand, sector in BRANDS["brands"].items():
        if brand in allow:
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(brand) + r"(?![a-z0-9])", low):
            problems.append(("WARN", f"{name}: mentions the brand '{brand}'. Use the sector instead -> {sector}"))
    for plat in BRANDS["platforms"]:
        if plat in allow:
            continue
        if plat in low:
            problems.append(("WARN", f"{name}: mentions the platform '{plat}'. Do not copy statements from other platforms; write your own wording."))
    if EMAIL.search(text):
        problems.append(("WARN", f"{name}: contains something that looks like an email address."))
    if PHONE.search(text):
        problems.append(("WARN", f"{name}: contains something that looks like a phone number."))


def validate(pdir: Path, run: bool):
    issues = []
    err = lambda m: issues.append(("ERROR", m))  # noqa: E731
    try:
        meta = json.loads((pdir / "meta.json").read_text())
    except Exception as e:
        return [("ERROR", f"meta.json is not valid JSON: {e}")]
    for k in REQUIRED:
        if k not in meta:
            err(f"meta.json: missing '{k}'")
    if meta.get("id") != pdir.name:
        err(f"meta.json: id '{meta.get('id')}' must equal the folder name '{pdir.name}'")
    if not re.match(r"^[a-z0-9][a-z0-9-]{2,63}$", pdir.name):
        err("folder name must be 3-64 chars: lowercase letters, digits and hyphens")
    if not meta.get("license"):
        issues.append(("WARN", "meta.json: no 'license' (suggested: CC-BY-4.0 or the license you own for your content)"))
    allow = {a.lower() for a in meta.get("lint_allow", [])}

    texts = {"meta.json": (pdir / "meta.json").read_text()}
    for f in ("problem.md", "problem.es.md", "starter.java", "Harness.java"):
        if (pdir / f).exists():
            texts[f] = (pdir / f).read_text()
    for f in (pdir / "reference").glob("*.java") if (pdir / "reference").is_dir() else []:
        texts["reference/" + f.name] = f.read_text()
    for name, text in texts.items():
        lint_text(f"{pdir.name}/{name}", text, allow, issues)

    if meta.get("kind") == "quiz":
        try:
            qs = json.loads((pdir / "quiz.json").read_text())
            for q in qs:
                for k in ("id", "topic", "code", "expected", "explanation"):
                    if k not in q:
                        err(f"quiz.json: question {q.get('id')} lacks '{k}'")
        except Exception as e:
            err(f"quiz.json invalid: {e}")
        return issues

    for k in CODE_REQUIRED:
        if k not in meta:
            err(f"meta.json: missing '{k}'")
    for f in ("problem.md", "starter.java", "Harness.java"):
        if not (pdir / f).exists():
            err(f"missing file {f}")
    ref = sorted((pdir / "reference").glob("*.java")) if (pdir / "reference").is_dir() else []
    if not ref:
        err("missing reference/<Class>.java (your own correct solution, used to prove the tests are fair)")
    for t in meta.get("tests", []):
        for k in TEST_KEYS:
            if k not in t:
                err(f"test '{t.get('id')}': missing '{k}'")
        if "fail_why_en" not in t or "fail_how_en" not in t:
            issues.append(("WARN", f"test '{t.get('id')}': no fail_why_en/fail_how_en (English users will see the Spanish text)"))
    es = pdir / "problem.es.md"
    if not es.exists():
        issues.append(("WARN", "no problem.es.md: the 'translate to Spanish' help will be unavailable for this problem"))
    elif (pdir / "problem.md").exists():
        a, b = blocks((pdir / "problem.md").read_text()), blocks(es.read_text())
        if len(a) != len(b):
            issues.append(("WARN", f"problem.md has {len(a)} blocks and problem.es.md has {len(b)}: hover translation needs the same structure"))

    if run and not issues_have_error(issues) and ref:
        os.environ.setdefault("ILAB_HOME", str(Path(tempfile.gettempdir()) / "ilab-validate"))
        try:
            rep = G.grade(pdir.name, ref[0], lang="en")
            if not rep["compile"]["ok"]:
                err("reference solution does not compile:\n" + rep["compile"]["message"])
            else:
                bad = [t for t in rep["tests"] if not t["passed"]]
                for t in bad:
                    err(f"reference solution fails test '{t['id']}': {t['detail']}")
            starter = G.grade(pdir.name, pdir / "starter.java", lang="en")
            if starter["score"] == starter["max"]:
                err("the starter template already scores 100%: tests are too weak")
        except Exception as e:
            err(f"could not run the grader: {e}")
    return issues


def issues_have_error(issues):
    return any(level == "ERROR" for level, _ in issues)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run = "--no-run" not in sys.argv
    if run and not (G.shutil.which("javac") and G.shutil.which("java")):
        print("JDK 21 not found: running with --no-run")
        run = False
    dirs = []
    for base in G.PROBLEM_DIRS:
        if base.is_dir():
            dirs += [d for d in sorted(base.iterdir()) if (d / "meta.json").exists()]
    if args:
        dirs = [d for d in dirs if d.name in args]
        if not dirs:
            print("no matching problem")
            return 2
    errors = warns = 0
    for d in dirs:
        issues = validate(d, run)
        e = sum(1 for lv, _ in issues if lv == "ERROR")
        w = sum(1 for lv, _ in issues if lv == "WARN")
        errors += e; warns += w
        print(f"{'FAIL' if e else 'ok  '} {d.name}" + (f"  ({e} errors, {w} warnings)" if issues else ""))
        for lv, msg in issues:
            print(f"     {lv}: {msg}")
    print(f"\n{len(dirs)} problems, {errors} errors, {warns} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
