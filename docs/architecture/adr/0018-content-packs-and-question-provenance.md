# ADR-0018: Content packs, and mandatory sources + review status for every question

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
The question bank must grow from 35 to hundreds of questions. Two risks: (1) a wrong or unsupported answer destroys the user's trust in the grading; (2) large curated banks may become a commercial asset that must never leak into the public repository (ADR-0016).

## Decision
1. **Provenance is mandatory.** Every multiple-choice question has `sources` (at least one title + https URL of official documentation) and `review` (`status` draft|reviewed, author, date; a reviewed question also names its reviewer). `tools/validate_bank.py` rejects questions without them and runs in CI and in the test suite. `--online` verifies that every URL answers; `--strict-review` can later demand that nothing ships as `draft`.
2. **AI-authored content starts as `draft`.** Only a human can mark a question `reviewed` (`tools/mark_reviewed.py`). The UI shows a *Draft* badge on unreviewed questions and, after grading, links the sources next to the explanation.
3. **Content packs.** The catalog also loads `packs/<name>/questions/*.json` for every folder containing a `pack.json`. A pack is its own (private) git repository, ignored by the main repository; the directory can be moved with `ILAB_PACKS_DIR`. Free sample content stays in `bank/`.
4. New levels `staff` and `principal` extend `jr < mid < sr`; the exam builder keeps choosing the closest level first, and the analyzer detects explicit role titles ("Staff Software Engineer", "Principal Engineer").

## Consequences
**Positive**
- A reader can verify any answer in one click; unreviewed content is visibly marked.
- The premium bank cannot leak through the main repository; the app works with or without packs.

**Negative / trade-offs**
- Authoring effort per question (sources, review).
- Draft questions may still contain mistakes until reviewed: the badge is the mitigation, not a guarantee.
- Pack authors need a separate repository and a build step (`authoring/`).

## Alternatives considered
- Sources optional: faster, but an unverifiable bank cannot be trusted or sold.
- Everything in one repo with a "premium" folder: one forgotten commit makes it public forever.

## Resumen (ES)
Toda pregunta lleva fuentes oficiales y un estado de revisión (obligatorio, validado en CI). Lo escrito por IA nace como borrador y solo una persona lo marca como revisado. Los bancos grandes viven en paquetes (`packs/`), repos privados aparte que el repo principal ignora. Se agregan los niveles Staff y Principal.
