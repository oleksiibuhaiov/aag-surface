---
name: aag-surface-reset-repositories
description: Use when explicitly asked to discard uncommitted work and return repositories in a specified directory to their main, default, or integration branches, or preview that operation.
---
# Reset repositories

## Purpose

Return explicitly selected repositories to clean, current integration branches while preserving committed history and files outside the authorized deletion scope.

## Procedure

1. Establish the directory, exclusions, and preview or execution mode. Inspect immediate child repositories by default. Include the directory itself or search recursively only when requested. Do not follow directory symlinks or descend into discovered repositories. Record the selected repository roots as the operation's allowlist.
2. Establish the deletion policy. The default execution policy discards staged and unstaged changes and deletes non-ignored untracked files. Preserve ignored files, commits, branches, and stashes. A request to inspect, preview, or prepare repositories does not authorize deletion; resolve ambiguous execution requests before changing state.
3. Resolve each repository's remote and integration branch from explicit overrides and repository guidance. Otherwise inspect the selected remote's advertised default with `git --no-optional-locks -C "<repo>" ls-remote --symref <remote> HEAD`. Do not infer the branch solely from names such as main or master. Resolve ambiguous remotes or branches before cleanup.
4. Inspect each repository using commands scoped with `git --no-optional-locks -C "<repo>"`. Record its branch, current commit, staged and unstaged changes, untracked paths, worktrees, and any operation already in progress. Use `git --no-optional-locks -C "<repo>" status --porcelain=v1 --untracked-files=all` and `git --no-optional-locks -C "<repo>" worktree list --porcelain` as part of this inspection. Disable optional locks throughout inspection and preview so status checks cannot refresh and write the index.
5. Identify blockers: detached HEAD, merge or rebase in progress, a target branch checked out in another worktree, dirty submodules, or cleanup that would affect ignored files or nested repositories. Report these rather than silently broadening the operation. Do not treat a bare repository as a working checkout.
6. Present the repository list, target branches, and deletion scope. In preview mode, inspect untracked cleanup with `git --no-optional-locks -C "<repo>" clean -nd` and stop without fetching or changing repository state. Identify conclusions that depend on potentially stale local tracking data.
7. In execution mode, fetch the selected remote branches before any destructive cleanup. Check that each existing local target branch is equal to or an ancestor of its fetched target. A target branch with local-only commits, whether ahead or divergent, is a blocker; preserve those commits and resolve it before cleanup. Resolve all preflight blockers before starting the batch; an unavailable remote or a divergent target branch is a blocker, not permission to use a stale or destructive fallback.
8. Recheck each repository immediately before changing it. Stop if its branch, commit, or working changes differ from the inspected state. Discard only authorized uncommitted changes against the current commit, remove only inspected non-ignored untracked paths, switch to the integration branch, and update it using a fast-forward-only operation. Create a tracking branch if absent. Preserve commits on the original branch and do not force-reset the target branch.
9. Verify the final branch and commit against the fetched target, then check `git --no-optional-locks -C "<repo>" status --porcelain=v1 --untracked-files=all`. Report remaining changes explicitly; ignored files may remain. If a command fails, stop the batch and identify the last completed operation before reporting the result.

## Boundaries

- An explicit execution request authorizes its stated scope; do not request redundant confirmation for each repository.
- Never discard committed history or delete branches, stashes, nested repositories, or other worktrees. Preserve ignored files by default; deleting them requires explicit authorization for the exact paths and a matching preview. Do not overwrite ignored files while restoring or switching branches; stop if they obstruct the requested checkout.
- Never push, create commits, or automatically stash discarded work. Do not use cleanup options that delete ignored files outside their explicit authorization or force deletion of nested repositories.
- Do not modify paths outside the recorded allowlist or act on changes discovered after preflight without resolving the new scope.
- A multi-repository reset is not an atomic operation. Do not describe a failed batch as rolled back or complete; distinguish completed, partially changed, and unprocessed repositories.

## Completion

- One row per repository: path, original branch, target or final branch, final commit when known, cleanliness, and outcome.
- Discarded changes and deleted untracked paths, or the proposed deletions for a preview.
- Preserved exceptions, blockers, and the exact partial state of any interrupted operation.
