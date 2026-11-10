#!/usr/bin/env python3
"""Interview Lab grader / Calificador de Interview Lab.

Usage / Uso:
    python3 grader/grade.py <problem-id> <solution.java> [--json] [--lang es|en]

Compiles the solution together with the problem's hidden Harness, runs every test in its own process
(with a time limit) and prints a report: what failed, why, and how to improve.
Compila la solución con el Harness oculto, ejecuta cada prueba en su propio proceso y entrega un reporte.

WARNING: the submitted code runs on this machine. Use the Docker image (see README) if you grade code you did not write.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("ILAB_HOME", ROOT / "workspace")).resolve()
PROBLEM_DIRS = [ROOT / "problems", HOME / "problems"]  # built-in first, then yours
RUNS = HOME / "runs"
MAX_DETAIL = 400


def problem_dir(problem_id: str) -> Path:
    for base in PROBLEM_DIRS:
        if (base / problem_id / "meta.json").exists():
            return base / problem_id
    raise FileNotFoundError(f"problem not found: {problem_id}")


def clean_env(tmp: Path) -> dict:
    """Minimal environment for the code under test: it must not see your tokens or API keys."""
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp), "LANG": "C.UTF-8",
            "JAVA_TOOL_OPTIONS": "-Djava.io.tmpdir=" + str(tmp)}


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


def compile_java(workdir: Path):
    proc = subprocess.run(
        ["javac", "-d", str(workdir / "out")] + sorted(str(f) for f in workdir.glob("*.java")),
        capture_output=True, text=True, timeout=60, cwd=workdir, env=clean_env(workdir), stdin=subprocess.DEVNULL,
    )
    msg = (proc.stderr or proc.stdout).strip().replace(str(workdir) + "/", "")
    return proc.returncode == 0, msg


def run_test(workdir: Path, test_id: str, timeout_ms: int, lang: str):
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            ["java", "-Xmx256m", "-Xss1m", f"-Dilab.lang={lang}", "-cp", str(workdir / "out"), "Harness", test_id],
            capture_output=True, text=True, timeout=timeout_ms / 1000, cwd=workdir, env=clean_env(workdir),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "ms": int((time.monotonic() - t0) * 1000),
                "detail": (f"TIMEOUT: exceeded {timeout_ms} ms" if lang == "en" else f"TIMEOUT: superó {timeout_ms} ms")}
    ms = int((time.monotonic() - t0) * 1000)
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            parts = line.split(" ", 4)
            verdict = parts[3] if len(parts) > 3 else "FAIL"
            rest = parts[4] if len(parts) > 4 else ""
            return {"passed": verdict == "PASS", "ms": ms, "detail": rest[:MAX_DETAIL]}
    msg = (proc.stderr.strip()[:200] or ("no output" if lang == "en" else "sin salida"))
    return {"passed": False, "ms": ms,
            "detail": ("No result (did the JVM fail?): " if lang == "en" else "Sin resultado (¿falló la JVM?): ") + msg}


def grade(problem_id: str, solution: Path, lang: str = "es"):
    lang = "en" if lang == "en" else "es"
    pdir = problem_dir(problem_id)
    meta = json.loads((pdir / "meta.json").read_text())
    source = solution.read_text()
    report = {"problem": problem_id, "title": meta["title"], "solution": str(solution), "lang": lang,
              "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "compile": {}, "tests": [], "score": 0, "max": 0}

    with tempfile.TemporaryDirectory(prefix="ilab-") as tmp:
        work = Path(tmp)
        (work / (meta.get("class", "A") + ".java")).write_text(source)
        for name in meta.get("support", ["Harness.java"]):
            shutil.copy(pdir / name, work / name)
        for common in (ROOT / "grader" / "common").glob("*.java"):
            shutil.copy(common, work / common.name)
        ok, msg = compile_java(work)
        report["compile"] = {"ok": ok, "message": msg}
        clean = strip_comments(source)
        static = meta.get("static_checks", {})
        for t in meta["tests"]:
            report["max"] += t["points"]
            why = t.get("fail_why_en") if lang == "en" and t.get("fail_why_en") else t["fail_why"]
            how = t.get("fail_how_en") if lang == "en" and t.get("fail_how_en") else t["fail_how"]
            entry = {"id": t["id"], "title": t["title"], "category": t["category"], "points": t["points"],
                     "fail_why": why, "fail_how": how}
            if t["id"] in static:
                rule = static[t["id"]]
                if isinstance(rule, str):
                    passed = bool(re.search(rule, clean))
                else:  # {"forbid": regex}: pasa si el patrón NO aparece
                    passed = not re.search(rule["forbid"], clean)
                entry.update(passed=passed, ms=0, detail=("static check of the source code" if lang == "en" else "chequeo estático del código fuente"))
            elif not ok:
                entry.update(passed=False, ms=0, detail=("Does not compile" if lang == "en" else "No compila"))
            else:
                entry.update(run_test(work, t["id"], meta.get("timeout_ms", 3000), lang))
            if entry["passed"]:
                report["score"] += t["points"]
            report["tests"].append(entry)
    return report


TXT = {
    "es": {"result": "Resultado", "score": "Puntaje", "compile": "Error de compilación",
           "compile_hint": "Una solución que no compila vale 0. Lee el primer error: indica línea y causa.",
           "tests": "Pruebas", "detail": "Detalle", "failed": "En qué fallaste y cómo mejorar", "why": "Por qué falló",
           "how": "Cómo mejorar", "allok": "Todo pasó",
           "next": "Ahora explica tu solución en voz alta, en inglés, en 60 segundos: qué hace, su complejidad (Big O) y qué casos borde cubriste."},
    "en": {"result": "Result", "score": "Score", "compile": "Compilation error",
           "compile_hint": "A solution that does not compile scores 0. Read the first error: it gives the line and the cause.",
           "tests": "Tests", "detail": "Detail", "failed": "What failed and how to improve", "why": "Why it failed",
           "how": "How to improve", "allok": "Everything passed",
           "next": "Now explain your solution out loud, in 60 seconds: what it does, its complexity (Big O) and which edge cases you covered."},
}


def to_markdown(r) -> str:
    x = TXT[r.get("lang", "es")]
    pct = round(100 * r["score"] / r["max"]) if r["max"] else 0
    out = [f"# {x['result']}: {r['title']}", "", f"**{x['score']}: {r['score']}/{r['max']} ({pct}%)**", ""]
    if not r["compile"]["ok"]:
        out += [f"## {x['compile']}", "```", r["compile"]["message"], "```", "", x["compile_hint"], ""]
    out += [f"## {x['tests']}", ""]
    for t in r["tests"]:
        mark = "✅" if t["passed"] else "❌"
        out.append(f"- {mark} **{t['category']}** · {t['title']} (+{t['points']} pts, {t['ms']} ms)")
        if not t["passed"]:
            out.append(f"  - {x['detail']}: {t['detail']}")
    failed = [t for t in r["tests"] if not t["passed"]]
    if failed:
        out += ["", f"## {x['failed']}", ""]
        for t in failed:
            out += [f"### ❌ {t['title']}", f"- **{x['why']}:** {t['fail_why']}", f"- **{x['how']}:** {t['fail_how']}", ""]
    else:
        out += ["", f"## {x['allok']}", x["next"], ""]
    return "\n".join(out)


def main():
    argv = sys.argv[1:]
    lang = "es"
    if "--lang" in argv:
        i = argv.index("--lang")
        lang = argv[i + 1] if i + 1 < len(argv) else "es"
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    if not shutil.which("javac") or not shutil.which("java"):
        print("ERROR: JDK not found (javac/java). Install JDK 21 or use Docker. / No hay JDK 21: instálalo o usa Docker.")
        sys.exit(3)
    report = grade(args[0], Path(args[1]), lang=lang)
    RUNS.mkdir(parents=True, exist_ok=True)
    with open(RUNS / "results.jsonl", "a") as f:
        f.write(json.dumps({k: report[k] for k in ("timestamp", "problem", "score", "max")}) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2) if "--json" in sys.argv else to_markdown(report))


if __name__ == "__main__":
    main()
