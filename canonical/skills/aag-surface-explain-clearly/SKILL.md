---
name: aag-surface-explain-clearly
description: Use only when the user explicitly invokes aag-surface-explain-clearly or asks to use this explanation skill.
invocation: explicit
---
# Explain clearly

## Purpose

Make technical behavior understandable and verifiable without assuming prior knowledge of the project's language, framework, or tooling.

## Procedure

1. Identify the question being answered. Assume general software engineering experience and limited familiarity with the current stack unless the conversation establishes otherwise.
2. Inspect the relevant implementation before describing its behavior. Lead with a direct answer and explain why it matters. If no implementation is available, identify the explanation as conceptual.
3. Scale the explanation to the question. For behavior or flow questions, use a concrete example and follow its input, processing, state changes, and output in execution order. A simple factual question may need only a direct answer; examples are required for discussed data models and interfaces as described below.
4. Link code references to existing files and verified line numbers. In local environments, use clickable Markdown links with absolute file paths and a starting line number, such as `[descriptive label](/absolute/path/file.ext:42)`, replacing the example with an inspected location. Use stable repository links when appropriate. Explain what each reference demonstrates; a link alone is not an explanation.
5. When discussing a data model, show a small representative instance. Explain relevant fields, relationships, optional values, and constraints. Use values consistent with the implementation, and label invented sample values as illustrative.
6. When discussing an application programming interface (API), show a representative request and response. Include the operation, relevant fields, and result status. For function or command interfaces, show an example call or invocation and its result. Include a failure example when error behavior is part of the question.
7. Expand acronyms on first use and briefly explain their role. Introduce unfamiliar language and framework terms before relying on them. Use established conversation context to avoid repeating explanations already understood.
8. Explain stack-specific tools by their purpose and role in this project. For commands, state what they do and what output or side effects to expect. Explain relevant syntax rather than assuming familiarity with decorators, macros, annotations, or similar features.
9. Distinguish verified implementation behavior, inference, and illustrative examples. Keep example values consistent throughout. Before responding, verify that links point to the stated code, examples match the described contracts, new terms are explained, and the answer addresses the original question.

## Boundaries

- Do not invent files, line numbers, interface fields, or runtime results. Label hypothetical examples and simplifications explicitly.
- If implementation evidence is unavailable, state that limitation rather than presenting a plausible example as the project's actual behavior.
- Preserve technical accuracy and discuss relevant tradeoffs. Avoid unexplained jargon, patronizing explanations, and unrelated background; scale detail to the question.
- Explaining code does not authorize modifying it or executing state-changing examples. Clearly distinguish commands shown for illustration from commands actually executed.

## Completion

- A direct answer followed by the reasoning needed to understand it.
- Verified implementation links for code claims.
- Concrete examples for discussed data models and interfaces.
- First-use explanations of unfamiliar acronyms, terms, and tooling.
- Explicit uncertainty wherever the available evidence is incomplete.
