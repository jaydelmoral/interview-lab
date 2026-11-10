# ADR-0003: Hexagonal (ports and adapters) layering

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The first version put HTTP handling, business rules, file access and JVM calls in one file. That was fast to write but hard to test and to extend (for example, adding an AI question generator would have touched everything).

## Decision
Split into `domain` (pure rules), `application` (use cases + ports declared with `typing.Protocol`), `adapters` (filesystem, JVM, URL fetch, generators) and `web` (HTTP + composition root). Dependencies point inward. Only `web/app.py:compose()` knows which concrete adapter implements each port.

## Consequences
**Positive**
- Domain and use cases are tested with no server, files or JVM (see `tests/test_domain.py`).
- Swapping an adapter (offline vs AI generator, fake vs real grader) is a one-line change in the composition root.
- The route table is the API surface and is easy to read.

**Negative / trade-offs**
- More files and indirection than a script; a small cost for a small project, paid back by testability.

## Alternatives considered
- Single module with functions (simple but couples everything).
- Full DDD with aggregates and an event bus (over-engineered for this scope).

## Resumen (ES)
Arquitectura hexagonal: dominio puro, casos de uso con puertos (Protocol), adaptadores de infraestructura y una capa web. Se prueba sin servidor ni JVM y se cambian adaptadores en un solo lugar.
