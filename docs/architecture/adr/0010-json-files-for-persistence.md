# ADR-0010: JSON files for persistence

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The data are small (exams, banks, result logs) and single-user. Users should be able to inspect, back up, version and delete their data trivially.

## Decision
Persist as human-readable JSON under `$ILAB_HOME` (`exams/`, `banks/`, `runs/*.jsonl`, `problems/`). Access goes through repository ports, so the storage can change without touching use cases.

## Consequences
**Positive**
- Zero setup; easy backup (copy a folder); diff-able.
- The user owns the data and can delete it.

**Negative / trade-offs**
- No transactions or concurrent writers (fine for one user; writes are append-only or whole-file).
- Listing scans a directory (capped at 50 exams).

## Alternatives considered
- SQLite (robust queries; more code and migrations).
- Embedded key-value store (opaque files).

## Resumen (ES)
Los datos se guardan como archivos JSON legibles dentro de la carpeta de trabajo, detrás de puertos de repositorio. Fácil respaldo y total propiedad del usuario; no hay transacciones, algo aceptable para un solo usuario.
