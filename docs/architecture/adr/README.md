# Architecture Decision Records

An ADR captures one significant decision: its context, the decision, and the consequences. ADRs are numbered and immutable once accepted; a later ADR can *supersede* an earlier one.
Un ADR documenta una decisión significativa: contexto, decisión y consecuencias. Son inmutables una vez aceptados; uno nuevo puede reemplazar a uno anterior.

| # | Decision | Status |
|---|---|---|
| 0001 | [Record architecture decisions](0001-record-architecture-decisions.md) | Accepted |
| 0002 | [Local-first, single process, standard library only](0002-local-first-single-process.md) | Accepted |
| 0003 | [Hexagonal (ports and adapters) layering](0003-hexagonal-layering.md) | Accepted |
| 0004 | [Grade code in a JVM subprocess; harden with a container](0004-jvm-subprocess-grading-and-container-hardening.md) | Accepted |
| 0005 | [Content as data: folders, JSON, bilingual Markdown](0005-content-model.md) | Accepted |
| 0006 | [Offline, heuristic analysis of CVs and job descriptions](0006-offline-profile-analysis.md) | Accepted |
| 0007 | [An exam is a reproducible definition of references; answers stay on the server](0007-exam-as-reproducible-definition.md) | Accepted |
| 0008 | [Same-origin guard instead of authentication](0008-same-origin-guard.md) | Accepted |
| 0009 | [SSRF-safe link fetching for the personal bank](0009-ssrf-safe-link-fetching.md) | Accepted |
| 0010 | [JSON files for persistence](0010-json-files-for-persistence.md) | Accepted |
| 0011 | [Optional AI question generator behind a port, with the user's own key](0011-optional-ai-generator-port.md) | Accepted |
| 0012 | [Licensing: Apache-2.0 code, CC BY 4.0 content, reserved brand](0012-content-licensing-and-brand-policy.md) | Accepted |
| 0013 | [Vanilla HTML/JS front end without a build step](0013-no-build-step-frontend.md) | Accepted |
| 0014 | [Section timers run in the browser](0014-client-side-section-timers.md) | Accepted |
| 0015 | [Design system with light/dark themes and one results dashboard](0015-ui-design-system-and-results-dashboard.md) | Accepted |
| 0016 | [No external contributions until a CLA; premium content in separate private repos](0016-contribution-policy-and-premium-content-separation.md) | Accepted |
| 0017 | [SQLite history and analytics, per profile](0017-sqlite-history-and-analytics.md) | Accepted |

## Template

```markdown
# ADR-NNNN: Title
- **Status:** Proposed | Accepted | Superseded by ADR-XXXX
- **Date:** YYYY-MM-DD
- **Deciders:** names

## Context
What forces are at play?

## Decision
What we will do.

## Consequences
**Positive** ... **Negative / trade-offs** ...

## Alternatives considered

## Resumen (ES)
Una o dos frases.
```
