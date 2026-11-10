"""ADAPTER: code grader that compiles and runs the hidden tests on a JVM (CodeGrader port). Wraps grader/grade.py."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path


class JavaCodeGrader:
    def __init__(self, root: Path, home: Path):
        # grader/grade.py reads ILAB_HOME at import time; load a private copy bound to this home
        os.environ["ILAB_HOME"] = str(home)
        spec = importlib.util.spec_from_file_location("ilab_grade_" + str(abs(hash(str(home)))), Path(root) / "grader" / "grade.py")
        self._mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self._mod)

    def grade(self, problem_id: str, source: Path, lang: str = "es") -> dict:
        return self._mod.grade(problem_id, source, lang=lang)
