"""APPLICATION: ports (interfaces) that the use cases depend on. Adapters implement them.

Using typing.Protocol keeps the dependency direction clean: services know these shapes, never the concrete adapters.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol


class FetchError(Exception):
    """A link could not be fetched safely."""


class GenerationError(Exception):
    """A question generator could not produce usable items."""


class ProblemRepository(Protocol):
    def list_summaries(self) -> list: ...
    def find(self, pid: str) -> Optional[tuple]: ...             # (folder, "builtin"|"user") or None
    def meta(self, pid: str) -> Optional[dict]: ...
    def public(self, pid: str, lang: str) -> Optional[dict]: ...
    def quiz_questions(self, pid: str) -> list: ...


class Catalog(Protocol):
    def candidates(self) -> list: ...                           # items usable to build exams
    def counts(self) -> dict: ...
    def resolve(self, ref: dict) -> Optional[dict]: ...         # full item (with answers) for a ref


class ExamRepository(Protocol):
    def save(self, exam: dict) -> None: ...
    def load(self, exam_id: str) -> Optional[dict]: ...
    def list(self) -> list: ...
    def record_result(self, record: dict) -> None: ...
    def last_results(self) -> dict: ...


class BankRepository(Protocol):
    def save(self, bank: dict) -> None: ...
    def list(self) -> list: ...
    def delete(self, bank_id: str) -> bool: ...


class UrlFetcher(Protocol):
    def fetch_text(self, url: str) -> tuple: ...                # (title, text, headings); raises FetchError


class QuestionGenerator(Protocol):
    name: str
    def generate(self, title: str, text: str, headings: list) -> list: ...   # raises GenerationError


class CodeGrader(Protocol):
    def grade(self, problem_id: str, source: Path, lang: str) -> dict: ...


class ResultsLog(Protocol):
    def append(self, record: dict) -> None: ...


class HistoryRepository(Protocol):
    """Long-term record of finished exams and code/quiz attempts, per profile (a single local profile for now)."""
    def record_run(self, profile_id: str, run: dict) -> int: ...
    def record_attempt(self, profile_id: str, attempt: dict) -> None: ...
    def runs(self, profile_id: str, with_details: bool = True) -> list: ...          # oldest first
    def run(self, profile_id: str, run_id: int) -> Optional[dict]: ...
    def attempts(self, profile_id: str) -> list: ...                                  # oldest first
