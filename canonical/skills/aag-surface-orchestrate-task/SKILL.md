---
name: aag-surface-orchestrate-task
description: Use when the user requests delegated planning, staged implementation, and review of an engineering task, or resumes an existing orchestration workflow.
---
# Orchestrate an engineering task

## Purpose

Coordinate a planner and a separate implementer across one or more repositories.
Keep the approved approach, review loop, and verification evidence intact through
long sessions and handoffs.

## Procedure

### 1. Establish or resume the task

- Use the work item already supplied; ask for it only when missing. Establish the
  outcome, acceptance criteria, affected repositories, exclusions, and constraints.
  Inspect relevant instructions, branches, working changes, conventions, and
  existing implementations. Verify development targets rather than assuming the
  remote default branch.
- Resolve routine choices from evidence. Ask only about missing decisions that
  materially affect scope, behavior, or authorization.
- For an existing task, read its plan and checkpoint first. Reconcile them with
  current user instructions and repository state; resume at the first unfinished
  step. Preserve applicable approvals instead of restarting planning.
- Before delegation, check the tool's inheritance behavior. Both planner and
  implementer must inherit the parent's model and reasoning settings when
  supported; do not specify model or effort overrides. Native inheritance does
  not require guessing the parent's model identifier. If inheritance is
  unavailable or cannot be established from the available controls, explain the
  limitation, propose supported alternatives, and wait for the user's choice.
  Record that choice and reuse it while it remains applicable. Never silently
  substitute a model or claim an unverified setting.

### 2. Delegate and review planning

- Assign one planner a focused brief: work item, acceptance criteria, relevant
  repositories and state, user decisions, constraints, and unresolved questions.
  Use native Plan mode when selectable; otherwise disclose the limitation and
  assign strictly read-only work. This instruction is not a technical sandbox.
- Planning must not change source, branches, dependencies, or infrastructure.
  The orchestrator may maintain the local task records described below, unless
  the user or environment requires all work to remain read-only.
- Require a plan covering behavior and contracts, relevant code and existing
  patterns, dependency order, small implementation stages and intended commits,
  meaningful checks, compatibility/lifecycle concerns, documentation, and delivery
  dependencies.
- Challenge the plan against the requirements and code. Return concrete findings
  to the same planner. Resolve disagreements through evidence; take a stalled
  material decision to the user rather than looping indefinitely.
- Present a brief outline, then one reviewable planning chunk at a time. Let the
  user review each before presenting the next. A small plan may need one chunk.
  Consolidate the accepted approach and obtain explicit implementation approval.
  Approval of planning chunks or checkpoint writes alone does not authorize
  implementation. Reuse existing approval when it already covers this plan.

### 3. Delegate implementation by stage

- After approval, use a separate implementer. Give it the approved plan/version,
  current stage, repository paths and branches, constraints, acceptance criteria,
  allowed changes, required checks, and whether local commits are authorized.
  Prohibit pushes, pull requests, publication, and other external writes.
- Keep one writer per checkout. The orchestrator reviews and coordinates; it must
  not edit the implementer's source concurrently. Reuse the same implementer for
  corrections. Additional agents or nested delegation require user agreement.
- If a role cannot be resumed, confirm its previous writer has stopped before
  assigning a replacement. Pass the checkpoint and record the replacement.
  If delegation is unavailable, explain and agree an alternative; do not silently
  substitute inline implementation.
- Establish a stage's prerequisites before starting it. Proceed through approved
  stages without repeated permission requests. Return to the user for material
  changes to the approved scope or design.
- Across repositories, distinguish development order from merge/release order.
  Prefer local packages, paths, or built artifacts for dependent testing. Record
  their provenance and keep temporary pins or scaffolding out of final changes.
  Do not publish a dependency just to obtain a development pin. Track unresolved
  production dependency choices explicitly.

### 4. Review every stage and its corrections

1. Inspect the actual changes, including new files and any stage commits, against
   the accepted plan. Check correctness, compatibility, repository conventions,
   dependency effects, lifecycle behavior, and whether tests establish useful
   behavior. Apply relevant review guidance within the agreed agent roles.
2. Send only actionable, evidence-backed findings to the same implementer. Handle
   routine fixes without asking the user to adjudicate them. Reject unnecessary
   abstractions, repetitive tests, and unrelated changes.
3. Inspect the corrections and relevant check results. A report of success is
   not a substitute for reviewing the diff and evidence. Keep blocked or unrun
   checks distinct from passes.
4. Associate evidence with the tested source state, dependencies, and environment.
   Changed inputs require affected checks again; unchanged inputs do not justify
   repeated full runs. Local or mocked checks do not establish deployment or
   upgrade behavior.
5. Update the checkpoint before proceeding. Do not silently advance past a failed
   prerequisite; resolve it or obtain an explicit adjustment to the plan.

### 5. Deliver for user review

- Create local commits only when authorized. Check the repository's author
  identity, commit conventions, and signing requirements. Follow the current
  signing rule; do not impose a universal commit format or hardware-key policy.
- Present resulting behavior, repository/branch/commit information, a useful
  review order, validation evidence, and remaining limitations or delivery
  dependencies. Exclude temporary testing changes from the proposed final diff.
- Address user feedback through the same implementer and review loop. Internal
  approval does not replace the user's final review.

### 6. Deliver externally only when authorized

- Require the user's final-content approval and explicit authorization for the
  external action and target. Reuse existing approval while its scope applies.
  Implementation or local-commit approval does not authorize pushing, creating a
  pull request, commenting, merging, publishing, or deploying.
- Before an authorized delivery, recheck remote state, approved contents, final
  dependency references, and automation triggered by the target branch. Resolve
  release-triggering consequences within the approval scope.
- Follow the current signing policy. A signing failure stops further actions
  until the user explicitly initiates another attempt. Rewriting published
  history requires separate approval. After changes to commits or dependencies,
  update dependent references and revalidate affected behavior.
- Monitor continuous integration (CI) for the exact pushed commits. If reruns are
  authorized, inspect the failure first and retry only a plausibly transient
  failure, using failed-job reruns when available. Allow at most two retry rounds
  for the same failure on the same commit; record the count across resumptions.
- Stop retries when the head changes, the run is superseded, or unexpected
  workflow changes appear. Code defects return to local implementation/review;
  changed content needs approval before another push unless that correction
  cycle was explicitly authorized. After the retry limit, report the cause,
  attempts, and smallest useful next step for the user's decision.

## Task records and continuity

Keep task records under
`~/aag-surface/state/aag-surface-orchestrate-task/<task-name>/`, outside the target
repositories. Use a short lowercase name in the user's session-title style, such
as `charmlibs migration`, `pg_cron forwardport`, or `orafce`. Prefer the supplied
task/session name, retaining meaningful spaces, underscores, and hyphens. Use a
single directory component and quote paths in shell commands. Reuse the directory
for the same task; add a short descriptive qualifier when a different task would
collide with it.

Start with this lightweight structure, adapting it as the task develops:

- `aag-surface-state.md`: the concise entry point for resuming. Record the task and
  current stage, next action/blockers, applicable approvals with their wording and
  scope, relevant repositories and current changes, agent assignments and inherited
  or user-selected settings, and links to the plan and evidence. Include dependency
  pins and CI retry counts when relevant.
- `aag-surface-plan.md`: the coherent plan, acceptance criteria, stages and checks,
  dependencies, and revision covered by approval. Distinguish proposed revisions
  from the approved approach.
- `aag-surface-evidence/`: optional logs, check results, review findings, and links
  to built artifacts, identified by the tested source/dependencies/environment.

These are useful defaults, not a fixed schema. Combine small records or split out
decisions, reviews, or evidence when that improves readability. Keep one obvious
entry point linking to the authoritative records; do not maintain competing copies
of the plan or approval state. Add files only when they carry useful information.
Keep large build artifacts in appropriate build locations and reference them.

The orchestrator owns the current-state and plan records. Delegates return updates
and evidence; any delegated evidence writes use assigned paths. Update records after
decisions, stage reviews, or material state changes. Preserve the provenance of
earlier results when later work changes the tested inputs.

When resuming from a checkpoint elsewhere, read it first and preserve its approval
history. Use the requested state location for subsequent records when permitted,
recording the prior location; do not delete the old checkpoint automatically.
Carry the current checkpoint entry path into handoffs and summaries. On resume,
verify live repository and agent state before writing. Records preserve approval
evidence; they do not grant permissions or override newer instructions. If writes
are prohibited, provide the checkpoint in the response and state that it was not
saved. State is machine-local and Git-ignored; pushing the skill does not back it up.

## Boundaries

- Current user and repository instructions, including surface rules, govern this
  workflow. Do not import permissions, repository lists, branches, or domain
  assumptions from a reference task.
- Keep planning, implementation, review, and delivery states distinct. Do not
  claim completion while an acceptance criterion or required check remains
  failed, blocked, or unverified.
- Keep updates concise and factual. Surface a decision or blocker with the
  evidence needed to resolve it.

## Completion

- Reviewed outcome and relevant repositories, branches, and commit hashes.
- Passed, failed, blocked, and unrun checks with their tested inputs.
- Remaining user decisions or authorized delivery steps, plus the checkpoint
  path and next action.
