# Content packs / Paquetes de contenido

**EN** — Each folder here is an optional *content pack*: extra exercises and questions that the app loads in addition to the built-in sample content. A pack is its **own, separate git repository** (clone it into `packs/<name>/`); this directory is git-ignored by the main repository, so a pack's files can never end up in the main repo's history. Premium or private banks live in packs, never in `bank/` or `problems/`.

A pack looks like:
```
packs/<name>/
  pack.json            {"name": "...", "version": "1.0.0", "license": "...", "description": "..."}
  questions/*.json     same format as bank/questions (see docs/CONTENT-GUIDELINES.md)
  problems/<id>/...    optional coding exercises
```

**ES** — Cada carpeta aquí es un *paquete de contenido* opcional: ejercicios y preguntas extra que la app carga además del contenido de muestra. Un paquete es **su propio repositorio git, aparte** (se clona en `packs/<nombre>/`); este directorio está ignorado por el repositorio principal, así que sus archivos nunca llegan al historial del repo principal. Los bancos premium o privados viven en paquetes, nunca en `bank/` ni en `problems/`.

Run `python3 tools/preflight.py` before pushing: it fails if anything under `packs/` (or personal `workspace/` data) was ever committed.
