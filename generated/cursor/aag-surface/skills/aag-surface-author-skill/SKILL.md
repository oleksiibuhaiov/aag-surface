---
name: "aag-surface-author-skill"
description: "Use when adding or revising a reusable procedure, workflow, or SKILL.md in the canonical aag-surface source."
---
# Author a skill

## Purpose

Produce a focused procedure that can be selected from its description and used without conversation history.

## Procedure

1. Work within `aag-surface-maintain`. If that workflow is already active, continue with the content steps below; otherwise enter its setup once, then resume here. This skill handles authoring and returns to maintenance for shared verification.
2. Choose a lowercase, hyphen-separated name starting with `aag-surface-`, at most 64 characters including the prefix. Copy `~/aag-surface/canonical/templates/aag-surface-skill.md` to `~/aag-surface/canonical/skills/<name>/SKILL.md`.
3. Set `name` to the directory name and `description` to a single line describing when to use the skill. These are the two supported canonical frontmatter fields; use plain text or a JSON-quoted string.
4. Write the purpose, ordered procedure, boundaries, and completion evidence. Every command must identify its source location or working directory. Keep supporting resources inside the same skill directory and refer to them relatively; invoke scripts through their interpreter.
5. Remove placeholders and test the procedure against a representative task. Do not claim behavioral validation from a syntax check alone.
6. Return the authored paths and representative-task evidence to the active maintenance workflow for its shared verification pass. Review both generated copies during that pass and report any unresolved runtime discovery issue.

## Boundaries

- Keep task triggers in the description and procedural details in the body.
- Use regular files and directories for resources; the generator rejects symlinks.
- Do not invent product metadata to hide duplicate discovery.

## Completion

- Canonical path, name, and description.
- Procedure evidence and generation results from shared maintenance verification, distinguishing actual client checks from static validation. Reuse the representative-task evidence rather than repeating the same check.
