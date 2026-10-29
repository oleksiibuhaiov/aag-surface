# aag-surface

One canonical source for personal agent rules, skills, and custom agents. The
source lives at `~/aag-surface`. Generated integrations use native user locations
and do not depend on the working directory or on a `~/git` workspace.

Stage 1 provides the source, generators, ownership-aware lifecycle, and fixture
tests. Local verification covers Codex CLI discovery and Cursor IDE's automatic
context with third-party imports disabled by the user. Manual explanation-skill
invocation and the other required clients still need verification. A successful
generator or installation command verifies file operations, not client loading.

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
    aag-surface-orchestrate-task/<task-name>/  # created when a task starts
```

The rules cover surface governance, workspace coordination, concise technical
writing, repository conventions, commit signing, and approval for side effects.
Signing is required only where repository or company policy requires it, after
change approval and an explicit push request; a signing failure stops further
actions until the user initiates another attempt. External actions require their
own explicit approval. Four skills maintain the surface and author rules, skills,
and agents. There are no production custom agents yet.

Two further skills support everyday work: `aag-surface-reset-repositories`
previews or performs explicitly requested cleanup to each repository's integration
branch, and `aag-surface-explain-clearly` provides grounded technical explanations
when explicitly invoked: `$aag-surface-explain-clearly` in Codex or
`/aag-surface-explain-clearly` in Cursor. Both skills are generated for Codex and
the Cursor plugin through the same workflow as the maintenance skills.

The [orchestration skill](canonical/skills/aag-surface-orchestrate-task/SKILL.md)
coordinates delegated planning, staged implementation, and review across one or
more repositories. Both delegated roles inherit the parent's model and reasoning
settings; unavailable inheritance requires the user's choice of an alternative.
Invoke it with `$aag-surface-orchestrate-task` in Codex or
`/aag-surface-orchestrate-task` in Cursor and provide the work item. It requires
approval of the plan before implementation and separate approval for external
actions.

Task records live under
`~/aag-surface/state/aag-surface-orchestrate-task/<task-name>/`, with short lowercase
names such as `charmlibs migration`. The suggested state, plan, and optional
evidence files can adapt to the task; these machine-local records are Git-ignored.
The full planning, implementation, review, and resume loop still needs verification
on a real task.

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
body. Skills require `name` and `description` frontmatter and optionally accept
`invocation: explicit` (default `auto`). Agents add
`access: read-only` or `access: inherit`. Metadata uses one-line plain text or
JSON-quoted strings; full YAML features are intentionally unsupported. Native
skill headers are generated with quoted string values so YAML punctuation and
boolean-like descriptions retain their meaning. Start
from the templates and the matching authoring skill. Skill resources are copied
with the skill; use interpreter commands for scripts. Symlinks are rejected.

For explicit invocation, the generator sets Cursor's documented
[`disable-model-invocation: true`](https://cursor.com/docs/skills#disabling-automatic-invocation)
on both skill copies, since Cursor also scans Codex skills. It also generates
Codex's [`agents/openai.yaml` policy](https://learn.chatgpt.com/docs/build-skills#optional-metadata)
with `allow_implicit_invocation: false`. Do not supply that resource in an explicit
canonical skill: generation rejects the conflict. Other skills retain contextual
selection. These controls do not resolve duplicate discovery.

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
For installation, use the client-discovery settings described below, then verify
loading after reload. The following commands are separate operations:

```sh
sh ~/aag-surface/aag-surface.sh status
sh ~/aag-surface/aag-surface.sh install
sh ~/aag-surface/aag-surface.sh uninstall
```

`status` compares installed entries with the ownership manifest's recorded
digests. It does not query running clients or compare installation contents with
current source. `validate` checks canonical/generated consistency; `install`
applies those generated copies.

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

`uninstall` removes only entries recorded for this source and home, then deletes
the empty ownership manifest so the uninstalled source can be moved. It preserves
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

[Cursor compatibility discovery](https://cursor.com/docs/skills) also scans
`~/.codex/skills` when third-party imports are enabled. Prefixes distinguish this
surface from company content but do not merge the plugin and native copies.

For this installation, the user disabled **Include Third-Party Plugins, Skills,
and Other Configs** in Cursor Settings. This is a supported
[third-party import setting](https://cursor.com/docs/reference/third-party-hooks).
It affects imports from other tools globally; the installer never changes it.
A fresh Cursor IDE 3.27.22 session in `~/git` confirmed that the rules and five
automatic skills came from the local plugin, with no Codex-origin duplicates.
The explanation skill was correctly absent from automatic context; its manual
picker selection and invocation remain untested. Separate installed copies are
expected and do not by themselves establish duplicate presentation.

Codex CLI 0.164.0 diagnostics confirmed user-wide rules and six enabled skills,
each once, from `~/git`, repositories inside and outside it, and a standalone
directory. Manual explanation-skill invocation, Cursor IDE sessions outside
`~/git`, Cursor Agent CLI, and the Codex app/IDE extension still need checks.
Do not assume the IDE's import setting controls Cursor Agent CLI. Do not count
an absent or untested client as a pass. Invoking `cursor agent` can install the
CLI automatically and is not a read-only discovery check.

Verify loading after installation and reload, before treating a client as ready.
Record automatic-context discovery separately from manual skill selection;
on-demand skills are intentionally omitted from the automatic catalog. Confirm
each logical skill appears once in its applicable catalog and any defined agents
load. Machine-local evidence is kept in `state/aag-surface-verification.json`.
`status` does not evaluate that evidence or claim runtime success.

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
