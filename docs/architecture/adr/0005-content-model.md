# ADR-0005: Content as data: folders, JSON, bilingual Markdown

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
Users must be able to add their own exercises without touching code, and the project is bilingual (Spanish and English). Statements are in English like real interviews, with Spanish help.

## Decision
A problem is a folder: `meta.json` (metadata, tests, bilingual feedback `fail_*` / `fail_*_en`), `problem.md` + `problem.es.md` (same block structure so paragraph-level hover translation works), `starter.java`, `Harness.java` (hidden tests using `Runner`/`Check`), `reference/` (a correct solution used to prove the tests are fair). Questions are JSON with `{es,en}` fields. A validator (`tools/validate.py`) enforces structure, runs the reference (must score 100%) and the starter (must not), checks block alignment and lints brand names.

## Consequences
**Positive**
- Contribution = adding files; no code changes.
- The reference-solution check keeps hidden tests honest.
- Same content model for built-in and user content.

**Negative / trade-offs**
- Translations are maintained by hand (or with a tool) and can drift; the validator flags structural drift only.

## Alternatives considered
- Database of problems (harder to share via git).
- Machine translation at runtime (needs network/AI; breaks local-first).

## Resumen (ES)
Cada ejercicio es una carpeta con metadatos, enunciado EN/ES alineado por bloques, plantilla, pruebas ocultas y una solución de referencia. Un validador comprueba que las pruebas sean justas. Agregar contenido no requiere tocar código.
