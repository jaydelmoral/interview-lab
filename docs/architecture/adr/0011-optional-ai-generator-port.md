# ADR-0011: Optional AI question generator behind a port, with the user's own key

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Javier Morales Barrera, Claude

## Context
The offline generator (cloze questions and flashcards) is limited. AI can produce better questions, but the project is public: it must never embed the author's API key, never bill the author, and never send data off the machine without the user's opt-in.

## Decision
`QuestionGenerator` is a port. The default adapter is offline. `AnthropicQuestionGenerator` is enabled only when the **user** sets `ILAB_AI_PROVIDER=anthropic` and their own `ANTHROPIC_API_KEY`, and installs the SDK (lazy import, optional dependency). The model reply is untrusted: it must be a JSON array of questions validated for shape and size; any failure falls back to the offline generator with a warning; provider error details are not leaked. The UI states which generator is active and where text goes.

## Consequences
**Positive**
- Clean extension point; costs and privacy remain the user's choice.
- No secret in the repository; failure-tolerant.

**Negative / trade-offs**
- Quality of AI questions depends on the model; facts are not verified against the source beyond the prompt rules.

## Alternatives considered
- Hard-coded hosted AI endpoint operated by the author (cost and privacy liability).
- No AI at all (limits usefulness).

## Resumen (ES)
La generación con IA es un puerto opcional: apagado por defecto y activo solo si el usuario pone su propia llave. Nunca se publica ni se usa una llave del autor. Si la IA falla, se usa el generador local.
