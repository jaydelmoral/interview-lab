# Content guidelines / Guía de contenido

**EN** — Read this before adding or publishing exercises. **You are responsible for the rights to the content you add.**
This guide is practical advice, not legal advice; when in doubt, ask a lawyer.

**ES** — Léela antes de agregar o publicar ejercicios. **Eres responsable de los derechos del contenido que agregues.**
Esta guía es orientación práctica, no asesoría legal; ante la duda, consulta a un abogado.

## 1. Write your own wording / Escribe con tus palabras
| Allowed / Permitido | Not allowed / No permitido |
|---|---|
| The *idea* (e.g. “find two items that add up to a value”, binary search, LRU cache). | Copying a statement, its examples, its test names or its datasets from a platform, book or course, even translated. |
| Your own story, names, numbers, class and method names. | Reusing the exact title + examples of a famous problem. |
| Telling a friend’s interview question **in your own words, with a different setting**. | Publishing questions from an interview you took under an NDA, or a company’s proprietary test. |

Platform terms of service usually forbid copying their content. Names of platforms in your exercises are flagged by `tools/validate.py`.
ES: las condiciones de uso de las plataformas suelen prohibir copiar su contenido. El validador avisa si las nombras.

## 2. Convert companies to a sector / Convierte las empresas en un giro
Keep the *kind of business* (it helps the learner understand the domain) but drop the name.
Conserva el *tipo de negocio* (ayuda a entender el dominio) pero quita el nombre.

| Instead of / En vez de | Write / Escribe |
|---|---|
| American Airlines, Aeroméxico | airline / aerolínea |
| Amazon, Mercado Libre | e-commerce / comercio electrónico |
| BBVA, Santander | bank / banco |
| Telcel, AT&T | telecom / telecomunicaciones |
| Walmart, Oxxo | retail / comercio minorista |
| FedEx, DHL | logistics / logística |
| Netflix, Spotify | streaming |

`tools/brands.json` holds the list used by the validator; extend it freely. If a name is legitimately technical (e.g. “Oracle” as a SQL dialect),
allow it in that problem’s `meta.json` with `"lint_allow": ["oracle"]`.

Also change anything that could identify a company indirectly: internal system names, ticket numbers, people’s names, real product codes, real prices or volumes.
Cambia también lo que identifique a una empresa de forma indirecta: nombres de sistemas internos, números de ticket, nombres de personas, códigos de producto, precios o volúmenes reales.

## 3. Never include / Nunca incluyas
- Personal data (names, emails, phones, IDs) of anyone. / Datos personales de nadie.
- Secrets: tokens, keys, internal URLs. / Secretos: tokens, llaves, URLs internas.
- Confidential information of a current or former employer or client. / Información confidencial de un empleador o cliente, actual o anterior.
- Your own attempts from real tests (they live in `workspace/runs/`, which git ignores). / Tus intentos de pruebas reales (están en `workspace/runs/`, que git ignora).

## 4. Licenses / Licencias
Built-in content is CC BY 4.0 (`LICENSE-CONTENT.md`). Content you keep in your `workspace/` is yours. If you contribute it to this project, you license it as CC BY 4.0 (see `CONTRIBUTING.md`).
Set `author` and `license` in each `meta.json`.

## 5. Checklist before publishing / Lista antes de publicar
- [ ] My statement, examples, names and data are mine. / Mi enunciado, ejemplos, nombres y datos son míos.
- [ ] No company, platform or person is named. / No nombro empresas, plataformas ni personas.
- [ ] No NDA-covered or confidential material. / Nada cubierto por NDA ni confidencial.
- [ ] `python3 tools/validate.py` shows no warnings. / El validador no muestra avisos.
- [ ] EN and ES statements and feedback exist. / Existen enunciados y retroalimentación en EN y ES.

## Multiple-choice questions: sources and review (mandatory) / Preguntas de opción múltiple: fuentes y revisión (obligatorio)
Every question in `bank/questions/*.json` (and in any content pack) must carry:
```json
"sources": [{"title": "PostgreSQL: Transaction isolation", "url": "https://www.postgresql.org/docs/current/transaction-iso.html"}],
"review":  {"status": "draft", "author": "who wrote it", "date": "2026-11-10"}
```
- Cite **official documentation** (or the standard/RFC) that supports the facts; never copy question wording from interview sites, books or courses.
- New questions start as `draft`. After a person checks the answer against the sources: `python3 tools/mark_reviewed.py --file bank/questions/sql.json --ids sql-001 --reviewer "Name"`.
- `python3 tools/validate_bank.py` fails on missing sources or review data; add `--online` to check that the links answer.
- Levels: `jr`, `mid`, `sr`, `staff`, `principal`. Premium or large banks go in a **content pack** (`packs/`, see `packs/README.md`), never in `bank/`.
