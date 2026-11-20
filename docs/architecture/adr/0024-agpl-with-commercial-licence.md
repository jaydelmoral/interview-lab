# ADR-0024: AGPL-3.0 for the code, with a separate commercial licence

- **Status:** Accepted
- **Date:** 2026-11-20
- **Deciders:** Javier Morales Barrera, Claude

## Context
[ADR-0012](0012-content-licensing-and-brand-policy.md) chose Apache-2.0 for the code, and [ADR-0016](0016-contribution-policy-and-premium-content-separation.md) postponed the final choice (Apache-2.0 vs AGPL-3.0 with a commercial option) until before the repository became public. The repository is now about to be published as a portfolio and, possibly, as the base of a paid product (premium packs, white-label for academies, hosted service). Under Apache-2.0 anyone could resell the engine, remove the Collaboration credit and keep their improvements private, and nothing could be done about it once copies exist.

## Decision
- The **code** is licensed under **AGPL-3.0** ([LICENSE](../../../LICENSE), unmodified official text so that hosting platforms recognise it), plus **additional terms under section 7** written in [NOTICE](../../../NOTICE): keep the Collaboration credit and logo shown by the unmodified program (7(b)), mark modified versions and do not present them as the original (7(c)), and no trademark rights (7(e)).
- A **commercial licence** is offered separately, case by case ([LICENSE-COMMERCIAL.md](../../../LICENSE-COMMERCIAL.md)), for who cannot or does not want to meet the AGPL terms (white label without the Collaboration brand, private changes, proprietary bundling).
- This is possible because Javier is the **only copyright holder** and external pull requests are not accepted until a CLA exists (ADR-0016). Once a CLA is in place, contributions can be taken without losing the ability to dual-license.
- Unchanged from ADR-0012: free exercises and questions are **CC BY 4.0**; Collaboration logos and brand are **all rights reserved**; premium packs stay private and are not covered by any of these licences.
- The repository was private until now, so no copy under Apache-2.0 was ever distributed; the change retracts nothing.

## Consequences
**Positive**
- Reuse by third parties keeps the credit and gives their changes back; a competitor cannot offer a closed hosted copy.
- White label becomes a paid, explicit agreement instead of a free right.
- Still open source in the OSI sense, which suits a public portfolio.

**Negative / trade-offs**
- Some companies avoid AGPL, which may reduce corporate adoption.
- The additional attribution terms are enforceable only as far as the law of each country allows; a lawyer should review them before commercial licences are granted. Brand protection of the name "Interview Lab" needs a trademark registration (IMPI), which a licence cannot replace.
- Copyright protection of AI-assisted work varies by country ([AUTHORS.md](../../../AUTHORS.md)).

## Alternatives considered
- Keep Apache-2.0: maximum adoption, but anyone could resell it and drop the brand.
- PolyForm Noncommercial: blocks resale completely, but is not open source and hurts the portfolio value.

## Resumen (ES)
El código pasa a AGPL-3.0 con términos adicionales de atribución a Collaboration y una licencia comercial aparte para marca blanca o cambios privados. Contenido gratuito en CC BY 4.0, marca reservada y paquetes premium privados, sin cambios. Como el repositorio era privado, no se retira nada a nadie.
