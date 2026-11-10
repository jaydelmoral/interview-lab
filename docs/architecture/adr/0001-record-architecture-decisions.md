# ADR-0001: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
Interview Lab is a portfolio-grade project that others will read, fork and extend. Design intent gets lost when it lives only in people's heads or in commit messages.

## Decision
We record every architecturally significant decision as a short Architecture Decision Record (ADR) in `docs/architecture/adr/`, numbered, immutable once accepted (superseded by a new ADR instead of edited), using the template in the index.

## Consequences
**Positive**
- Newcomers and reviewers can see *why*, not only *what*.
- A small writing cost per decision.

**Negative / trade-offs**
- Wiki pages (drift away from the code); comments in code (not discoverable as a set).

## Resumen (ES)
Cada decisión de arquitectura relevante se registra como un ADR numerado dentro del repositorio, para que se entienda el porqué y no solo el qué.
