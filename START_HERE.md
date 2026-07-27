# Start Here

Last Updated: 2026-06-13
Status: active
Owner: Adam Goodwin

## Current Plan

This repository maintains the governance framework used to create and upgrade governed projects. For ordinary scoped work, start with the lean startup checklist below; read this file and follow the active plan named here for material work, unclear scope, handoffs, or changes that affect the active plan.

Current priorities:

- keep the project scaffold safe to apply to new and existing builds
- classify projects by use case before development begins
- make the durable development policy part of every governed build
- make ship-readiness evidence part of every governed build
- make context hygiene, scoped reads, compaction, and handoff practices available to every governed build
- make `docs/context-map.md` the short routing map for task-specific context loads
- keep startup lean: use short repo orientation first, then trigger governance, Graphify, plugins, MCP tools, and release checks by task risk or scope
- make Graphify the first orientation tool before broad source exploration or architecture analysis, using workspace routing plus repo-local semantic graphs for heavy active repos
- make agent work traceable with timestamps
- keep planning and implementation in context-window-friendly chunks
- preserve copy-if-missing behavior for existing projects
- integrated a downloaded codex startup-preflight lean-out plan into durable standards and agent instructions on 2026-06-13; do not add that downloaded plan as a new mandatory startup read
- integrated a downloaded cost-effective agentic coding context standard into durable standards, context routing, templates, and managed upgrades on 2026-06-13; do not add that downloaded standard as a new mandatory startup read
- integrated a downloaded GitHub resource-efficiency standard on 2026-07-26 as a single canonical copy (`docs/standards/github-resource-efficiency-standard.md`, STD-ENG-022) with a short guardrail summary in the workspace-level `CLAUDE.md`; these are guardrails rather than enforced checks, and no per-repo copy of the standard is generated

## Current Build Pathway

Default live build route: [docs/current-build-pathway.md](docs/current-build-pathway.md).

If a project later promotes a different active plan, name it in `START_HERE.md`
and route agents there instead of rereading archived pathway history.

For ordinary scoped work:

1. Run `git status --short`.
2. Read the repo-local agent instructions.
3. Use `docs/context-map.md` when context routing is unclear.
4. Inspect the specific files, errors, or docs needed for the task.
5. Run targeted validation after the change.

For material or risk-triggering changes:

1. Run `bash automation/governance_check.sh /path/to/project`.
2. Review `docs/standards/README.md`.
3. Review `docs/standards/engineering-governance-by-use-case.md`.
4. Review `docs/policy/durable-development-engineering-policy.md`.
5. Review `docs/standards/ship-ready-engineering-standard.md`.
6. Review `project-control.yaml`.
7. Check `exceptions` in `project-control.yaml` and any exception records.
8. For broad source exploration, architecture analysis, dependency tracing, or cross-repo planning, use the Graphify governance policy (in the Graphify tool repo, `docs/agent-governance.md`) before reading raw source broadly. Reference the Graphify workspace graph for cross-repo routing, set up repo-local Graphify when a new repo becomes active, run `/graphify /path/to/repo` from Claude Code for full semantic repo graphs on heavy active repos, and update the relevant graph after code changes.
9. Capture the work timestamp with `date -Iseconds`.
10. Work in the smallest complete chunk that can be reviewed safely.

Risk-triggering work includes production, deployment, authentication, authorization, payments, secrets, sensitive data, database migrations, customer communications, external side effects, infrastructure or provider settings, destructive actions, autonomous tool use, risk classification, governance policy changes, or release readiness.

## Agent Handoff

Agents should leave enough context for the next session to resume without rereading the entire repo. Update the current build pathway when the active plan, status, risks, or next chunk changes.

After compaction or a context clear, restart from the latest handoff/work packet,
then run `git status --short`, read the short repo-local instructions, and open
only the active plan and files needed for the next objective.
