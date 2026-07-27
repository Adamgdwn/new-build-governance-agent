# Context Map

Document type: project context routing map
Last Updated: 2026-07-10
Status: active
Owner: Technical Lead
Audience: coding agents, human coders, reviewers, and project owners

## Purpose

This file keeps agent context loads small, deliberate, and recoverable.

The repository remembers. Agents rent context. Use this map to decide what to
load first, what to load by task type, and what to avoid unless the task needs
it.

## Always Load

- `AI_BOOTSTRAP.md` (the canonical agent instruction file; `CLAUDE.md` and `AGENTS.md` route to it)
- `START_HERE.md` for material work, unclear scope, or changes to the active plan
- `project-control.yaml` when risk, governance level, controls, or required docs matter

Keep these files compact. They should route to durable docs, not duplicate them.

## Load By Task

| Task | Load First |
|---|---|
| Current plan, chunking, validation, or handoff | Active plan named by `START_HERE.md`; default `docs/current-build-pathway.md` |
| Engineering standards map | `docs/standards/README.md` |
| Context windows, token budgets, compaction, scoped reads, or handoffs | `docs/standards/context-hygiene-standard.md` |
| Durable implementation, design quality, testing discipline, or AI coding fundamentals | `docs/policy/durable-development-engineering-policy.md` |
| Governance level meaning, level-to-tier crosswalk, or agent-action tiers | `docs/standards/governance-level-standard.md` |
| Use-case controls, agent governance records, or owner decisions | `docs/standards/engineering-governance-by-use-case.md` |
| Risk tier definitions or reclassification | `docs/standards/risk-classification-standard.md` |
| Completion labels, Definition of Shipped, release evidence, or finish reports | `docs/standards/ship-ready-engineering-standard.md` |
| Architecture decisions or system shape | `docs/architecture.md` and relevant ADRs |
| Domain terms or naming | `docs/domain-language.md` |
| Repository storage, `.gitignore`, Git LFS, Actions workflows, artifacts, caches, Packages, releases, runners, or GitHub billing | `docs/standards/github-resource-efficiency-standard.md` |
| Deployment, release, rollback, or environment changes | `docs/deployment-guide.md`, `docs/runbook.md`, and release standards |
| Agent autonomy, tools, prompts, models, or permissions | `docs/agent-inventory.md`, `docs/model-registry.md`, `docs/prompt-register.md`, and `docs/tool-permission-matrix.md` |

## Search Before Loading

- long audit reports
- old pathway history below the current active chunk
- logs, generated reports, and command output
- exported manifests
- archived plans or superseded briefs

Use `rg` or targeted file excerpts before opening long files.

## Avoid Unless Needed

- `.git/`
- `.venv/`, `venv/`, `node_modules/`, and dependency caches
- build output, coverage, and generated artifacts
- ignored Graphify output
- secrets and environment files
- large transcripts or pasted chat histories

Do not print, summarize, index, or commit secrets.

## Work Packet Reminder

For meaningful work, define:

- goal
- budget class: Tiny, Small, Medium, Large, or Strategic
- context to load first
- files or folders to avoid unless needed
- constraints and non-goals
- done-when checks
- handoff location

Tiny edits may use an inline version of this packet. Large or strategic work
should record the packet in the active plan named by `START_HERE.md`, an ADR, or
a short handoff note.

## Maintenance

Update this file when the repo's routing paths change or when agents repeatedly
load the wrong material. Keep it short enough to read at startup when context
routing is unclear.

Integration note: a downloaded cost-effective agentic coding context standard was integrated into this map on 2026-06-13. Do not add that downloaded standard as a new mandatory startup read.

Integration note: a downloaded GitHub resource-efficiency standard was integrated on 2026-07-26 as `docs/standards/github-resource-efficiency-standard.md` (STD-ENG-022), with a short guardrail summary in the workspace-level `CLAUDE.md`. Do not add that standard as a new mandatory startup read, and do not generate a per-repo copy of it.
