# ADR-0023: Heading typeface hosted in the app, and gold as the colour of action

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
ADR-0015 chose a calm blue system built on the Collaboration logo palette, with system fonts only. The "Pro" redesign (ADR-0022) asks for two visual changes that touch every page: headings in a geometric typeface close to the one in the logo (perfect circles), and **gold mixed with the logo blues in both themes** as the colour of action. The no-external-assets rule (ADR-0006, ADR-0015) forbids a font CDN, and the CSP already allows `font-src 'self'`.

## Decision
**Typeface**
- **Outfit** (SIL OFL 1.1) hosted in `web/fonts/` as one variable `woff2`: Latin subset (Spanish and English), weights 400–600, **24 656 bytes** (budget 40 KB). Origin, upstream SHA-256, the SHA-256 of the shipped file and the exact subsetting commands are in `web/fonts/ORIGEN.md`; the licence text is `web/fonts/OFL.txt`; `NOTICE` lists it as third-party.
- Token `--font-display: "Outfit", "Century Gothic", "Futura", "URW Gothic", ui-sans-serif, system-ui, sans-serif`. Used for `h1`–`h3`, highlighted figures, the product name in the bar and the fixed list of advantages. Body text keeps the system font (no weight cost).
- `@font-face` with `font-display: swap` (text appears at once in the fallback stack); `<link rel="preload" as="font" crossorigin>` on the landing only. The file is a plain static asset (`/fonts/Outfit-latin-400-600.woff2`, type `font/woff2`). The CSP is unchanged. If the file were missing the fallback stack would take over.

**Gold**
- Rule: *blue is the brand and the structure; gold is the action and the achievement*, and it is an accent, not a surface.
- Tokens in `web/common.css` for both themes: `--gold`, `--gold-2`, `--gold-fg`, `--gold-line`, `--gold-ink`, `--glint-1/2`, plus the three arc pairs `--o-a*`, `--o-b*`, `--o-c*`. Existing tokens are unchanged.
- Gold goes on: every primary button (`button.primary`, `.btn.primary`) on all four pages, highlighted figures (landing strip, dashboard KPIs, scores), small marks (badge dot, "Step n" labels, active item of the fixed list, current exam step) and the O's glint. It never goes on running text, links, focus rings, charts or status colours (`--ok`, `--bad`, `--warn`), so it cannot be mistaken for the amber warning.
- In light theme the fill alone is only 2.1:1 on the page background, so the primary button carries a `--gold-line` border (4.0:1). Text on gold is 9.9:1 (dark) and 7.4–9.4:1 (light); gold ink on the page is 14.7:1 (dark) and 6.0:1 (light).

## Consequences
**Positive**
- The brand reads as one system (blue structure, gold action) in both themes, still without an external request; the typeface costs 24 KB once and nothing for body text.
- One place (tokens) to retune the palette.

**Negative / trade-offs**
- One binary asset in the repository and a licence obligation (kept in `web/fonts/` and `NOTICE`).
- Primary buttons changed colour everywhere, including the "selected problem tab" in the exam (it reuses `button.primary`).
- The subset is Latin only: a future language with other scripts needs a new subset (the commands are documented).

## Alternatives considered
- **System geometric fonts only** (Century Gothic, Futura): not installed on Linux or most phones; headings would differ per machine.
- **Google Fonts or another CDN:** breaks offline-first and the CSP.
- **Full variable font (45 KB):** over budget; weights above 600 and non-Latin glyphs are not used.
- **Gold as a surface or for links and charts:** too loud, low contrast on light backgrounds, and it would blur the meaning of the status colours.

## Resumen (ES)
Los títulos usan Outfit (licencia libre OFL), alojada en la propia app (24.6 KB, solo latín, pesos 400–600), sin CDN y sin cambiar la política de seguridad; si faltara, entra una pila de respaldo. El dorado es el color de la acción (botones principales, cifras destacadas, marcas pequeñas y el destello de la O) en ambos temas, mezclado con los azules del logotipo; nunca va en texto corrido, enlaces, gráficas ni colores de estado. En tema claro el botón lleva borde para conservar el contraste.
