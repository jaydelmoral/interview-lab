# ADR-0020: Optional Monaco editor, installed at setup time from a pinned, hash-verified archive

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
Practising for interviews on HackerRank-style platforms means a real code editor (line numbers, syntax highlighting, familiar keys). The plain `<textarea>` works but feels poor. Full VS Code in the browser (code-server) was rejected: heavy and a large attack surface. Monaco (the editor component of VS Code, MIT) is the lightweight option, but it is about 25 MB: committing it would bloat the repository, and fetching it from a CDN at runtime would break the no-external-assets rule (ADR-0006).

## Decision
- Monaco is **optional** and **not in the repository**. `python3 tools/fetch_monaco.py` downloads a **pinned version** (`0.57.0`) from the official npm registry, **verifies its SHA-512** against the value pinned in the script (a mismatch aborts before extracting), extracts only `min/vs` and the licence files with path checks, into the git-ignored `web/vendor/monaco/`.
- The server exposes it through a read-only route confined to that folder (`/vendor/monaco/vs/...`, no `..`, known extensions only).
- CSP gains `font-src 'self' data:` (Monaco's icon font is embedded) and `worker-src 'self' blob:` (editor web workers). Everything stays same-origin; no external hosts are allowed.
- `web/editor.js` attaches Monaco to the existing textarea and redirects the textarea's `value` to the editor, so all other code is unchanged. If Monaco is missing or fails to load, the page silently keeps the textarea.
- Interview mode: autocompletion, hints and hover are off (a plain whiteboard); the theme follows the light/dark switch.

## Consequences
**Positive**
- Familiar editor experience with zero impact on the repository or on users who skip it; integrity of the download is verified.
- The pinned-hash pattern is reusable for other optional vendored assets.

**Negative / trade-offs**
- One more optional setup step; a version bump means updating the pinned hash deliberately.
- The CSP is slightly wider (fonts and workers), still without external origins.
- Monaco is large and is served without caching headers (the app sends `no-store`); fine on loopback, slower through a tunnel.

## Alternatives considered
- code-server / OpenVSCode Server: too heavy, larger attack surface.
- CDN: breaks local-first and the CSP.
- Commit Monaco into the repository: bloats history permanently.

## Resumen (ES)
Monaco (el editor de VS Code) es opcional y no vive en el repo: `python3 tools/fetch_monaco.py` descarga una versión fijada, verifica su hash SHA-512 y la guarda en una carpeta ignorada por git. Si no está instalado, la app sigue con el cuadro de texto. La política de seguridad solo agrega fuentes y workers del mismo origen.
