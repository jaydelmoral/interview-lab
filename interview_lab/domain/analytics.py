"""DOMAIN: pure analytics over finished exam runs and code attempts. No I/O, no SQL: easy to test.

Input shapes (produced by a HistoryRepository, oldest first):
  run     = {id, exam_id, finished_at 'YYYY-MM-DD HH:MM:SS', title, seniority, language, version, overall_pct,
             total_minutes, used_minutes, sections: [{module, title, pct, correct, total, used_min, allotted_min}],
             missed: [{section, question, expected, explanation, tags: [str]}]}
  attempt = {problem_id, kind 'code'|'quiz', attempted_at, score, max, passed, total}
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

PASS_LINE = 60.0
SERIES_LEN = 12


def _mean(xs: list) -> Optional[float]:
    return sum(xs) / len(xs) if xs else None


def _round(x: Optional[float], n: int = 1) -> Optional[float]:
    return None if x is None else round(x, n)


def delta(series: list) -> Optional[float]:
    """Last value minus the mean of the (up to 3) values before it. None with fewer than two values."""
    if len(series) < 2:
        return None
    return _round(series[-1] - _mean(series[-4:-1]))


def streak_days(days: set, today: Optional[date] = None) -> int:
    """Consecutive days with any activity, counting back from today (or from yesterday if today has none yet)."""
    today = today or date.today()
    cur = today if today.isoformat() in days else today - timedelta(days=1)
    n = 0
    while cur.isoformat() in days:
        n += 1
        cur -= timedelta(days=1)
    return n


def summarize(runs: list, attempts: list, today: Optional[date] = None) -> dict:
    overall = [r["overall_pct"] for r in runs]
    days = {r["finished_at"][:10] for r in runs} | {a["attempted_at"][:10] for a in attempts}

    # ---- per module
    by_mod: dict = {}
    for r in runs:
        for s in r["sections"]:
            m = by_mod.setdefault(s["module"], {"module": s["module"], "title": s["title"] or s["module"], "series": [], "used": [], "allotted": []})
            m["title"] = s["title"] or m["title"]
            m["series"].append(s["pct"])
            if s.get("allotted_min"):
                m["used"].append(s.get("used_min") or 0)
                m["allotted"].append(s["allotted_min"])
    modules = []
    for m in by_mod.values():
        modules.append({"module": m["module"], "title": m["title"], "runs": len(m["series"]), "avg": _round(_mean(m["series"])),
                        "last": _round(m["series"][-1]), "best": _round(max(m["series"])), "delta": delta(m["series"]),
                        "series": [_round(x) for x in m["series"][-SERIES_LEN:]],
                        "avg_used": _round(_mean(m["used"])), "avg_allotted": _round(_mean(m["allotted"]))})
    modules.sort(key=lambda m: m["avg"])                          # weakest first

    # ---- weak topics (tags of missed questions)
    tags: dict = {}
    for r in runs:
        for q in r["missed"]:
            for t in q.get("tags") or []:
                e = tags.setdefault(t, {"tag": t, "count": 0, "last_seen": ""})
                e["count"] += 1
                e["last_seen"] = max(e["last_seen"], r["finished_at"][:10])
    weak = sorted(tags.values(), key=lambda e: (-e["count"], e["tag"]))[:10]

    # ---- code / quiz practice per problem
    probs: dict = {}
    for a in attempts:
        pct = round(100 * a["score"] / a["max"], 1) if a["max"] else 0.0
        p = probs.setdefault(a["problem_id"], {"problem": a["problem_id"], "kind": a["kind"], "attempts": 0, "best": 0.0, "first": pct, "last": pct, "last_at": ""})
        p["attempts"] += 1
        p["best"] = max(p["best"], pct)
        p["last"], p["last_at"] = pct, a["attempted_at"]
    code = sorted(probs.values(), key=lambda p: p["last_at"], reverse=True)
    for p in code:
        p["improved"] = _round(p["last"] - p["first"]) if p["attempts"] > 1 else None

    recent = [{"id": r["id"], "title": r["title"] or r["exam_id"], "finished_at": r["finished_at"], "overall": _round(r["overall_pct"]),
               "seniority": r["seniority"], "language": r["language"], "version": r["version"],
               "sections_passed": sum(1 for s in r["sections"] if s["pct"] >= PASS_LINE), "sections_total": len(r["sections"])}
              for r in reversed(runs[-10:])]

    return {
        "kpis": {"runs": len(runs), "avg_overall": _round(_mean(overall)), "best_overall": _round(max(overall)) if overall else None,
                 "last_overall": _round(overall[-1]) if overall else None, "delta": delta(overall),
                 "minutes_used": _round(sum(r["used_minutes"] or 0 for r in runs)), "attempts": len(attempts),
                 "active_days": len(days), "streak_days": streak_days(days, today)},
        "trend": [{"id": r["id"], "when": r["finished_at"], "overall": _round(r["overall_pct"]), "title": r["title"] or r["exam_id"]} for r in runs[-30:]],
        "modules": modules, "weak_tags": weak, "code": code[:20], "recent": recent, "pass_line": PASS_LINE,
    }
