# Security model

Scope: Interview Lab as a **single-user, local** tool. Multi-user hosting and public exposure are out of scope.
Alcance: herramienta **local de un solo usuario**. El alojamiento multiusuario o público queda fuera de alcance.

## Assets
1. The user's machine and files (the app executes code).
2. The user's CV text, notes, attempts and scores (privacy).
3. Third-party credentials, if the optional AI is enabled (`ANTHROPIC_API_KEY`).

## Trust boundaries
Browser ⇄ local server (loopback) ⇄ JVM child processes ⇄ files. Optional outbound: public web pages (links) and the AI provider.

## Threats and mitigations

| # | Threat | Mitigation | Residual risk |
|---|---|---|---|
| T1 | Another web page makes the browser POST code to `localhost` (CSRF) | `Origin` must be ours; JSON content type required (no simple cross-origin request) — ADR-0008 | Low |
| T2 | DNS rebinding makes a hostile name resolve to 127.0.0.1 | `Host` must be in an allow-list | Low |
| T3 | Submitted code steals secrets or damages the host | Env scrubbed (no tokens), temp dir, limits; **Docker**: non-root, read-only FS, no caps, limits — ADR-0004 | **Medium without Docker**: code runs as the user. Medium in Docker: network allowed |
| T4 | Infinite loops / memory bombs / endless output / leftover child processes | Per-test timeout, `-Xmx256m`, captured output capped at 200 KB per stream, the test's process group is killed when it ends, container CPU/mem/PID limits | Low (a process that detaches itself with `setsid` escapes the group outside Docker) |
| T5 | SSRF via "My bank" links (metadata service, LAN, localhost) | Public-IP-only, pinned connection, revalidated redirects, size/time/type limits — ADR-0009 | Low |
| T6 | XSS from fetched or generated text | Every dynamic value escaped; strict CSP (no remote sources, `script-src 'self'`: no inline scripts, so an unescaped value cannot run code); text rendered via `textContent`/`esc()` | Low |
| T7 | Prompt injection in fetched text steering the AI generator | AI output validated for shape/size and treated as study text only; no tools, no actions; user opt-in | Low (bad questions possible) |
| T8 | Leaking the AI key | Key only from the user's environment; never stored, logged or returned; errors scrubbed | Low |
| T9 | Path traversal through ids | Strict id regexes; fixed base directories | Low |
| T10 | Oversized requests | Per-route body limits (100 KB; 4.5 MB for CV upload) | Low |
| T11 | Malformed files (docx zip bombs) | `.docx` size check; text length cap | Low |
| T12 | Answers extracted from the browser | Answers stay server-side; public items omit them | Low (flashcards intentionally include theirs) |

## Not defended (by design)
- Hostile code that wants the network or the user's files **outside Docker**.
- Tampering with the browser's timer *display* has no effect on exams with an attempt id (the server enforces the deadline); the rest time between sections is not limited, and free practice has no clock.
- Cheating yourself: with an attempt id the server grades each section once and computes the final result itself ([ADR-0021](architecture/adr/0021-server-side-exam-attempts.md)); the server also owns each section's clock and closes it as it was left when time is up; a request without an attempt id keeps the old client-trusted (clamped) behaviour. Code under test shares the JVM with the hidden harness, so it could print a fake result line. A hosted or proctored edition must keep attempt state and verdicts on the server.
- Exposing the port beyond loopback, or serving several users.

## Operational guidance
- Use Docker for any code you did not write; never grade strangers' code; never publish the port.
- Keep the image updated; rebuild after `git pull`.
- Report vulnerabilities privately (see [SECURITY.md](../SECURITY.md)).

## Resumen (ES)
La herramienta asume un usuario local. Se defiende de CSRF y DNS rebinding (Host/Origin/JSON), de SSRF al leer enlaces, de XSS y de peticiones enormes. El código del usuario corre con entorno limpio y límites; **sin Docker se ejecuta con tus permisos**, y con Docker aún puede usar la red del contenedor. No está pensada para exponerse a internet.

## Update 2026-11-10 / Actualización
- CSP now also allows `font-src 'self' data:` and `worker-src 'self' blob:` for the optional Monaco editor (ADR-0020); still no external origins.
- Optional runtimes are installed only by the user at setup time (`install.py`, `tools/fetch_monaco.py`); the web app has no install endpoint (ADR-0019).
- A local Ollama daemon is contacted only on loopback unless `ILAB_OLLAMA_ALLOW_REMOTE=1` is set deliberately.
- Content packs and premium material are blocked from the public repository by `tools/preflight.py` (ADR-0016).

## Audit 2026-11-10 / Auditoría
Fixed (regression tests in `tests/test_hardening.py`):
- The grader buffered all output of the code under test: an endless print loop used about 7 GB of server memory. Output is now capped and drained.
- Processes started by the code under test survived the test; the whole process group is now killed.
- A negative `Content-Length` blocked a server thread; wrong types in exam preferences returned a 500; a finished exam accepted any score (history could show 1e32 %). All validated now.
- Two submissions of the same problem within one second shared a file name; schema migrations were not atomic; a page with an unknown charset failed the whole bank; question-source links accept only `http(s)`.
- The server prints a warning when it listens beyond loopback.
- P4 (local step): the exam result is computed from what the server graded, per attempt, and finishing twice never stores two runs (ADR-0021; tests in `tests/test_attempts.py`).

Se corrigieron los puntos anteriores (pruebas en `tests/test_hardening.py`). Lo que queda abierto está en "Not defended" y en el plan de trabajo.
- Scripts live in `web/*.js` and the CSP no longer allows `'unsafe-inline'` for scripts (ADR-0013, audit P7). Styles still allow it. A test fails if a page gains an inline `<script>`, an `on*=` attribute or a `javascript:` URL.
