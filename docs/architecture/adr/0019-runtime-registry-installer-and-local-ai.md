# ADR-0019: A runtime registry and a setup-time installer; optional local AI through Ollama; optional PDF reading

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
The product needs more than one language runtime over time (Python, JavaScript...) and optional tools (PDF text extraction), and the user wants an optional **local** AI that keeps data on the machine. Letting a running web app (or an AI agent) install software on demand is a security hole, and on a shared or hosted deployment it would be remote code execution by design.

## Decision
1. **Registry.** `runtimes/<id>.json` describes each language or tool: how to detect it, its version command, and the package names per package manager (apt, Homebrew) plus the official docs. The registry is audited code in the repository, plain data, no shell snippets.
2. **Detection is read-only.** `GET /api/runtimes` reports what is installed. The web UI shows it; it has **no** endpoint that installs anything.
3. **Installation is a setup-time, human action:** `python3 install.py install --lang <id>` prints the exact command, requires typing `yes`, runs without a shell, and each user is responsible for what they install on their own machine. `--dry-run` shows the command only.
4. **Local AI:** an optional `OllamaQuestionGenerator` (standard library, `ILAB_AI_PROVIDER=ollama`) talks to a local daemon. It is **loopback-only** unless `ILAB_OLLAMA_ALLOW_REMOTE=1`. Model output is untrusted and passes the same strict validation as other generators; generated questions stay in the user's personal bank as drafts.
5. **PDF:** an optional `PdftotextExtractor` runs the system `pdftotext` in a separate process (temp file 0600, timeout, no shell) so the project keeps zero Python dependencies.

## Consequences
**Positive**
- Languages and tools can grow without touching the web surface; nothing is ever installed implicitly.
- Local AI and PDF are optional and degrade gracefully with actionable messages.

**Negative / trade-offs**
- Setup needs one extra command per runtime; a small registry must be maintained per package manager.
- A 7–9B local model on CPU takes minutes and makes mistakes (draft status is the mitigation).
- Windows is not covered by the installer yet (manual install; the app still detects what exists).

## Alternatives considered
- Let the AI or the web UI install languages on request: rejected (arbitrary code execution path).
- A Python dependency for PDFs (pypdf): works, but breaks the zero-dependency rule; `pdftotext` is optional and isolated.

## Resumen (ES)
Los lenguajes y herramientas se describen en un registro auditado (`runtimes/`). La app solo detecta lo instalado (solo lectura); instalar es una acción humana al configurar (`python3 install.py`), con confirmación y sin shell. La IA local (Ollama) y la lectura de PDF (`pdftotext`) son opcionales, locales y con degradación elegante.
