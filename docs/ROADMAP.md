# Roadmap

Done in 1.0 / Hecho en 1.0: tailored exam builder, section timers, 9 modules (coding, output quiz, SQL, QA, microservices, DevOps, architecture, security, Unix), bilingual UI with Spanish help, personal bank (links, notes), optional AI generator port, hexagonal architecture, ADRs and diagrams.

Next, in rough priority order / Siguiente, en orden aproximado:
- [ ] More content per module (today 5 questions each) and Python/JavaScript coding exercises with their own graders (the grader is behind a port). / Más contenido por módulo y ejercicios de código en Python/JavaScript.
- [x] Local AI question generator through Ollama (loopback-only, optional) — done, tested with qwen3.5:9b. / IA local con Ollama — hecho.
- [ ] AI / LLM module (prompting, RAG, evaluation questions). / Módulo de IA y LLMs.
- [ ] SQL exercises with a real local engine; PostgreSQL / MySQL / Oracle dialect differences. / Ejercicios de SQL con motor local.
- [ ] JUnit 5 + Mockito: write tests for a class, graded with mutants. Needs Maven. / JUnit con mutación.
- [ ] BDD / Cucumber and functional tests (Spring Boot Test, MockMvc / RestAssured). / BDD y pruebas funcionales.
- [ ] "Broken microservices": multi-file project that does not compile. / Microservicios rotos.
- [ ] Spoken-English practice (text first, voice later). / Práctica oral en inglés.
- [ ] Weakness dashboard across attempts (`workspace/runs`). / Panel de debilidades.
- [ ] Import / export an exercise or bank as a `.zip` from the UI. / Importar y exportar como `.zip`.
- [ ] Network-isolated grading inside Docker. / Calificación sin red.
- [x] PDF support for CV analysis through the system `pdftotext` (optional) — done. / PDF — hecho.
- [ ] Spaced repetition for personal-bank flashcards. / Repaso espaciado.

## Decisions and backlog added 2026-11-10 / Decisiones y pendientes (2026-11-10)

**Release scope / Alcance del primer release:** **local only**, single user on their own machine; each user is responsible for the data and software they load. No hosted service, no accounts, no personal-data processing by the project. A cloud edition is a later, separate refactor (see below). / Solo local; cada usuario es responsable de lo que carga e instala. La nube es un refactor posterior.

**MUST-HAVE (question bank) / Obligatorio:** every question carries a **source** (link to official documentation) and a **review status** (`draft` → `reviewed` + reviewer + date). The validator rejects questions without a source; unreviewed questions are flagged in the UI. A wrong grade destroys trust. / Cada pregunta con fuente oficial y estado de revisión; el validador rechaza las que no la tengan.

**Next / Siguiente**
- [x] SQLite history (`workspace/ilab.db`) with `profile_id` from day 1 — done, see ADR-0017. / Historial en SQLite — hecho.
- [x] Analytics dashboard (`/history`): trend, per module, weak topics, time used vs allotted, per-exercise progress — done. / Tablero de analítica — hecho.
- [x] Question bank: sources + review status mandatory (validator, ADR-0018); 276 senior/staff/principal questions written into a separate private pack (all `draft`, awaiting human review). / Banco con fuentes — hecho; falta la revisión humana.
- [ ] Human review pass of the draft questions (`tools/mark_reviewed.py`).
- [x] In-browser editor: **Monaco** (optional, pinned + hash-verified install, autocomplete off) — done, ADR-0020. / Editor Monaco — hecho.
- [ ] HackerRank-style *Run* (sample cases) vs *Submit* (hidden tests) and a language picker.
- [x] Runtime registry + `python3 install.py` (confirmation, no shell, never from the web UI) and read-only detection in the app — done, ADR-0019. Next: a Python code grader that uses it. / Instalador — hecho; falta el calificador de Python.
- [ ] Document "desktop-first": no mobile work (real interviews use a laptop). / Diseñado para escritorio.
- [ ] Privacy notice in README: nothing leaves your machine; you are responsible for the CV and links you load. / Aviso de privacidad local.

**Later (cloud edition) / Después (nube)** — only after the local release works:
- [ ] ADR "local edition vs cloud edition", threat model and a design doc **before** any public exposure.
- [ ] Sandboxed code execution (containers, no network, non-root, CPU/memory/time limits, separate host from the data).
- [ ] Authentication: do **not** hand-roll. Preferred: a managed or self-hosted OIDC provider (e.g. Keycloak, Auth0, Cognito, Supabase Auth) with Google/GitHub sign-in, passkeys (WebAuthn) and TOTP; if passwords are stored, `argon2id`, email verification, rate limiting and lockout.
- [ ] Postgres migration (the SQLite schema already carries `profile_id`).
- [ ] Pricing model: monthly plan with included attempts + extra packs; cost budget (cloud + AI) and per-user quotas; payment through a processor (never handle card data).
- [ ] Privacy-law review (personal data in CVs) and terms of service before offering a hosted service.
- [ ] Licence strategy decided **before** publishing (see `docs/architecture/adr/0012` and the open-core discussion): premium question packs live in a separate private repo, never in the public history. DCO is not enough to dual-license later: **no external PRs until a CLA exists** (see ADR-0016).
