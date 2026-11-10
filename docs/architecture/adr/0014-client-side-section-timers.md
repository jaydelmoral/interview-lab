# ADR-0014: Section timers run in the browser

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
Exams have a timer per section (standard minutes per question type; each coding problem has its own limit). Users practice alone on their own machine.

## Decision
Timers are client-side: `endAt` is computed when a section starts, stored in `localStorage` so an exam can be resumed, and when it reaches zero the section is submitted automatically. The server does not enforce time. Standard durations live in the domain (`MIN_PER_ITEM`, `PACE`: tight 0.8, standard 1.0, relaxed 1.25).

## Consequences
**Positive**
- Simple, works offline, responsive.
- Fits the practice use case (no one to cheat).

**Negative / trade-offs**
- Not tamper-proof: unsuitable for proctored assessments. This is documented as a non-goal.

## Alternatives considered
- Server-enforced deadlines (needs session state; pointless for self-practice).

## Resumen (ES)
Los temporizadores corren en el navegador y se reanudan con localStorage. Sirven para practicar solo; no sirven como evaluación vigilada y así se documenta.
