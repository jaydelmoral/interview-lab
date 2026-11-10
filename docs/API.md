# HTTP API

Internal API used by the pages. JSON in, JSON out. All `POST`/`DELETE` requests need `Content-Type: application/json` (for `POST`) and a same-origin `Origin` header (see [ADR-0008](architecture/adr/0008-same-origin-guard.md)).
`lang` (`es` | `en`) can be sent as a query parameter (GET) or in the body (POST); it localizes explanations and feedback.

Errors: `{"error": "message", ...details}` with status `400` invalid request, `403` forbidden origin/host or feature disabled, `404` not found, `413` too large, `415` wrong content type, `422` valid request that cannot be fulfilled, `500` unexpected.

## Pages and assets
| Method | Path | Notes |
|---|---|---|
| GET | `/`, `/practice`, `/exam?id=…` | HTML pages |
| GET | `/common.js`, `/common.css`, `/theme.js`, `/editor.js`, `/brand/<file>`, `/vendor/monaco/vs/...` (only if installed) | static assets |
| GET | `/api/brand` | name, tagline, logo files (replaceable white-label) |

## Catalog and analysis
| Method | Path | Body → Response |
|---|---|---|
| POST | `/api/analyze` | `{text}` or `{filename, data(base64)}` (`.txt`/`.md`/`.docx`, ≤ 4.5 MB) → `{language, version, seniority, years, modules[{id,score,hits}], coming[], language_counts}`. Nothing is stored. |
| GET | `/api/modules` | → `{modules[{id,title,count}], coming[], fetch, ai, generator}` |

## Exams
| Method | Path | Body → Response |
|---|---|---|
| POST | `/api/exams` | `{seniority: jr\|mid\|sr, language, version, modules[], pace: tight\|standard\|relaxed, banks[], counts{module:n}, title}` → public exam (no answers). `400` no modules; `422` nothing to build (with `notes`). |
| GET | `/api/exams` | → list with config, total minutes and last result |
| GET | `/api/exams/{id}` | → public exam |
| POST | `/api/exams/{id}/section` | `{section: index, answers{key: value}, attempt?}` → `{score, max, items[{key, correct, expected, explanation, expected_index?, tags}], weak[]}`. With `attempt` (32 hex chars) each section is graded once per attempt: asking again returns the first report; `400` after the attempt is finished. Values: MCQ = displayed option index (or list), output = text, flashcard = `"know"`/`"dont"`. |
| POST | `/api/exams/{id}/finish` | `{sections[{module, score, max}]}` → stored result. With `attempt`: `{attempt, sections[{section: index, title?, used?}], lang?}`; scores, totals and missed questions are computed from what the server graded (client values are ignored), and finishing twice returns the stored result without recording another run ([ADR-0021](architecture/adr/0021-server-side-exam-attempts.md)). |

Public item shapes: `code {key,type,id,title,minutes}`, `output {key,type,topic,code}`, `mcq {key,type,q,options[],multi}`, `flash {key,type,q,a}`.

## Memory banks
| Method | Path | Body → Response |
|---|---|---|
| GET | `/api/banks` | → `[{id,title,created,items,sources[]}]` |
| POST | `/api/banks` | `{title, urls[] (≤5), notes}` → `{id, title, items, sources[], errors[], warnings[], generator}`. `403` if fetching disabled; `422` if nothing could be built. |
| DELETE | `/api/banks/{id}` | → `{deleted}` |

## Free practice
| Method | Path | Body → Response |
|---|---|---|
| GET | `/api/problems` | → list of problems and the quiz |
| GET | `/api/problems/{id}` | → statement (EN and ES), starter code, test names; or quiz questions |
| POST | `/api/grade` | `{problem, code (≤ 50 KB), exam?, attempt?}` (with both, the best score of the exercise is kept for that exam attempt; `400` if the exercise is not in the exam) → report `{score, max, compile, tests[{id,title,passed,ms,detail,fail_why,fail_how}]}` |
| POST | `/api/quiz` | `{problem, answers{id: text}}` → `{score, max, results[]}` |

## Runtimes / Entornos instalados
| Method | Path | Description |
|---|---|---|
| GET | `/api/runtimes` | Read-only list of languages/tools detected on this machine (`id`, `installed`, `version`, `grader`, `install_hint`). The web app cannot install anything; use `python3 install.py` at setup time (ADR-0019). |

## History and analytics / Historial
| Method | Path | Description |
|---|---|---|
| GET | `/history` | History page (dashboard) |
| GET | `/api/history` | Aggregated analytics for the local profile: `kpis`, `trend`, `modules` (weakest first), `weak_tags`, `code`, `recent` |
| GET | `/api/history/runs/{id}` | One finished exam with its sections and missed questions |
| POST | `/api/exams/{id}/finish` | Body: `sections[{module,title,score,max,pct,correct,total,used,allotted}]` and optional `missed[{section,q,expected,explanation,tags}]`. Stores the result (JSONL + SQLite). Every field is validated and clamped. |
