# aag-surface

One canonical source for personal agent rules, skills, and custom agents. The
source lives at `~/aag-surface`. Generated integrations use native user locations
and do not depend on the working directory or on a `~/git` workspace.

Stage 1 provides the source, generators, ownership-aware lifecycle, and fixture
tests. **Live activation is not yet verified.** Cursor discovers skills from
both its plugin and `~/.codex/skills`; exactly-once discovery remains unresolved.
Keep the existing integration active until that requirement is verified in the
required clients. A successful generator or installation command verifies file
operations, not client loading.

## Contents

```text
~/aag-surface/
  aag-surface.md
  aag-surface.sh
  canonical/
    rules/aag-surface-*.md
    skills/aag-surface-*/SKILL.md
    agents/aag-surface-*.md       # added when a real role is needed
    templates/aag-surface-{rule,skill,agent}.md
  generated/
    codex/
      AGENTS.md
      skills/aag-surface-*/SKILL.md
      agents/aag-surface-*.toml  # generated for defined roles
    cursor/aag-surface/
      .cursor-plugin/plugin.json
      rules/aag-surface-*.mdc
      skills/aag-surface-*/SKILL.md
      agents/aag-surface-*.md    # generated for defined roles
  scripts/aag-surface.py
  tests/aag-surface-test.py
  state/                        # machine-local; Git-ignored
    aag-surface-install.json
    aag-surface.lock
```

The initial content contains two rules: surface governance and workspace
coordination. Workspace coordination covers task scope, existing work, and
dependency-aware implementation, validation, and delivery across repositories.
Four skills maintain the surface and author rules, skills, and agents. There
are no production custom agents yet.

Two further skills support everyday work: `aag-surface-reset-repositories`
previews or performs explicitly requested cleanup to each repository's integration
branch, and `aag-surface-explain-clearly` provides grounded technical explanations.
The `aag-surface-technical-explanation-clarity` rule selects the explanation skill
automatically. Both skills are generated for Codex and the Cursor plugin through
the same workflow as the maintenance skills.

## Generate and validate

Use Python 3.11 or newer and a POSIX shell. There are no third-party Python
dependencies. Commands locate the source from the script location and work from
any current directory. After source changes, regenerate and validate once:

```sh
sh ~/aag-surface/aag-surface.sh sync
sh ~/aag-surface/aag-surface.sh validate
git -C ~/aag-surface diff --check
```

Commit reproducible output alongside its source. For validation alone, run
`validate` against the existing output without running `sync` first; stale output
should be reported. `sync --check` is an equivalent read-only consistency check,
so either command suffices.

Use representative tasks and resource checks for content changes. For generator,
lifecycle, or test changes, run the full suite:

```sh
python3 ~/aag-surface/tests/aag-surface-test.py
```

The tests copy the source into temporary directories and install into temporary
fixture homes; they do not modify actual agent configuration. They check
canonical entries against their native outputs and exercise adding a rule, a
skill with executable resources, and an agent through the installation lifecycle.

`aag-surface-maintain` owns operation selection and shared verification. The
three authoring skills handle their respective content steps within that
workflow, then return to it. Reuse completed checks while their inputs remain
unchanged.

Canonical names start with `aag-surface-`, use lowercase letters, digits, and
single hyphens, and are at most 64 characters. Rules are Markdown with an H1 and
body. Skills use exactly `name` and `description` frontmatter. Agents add
`access: read-only` or `access: inherit`. Metadata uses one-line plain text or
JSON-quoted strings; full YAML features are intentionally unsupported. Native
skill headers are generated with quoted string values so YAML punctuation and
boolean-like descriptions retain their meaning. Start
from the templates and the matching authoring skill. Skill resources are copied
with the skill; use interpreter commands for scripts. Symlinks are rejected.

Codex agent TOML contains `name`, `description`, and `developer_instructions`.
For read-only intent, Cursor receives `readonly: true`; Codex receives a no-write
instruction and inherits parent permissions. The agent file does not establish
an independent Codex sandbox. See [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Installation and ownership

| Product | Owned destination | Mechanism |
| --- | --- | --- |
| Codex rules | `~/.codex/AGENTS.md` | Entire generated file |
| Codex skills | `~/.codex/skills/aag-surface-*/` | Individual generated directories |
| Codex agents | `~/.codex/agents/aag-surface-*.toml` | Individual generated files |
| Cursor | `~/.cursor/plugins/local/aag-surface/` | One complete native plugin copy |

All integrations are real copies, isolated from the source. No `~/.agents`
entries, product wrappers, alternate HOME/CODEX_HOME, hooks, or Codex plugins are
needed. The native defaults apply; a client configured to use a different home
will need separate compatibility verification. Configuration such as
`~/.codex/config.toml` is outside this installation's ownership.

The lifecycle commands inspect, install/update, or remove an installation.
Resolve the runtime blocker below before installation/update; status and removal
remain available independently:

```sh
sh ~/aag-surface/aag-surface.sh status
sh ~/aag-surface/aag-surface.sh install
sh ~/aag-surface/aag-surface.sh uninstall
```

`install` also updates an existing installation. It first checks the complete
destination set, refuses any existing unowned entry, stages generated copies,
and records each owned path in `state/aag-surface-install.json`. Identical names
or contents do not establish ownership. Do not delete that manifest while the
installation is active, or move the source while installed: its source/home
binding prevents a different checkout from claiming the same entries. To move
the source, uninstall from the original location first.

Updates replace owned entries and remove entries that were removed from the
canonical source. The ownership assumption is that other tools may add sibling
entries but do not modify our owned files or directories. The whole global
`AGENTS.md` belongs to this surface after a collision-free installation; there
are no merged sections or background repair processes.

`uninstall` removes only entries recorded for this source and home. It preserves
shared parent directories, other plugins, `.system` skills, company content,
configuration, credentials, and the entire source repository with its generated
files. Repeating installation or removal is supported. Without a manifest,
removal leaves even prefixed entries alone. Symlinked destinations or shared
parents are rejected instead of followed. Removal depends on ownership state,
not valid canonical source or passing authoring tests: inspect status, uninstall,
and inspect status again without regenerating first.

Ordinary failures roll back completed replacements. If rollback itself fails,
the command reports recovery directories named `.aag-surface-*` beside affected
entries and preserves their backups. Do not delete those directories until the
original entries have been recovered. This is not a crash-proof multi-directory
filesystem transaction: power loss or forced process termination can require
manual recovery. State locking serializes commands from this source checkout.

`--fixture-home <path>` on lifecycle commands is exclusively for a real directory
beneath the system temporary directory. It uses that explicit target without
changing the process HOME or CODEX_HOME. The test suite also copies the source,
so its machine-local ownership manifest stays separate from the actual source.

## Client verification and migration gate

Required local clients are Cursor IDE and Agent CLI, plus Codex CLI, app, and IDE
extension. Cloud/remote clients are outside this stage. User-wide Codex skills
under `~/.codex/skills` are described in the [Codex skills guide](https://learn.chatgpt.com/use-cases/reusable-codex-skills)
and used by Codex's bundled skill installer. The main skills documentation also
describes `~/.agents/skills`; this surface deliberately uses the Codex directory.

Cursor's [local plugin mechanism](https://cursor.com/docs/plugins#test-plugins-locally)
loads the real plugin directory after reload, subject to the organization's local
import policy. Its [native manifest](https://cursor.com/docs/reference/plugins)
discovers the default rules, skills, and agents directories. Cursor documents
[plugins in the desktop and CLI clients](https://cursor.com/help/customization/plugins).
The directory structure alone does not prove a particular installed client or
organization policy loaded it.

The outstanding issue is [Cursor skill compatibility discovery](https://cursor.com/docs/skills):
it also scans `~/.codex/skills`. Prefixes distinguish this surface from company
content but do not merge the plugin and native copies. A read-only inspection
of Cursor IDE 3.27.22's bundled loader found path-based deduplication that treats
those locations differently. Its internal `metadata.surfaces` filter has no
verified documented contract and is not used here. No duplicate-hiding metadata,
global import disabling, or product modifications are applied.

Before live activation or legacy removal, establish an agreed, supported
exactly-once mechanism and verify all required clients from a normal repository
under `~/git`, a repository elsewhere, and a standalone directory. Confirm each
rule loads, each logical skill appears once, and any defined agents load.
Record client versions and evidence. At preparation time Codex CLI 0.164.0 and
Cursor IDE 3.27.22 were found; Cursor Agent CLI was not found. Do not count an
absent client or an untested app/extension as a pass. Invoking `cursor agent`
can install the CLI automatically and is not a read-only discovery check.

Normal [Codex instruction precedence](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
applies: global `AGENTS.override.md` can supersede global `AGENTS.md`, and project
guidance may override global guidance. No custom workaround is needed.

After the replacement is verified, legacy cleanup may remove only the exact
symlinks below when each still points into `~/git/agent-surface` as shown. Inspect
them before removal, preserve their real parent directories, and leave the old
repository/history unchanged. The lifecycle commands do not remove legacy links.

| Legacy link | Expected target under `~/git/agent-surface/` |
| --- | --- |
| `~/git/.cursor/rules` | `adapters/cursor/rules` |
| `~/git/.cursor/skills` | `canonical/skills` |
| `~/git/.codex/AGENTS.md` | `adapters/codex/AGENTS.md` |
| `~/git/.codex/config.toml` | `adapters/codex/config.toml` |
| `~/git/.codex/skills` | `canonical/skills` |

## Git

This source starts with fresh history and origin
`https://github.com/oleksiibuhaiov/aag-surface`. A local commit and origin setup do
not require GitHub authentication. Existing local author/signing settings are
preserved; remote access would be checked separately if a future task requests a
push. Stage 1 does not publish or change global Git/GitHub account settings.
