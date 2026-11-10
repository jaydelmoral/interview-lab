# ADR-0021: Server-side state per exam attempt
- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier (owner), Claude (implementation)

## Context
Until now the browser reported each section's score when an exam finished, and the server only checked it was a valid 0-100 % value. A section could also be graded several times (an empty submission returns every correct answer), and the timers are the browser's ([ADR-0014](0014-client-side-section-timers.md)). The audit of 2026-11-10 (finding P4) asked for a cheap local step; a full cloud model (attempt entity with server clock and per-section deadlines) is deliberately left for a second edition.

## Decision
The browser mints a random **attempt id** (32 hex chars) each time a new attempt starts and sends it with `/section`, `/api/grade` (plus the `exam` id) and `/finish`. With an attempt id the server:
- grades each question section **once per attempt** and stores that report; asking again returns the first one;
- keeps the **best graded score per code exercise** of the attempt (`/api/grade` with `exam` + `attempt`; the exercise must belong to the exam);
- computes `/finish` from that state, ignoring client `score`/`pct`/`correct`/`total`/`missed` (the client only lists which sections it finished by `section` index, and how long each took, clamped to the section's minutes); a section never graded counts as nothing answered;
- owns the **clock**: `POST /api/exams/{id}/start` fixes a section's deadline the first time it is called (start + the section's minutes) and returns the remaining time, so a reload or a tampered browser timer cannot buy more time; the time used in the history is measured by the server;
- keeps the latest answers of a running section (`POST /api/exams/{id}/answers`, debounced by the page). If the section's time is over (deadline + 15 s of grace) it is closed **as it was left**: graded with those saved answers, whatever the browser sends now; late autosaves and late code submissions are refused (`400`);
- stores the result inside the attempt, so finishing twice returns the stored result and **never records the run twice** (a retry after a lost response is harmless); a finished attempt accepts no more grades.

State lives in `exam-attempts/<exam id>-<attempt id>.json`, replaced atomically, behind the `AttemptRepository` port. Without an attempt id (old clients, progress saved by an older version) the previous client-trusted behaviour is kept, still validated and clamped.

## Consequences
**Positive:** the history can no longer be inflated from the browser; a double or repeated `finish` is idempotent; the answers of a section cannot be "peeked at" and then re-submitted for a better score. 
**Negative / trade-offs:** an extra small file per attempt, and one small request per answer change (local, so cheap); the rest time *between* sections is not limited (the next clock starts when the user clicks); someone calling the API by hand can still read answers by grading with empty answers, but that locks in a zero score for the section.

## Alternatives considered
- Keep trusting the client (status quo): simplest, but the history is forgeable.
- Store attempts in SQLite: heavier migration for data that is only needed until the run is finished; JSON files match [ADR-0010](0010-json-files-for-persistence.md).
- Require the attempt id: cleaner, but breaks older clients and in-progress exams.

## Resumen (ES)
Con un id de intento, el servidor califica cada sección una sola vez, guarda el mejor puntaje de cada ejercicio de código y calcula el resultado final él mismo, ignorando los puntajes del navegador; terminar dos veces no duplica la corrida. El reloj también es del servidor: fija el límite de cada sección al empezarla, guarda las últimas respuestas y, si se acaba el tiempo, cierra la sección tal como quedó. Sin id se mantiene el modo anterior.
