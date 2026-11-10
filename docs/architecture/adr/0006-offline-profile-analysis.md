# ADR-0006: Offline, heuristic analysis of CVs and job descriptions

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The landing page must infer seniority, language/version and relevant modules from a CV or a job description. An AI model would do this well but would send sensitive text to a third party and require a key.

## Decision
Implement a pure, deterministic analyzer (`domain/profile.py`): keyword/regex detection of technologies per module, language and version, and seniority from years of experience and title keywords. The result only pre-fills the form; the user can always override. Nothing is stored. `.docx` is parsed with `zipfile`; PDF is intentionally unsupported (paste text).

## Consequences
**Positive**
- Private, instant, free, explainable (we show the matched keywords).
- Unit-testable with plain strings.

**Negative / trade-offs**
- Heuristics miss nuance (for example 'led teams' vs years); vocabulary lists need upkeep.
- No PDF support.

## Alternatives considered
- LLM analysis (better recall, privacy and cost issues; possible later as another adapter).
- Local ML models (heavy dependencies).

## Resumen (ES)
El análisis de CV o vacante es local y heurístico (palabras clave y patrones): privado, instantáneo y explicable. Solo rellena el formulario; el usuario puede corregirlo. No se guarda nada.
