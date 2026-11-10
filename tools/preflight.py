#!/usr/bin/env python3
"""Pre-publication guard. Run before every push (a local git hook can call it) and in CI.

Git history is permanent, so this checks BOTH the tracked files and every commit's file names:
  * premium/private content must never be committed (`packs/`, personal `workspace/` data, `.env`);
  * no secrets, no personal paths, no oversized files.

Exit code 0 = safe to push, 1 = something to fix first.   Usage: python3 tools/preflight.py [--no-history]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_PREFIXES = ("packs/", "workspace/")          # exceptions listed in ALLOWED_PATHS
ALLOWED_PATHS = {"packs/README.md", "workspace/README.md"}
FORBIDDEN_NAMES = (".env", "id_rsa", "id_ed25519")
MAX_BYTES = 2_000_000
SECRET = re.compile(r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,}|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|xox[baprs]-|AIza[0-9A-Za-z_-]{20,}")
PERSONAL = re.compile(r"/home/[a-z][a-z0-9_-]+/|/Users/[A-Za-z][A-Za-z0-9._-]+/|collaboration-mx|lightsail")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}")
EMAIL_OK = re.compile(r"@(example\.(com|org)|b\.com|users\.noreply\.github\.com)$|^noreply@anthropic\.com$|^security@|^conduct@")
SELF = "tools/preflight.py"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def bad_path(p: str) -> bool:
    if p in ALLOWED_PATHS:
        return False
    return p.startswith(FORBIDDEN_PREFIXES) or Path(p).name in FORBIDDEN_NAMES


def main(argv: list) -> int:
    problems = []
    tracked = [p for p in git("ls-files").split("\n") if p]
    for p in tracked:
        if bad_path(p):
            problems.append(f"tracked private path: {p}")
        f = ROOT / p
        if not f.is_file():
            continue
        if f.stat().st_size > MAX_BYTES:
            problems.append(f"file over {MAX_BYTES // 1000} KB: {p}")
        if p == SELF or f.suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".class", ".jar"}:
            continue
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        if '"license": "proprietary"' in text and p.endswith("pack.json"):
            problems.append(f"premium pack manifest is tracked: {p}")
        for m in SECRET.finditer(text):
            problems.append(f"possible secret in {p}: {m.group(0)[:12]}…")
        for m in PERSONAL.finditer(text):
            if not p.startswith("tests/"):
                problems.append(f"personal path/host in {p}: {m.group(0)}")
        for m in EMAIL.finditer(text):
            if not EMAIL_OK.search(m.group(0)) and not p.startswith("tests/"):
                problems.append(f"unexpected e-mail in {p}: {m.group(0)}")
    if "--no-history" not in argv:
        has_commits = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=ROOT, capture_output=True).returncode == 0
        if has_commits:
            for p in sorted(set(git("log", "--all", "--name-only", "--pretty=format:").split("\n")) - {""}):
                if bad_path(p):
                    problems.append(f"private path exists in HISTORY: {p}  (history is permanent: rewrite before publishing)")
    if problems:
        print("PREFLIGHT FAILED — do not push:")
        for x in sorted(set(problems)):
            print("  ✗", x)
        return 1
    print(f"preflight ok: {len(tracked)} tracked files, no premium/private content, no secrets, no personal paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
