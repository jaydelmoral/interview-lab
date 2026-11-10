# ADR-0012: Licensing: Apache-2.0 code, CC BY 4.0 content, reserved brand

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The project should be free to use (including by companies) while keeping authorship visible. Early content derived closely from third-party platforms (problem statements, examples, test names) was a legal risk. The consultancy logos are a trademark the author wants to keep.

## Decision
Code: Apache-2.0 (permissive, patent grant, `NOTICE` keeps the attribution). Content (exercises, quiz, bank, docs): CC BY 4.0 (attribution). Logos and brand assets: all rights reserved, explicitly excluded from both licenses and replaceable through `web/brand/brand.json`. All built-in exercises are original wordings of classic algorithmic ideas, set in generic business sectors (never real companies); user content stays in the git-ignored `workspace/`. A validator warns about brand and platform names. Contributions are signed off (DCO).

## Consequences
**Positive**
- Clear reuse terms; commercial use allowed with credit.
- White-label friendly.

**Negative / trade-offs**
- Anyone can use the code commercially without paying; relicensing future versions would not retract released ones.
- Copyright protection of AI-assisted work varies by country; authorship is credited in `AUTHORS.md`.

## Alternatives considered
- Non-commercial license (not open source, hurts adoption).
- Copyleft (AGPL) (discourages company adoption).

## Resumen (ES)
Código bajo Apache-2.0, contenido bajo CC BY 4.0 y logotipos con todos los derechos reservados, reemplazables por quien haga un fork. Los ejercicios son originales y con giros de negocio genéricos.
