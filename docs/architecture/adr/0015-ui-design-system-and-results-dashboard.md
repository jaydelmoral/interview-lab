# ADR-0015: A token-based design system with light/dark themes, and one results dashboard

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
The first UI used a generic card layout and followed the OS colour scheme only. The product is also a professional portfolio piece, so it needs a distinctive, polished look that matches the Collaboration brand, works in a light and a dark theme with a visible switch, and explains *how* a candidate is scored before the exam and *how they did* after it.

The strict CSP (`default-src 'none'`, see ADR-0006) and the local-first promise (ADR-0001) rule out web fonts, CDNs and any third-party asset.

## Decision
1. **One stylesheet, design tokens.** `web/common.css` defines all colour, radius and shadow decisions as CSS custom properties, with a dark and a light set selected by `html[data-theme]`. The palette is sampled from the Collaboration logos (cyan `#0cb4e4`, blue `#0c84b4`, deep teal `#0c6c84`). The visual language follows calm-tech product sites: soft radial glows, thin 1 px borders, pill-shaped navigation and buttons, large light headings.
2. **Theme.** `web/theme.js` runs synchronously in `<head>` (no flash of the wrong theme). The effective theme is the user's explicit choice (`localStorage`) or the OS preference. A toggle in the app bar switches it; the matching logo variant is shown through CSS only.
3. **System font stack.** No downloaded fonts: the UI uses the platform's UI font (`Inter`/SF/Segoe when present).
4. **One dashboard renderer.** `renderDashboard(data)` in `web/common.js` draws the KPIs, per-section bars, time per section, radar profile, opportunity areas and the list of missed questions, as inline SVG/HTML. The landing page feeds it **clearly labelled sample data** ("illustrative example"); the exam page feeds it **real results**. Both are therefore always consistent.
5. **Scoring rules shown to the user are the real rules**: section score 0–100 %, overall = mean of sections, ≥ 60 % passes, ≥ 80 % is "solid". Opportunity areas come from sections under 60 %, code-test categories under 80 % and the tags of missed questions.

## Consequences
**Positive**
- Same look on every page; a rebrand is a change of a few variables (plus `brand.json`).
- Landing sample and real report cannot drift apart.
- Works offline, keeps the CSP unchanged, no build step (ADR-0013).

**Negative / trade-offs**
- Hand-written SVG charts are less flexible than a charting library; acceptable for four chart types.
- The sample data is invented; it is labelled as such, and a test keeps the pages free of external URLs.
- Theme preference is per browser (not synced).

## Alternatives considered
- Tailwind/Bootstrap via CDN: blocked by CSP and by the offline promise.
- A charting library: adds a dependency and a build/vendoring step for little gain.
- OS-only dark mode: no user control, and the brand has two logo variants that deserve an explicit switch.

## Resumen (ES)
Un solo sistema de diseño con variables CSS (paleta tomada de los logotipos de Collaboration), modo claro y oscuro con botón, sin fuentes ni recursos externos. Un único tablero de resultados se usa en la landing (con datos de ejemplo etiquetados) y en el reporte final (con datos reales), para que nunca se contradigan.
