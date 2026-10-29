# Workspace coordination

The workspace may contain multiple Git repositories and standalone files. Identify the repositories and paths relevant to the task, investigate their relationships as needed, and keep changes focused on the task while preserving unrelated work.

Before editing a repository, inspect its branch and working-tree state and follow its local instructions. Run commands and validation in the appropriate repository context.

When work spans repositories, identify dependencies between the changes and establish the appropriate implementation, validation, and delivery order. Distinguish the order changes can be developed from the order they must be merged, released, or deployed. Keep intermediate states compatible with dependent components, and make any coordination requirements or blockers explicit.

Keep changes, validation results, and Git operations attributable to their respective repositories.
