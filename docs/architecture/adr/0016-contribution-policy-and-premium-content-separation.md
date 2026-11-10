# ADR-0016: No external contributions until a CLA exists; premium content lives in separate private repositories

- **Status:** Accepted
- **Date:** 2026-11-10
- **Deciders:** Javier Morales Barrera, Claude

## Context
The maintainer wants to give the engine to the world **and** keep the option of a paid business (premium question banks, hosted service, commercial licence). Two facts make that fragile if not handled now:
1. Git history is permanent: any premium file committed once to a repository that later becomes public is public forever.
2. Under the Developer Certificate of Origin (ADR-0012) a contributor keeps their copyright and licenses it under the project's open licence. The maintainer then **cannot** relicense or dual-license that contribution commercially without asking every contributor.

## Decision
1. **Premium and private content never enters this repository.** It lives in *content packs* (`packs/<name>/`), each its own private git repository, loaded at runtime. `packs/*` and `workspace/*` are git-ignored; `tools/preflight.py` fails if anything under them (or `.env`, secrets, personal paths, oversized files) is tracked **or exists anywhere in history**. It runs in CI and as a local `pre-push` hook.
2. **No external pull requests until a CLA exists.** Issues and discussions are welcome; the maintainer writes the final content. A CLA (reviewed by an IP lawyer) will let the project keep relicensing options; the DCO remains as a second, origin-only layer.
3. The final split between free sample content and premium packs, and the engine's licence (Apache-2.0 vs AGPL-3.0 with a commercial option), are decided **before the repository becomes public**.

## Consequences
**Positive**
- Nothing premium can leak through git history by accident; the guard is automatic.
- Commercial options stay open (dual licensing, premium packs, hosted service).

**Negative / trade-offs**
- Slower community growth (no PRs at first).
- A CLA adds friction for contributors once it opens.
- Pack authors must remember to keep the pack in its own repository (the guard catches mistakes, it cannot replace judgement).

## Alternatives considered
- Keep everything in one repository and filter at publish time: one forgotten file or branch makes it permanent.
- DCO only: simple, but forecloses commercial relicensing.

## Resumen (ES)
El contenido premium y privado nunca entra a este repositorio: vive en paquetes (`packs/`), cada uno un repo privado aparte, y `tools/preflight.py` bloquea cualquier push si algo privado aparece en archivos o en el historial. Hasta que exista un CLA no se aceptan pull requests, para no perder la posibilidad de licenciar comercialmente. La licencia final del motor y la frontera gratis/premium se deciden antes de volver público el repo.
