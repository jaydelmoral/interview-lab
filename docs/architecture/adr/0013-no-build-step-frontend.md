# ADR-0013: Vanilla HTML/JS front end without a build step

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The UI is a few pages (wizard, exam runner, free practice). A framework and bundler would add a toolchain, dependencies and supply-chain surface to a project whose selling points are simplicity and trust.

## Decision
Static HTML pages with small vanilla-JS scripts and one shared `common.js`/`common.css`; no npm, no bundling. A strict CSP (`default-src 'none'`, scripts/styles from self plus inline, images from self) and output escaping (`esc()`) on every dynamic value. Light/dark theme follows the OS (`prefers-color-scheme`), including the logo variants.

## Consequences
**Positive**
- Nothing to install or compile; the whole front end is readable in minutes.
- Small attack surface.

**Negative / trade-offs**
- No component model or type checking; some duplication between pages (mitigated by `common.js`).
- Inline scripts require `'unsafe-inline'` in the CSP.

## Alternatives considered
- React/Vue + Vite (productive, but a toolchain and many dependencies).
- Server-side templates (more server code, less interactive timers).

## Resumen (ES)
El front end es HTML y JavaScript sin paso de compilación ni npm: nada que instalar, superficie de ataque pequeña y una política CSP estricta. El costo es menos estructura que con un framework.
