# ADR-0002: Local-first, single process, standard library only

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The users are job seekers practicing privately; their CVs, notes and attempts are sensitive. Many of them cannot or should not run servers, databases or cloud accounts. The tool must start with one command and work offline (apart from optional links).

## Decision
Run as one Python process using only the standard library (`http.server`, `json`, `zipfile`, `html.parser`, `ssl`). No accounts, no telemetry, no external database. Optional capabilities (link fetching, AI generation) are opt-in and isolated behind ports.

## Consequences
**Positive**
- Privacy by construction: data stays in `workspace/`.
- Trivial install; tiny attack surface; no dependency vulnerabilities.
- Easy to audit by recruiters and companies.

**Negative / trade-offs**
- `http.server` is not built for high concurrency: fine for one user, not for hosting many (explicit non-goal).
- Some features (PDF parsing, rich NLP) must be written by hand or left out.

## Alternatives considered
- Flask/FastAPI + SQLite (more convenient, adds dependencies and an upgrade burden).
- Electron/desktop app (heavy, harder to run in a container).

## Resumen (ES)
Un solo proceso Python con la biblioteca estándar, sin cuentas, sin telemetría y sin base de datos externa. Privacidad por diseño e instalación trivial, a cambio de no escalar a muchos usuarios (no es el objetivo).
