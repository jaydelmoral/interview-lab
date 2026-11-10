# ADR-0004: Grade code in a JVM subprocess; harden with a container

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The core feature is compiling and running the candidate's Java and hidden tests, with timing, and explaining failures. User code is by nature arbitrary code execution.

## Decision
Each graded run uses a fresh temporary directory, compiles with `javac`, and runs **one JVM per hidden test** with a wall-clock timeout, `-Xmx256m`, no stdin and a **minimal environment** (the code cannot read the user's tokens in env vars). The recommended deployment is a container: non-root, read-only root filesystem, tmpfs scratch, all capabilities dropped, `no-new-privileges`, CPU/memory/PID limits, port on loopback only. Hidden test names are shown; results only after submitting.

## Consequences
**Positive**
- Per-test isolation gives accurate per-test timings and failures (an infinite loop cannot hide other results).
- Realistic feedback: the same toolchain interviews use.

**Negative / trade-offs**
- Not a sandbox for hostile code: without Docker the code can read what the user can read; in Docker it can use the network. Documented in the security model.
- JVM start-up cost per test (~25 ms each; acceptable).

## Alternatives considered
- In-process class loading (no isolation, no timeouts).
- Remote execution service (privacy and cost issues).
- WebAssembly/other sandbox for Java (immature for this use).

## Resumen (ES)
El código se compila y ejecuta en una JVM por cada prueba oculta, con límites de tiempo y memoria y sin variables de entorno del usuario. Se recomienda Docker endurecido. No es un sandbox para código hostil y así se documenta.
