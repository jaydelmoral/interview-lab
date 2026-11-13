"""APPLICATION: use cases. Orchestrate domain rules and ports; contain no HTTP, no file paths and no JVM details."""
from __future__ import annotations

import base64
import hashlib
import logging
import threading
import time
from pathlib import Path

from ..domain import analytics
from ..domain import exam as rules
from ..domain import profile
from .errors import Forbidden, InvalidRequest, NotFound, Unprocessable
from .ports import FetchError, GenerationError

log = logging.getLogger("interview_lab")
PROFILE = "local"          # single-user edition; every history row already carries a profile id


def _num(x, lo: float, hi: float, default=None):
    """Untrusted client number -> clamped float, or `default` when it is not a number."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return default
    return max(lo, min(hi, float(x)))


def _txt(x, n: int) -> str:
    return str(x if x is not None else "")[:n]


GRACE_SECONDS = 15.0       # network/auto-submit slack after a section's deadline, before it is closed "as it was left"
MAX_SECTIONS = 30


def _clean_config(cfg: dict) -> dict:
    """Untrusted exam preferences -> the types the domain rules expect. Wrong types fall back to defaults, never to a 500."""
    text = lambda v, default="": v if isinstance(v, str) else default    # noqa: E731
    counts = cfg.get("counts") if isinstance(cfg.get("counts"), dict) else {}
    return {"seniority": text(cfg.get("seniority")), "language": text(cfg.get("language")).strip().lower()[:20] or "java",
            "version": cfg.get("version") if isinstance(cfg.get("version"), (int, str)) and not isinstance(cfg.get("version"), bool) else None,
            "modules": [m for m in cfg["modules"] if isinstance(m, str)], "pace": text(cfg.get("pace"), "standard") or "standard",
            "banks": [b for b in (cfg.get("banks") if isinstance(cfg.get("banks"), list) else []) if isinstance(b, str)][:50],
            "counts": {k: min(v, 200) for k, v in counts.items() if isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool)},
            "title": text(cfg.get("title"))}


def _clean_section(x: dict) -> dict:
    pct = _num(x.get("pct"), 0, 100, 0.0)
    return {"module": _txt(x.get("module"), 30), "title": _txt(x.get("title") or x.get("module"), 80), "pct": round(pct, 2),
            "correct": int(_num(x.get("correct"), 0, 100000, 0)), "total": int(_num(x.get("total"), 0, 100000, 0)),
            "used_min": _num(x.get("used"), 0, 10000), "allotted_min": _num(x.get("allotted"), 0, 10000)}


def _clean_missed(m: dict) -> dict:
    tags = [_txt(t, 40) for t in (m.get("tags") if isinstance(m.get("tags"), list) else [])[:6] if isinstance(t, str)]
    return {"section": _txt(m.get("section"), 80), "question": _txt(m.get("q") or m.get("question"), 400),
            "expected": _txt(m.get("expected"), 400), "explanation": _txt(m.get("explanation"), 600), "tags": tags}


# ------------------------------------------------------------------ profile analysis
class AnalysisService:
    """Use case: understand a CV or a job description. Nothing is stored."""

    def __init__(self, pdf=None):
        self.pdf = pdf                                       # optional PdfExtractor port (text from PDF files)

    def analyze(self, text=None, filename: str = "", data_b64=None) -> dict:
        try:
            if data_b64 is not None:
                raw = base64.b64decode(data_b64, validate=True)
                name = filename.lower()
                if name.endswith(".docx"):
                    text = profile.docx_text(raw)
                elif name.endswith((".txt", ".md")):
                    text = raw.decode("utf-8", "replace")
                elif name.endswith(".pdf"):
                    if not self.pdf:
                        raise InvalidRequest("PDF support is not enabled; paste the text instead")
                    try:
                        text = self.pdf.extract(raw)
                    except FetchError as e:
                        raise InvalidRequest(str(e)) from e
                else:
                    raise InvalidRequest("unsupported file: use .txt, .md, .docx or .pdf (PDF needs pdftotext), or paste the text")
        except InvalidRequest:
            raise
        except Exception as e:
            raise InvalidRequest("could not read the file") from e
        if not isinstance(text, str) or not text.strip():
            raise InvalidRequest("no text to analyze")
        return profile.analyze(text)


# ------------------------------------------------------------------ exams
class ExamService:
    def __init__(self, catalog, exams, attempts, history=None, problems=None, clock=time.time):
        self.catalog, self.exams, self.history = catalog, exams, history
        self.attempts, self.problems = attempts, problems     # attempt state lives on the server: every exam call needs an attempt id
        self.clock = clock                                    # the server's clock is the only one that counts; injectable for tests
        self._lock = threading.Lock()                         # serializes read-modify-write of attempt state

    def modules(self, lang: str, fetch_enabled: bool, ai_enabled: bool) -> dict:
        counts = self.catalog.counts()
        return {"modules": [{"id": m, "title": rules.pick(rules.TITLES[m], lang), "count": counts.get(m, 0)} for m in rules.MODULE_ORDER],
                "coming": [{"id": "ai", "title": "IA / LLMs"}], "fetch": fetch_enabled, "ai": ai_enabled}

    def create(self, cfg: dict, lang: str) -> dict:
        if not isinstance(cfg.get("modules"), list) or not cfg["modules"]:
            raise InvalidRequest("choose at least one module")
        exam = rules.build(_clean_config(cfg), self.catalog.candidates())
        if not exam["sections"]:
            raise Unprocessable("nothing to build with those filters",
                                {"notes": [{"module": n["module"], "text": rules.pick(n, lang)} for n in exam["notes"]]})
        self.exams.save(exam)
        return rules.public_exam(exam, self.catalog.resolve, lang)

    def _load(self, exam_id: str) -> dict:
        exam = self.exams.load(exam_id)
        if not exam:
            raise NotFound("exam not found")
        return exam

    def get_public(self, exam_id: str, lang: str) -> dict:
        return rules.public_exam(self._load(exam_id), self.catalog.resolve, lang)

    # ---- attempts: the server keeps what it graded, so the final result never depends on client-reported scores
    @staticmethod
    def _attempt(attempt) -> str:
        """The attempt id of an exam call. It is mandatory: without it the server could not keep the clock or grade anything itself."""
        if not rules.valid_attempt(attempt):
            raise InvalidRequest("a valid attempt id is required")
        return attempt

    def _state(self, exam_id: str, attempt: str) -> dict:
        state = self.attempts.load(exam_id, attempt) or {}
        for k, empty in (("sections", {}), ("code", {}), ("finished", None), ("started", {}), ("closed", {}), ("draft", {})):
            state.setdefault(k, empty)                       # section number -> value; older files may lack the timing parts
        return state

    @staticmethod
    def _deadline(exam: dict, state: dict, idx: int):
        """Server time at which the section ends, or None if it was never started."""
        start = state["started"].get(str(idx))
        return None if start is None else start + exam["sections"][idx]["minutes"] * 60

    def _open_section(self, exam: dict, state: dict, idx: int) -> float:
        """Deadline of a section that must be running (started, not closed, within the grace period); else InvalidRequest."""
        deadline = self._deadline(exam, state, idx)
        if str(idx) in state["closed"]:
            raise InvalidRequest("this section is already closed")
        if deadline is None:
            raise InvalidRequest("section not started")
        if self.clock() > deadline + GRACE_SECONDS:
            raise InvalidRequest("the time for this section is over")
        return deadline

    def start_section(self, exam_id: str, idx, attempt) -> dict:
        """Starts the clock of a section (once: asking again after a reload returns the same deadline) and says how much time is left.
        `expired` means time is up (or the section was already closed): the caller must close it with /section."""
        exam = self._load(exam_id)
        attempt = self._attempt(attempt)
        if not isinstance(idx, int) or isinstance(idx, bool) or not 0 <= idx < len(exam["sections"]):
            raise InvalidRequest("invalid request")
        with self._lock:
            state = self._state(exam["id"], attempt)
            if state["finished"]:
                raise InvalidRequest("this attempt is already finished")
            now = self.clock()
            if str(idx) not in state["started"]:
                state["started"][str(idx)] = now
                self.attempts.save(exam["id"], attempt, state)
            deadline = self._deadline(exam, state, idx)
            closed = str(idx) in state["closed"]
            return {"section": idx, "minutes": exam["sections"][idx]["minutes"], "remaining_ms": max(0, int((deadline - now) * 1000)),
                    "expired": closed or now >= deadline, "closed": closed}

    def save_answers(self, exam_id: str, idx, answers, attempt) -> dict:
        """Keeps the latest answers of a running section on the server: if the time runs out, the section is graded with them."""
        exam = self._load(exam_id)
        attempt = self._attempt(attempt)
        if not isinstance(idx, int) or isinstance(idx, bool) or not 0 <= idx < len(exam["sections"]) or not isinstance(answers, dict):
            raise InvalidRequest("invalid request")
        with self._lock:
            state = self._state(exam["id"], attempt)
            if state["finished"]:
                raise InvalidRequest("this attempt is already finished")
            self._open_section(exam, state, idx)
            state["draft"][str(idx)] = rules.clean_answers(exam["sections"][idx], answers)
            self.attempts.save(exam["id"], attempt, state)
        return {"saved": True}

    def _grade(self, exam: dict, idx: int, answers: dict, lang: str) -> dict:
        report = rules.grade_section(exam, idx, answers, self.catalog.resolve, lang)
        report["weak"] = rules.weak_tags(report["items"])
        return report

    def grade_section(self, exam_id: str, idx, answers, lang: str, attempt) -> dict:
        exam = self._load(exam_id)
        if not isinstance(idx, int) or isinstance(idx, bool) or not 0 <= idx < len(exam["sections"]) or not isinstance(answers, dict):
            raise InvalidRequest("invalid request")
        attempt = self._attempt(attempt)
        answers = rules.clean_answers(exam["sections"][idx], answers)      # what is graded is also stored: keep only what grading understands
        with self._lock:
            state = self._state(exam["id"], attempt)
            key = str(idx)
            if state["finished"]:
                raise InvalidRequest("this attempt is already finished")
            if key in state["sections"]:                     # graded once per section and attempt: asking again returns the first report
                return state["sections"][key]
            deadline = self._deadline(exam, state, idx)
            if deadline is None:
                raise InvalidRequest("section not started")
            now = self.clock()
            if now > deadline + GRACE_SECONDS:               # too late to trust what the browser says now: close the section as it was left
                answers = state["draft"].get(key, {})
            report = state["sections"][key] = self._grade(exam, idx, answers, lang) | {"answers": answers}   # the page shows exactly what was graded
            state["closed"][key] = min(now, deadline)
            self.attempts.save(exam["id"], attempt, state)
            return report

    def code_target(self, exam_id, attempt, problem):
        """Checks a code submission that claims to belong to an exam attempt. Returns (exam id, attempt, item key, section index),
        or None when it is plain free practice (neither an exam nor an attempt is named). Naming only one of them is an error."""
        if exam_id is None and attempt is None:
            return None
        attempt = self._attempt(attempt)
        if not isinstance(exam_id, str):
            raise InvalidRequest("an attempt belongs to an exam")
        exam = self._load(exam_id)
        found = [(i, r) for i, s in enumerate(exam["sections"]) for r in s["items"] if r["t"] == "code" and r.get("id") == problem]
        if not found:
            raise InvalidRequest("that exercise is not part of this exam")
        with self._lock:
            state = self._state(exam["id"], attempt)
            if state["finished"]:
                raise InvalidRequest("this attempt is already finished")
            self._open_section(exam, state, found[0][0])      # the exercise's section must be running: no grading after time is up
        return exam["id"], attempt, rules.item_key(found[0][1]), found[0][0]

    def record_code(self, target: tuple, report: dict) -> None:
        """Keeps the best graded score of each exercise of the attempt."""
        exam_id, attempt, key, idx = target
        tests = report.get("tests") or []
        with self._lock:
            state = self._state(exam_id, attempt)
            prev = state["code"].get(key)
            if state["finished"] or str(idx) in state["closed"] or (prev and report["score"] <= prev["score"]):
                return                                        # a grade that lands after its section was closed is not counted
            state["code"][key] = {"score": int(report["score"]), "max": int(report["max"]),
                                  "passed": sum(1 for t in tests if t.get("passed")), "total": len(tests)}
            self.attempts.save(exam_id, attempt, state)

    def _points(self, section: dict) -> dict:
        """problem id -> (max points, number of tests), from the problem definitions."""
        out = {}
        for ref in section["items"]:
            meta = self.problems.meta(ref.get("id")) if self.problems else None
            tests = (meta or {}).get("tests") or []
            out[ref.get("id")] = (sum(t.get("points", 0) for t in tests), len(tests))
        return out

    def finish(self, exam_id: str, sections, attempt, lang: str = "es") -> dict:
        """The client only says WHICH sections it finished; scores, totals, missed questions and the time used
        come from what the server graded and timed. Finishing twice returns the stored result, so a retry is harmless."""
        exam = self._load(exam_id)
        attempt = self._attempt(attempt)
        n = len(exam["sections"])
        if (not isinstance(sections, list) or not 0 < len(sections) <= MAX_SECTIONS
                or not all(isinstance(x, dict) and isinstance(x.get("section"), int) and not isinstance(x["section"], bool) and 0 <= x["section"] < n for x in sections)
                or len({x["section"] for x in sections}) != len(sections)):
            raise InvalidRequest("invalid request")
        with self._lock:
            state = self._state(exam["id"], attempt)
            if state["finished"]:
                return state["finished"]
            secs, missed = [], []
            for x in sorted(sections, key=lambda x: x["section"]):
                section = exam["sections"][x["section"]]
                key, deadline = str(x["section"]), self._deadline(exam, state, x["section"])
                if deadline is not None and key not in state["closed"]:
                    state["closed"][key] = min(self.clock(), deadline)       # finishing closes any section still open (e.g. a code section)
                title = _txt(x.get("title"), 80) or rules.pick(section["title"], lang)
                if rules.is_code_section(section):
                    res = rules.code_result(section, state["code"], self._points(section))
                else:                                        # never graded = nothing answered
                    report = state["sections"].get(str(x["section"])) or rules.grade_section(      # never closed: grade what the server holds
                        exam, x["section"], state["draft"].get(str(x["section"]), {}), self.catalog.resolve, lang)
                    res = {"score": report["score"], "max": report["max"], "correct": report["score"], "total": report["max"]}
                    missed += rules.missed_items(exam, x["section"], report, self.catalog.resolve, title, lang)
                pct = 100.0 * res["score"] / res["max"] if res["max"] else 0.0
                secs.append({"module": section["module"], "title": title, "score": round(pct), "max": 100, "pct": round(pct, 1),
                             "correct": res["correct"], "total": res["total"], "allotted": section["minutes"],
                             "used": self._used_minutes(exam, state, x["section"])})
            state["finished"] = self._store_run(exam, secs, missed)
            self.attempts.save(exam["id"], attempt, state)
            return state["finished"]

    def _used_minutes(self, exam: dict, state: dict, idx: int) -> float:
        """Time spent in a section by the server's clock: from its start to its close (or to now/the deadline if never closed)."""
        start = state["started"].get(str(idx))
        if start is None:
            return 0.0
        end = state["closed"].get(str(idx)) or min(self.clock(), start + exam["sections"][idx]["minutes"] * 60)
        return round(max(0.0, end - start) / 60, 1)

    def _store_run(self, exam: dict, sections: list, missed) -> dict:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        rec = {"exam": exam["id"], "when": now, "score": sum(x["score"] for x in sections),
               "max": sum(x["max"] for x in sections),
               "sections": [{"module": str(x.get("module", ""))[:30], "score": x["score"], "max": x["max"]} for x in sections]}
        self.exams.record_result(rec)
        self._record_history(exam, now, sections, missed)
        return rec

    def _record_history(self, exam: dict, now: str, sections: list, missed) -> None:
        """Best effort: the long-term history must never break finishing an exam."""
        if not self.history:
            return
        try:
            secs = [_clean_section(x) for x in sections[:30]]
            cfg = exam.get("config") or {}
            self.history.record_run(PROFILE, {
                "exam_id": exam["id"], "finished_at": now, "title": exam.get("title"), "seniority": cfg.get("seniority"),
                "language": cfg.get("language"), "version": cfg.get("version"), "total_minutes": exam.get("total_minutes"),
                "overall_pct": round(sum(s["pct"] for s in secs) / len(secs), 2) if secs else 0.0,
                "used_minutes": round(sum(s["used_min"] or 0 for s in secs), 2), "sections": secs,
                "missed": [_clean_missed(m) for m in (missed if isinstance(missed, list) else [])[:200] if isinstance(m, dict)]})
        except Exception:                                    # noqa: BLE001 - deliberate: log and move on
            log.exception("could not record exam history")

    def list(self) -> list:
        results = self.exams.last_results()
        rows = []
        for e in self.exams.list():
            r = results.get(e["id"])
            rows.append({"id": e["id"], "created": e["created"], "title": e.get("title", ""), "config": e["config"],
                         "total_minutes": e["total_minutes"],
                         "last": {"score": r["score"], "max": r["max"], "when": r["when"]} if r else None})
        return rows


# ------------------------------------------------------------------ memory bank
class BankService:
    """Use case: turn links and notes into a personal question bank. Generation strategy is injected (offline or AI)."""
    MAX_URLS = 5

    def __init__(self, banks, fetcher, generator, fallback, allow_fetch: bool):
        self.banks, self.fetcher, self.generator, self.fallback, self.allow_fetch = banks, fetcher, generator, fallback, allow_fetch

    def list(self) -> list:
        return [{"id": b["id"], "title": b["title"], "created": b["created"], "items": len(b["items"]),
                 "sources": [{"url": s.get("url", ""), "title": s.get("title", "")} for s in b["sources"]]} for b in self.banks.list()]

    def delete(self, bank_id: str) -> None:
        if not self.banks.delete(bank_id):
            raise NotFound("bank not found")

    def create(self, title: str, urls: list, notes: str) -> dict:
        if urls and not self.allow_fetch:
            raise Forbidden("fetching links is disabled (ILAB_ALLOW_FETCH=0)")
        if not urls and not notes.strip():
            raise InvalidRequest("add at least one link or some notes")
        texts, errors = [], []
        for u in urls[:self.MAX_URLS]:
            try:
                t, text, heads = self.fetcher.fetch_text(u)
                texts.append((u, t or u, text, heads))
            except FetchError as e:
                errors.append({"url": u, "error": str(e)})
        if notes.strip():
            body = notes[:200_000]
            texts.append(("", "notes", body, [ln.strip("# ").strip() for ln in body.splitlines() if ln.startswith("#")][:6]))
        sources, items, warnings = [], [], []
        for url, t, text, heads in texts:
            try:
                new = self.generator.generate(t, text, heads)
            except GenerationError as e:
                warnings.append(f"{self.generator.name}: {e}; used the offline generator")
                new = self.fallback.generate(t, text, heads)
            sources.append({"url": url, "title": t, "chars": len(text), "items": len(new)})
            items += new
        seen, unique = set(), []
        for it in items:
            if it["id"] not in seen:
                seen.add(it["id"])
                unique.append(it)
        if not unique:
            raise Unprocessable("could not build questions from that material", {"errors": errors})
        bank = {"id": "b-" + hashlib.sha1((title + str(time.time())).encode()).hexdigest()[:8], "title": (title or "Mi banco")[:80],
                "created": time.strftime("%Y-%m-%d %H:%M:%S"), "sources": sources, "items": unique, "generator": self.generator.name}
        self.banks.save(bank)
        return {"id": bank["id"], "title": bank["title"], "items": len(unique), "sources": sources, "errors": errors, "warnings": warnings,
                "generator": self.generator.name}


# ------------------------------------------------------------------ free practice
class PracticeService:
    """Use cases of the free-practice screen: list/get problems, grade code on the JVM, grade the output quiz."""

    def __init__(self, problems, grader, results, attempts_dir: Path, max_code: int, history=None):
        self.problems, self.grader, self.results, self.history = problems, grader, results, history
        self.attempts_dir, self.max_code, self._lock = Path(attempts_dir), max_code, threading.Lock()   # one grading at a time

    def list(self) -> list:
        return self.problems.list_summaries()

    def get(self, pid: str, lang: str) -> dict:
        p = self.problems.public(pid, lang)
        if not p:
            raise NotFound("not found")
        return p

    def _kind(self, pid: str) -> str:
        m = self.problems.meta(pid)
        if not m:
            raise InvalidRequest("unknown problem")
        return m.get("kind", "code")

    def _log(self, report: dict, kind: str = "code") -> None:
        self.results.append({k: report[k] for k in ("timestamp", "problem", "score", "max")})
        if not self.history:
            return
        try:
            tests = report.get("tests")
            self.history.record_attempt(PROFILE, {"problem_id": report["problem"], "kind": kind, "attempted_at": report["timestamp"],
                                                  "score": report["score"], "max": report["max"],
                                                  "passed": sum(1 for t in tests if t.get("passed")) if tests is not None else report["score"],
                                                  "total": len(tests) if tests is not None else report["max"]})
        except Exception:                                    # noqa: BLE001
            log.exception("could not record attempt history")

    def grade_quiz(self, pid: str, answers, lang: str) -> dict:
        if self._kind(pid) != "quiz" or not isinstance(answers, dict):
            raise InvalidRequest("invalid request")
        results, right, qs = [], 0, self.problems.quiz_questions(pid)
        for q in qs:
            given = answers.get(q["id"], "")
            ok = rules.normalize(given) == rules.normalize(q["expected"])
            right += ok
            expl = q.get("explanation_en") if lang == "en" and q.get("explanation_en") else q["explanation"]
            results.append({"id": q["id"], "correct": ok, "given": given, "expected": q["expected"], "explanation": expl})
        report = {"problem": pid, "score": right, "max": len(qs), "results": results, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        self._log(report, "quiz")
        return report

    def grade_code(self, pid: str, code, lang: str) -> dict:
        if self._kind(pid) != "code" or not isinstance(code, str) or len(code) > self.max_code:
            raise InvalidRequest("invalid code")
        folder = self.attempts_dir / pid
        folder.mkdir(parents=True, exist_ok=True)
        with self._lock:                                     # the file is written under the lock: two submissions never share a name
            stamp, n = time.strftime("%Y%m%d-%H%M%S"), 1
            path = folder / (stamp + ".java")
            while path.exists():                             # same problem twice within one second
                n += 1
                path = folder / f"{stamp}-{n}.java"
            path.write_text(code)
            report = self.grader.grade(pid, path, lang)
        self._log(report)
        return report


# ------------------------------------------------------------------ history and analytics
class HistoryService:
    """Use cases of the History screen: analytics over every finished exam and code attempt of the (local) profile."""

    def __init__(self, history):
        self.history = history

    def overview(self) -> dict:
        return analytics.summarize(self.history.runs(PROFILE, with_details=True), self.history.attempts(PROFILE))

    def run(self, run_id) -> dict:
        r = self.history.run(PROFILE, run_id) if isinstance(run_id, int) else None
        if not r:
            raise NotFound("run not found")
        return r
