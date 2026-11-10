# ADR-0009: SSRF-safe link fetching for the personal bank

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
Users paste links to build study questions. Server-side fetching of user-provided URLs is a classic SSRF risk: it could reach `localhost`, the LAN or cloud metadata endpoints (169.254.169.254).

## Decision
`SafeUrlFetcher` allows only `http`/`https`, ports 80/443, no credentials in the URL; resolves the host and **requires every address to be public** (`ipaddress.is_global`); **pins the TCP connection to the validated IP** (so DNS cannot change between check and use) while keeping SNI/Host; re-validates on each redirect (max 3); limits size (1.5 MB), time (8 s) and content types (HTML/plain text). Fetching can be disabled with `ILAB_ALLOW_FETCH=0`.

## Consequences
**Positive**
- Blocks loopback, private, link-local and metadata addresses (tested, including a redirect to loopback).
- Content is stored locally only.

**Negative / trade-offs**
- Cannot read pages that require login or JavaScript rendering, nor PDFs.
- Copyright of fetched content remains the user's responsibility (documented).

## Alternatives considered
- Fetch in the browser (CORS blocks most pages).
- Allow-list of domains (too restrictive for study material).

## Resumen (ES)
La lectura de enlaces solo permite http(s), puertos 80/443 y direcciones públicas, fija la conexión a la IP ya validada, revalida las redirecciones y limita tamaño y tiempo. Protege contra SSRF; se puede desactivar.
