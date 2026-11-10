#!/usr/bin/env python3
"""Interview Lab setup helper: see which runtimes (languages and tools) you have and install the ones you choose.

    python3 install.py list                         # what is installed on this machine
    python3 install.py install --lang python       # show the exact commands, ask for confirmation, then run them
    python3 install.py install --lang python --dry-run

Design (ADR-0019): installing software is a deliberate action done HERE, at setup time, by you. The web app never
installs anything. Commands come only from the audited registry in runtimes/*.json (no shell, no downloads of scripts),
are always printed first, and nothing runs without you typing "yes". You are responsible for what you install.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from interview_lab.adapters.runtimes import detect, load_registry  # noqa: E402


def package_manager():
    if sys.platform == "darwin" and shutil.which("brew"):
        return "brew", ["brew", "install"]
    if shutil.which("apt-get"):
        return "apt", ["sudo", "apt-get", "install", "-y"] if os.geteuid() != 0 else ["apt-get", "install", "-y"]
    return None, None


def cmd_list(reg):
    print(f"{'runtime':<12} {'kind':<9} {'installed':<10} {'version':<14} grader")
    for r in reg:
        st = detect(r)
        print(f"{r['id']:<12} {r.get('kind', 'language'):<9} {'yes' if st['installed'] else 'no':<10} {(st['version'] or '-'):<14} {'yes' if r.get('grader') else 'not yet'}")
    print("\nInstall one with:  python3 install.py install --lang <id>")


def cmd_install(reg, lang, dry_run, assume_yes):
    r = next((x for x in reg if x["id"] == lang), None)
    if not r:
        raise SystemExit(f"unknown runtime {lang!r}; run `python3 install.py list`")
    st = detect(r)
    if st["installed"]:
        print(f"{r['name']} is already installed (version {st['version'] or 'unknown'}). Nothing to do.")
        return 0
    manager, base = package_manager()
    pkgs = (r.get("install") or {}).get(manager or "", [])
    print(f"{r['name']} is not installed.")
    if not manager or not pkgs:
        print(f"No supported package manager found (apt or Homebrew). Install it yourself: {(r.get('install') or {}).get('docs', '')}")
        return 1
    cmd = base + pkgs
    print(f"\nThis would run (from the audited registry, no shell):\n    {' '.join(cmd)}\n")
    print(f"Official instructions: {(r.get('install') or {}).get('docs', '')}")
    if dry_run:
        print("\n--dry-run: nothing was run.")
        return 0
    if os.geteuid() == 0 and not assume_yes:
        print("Running as root: only continue if you understand what is installed.")
    if not assume_yes:
        if input("Type 'yes' to run it: ").strip().lower() != "yes":
            print("Cancelled. Nothing was installed.")
            return 1
    rc = subprocess.run(cmd).returncode              # no shell; the user sees the real package-manager output
    st = detect(r)
    print(f"\n{'OK' if st['installed'] else 'Not detected yet'}: {r['name']} {st['version'] or ''}".rstrip())
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    i = sub.add_parser("install")
    i.add_argument("--lang", required=True, help="runtime id from `list` (python, javascript, pdftotext, ...)")
    i.add_argument("--dry-run", action="store_true")
    i.add_argument("--yes", action="store_true", help="skip the confirmation prompt (you still own the consequences)")
    a = ap.parse_args()
    reg = load_registry(ROOT)
    if a.cmd == "list":
        return cmd_list(reg)
    return cmd_install(reg, a.lang, a.dry_run, a.yes)


if __name__ == "__main__":
    sys.exit(main() or 0)
