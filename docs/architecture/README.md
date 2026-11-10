# Architecture / Arquitectura

> **EN** — How Interview Lab is built and why. Every significant decision has an [ADR](adr/README.md).
> **ES** — Cómo está construido Interview Lab y por qué. Cada decisión importante tiene su [ADR](adr/README.md).

## 1. Goals and quality attributes

| Attribute | What it means here | How it is achieved |
|---|---|---|
| **Privacy (local-first)** | CVs, attempts and notes never leave the machine unless the user opts in. | No accounts, no telemetry, no database server; offline analysis; optional AI is off by default ([ADR-0002](adr/0002-local-first-single-process.md), [ADR-0011](adr/0011-optional-ai-generator-port.md)). |
| **Security** | The app compiles and runs code and downloads links. | Same-origin guard, SSRF-safe fetch, clean environment for graded code, hardened container ([ADR-0004](adr/0004-jvm-subprocess-grading-and-container-hardening.md), [ADR-0008](adr/0008-same-origin-guard.md), [ADR-0009](adr/0009-ssrf-safe-link-fetching.md)). |
| **Portability** | One command to run on Linux, macOS, Windows (WSL2). | Standard library only; Docker image; no build step ([ADR-0013](adr/0013-no-build-step-frontend.md)). |
| **Testability** | Rules testable without server, files or JVM. | Hexagonal layering with injected ports ([ADR-0003](adr/0003-hexagonal-layering.md)). |
| **Extensibility** | Users add exercises; teams add modules or generators. | Content is data (folders + JSON), generators are a port ([ADR-0005](adr/0005-content-model.md), [ADR-0011](adr/0011-optional-ai-generator-port.md)). |
| **Fairness & integrity** | Answers never reach the browser; exams are reproducible. | Server-side grading, seeded shuffles ([ADR-0007](adr/0007-exam-as-reproducible-definition.md)). |

Non-goals: multi-user hosting, cheating prevention (timers are client-side, see [ADR-0014](adr/0014-client-side-section-timers.md)), sandboxing hostile code.

## 2. System context (C4 level 1)

```mermaid
flowchart LR
    user(["Job seeker or trainer<br/>(browser on localhost)"])
    lab["Interview Lab<br/>local web application"]
    jvm[["JDK 21<br/>compiles and runs hidden tests"]]
    pages[["Public web pages<br/>(optional links)"]]
    ai[["AI provider<br/>(optional, user's own key)"]]
    user -->|"HTTP on 127.0.0.1"| lab
    lab -->|"javac / java subprocess"| jvm
    lab -. "fetch text, SSRF-safe" .-> pages
    lab -. "generate questions" .-> ai
```

## 3. Containers (C4 level 2)

Interview Lab is a **single process** plus a JVM child process per graded test, and a folder of JSON/Markdown files.

```mermaid
flowchart TB
    subgraph browser["Browser (vanilla HTML/JS, no build)"]
        landing["landing.html<br/>profile → exam wizard"]
        exam["exam.html<br/>sections + timers + report"]
        practice["index.html<br/>free practice"]
        common["common.js / common.css"]
    end
    subgraph proc["Python process (standard library)"]
        server["interview_lab.web<br/>HTTP server"]
    end
    subgraph jvmproc["Child processes"]
        javac["javac + java<br/>one JVM per hidden test"]
    end
    subgraph disk["Files"]
        builtin[("problems/ · bank/<br/>built-in content, CC BY 4.0")]
        workspace[("workspace/ (your data)<br/>problems · banks · exams · exam-attempts · runs")]
    end
    browser -->|"JSON over HTTP"| server
    server --> javac
    server --> builtin
    server <--> workspace
```

## 4. Components and layering (C4 level 3)

Dependencies point **inward**: `web → application → domain`. Adapters implement the ports declared by the application layer and are wired only in the composition root (`interview_lab/web/app.py`).

```mermaid
flowchart TB
    subgraph web["web — HTTP"]
        guard["RequestGuard<br/>Host / Origin / JSON"]
        routes["Routes + Handlers"]
        compose["compose()<br/>composition root"]
    end
    subgraph app["application — use cases"]
        analysis["AnalysisService"]
        examsvc["ExamService"]
        banksvc["BankService"]
        practice["PracticeService"]
        ports{{"Ports<br/>Catalog · ExamRepository · BankRepository<br/>UrlFetcher · QuestionGenerator · CodeGrader"}}
    end
    subgraph domain["domain — pure rules"]
        examrules["exam.py<br/>build · present · grade"]
        profile["profile.py<br/>CV / JD analysis"]
    end
    subgraph adapters["adapters — infrastructure"]
        fs["Fs* repositories + catalog"]
        grader["JavaCodeGrader → grader/grade.py"]
        fetcher["SafeUrlFetcher"]
        offline["OfflineQuestionGenerator"]
        anthropic["AnthropicQuestionGenerator<br/>(optional)"]
    end
    routes --> analysis & examsvc & banksvc & practice
    guard --> routes
    analysis --> profile
    examsvc --> examrules
    examsvc & banksvc & practice --> ports
    fs -.implements.-> ports
    grader -.implements.-> ports
    fetcher -.implements.-> ports
    offline -.implements.-> ports
    anthropic -.implements.-> ports
    compose --> adapters
```

## 5. Key flows

### 5.1 Build and take a tailored exam

```mermaid
sequenceDiagram
    actor U as User
    participant L as landing.html
    participant S as Server
    participant D as Domain
    participant FS as Catalog/Repo
    U->>L: paste CV or job description
    L->>S: POST /api/analyze
    S->>D: profile.analyze(text)
    D-->>L: seniority, language, version, modules
    U->>L: adjust options, press "Create"
    L->>S: POST /api/exams
    S->>FS: candidates()
    S->>D: exam.build(config, candidates)
    S->>FS: save(exam definition)
    S-->>L: exam without answers
    L->>U: redirect to exam.html
    loop each section (timer running)
        U->>S: POST /api/exams/{id}/section (answers)
        S->>D: grade_section(...)
        S-->>U: results + explanations
    end
    U->>S: POST /api/exams/{id}/finish
    S->>FS: append result
```

### 5.2 Grade code on the JVM

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as PracticeService
    participant G as JavaCodeGrader
    participant J as JVM (javac + java)
    B->>S: POST /api/grade {problem, code}
    S->>S: validate kind and size, store attempt
    S->>G: grade(problem, file, lang)
    G->>G: temp dir + Harness + clean environment
    G->>J: javac
    loop each hidden test
        G->>J: java Harness <test> (time and memory limits)
        J-->>G: RESULT line
    end
    G-->>S: report (score, what failed, why, how to improve)
    S-->>B: report in the user's language
```

### 5.3 Add a link to "My bank"

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as BankService
    participant F as SafeUrlFetcher
    participant Q as QuestionGenerator
    B->>S: POST /api/banks {urls, notes}
    S->>F: fetch_text(url)
    F->>F: validate scheme/port, resolve, require public IP, pin connection
    F-->>S: title, text, headings (or FetchError)
    S->>Q: generate(title, text, headings)
    alt generator fails
        S->>Q: offline fallback
    end
    S->>S: de-duplicate, save bank under workspace/banks
    S-->>B: summary (items, sources, errors, warnings)
```

## 6. Data model

All data are JSON files (see [ADR-0010](adr/0010-json-files-for-persistence.md)).

```mermaid
erDiagram
    EXAM ||--|{ SECTION : has
    SECTION ||--|{ ITEM_REF : lists
    ITEM_REF }o--|| PROBLEM : "code ref"
    ITEM_REF }o--|| QUIZ_QUESTION : "output ref"
    ITEM_REF }o--|| MCQ_QUESTION : "mcq ref"
    ITEM_REF }o--|| BANK_ITEM : "bank ref"
    BANK ||--|{ BANK_ITEM : contains
    EXAM ||--o{ RESULT : "finished as"
    EXAM {
        string id "YYYYMMDD-HHMMSS-xxxx"
        object config "seniority, language, version, modules, pace"
        int total_minutes
    }
    SECTION {
        string module
        int minutes
    }
    BANK {
        string id "b-xxxxxxxx"
        string generator "offline or anthropic"
    }
    RESULT {
        string exam
        int score
        int max
    }
```

An exam stores only **references** to items, never the items or answers; it is therefore small, reproducible and safe to expose (the browser receives items without answers).

## 7. Deployment

```mermaid
flowchart LR
    subgraph host["Your computer"]
        subgraph ctr["Docker container (optional but recommended)"]
            app["python3 server.py<br/>non-root, read-only FS<br/>caps dropped, CPU/mem/PID limits"]
            tmp["tmpfs /tmp<br/>(compile scratch)"]
        end
        vol[("./workspace → /data<br/>your data")]
        port["127.0.0.1:8765"]
    end
    browser["Browser"] --> port --> app
    app --> tmp
    app <--> vol
```

The port is published **only on loopback**. Exposing it to a network is explicitly unsupported (see [SECURITY](../SECURITY-MODEL.md)).

## 8. Front-end design layer (landing, brand, tokens)

The browser side is still static files with no build step ([ADR-0013](adr/0013-no-build-step-frontend.md)); the "Pro" redesign adds a thin design layer on top, all of it declarative:

| Piece | Where | Decision |
|---|---|---|
| Design tokens: blues, the three arc colours, gold, `--font-display` | `web/common.css` (both themes) | [ADR-0015](adr/0015-ui-design-system-and-results-dashboard.md), [ADR-0023](adr/0023-hosted-heading-typeface-and-gold-action-colour.md) |
| Heading typeface (Outfit, OFL, 24 KB) | `web/fonts/` + `ORIGEN.md`, served by `ASSETS` in `interview_lab/web/handlers.py` | [ADR-0023](adr/0023-hosted-heading-typeface-and-gold-action-colour.md) |
| Isotype definition (one `<defs>`, reused with `<use>`) and the brand-gated bar | `web/common.js` (`ISOTYPE_DEFS`, `installIsotype`, `brandBlock`), `isotype` key in `web/brand/brand.json` | [ADR-0022](adr/0022-scroll-driven-isotype-without-libraries.md) |
| Scroll-driven "O" layer (CSS keyframes tied to `animation-timeline`, one passive-scroll fallback) | `web/landing.html` (layer), `web/common.css` (keyframes), `web/landing.js` (`orbit()`) | [ADR-0022](adr/0022-scroll-driven-isotype-without-libraries.md) |

The landing page itself (`landing.html` + `landing.js`) is the profile → exam wizard plus marketing blocks whose figures are read from `/api/modules` and `/api/brand`, never typed by hand. `brand.json` declares the company name, tagline, PNG logos, the optional `isotype` and an optional `link` (empty until the owner confirms the domain).

## 9. Repository map

| Path | Layer / purpose |
|---|---|
| `interview_lab/domain/` | Pure rules: exam building/grading, CV/JD analysis |
| `interview_lab/application/` | Use cases, ports, errors |
| `interview_lab/adapters/` | Filesystem, JVM grader, URL fetcher, generators |
| `interview_lab/web/` | HTTP server, routes, security guard, composition root |
| `grader/` | JVM grading runtime (CLI + Java `Runner`/`Check`) |
| `problems/`, `bank/` | Built-in content (CC BY 4.0) |
| `web/` | Static front end (HTML, JS, CSS, brand, hosted heading typeface in `fonts/`) |
| `tools/` | `new_problem.py`, `validate.py`, `gen_quiz.py` |
| `tests/` | Domain, adapter, API and JVM tests |
| `docs/` | Architecture, ADRs, install, user guide, API, security model |

---

## Resumen (ES)
El sistema es **local primero**: un solo proceso Python (solo biblioteca estándar) que sirve páginas estáticas y una API JSON, lanza una JVM por prueba oculta y guarda todo en archivos JSON. El código sigue una **arquitectura hexagonal** (web → aplicación → dominio; los adaptadores implementan los puertos). Los exámenes guardan solo referencias a los ejercicios, las respuestas nunca llegan al navegador y el reparto de opciones es reproducible. Las decisiones están en los ADR enlazados arriba.
