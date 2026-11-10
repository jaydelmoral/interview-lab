# ADR-0022: Isotype animated with the scroll, without libraries

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
The landing is the first thing a visitor sees and it should look like a professional product. The owner's company mark (the "O" of Collaboration: three crescents) is the natural centrepiece, and the owner asked for it to follow the page: it starts **closed** so the brand is recognised, comes apart while scrolling and closes again over the final section. Constraints already in force: no build step and no libraries (ADR-0013), a CSP with `script-src 'self'` and no inline scripts, offline-first (no external assets, ADR-0006), and a light footprint. The reference idea (an object that animates as you scroll) usually ships with WebGL or an animation library.

## Decision
- **One definition, many uses.** The three crescents, the glint and their gradients are defined once (`ISOTYPE_DEFS` in `web/common.js`, injected as a 0×0 inline `<svg><defs>`) and reused with `<use href="#oA">` by the app bar (every page), the animated layer and the three "how it works" cards. A brand opts in with `"isotype": "collaboration-o"` in `web/brand/brand.json`; without it the bar keeps the PNG logo and the layer is not shown, so a rebrand never leaves another company's mark behind. (The orbit layer's markup is in `landing.html`; the path data lives in `common.js` because the bar of the other three pages needs it too.)
- **One variable, plain keyframes.** All movement is five ordinary 1-second `@keyframes` (stage, three arcs, glint) that the scroll "rubs": `animation-timeline: scroll(root block)` inside `@supports`. The browser moves the animation; there is no per-frame JavaScript. Only `transform` and `opacity` are animated; no filters, shadows or `backdrop-filter` on the layer; `will-change: transform` only on the five animated elements and only while `orbit-on` is set.
- **Fallback path.** Without `animation-timeline`, `landing.js` adds `orbit-js` and a single passive, `requestAnimationFrame`-throttled scroll listener writes `--p` (0..1); the paused animation is placed with `animation-delay: calc(var(--p) * -1s)`. The same keyframes drive both paths. `?fallback` forces this path for testing (the native rule is disabled under `.orbit-js`).
- **Static states.** With `prefers-reduced-motion: reduce`, no JavaScript, or an error, `orbit-on` is never added: the layer stays `position: absolute` in the header with the O closed and still, and scrolls away with the page.
- **Layer mechanics.** The layer is one screen tall (`100svh`), `position: sticky; top: 0; margin-bottom: -100svh`, the first child of `.wrap`, so it follows all the content and is released together with the end of `.wrap`, exactly over the closing section (`min-height: 100svh`). `body { overflow-x: clip }` hides the sideways travel (never `overflow: hidden`, which breaks sticky). The closing section's top padding is computed from the O's own size so the text never sits under it.
- **Legibility rule.** The O is at 100 % opacity only in the header and in the closing; behind text it never exceeds 0.18 once the page is past the dashboard. While the sample dashboard is on screen (about 4–24 % of the progress) the O is a visible but soft glow (0.7 at 10 %, 0.38 at 16 %, lower than the first design's 0.9 and 0.5) because the landing's cards, the dashboard and its panels are **translucent glass** (`--glass`, about 52–60 % of the surface colour, no `backdrop-filter`) so the movement shows through; the figures sit on the denser panels.
- **Header height and alignment.** The header is capped at 700 px (`--hero-h`) instead of filling tall screens, and the closed O is levelled with the header text through `--sh` in the first keyframes (the offset fades out by 24 %).
- **Scroll anchoring off.** The bar and the texts are filled in by JavaScript after load; with the browser's scroll anchoring on, every refresh pushed the page further down. `overflow-anchor: none` on the landing's root fixes it.
- **Phones (≤ 860 px).** Same mechanism with its own stage keyframes. The progress is a share of the *whole page*, and a phone page is about 13 000 px tall, so the phone keyframes fade the O to a watermark within the first ~250 px (the percentages of the desktop keyframes would leave an opaque O above the scrolling header text) and bring it back during the last screen before the closing.

## Measured (2026-11-10)
| What | Budget | Measured |
|---|---|---|
| O and panels: SVG defs + layer + CSS + JS, comments and indentation excluded | 12 KB | **10 844 B** (O CSS 3 705 · panel CSS 2 794 · defs 1 143 · orbit JS 721 · panel JS 1 921 · layer 560) |
| Scroll listeners | ≤ 1, passive, fallback only | 1 (fallback only) |
| Animated properties | `transform`, `opacity` | exactly those (tested) |

A test (`tests/test_content.py::TestLandingPro`) fails if the budget, the animated properties or the listener count regress.

## Consequences
**Positive**
- A distinctive, on-brand landing with no dependency, no build step and no CSP change; the native path costs no JavaScript while scrolling.
- Graceful degradation in three directions (no `animation-timeline`, reduced motion, no JavaScript).
- The isotype is reusable (bar, step cards) and brand-gated.

**Negative / trade-offs**
- The progress is a percentage of the page, so the timing depends on page height. The desktop keyframes come from the approved design; the phone ones were calibrated to today's page length and need a second look if the page grows or shrinks a lot.
- Keyframes are hand-tuned numbers, not a general animation system.
- The path data of the mark lives in `common.js` (not in `landing.html`) to avoid duplicating it on every page.

## Alternatives considered
- **WebGL / Three.js:** heavy, needs a library, overkill for a flat vector mark.
- **Animation libraries (GSAP, Lenis, Lottie):** break ADR-0013 and add weight and supply-chain surface for something CSS does natively.
- **Pre-rendered video:** large, not themeable (light/dark, brand tokens), blurry on high-density screens and impossible to scrub accurately.
- **`<canvas>` or per-frame JavaScript:** more code and main-thread work than the declarative timeline.
- **Animating `top`/`left`/`width`/`filter`:** triggers layout or paint on every frame.

## Resumen (ES)
La "O" de Collaboration (tres arcos) acompaña toda la landing: empieza cerrada, se desarma al bajar y se cierra sobre la sección final. Se define una sola vez en SVG y todo el movimiento son cinco `@keyframes` de CSS ligados al desplazamiento (`animation-timeline`), sin librerías ni JavaScript por cuadro; si el navegador no lo soporta, un único oyente pasivo de scroll hace lo mismo. Con movimiento reducido queda cerrada y quieta. Pesa 10.8 KB (tope 12 KB) y solo anima `transform` y `opacity`. En móvil los fotogramas se calibraron al largo real de la página (~13 000 px).
