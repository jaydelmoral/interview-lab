# ADR-0008: Same-origin guard instead of authentication

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The server binds to localhost and executes submitted code. Any web page open in another browser tab can send requests to `http://localhost:PORT` (cross-site request forgery) or rebind a hostname to 127.0.0.1 (DNS rebinding). The first version only checked `Host`, so a malicious page could still POST code.

## Decision
Every request must pass `RequestGuard`: allowed `Host` (blocks DNS rebinding), allowed `Origin` when present (blocks cross-origin POSTs; `Origin: null` is rejected), and `Content-Type: application/json` for POST (browsers cannot send it cross-origin without a preflight, which we never answer). Responses carry `Content-Security-Policy`, `X-Frame-Options: DENY`, `nosniff`, `no-referrer`, `no-store`. No login: a single-user local tool has no second identity to authenticate.

## Consequences
**Positive**
- Closes a real drive-by code-execution path found during review; covered by API tests.
- No password UX, no session storage.

**Negative / trade-offs**
- Not suitable for multi-user or networked deployments (explicit non-goal; changing `ILAB_HOST` is the operator's responsibility).

## Alternatives considered
- Random token in a header/cookie (works, but needs bootstrapping the token into the page and adds state).
- HTTP basic auth (poor UX, no CSRF protection by itself).

## Resumen (ES)
Cada petición debe venir de nuestro propio sitio: se verifican Host y Origin y se exige JSON. Así otra pestaña no puede mandar código a tu equipo. No hay login porque es una herramienta local de un solo usuario.
