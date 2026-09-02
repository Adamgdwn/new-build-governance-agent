# Current Build Pathway

Last Updated: YYYY-MM-DD
Status: draft
Owner: Technical Lead

> **Single active pathway document.** This is the one active pathway for this project.
> All prior pathway, deployment-plan, and build-plan documents in this repo must carry
> `Status: superseded` and reference this file.

## Purpose

This document is the live path from current plan to completed build. It keeps agent work small, timestamped, and easy to resume. It holds the header and the active chunks only; completed pathways move to `docs/archive/` with `Status: superseded`.

## Required Work Pattern

For ordinary scoped work, use lean startup:

1. Check `git status --short`.
2. Read `AGENTS.md`.
3. Use `docs/context-map.md` when context routing is unclear.
4. Inspect only the specific files, errors, or docs needed for the task.
5. Run targeted validation after the change.

For material or risk-triggering work sessions:

1. Start from `START_HERE.md`.
2. Run `bash scripts/governance-preflight.sh`.
3. Review `docs/standards/README.md`.
4. Review `docs/standards/engineering-governance-by-use-case.md`.
5. Review `docs/policy/durable-development-engineering-policy.md`.
6. Review `docs/standards/ship-ready-engineering-standard.md`.
7. Review `project-control.yaml` and open exceptions.
8. Capture a timestamp with `date -Iseconds`.
9. Plan once: write every chunk of the build below and get one owner approval of the whole plan.
10. Run one chunk per fresh agent session; complete and validate it before expanding scope.
11. Update this document with status, validation, and the next chunk.

Risk-triggering work includes production, deployment, authentication, authorization, payments, secrets, sensitive data, database migrations, customer communications, external side effects, infrastructure or provider settings, destructive actions, autonomous tool use, risk classification, governance policy changes, or release readiness.

After compaction or a context clear, restart from this document and `CARRY_FORWARD.md`, then run `git status --short`, read `AGENTS.md`, and open only the files the next chunk names.

Unattended runs: when the project has the agent runner installed, `node scripts/agent/run-chunks.mjs` takes each `Status: Ready` chunk in turn, runs a worker in a fresh context, gates on the Validation commands, has an independent verifier check the acceptance criteria against evidence, and commits. The runner and its hooks are documented in the AI Coding Best Practices knowledge base (RUN-AIC-001, STD-AIC-003, STD-AIC-004).

## Chunking Standard

Approval happens once per plan, not once per chunk. Each chunk should fit comfortably in one agent context window and take about 25 minutes of unattended work.

A good chunk has:

- one objective
- a budget class: Tiny, Small, Medium, Large, or Strategic
- a target completion state
- a runner: `claude`, `codex`, or `human`
- a `Files:` allow-list of the paths the chunk may change; hooks block writes outside it when the runner is installed
- acceptance criteria an independent reviewer can check against evidence, not against the worker's claim
- explicit validation commands
- an explicit stop condition or escalation trigger
- a timestamped status note

Use third-level headings with a `P-NN` number so the unattended runner and its hooks can find each chunk:

```md
### P-01 - Short Objective
### P-02 - Short Objective
```

Status vocabulary: `Ready`, `Running`, `Review`, `Done`, `Blocked`, `Deferred`. Only `Status:` and `Files:` are machine-read; everything else is for people and the verifier. Keep chunks independent enough to run in any order unless a chunk states what it depends on. Avoid mixing unrelated code, governance, deployment, and product decisions in one chunk unless the change cannot be validated any other way.

## Active Path

| Step | Status | Timestamp | Owner | Notes |
|------|--------|-----------|-------|-------|
| Write and approve the plan | active | YYYY-MM-DD | Technical Lead | Replace this row once every chunk below is written and the owner has approved the plan. |
| Run the chunks | pending | YYYY-MM-DD | Agent | One chunk per fresh session, or `node scripts/agent/run-chunks.mjs` when installed. |
| Human review of the Done chunks | pending | YYYY-MM-DD | Technical Lead | Read the diffs and the verifier verdicts; decide merge, push, and release. |

## Chunks

### P-01 - Current Objective

Status: Ready

Completion target: Draft complete / Task complete / Integration complete / Release ready / Blocked

Budget class: Tiny / Small / Medium / Large / Strategic

Runner: claude / codex / human

Files:

- `path/to/file-or-folder-this-chunk-may-change`

Objective:

Acceptance criteria:

- [ ] Criterion one, checkable from evidence
- [ ] Criterion two

Validation:

- Replace with the commands, tests, reviews, or manual checks required for this chunk.

Stop condition:

- Stop when the completion target is reached, when acceptance criteria are unclear, or when repeated attempts stop producing new evidence.

Known gaps:

- Replace with unverified items, deferred hardening, or risks.

## Timestamp Rule

Use ISO-style timestamps for work notes, handoffs, decisions, exceptions, release notes, and validation records. Prefer the local command:

```bash
date -Iseconds
```

## Validation Log

| Timestamp | Command | Result | Notes |
|-----------|---------|--------|-------|
| YYYY-MM-DD | `git status --short` | pending | Always check repo state before edits. |
| YYYY-MM-DD | `bash scripts/governance-preflight.sh` | pending | Required for material or risk-triggering work; replace with the real validation result when run. |

## Next Handoff

The next session starts fresh: check `git status --short`, read `AGENTS.md`, take the first `Status: Ready` chunk above, and open only the files it names. After compaction or a context clear, resume from this document and `CARRY_FORWARD.md` before loading anything else.
