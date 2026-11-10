# ADR-0017: SQLite history and analytics, per profile

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
Exam results lived in append-only JSONL files (`runs/exams.jsonl`, `runs/results.jsonl`): fine for a log, poor for queries, integrity after an interrupted write, or trends over time. The user wants to track their own attempts and see analytics. A multi-user cloud edition may come later (ADR-0016), but the first release is local and single-user.

## Decision
- A new port `HistoryRepository` and a standard-library `sqlite3` adapter (`<home>/ilab.db`). No dependency, one file, WAL mode, one connection per call (the HTTP server is threaded).
- **Every table has `profile_id`** (a single default profile `local` today). A future multi-user edition then needs no data migration, only authentication on top.
- Schema versioning with `PRAGMA user_version` and an ordered list of migrations.
- Tables: `exam_runs`, `section_results`, `missed_items` (with tags), `code_attempts`, `profiles`, `meta`.
- Analytics are **pure functions** in `domain/analytics.py` (trend, per-module averages and deltas, weak topics, time used vs allotted, streak, per-exercise progress): testable without a database.
- The old JSONL files are still written (the exam list uses them) and are **imported once** and idempotently into SQLite.
- Recording is best effort: a history failure is logged and never breaks finishing an exam or grading code.
- The client reports section results when finishing an exam; the server validates and clamps every field (local single-user trust model, documented as not tamper-proof).

## Consequences
**Positive**
- Dashboards and trends with plain SQL/Python; integrity from SQLite transactions.
- Cloud-ready data model; Postgres migration later keeps the same shape.

**Negative / trade-offs**
- Two stores for a while (JSONL for the exam list, SQLite for history); to be unified later.
- Results are client-reported at finish time (code grading is server-side; section totals are not re-derived).

## Alternatives considered
- Keep JSONL and aggregate in memory: no integrity, slow with growth.
- An ORM or Postgres now: a dependency and a service for a single-user local tool.

## Resumen (ES)
El historial vive en SQLite (un archivo, sin dependencias) con `profile_id` en todas las tablas para poder escalar a multiusuario sin migrar datos. La analítica son funciones puras; los JSONL viejos se importan una sola vez. Registrar el historial nunca rompe un examen.
