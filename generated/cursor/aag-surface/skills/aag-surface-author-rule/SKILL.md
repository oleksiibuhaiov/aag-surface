---
name: "aag-surface-author-rule"
description: "Use when adding or revising an always-on rule, policy, or convention in the canonical aag-surface source."
---
# Author a rule

## Purpose

Produce one clear, agent-agnostic requirement that can be projected into both products without a workspace-root assumption.

## Procedure

1. Work within `aag-surface-maintain`. If that workflow is already active, continue with the content steps below; otherwise enter its setup once, then resume here. This skill handles authoring and returns to maintenance for shared verification.
2. Confirm that the requirement belongs in every session. Put task-specific procedures in a skill instead.
3. Choose a lowercase, hyphen-separated name starting with `aag-surface-`, at most 64 characters including the prefix. Copy `~/aag-surface/canonical/templates/aag-surface-rule.md` to `~/aag-surface/canonical/rules/<name>.md`.
4. Replace the H1 with a short title and state one requirement with its trigger and scope. Add only the conditions and references needed to apply it. Refer to skills by their prefixed names.
5. Remove placeholders. Keep the file UTF-8 with a final newline, no frontmatter, and no product-specific rule configuration.
6. Return the authored paths and requirement to the active maintenance workflow for its shared verification pass. Review how the rule appears in both generated products during that pass.

## Boundaries

- Edit canonical source; generated output is rebuilt.
- Do not impose `~/git` as a root or assume the current directory is the surface source.
- Avoid duplicate or unrelated requirements in one rule.

## Completion

- Canonical path, name, title, and requirement.
- Referenced skills and validation results from the shared maintenance pass.
