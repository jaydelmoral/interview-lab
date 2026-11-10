# ADR-0007: An exam is a reproducible definition of references; answers stay on the server

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
Exams combine coding problems, output questions, multiple-choice questions and personal-bank items, with per-section timers. The browser must not learn the answers, and a user must be able to retake the same exam.

## Decision
An exam is stored as `{config, sections[{module, minutes, items: [refs]}]}`. Items are selected by closeness of level to the requested seniority, with ties shuffled using a seed derived from the exam id. The public view omits answers; multiple-choice options are shuffled deterministically per `(exam id, item key)`, and grading maps the displayed index back through the same permutation. Self-study flashcards are the only items that carry their answer, by design.

## Consequences
**Positive**
- Answers never leave the server; retaking the same exam is exact; the file is tiny.
- Domain functions are pure and tested (including 'garbage answers never crash').

**Negative / trade-offs**
- If the underlying bank changes (items deleted), an old exam silently loses those items (`resolve` returns none).

## Alternatives considered
- Store full item copies in the exam (bigger, leaks answers if served).
- Random selection on each open (not reproducible).

## Resumen (ES)
Un simulacro guarda solo referencias a ejercicios; las respuestas nunca llegan al navegador y el orden de opciones es reproducible con una semilla. Repetir un simulacro da exactamente los mismos reactivos.
