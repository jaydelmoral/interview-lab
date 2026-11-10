"""ADAPTER: extracts text from a PDF with the system's `pdftotext` (poppler) if it is installed. Optional, no Python dependency.

The PDF is untrusted input: it is written to a private temporary file, parsed by a separate process with a timeout and
no shell, and only plain text comes back (capped). If pdftotext is missing the caller gets a clear message instead.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

from ..application.ports import FetchError

MAX_PDF_BYTES = 4_500_000
MAX_TEXT = 200_000


class PdftotextExtractor:
    name = "pdftotext"

    def available(self) -> bool:
        return shutil.which("pdftotext") is not None

    def extract(self, raw: bytes) -> str:
        if not self.available():
            raise FetchError("PDF support needs pdftotext: run `python3 install.py install --lang pdftotext`, or paste the text")
        if len(raw) > MAX_PDF_BYTES or not raw.startswith(b"%PDF"):
            raise FetchError("not a valid PDF (or too large)")
        fd, path = tempfile.mkstemp(suffix=".pdf")              # created 0600 by mkstemp
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(raw)
            r = subprocess.run(["pdftotext", "-layout", "-q", path, "-"], capture_output=True, timeout=20, stdin=subprocess.DEVNULL,
                               env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8"})
            if r.returncode != 0:
                raise FetchError("could not read that PDF")
            text = r.stdout.decode("utf-8", "replace")[:MAX_TEXT]
            if not text.strip():
                raise FetchError("the PDF has no extractable text (scanned image?); paste the text instead")
            return text
        except subprocess.TimeoutExpired as e:
            raise FetchError("reading the PDF took too long") from e
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
