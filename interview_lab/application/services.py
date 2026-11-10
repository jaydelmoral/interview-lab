"""APPLICATION: use cases. Orchestrate domain rules and ports; contain no HTTP, no file paths and no JVM details."""
from __future__ import annotations

import base64
import hashlib
import threading
import time
from pathlib import Path

from ..domain import exam as rules
from ..domain import profile
from .errors import Forbidden, InvalidRequest, NotFound, Unprocessable
from .ports import FetchError, GenerationError


# ------------------------------------------------------------------ profile analysis
class AnalysisService:
    """Use case: understand a CV or a job description. Nothing is stored."""

    def analyze(self, text=None, filename: str = "", data_b64=None) -> dict:
        try:
            if data_b64 is not None:
                raw = base64.b64decode(data_b64, validate=True)
                name = filename.lower()
                if name.endswith(".docx"):
                    text = profile.docx_text(raw)
                elif name.endswith((".txt", ".md")):
                    text = raw.decode("utf-8", "replace")
                else:
                    raise InvalidRequest("unsupported file: use .txt, .md or .docx, or paste the text (PDF is not supported)")
        except InvalidRequest:
            raise
        except Exception as e:
            raise InvalidRequest("could not read the file") from e
        if not isinstance(text, str) or not text.strip():
            raise InvalidRequest("no text to analyze")
        return profile.analyze(text)


# ------------------------------------------------------------------ exams
class ExamService:
    def __init__(self, catalog, exams):
        self.catalog, self.exams = catalog, exams

    def modules(self, lang: str, fetch_enabled: bool, ai_enabled: bool) -> dict:
        counts = self.catalog.counts()
        return {"modules": [{"id": m, "title": rules.pick(rules.TITLES[m], lang), "count": counts.get(m, 0)} for m in rules.MODULE_ORDER],
                "coming": [{"id": "ai", "title": "IA / LLMs"}], "fetch": fetch_enabled, "ai": ai_enabled}

    def create(self, cfg: dict, lang: str) -> dict:
        if not isinstance(cfg.get("modules"), list) or not cfg["modules"]:
            raise InvalidRequest("choose at least one module")
        exam = rules.build(cfg, self.catalog.candidates())
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

    def grade_section(self, exam_id: str, idx, answers, lang: str) -> dict:
        exam = self._load(exam_id)
        if not isinstance(idx, int) or not 0 <= idx < len(exam["sections"]) or not isinstance(answers, dict):
            raise InvalidRequest("invalid request")
        report = rules.grade_section(exam, idx, answers, self.catalog.resolve, lang)
        report["weak"] = rules.weak_tags(report["items"])
        return report

    def finish(self, exam_id: str, sections) -> dict:
        exam = self._load(exam_id)
        if not isinstance(sections, list) or not all(isinstance(x, dict) and isinstance(x.get("score"), int) and isinstance(x.get("max"), int) for x in sections):
            raise InvalidRequest("invalid request")
        rec = {"exam": exam["id"], "when": time.strftime("%Y-%m-%d %H:%M:%S"), "score": sum(x["score"] for x in sections),
               "max": sum(x["max"] for x in sections),
               "sections": [{"module": str(x.get("module", ""))[:30], "score": x["score"], "max": x["max"]} for x in sections]}
        self.exams.record_result(rec)
        return rec

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

    def __init__(self, problems, grader, results, attempts_dir: Path, max_code: int):
        self.problems, self.grader, self.results = problems, grader, results
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

    def _log(self, report: dict) -> None:
        self.results.append({k: report[k] for k in ("timestamp", "problem", "score", "max")})

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
        self._log(report)
        return report

    def grade_code(self, pid: str, code, lang: str) -> dict:
        if self._kind(pid) != "code" or not isinstance(code, str) or len(code) > self.max_code:
            raise InvalidRequest("invalid code")
        folder = self.attempts_dir / pid
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (time.strftime("%Y%m%d-%H%M%S") + ".java")
        path.write_text(code)
        with self._lock:
            report = self.grader.grade(pid, path, lang)
        self._log(report)
        return report
