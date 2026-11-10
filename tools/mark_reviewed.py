#!/usr/bin/env python3
"""Record that a HUMAN reviewed questions against their sources (MUST-HAVE review workflow).

    python3 tools/mark_reviewed.py --file packs/NAME/questions/sql.json --reviewer "Your Name" --all
    python3 tools/mark_reviewed.py --file bank/questions/qa.json --reviewer "Your Name" --ids qa-001,qa-002
    python3 tools/mark_reviewed.py --file ... --reviewer "Your Name" --ids sql-007 --status draft   # undo / send back to draft

If the questions belong to a pack that has an authoring/ folder, the decision is also stored in the pack's reviews.json
so rebuilding the pack from authoring/*.py does not lose it. Never run this on questions you did not actually check.
"""
import argparse
import json
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--ids", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--status", default="reviewed", choices=["reviewed", "draft"])
    a = ap.parse_args()
    f = Path(a.file)
    items = json.loads(f.read_text())
    wanted = {x.strip() for x in a.ids.split(",") if x.strip()}
    if not a.all and not wanted:
        ap.error("pass --all or --ids")
    changed = []
    for q in items:
        if a.all or q["id"] in wanted:
            rv = q.setdefault("review", {})
            rv["status"] = a.status
            if a.status == "reviewed":
                rv.update({"reviewer": a.reviewer, "reviewed_on": time.strftime("%Y-%m-%d")})
            else:
                rv.pop("reviewer", None)
                rv.pop("reviewed_on", None)
            changed.append(q["id"])
    missing = wanted - {q["id"] for q in items}
    if missing:
        raise SystemExit(f"unknown ids: {sorted(missing)}")
    f.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n")
    pack = f.resolve().parent.parent
    if (pack / "authoring").is_dir():                       # keep the decision across rebuilds
        rf = pack / "reviews.json"
        store = json.loads(rf.read_text()) if rf.exists() else {}
        for q in items:
            if q["id"] in changed:
                store[q["id"]] = {k: q["review"].get(k) for k in ("status", "reviewer", "reviewed_on")}
        rf.write_text(json.dumps(store, indent=1, sort_keys=True) + "\n")
    print(f"{len(changed)} question(s) set to '{a.status}' in {f}")


if __name__ == "__main__":
    main()
