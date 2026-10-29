---
name: aag-surface-author-agent
description: Use when adding or revising a delegated role, custom agent, description, inputs, outputs, or access intent in the canonical aag-surface source.
---
# Author an agent

## Purpose

Produce one delegated role with explicit inputs, output evidence, and honest access semantics in each product.

## Procedure

1. Work within `aag-surface-maintain`. If that workflow is already active, continue with the content steps below; otherwise enter its setup once, then resume here. This skill handles authoring and returns to maintenance for shared verification. Confirm a separate agent context is useful; use a skill for a reusable procedure.
2. Choose a lowercase, hyphen-separated name starting with `aag-surface-`, at most 64 characters including the prefix. Copy `~/aag-surface/canonical/templates/aag-surface-agent.md` to `~/aag-surface/canonical/agents/<name>.md`; create the directory for the first real role.
3. Set `name` to the filename stem, `description` to a single-line responsibility and delegation trigger, and `access` to `read-only` or `inherit`. Use only these three canonical frontmatter fields.
4. State one role, required parent inputs, procedure, output shape, and boundaries. Address the delegated agent directly and return missing-input questions to its parent.
5. Interpret `read-only` accurately: Cursor receives `readonly: true`; Codex receives a no-write instruction but inherits parent permissions. Codex agent TOML does not establish a separate read-only sandbox. If enforced isolation is essential, the parent session must provide it before delegation.
6. Remove placeholders and return the authored paths, role, and access intent to the active maintenance workflow for its shared verification pass. Inspect the Cursor Markdown and Codex TOML during that pass.

## Boundaries

- Do not claim instructions enforce permissions.
- Do not invent production agent roles as examples; add roles only for an actual need.
- Keep the shared body independent of products unless the role itself is product-specific.

## Completion

- Canonical path, name, description, inputs, and output shape.
- Access intent, product differences, and validation evidence from the shared maintenance pass.
