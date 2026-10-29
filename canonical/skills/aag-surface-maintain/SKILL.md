---
name: aag-surface-maintain
description: Use when changing, generating, validating, installing, uninstalling, or committing aag-surface sources or their owned user-level Cursor and Codex integrations.
---
# Maintain the agent surface

## Purpose

Keep canonical sources, generated products, and any installed owned copies consistent while preserving unrelated content and reporting runtime limitations accurately.

## Procedure

1. Locate `~/aag-surface`, read the relevant sections of `aag-surface.md`, and inspect `git -C ~/aag-surface status --short --branch`. Preserve unrelated or pre-existing work. The current directory may be anywhere. Establish this workflow once per task; an author skill entering it resumes its content steps after this setup.
2. Select only the operations needed for the task below. When several operations apply, complete source changes and their shared verification before installation or commit. Reuse verification results while the relevant inputs remain unchanged.

## Operations

- **Source changes:** use `aag-surface-author-rule`, `aag-surface-author-skill`, or `aag-surface-author-agent` for the content-authoring portion. Those skills return here without restarting maintenance. Edit management code only when the requested behavior requires it. Finish with the shared verification pass below.
- **Generation:** run `sh ~/aag-surface/aag-surface.sh sync` and then `sh ~/aag-surface/aag-surface.sh validate`. For source changes, these commands belong to the shared pass and run once.
- **Validation only:** run `sh ~/aag-surface/aag-surface.sh validate` against the existing source and output. Report stale output or errors without regenerating. `sync --check` is an equivalent read-only command; either one suffices.
- **Installation/update:** inspect `sh ~/aag-surface/aag-surface.sh status` and existing destinations. Resolve runtime blockers in the documentation before activating a replacement, and preserve the legacy integration until its replacement is verified. Run `sh ~/aag-surface/aag-surface.sh install`, which checks generated consistency itself. Reload the required clients and verify instructions, skills, and defined agents from directories inside and outside `~/git`. Each logical skill must appear exactly once per client; absent clients or unresolved duplication mean verification is incomplete.
- **Removal:** inspect status and ownership, run `sh ~/aag-surface/aag-surface.sh uninstall`, then inspect status again. Removal uses ownership state; it does not require generation, valid canonical content, or passing authoring tests. Preserve the source repository, internal generated output, shared parents, and unrelated content.
- **Commit:** when included in the task, review the staged scope, use the verification results for those contents, and commit only the reviewed surface changes. Report the hash and worktree status. Keep changes to other repositories separate.

## Shared verification after source changes

1. Run `sh ~/aag-surface/aag-surface.sh sync`, then `sh ~/aag-surface/aag-surface.sh validate`, once after the edits. Inspect both generated products.
2. For rules, skills, and agents, check representative tasks and relevant resources. For generator, lifecycle, or test changes, run `python3 ~/aag-surface/tests/aag-surface-test.py`. Add further checks only for behavior affected by the change; distinguish procedure checks from actual client loading.
3. Run `git -C ~/aag-surface diff --check` and `git -C ~/aag-surface diff --cached --check`. Inspect the complete scoped changes, including new files, staged content, generated output, and deletions. Record the results for any subsequent operation in this task.

## Boundaries

- Never hand-edit generated outputs or installed copies. Change canonical sources or the generator, then follow the applicable generation or installation operation.
- Never overwrite an unowned destination, delete shared agent directories, or remove ownership state while installed entries still exist.
- Respect normal global and project instruction precedence. Do not replace user HOME, CODEX_HOME, or launch conventions.
- A successful static check or filesystem install does not establish client compatibility. Do not bypass unresolved discovery with unrelated global settings.

## Completion

- Source and generated changes, verification commands/results, and reviewed scope.
- Commit information when requested.
- Installed/removed entries and preserved unrelated content when applicable.
- Actual client checks, skipped checks, unresolved discovery, and migration status.
