# Current Build Pathway

Last Updated: 2026-08-31
Status: active
Owner: Technical Lead

## Purpose

This document is the live path from current plan to completed build. It keeps agent work small, timestamped, and easy to resume.

## Required Work Pattern

For ordinary scoped work, use lean startup:

1. Check `git status --short`.
2. Read the short repo-local agent instructions.
3. Use `docs/context-map.md` when context routing is unclear.
4. Inspect only the specific files, errors, or docs needed for the task.
5. Run targeted validation after the change.

For material or risk-triggering work sessions:

1. Start from `START_HERE.md`.
2. Run the governance preflight for the target project.
3. Review `docs/standards/README.md`.
4. Review `docs/standards/engineering-governance-by-use-case.md`.
5. Review `docs/policy/durable-development-engineering-policy.md`.
6. Review `docs/standards/ship-ready-engineering-standard.md`.
7. Review `project-control.yaml` and open exceptions.
8. Capture a timestamp with `date -Iseconds`.
9. Define the next build chunk in this document.
10. Complete and validate that chunk before expanding scope.
11. Update this document with status, validation, and the next chunk.

Risk-triggering work includes production, deployment, authentication, authorization, payments, secrets, sensitive data, database migrations, customer communications, external side effects, infrastructure or provider settings, destructive actions, autonomous tool use, risk classification, governance policy changes, or release readiness.

## Chunking Standard

Each build chunk should be small enough to fit comfortably in an agent context window.

A good chunk has:

- one objective
- a budget class: Tiny, Small, Medium, Large, or Strategic
- clear input files or documents
- clear output files or behavior
- explicit validation steps
- a timestamped status note

Use second-level Markdown headings for active and planned chunks:

```md
## Chunk One - Short Objective
## Chunk Two - Short Objective
```

## Chunk Thirty-Five - Repository Audit And Portability Remediation

Status: in progress

Completion target: Task complete

Budget class: Small

Objective: audit the governance source, refresh stale control records, and remove verified portability failures without expanding into the strategic Tier 2/3 backlog.

Acceptance criteria:

- [ ] Governance preflight and automated audit have no blockers or required gaps.
- [ ] Active/generated guidance contains no user-specific operational filesystem paths; historical audit and archive records remain unchanged.
- [ ] Architecture and generated guidance describe current module boundaries and portable discovery paths.
- [ ] Open carry-forward flags can record a review date without being falsely treated as abandoned.
- [ ] CI installs one pinned validation toolchain and cancels superseded runs within a bounded timeout.
- [ ] Risk, change, backlog, carry-forward, and pathway records reflect the 2026-08-31 review.
- [ ] Focused tests pass; any full-gate limitation is recorded without weakening enforcement.

Stop condition: stop before any risk-tier/governance-level decision, dependency adoption, provider change, or broader backlog item that requires owner direction.

## Recent Completed Work

| Step | Status | Timestamp | Notes |
|------|--------|-----------|-------|
| Chunk Twenty-Three - Graphify Policy Consolidation | complete | 2026-06-12T15:54:47-06:00 | Consolidated Graphify guidance across live instructions, templates, managed upgrade blocks, tests, and handoff files. |
| Chunk Twenty-Four - Graphify Folder Consolidation | complete | 2026-06-12T17:50:14-06:00 | Single master Graphify Tool folder; removed duplicate root graphify-out/; updated all paths. |
| Chunk Twenty-Five - Completion States And Stop Rules | complete | 2026-06-12T18:58:28-06:00 | Honest completion states, human-owned project completion, anti-loop stop rules, managed upgrade guidance. |
| Chunk Twenty-Six - Lean Startup And Preflight Integration | complete | 2026-06-13T09:13:03-06:00 | Lean startup integrated into context hygiene, live/generated instructions, and managed upgrade blocks. |
| Chunk Twenty-Seven - Cost-Effective Agentic Context Integration | complete | 2026-06-13T10:18:57-06:00 | Repo-memory, budget classes, context-map, summary-only scouts integrated without new mandatory startup reads. |
| Chunk Twenty-Eight - Governance Package Documentation Closeout | complete | 2026-06-13T10:25:50-06:00 | Public docs, generated docs, and shared handoffs updated for lean startup and cost-effective context. |
| Chunk Twenty-Nine - Token-Friendly Startup Tightening | complete | 2026-06-16T18:28:42-06:00 | Lean startup clarified; START_HERE.md made conditional; no-full-rebuild-after-clear rule propagated. |
| Chunk Thirty - Compaction Restart Efficiency | complete | 2026-06-16T19:05:02-06:00 | Active-plan routing indirect through START_HERE.md; post-compaction restart guidance added. |
| Chunk Thirty-One - Housekeeping | complete | 2026-06-16 | Hard-coded personal names removed from automation; AGENTS.md trimmed to router; pathway split. |
| Chunk Thirty-Two - Document Supersession Enforcement | complete | 2026-06-16 | Supersession scanner in change_control.py; Document Supersession section in audit report; GUI summary; template banner. |
| Chunk Thirty-Four - GitHub Resource Efficiency Ingestion | complete | 2026-07-26T20:22:46-06:00 | STD-ENG-022 added as a single canonical copy; guardrail summary distributed through the workspace-level CLAUDE.md and the project bootstrap template; no per-repo standard copy, no enforced checks. |

Full history: `docs/archive/pathway-history.md`

## Chunk Thirty - Compaction Restart Efficiency

Status: complete

Completion target: Task complete

Budget class: Small

Objective: make turnovers after compaction, context clear, and fresh restarts faster by routing agents through the latest handoff/work packet and the active plan named by `START_HERE.md` instead of hardcoding historical pathway reads.

Acceptance criteria:

- [x] Source instructions route material work to the active plan named by `START_HERE.md`, defaulting to `docs/current-build-pathway.md`.
- [x] Generated project templates inherit the same active-plan indirection.
- [x] Context hygiene source and template include a concise post-compaction/context-clear restart checklist.
- [x] Existing-project managed instruction upgrades carry the restart guidance.
- [x] Focused tests cover the new active-plan and restart guidance.

Validation:

- `python3 -m unittest tests.test_scaffold_project tests.test_change_control` passed.
- `bash automation/governance_check.sh .` passed with 0 required gaps.
- `bash scripts/validate.sh` passed with 38 tests.

## Chunk Thirty-One - Housekeeping

Status: complete

Completion target: Task complete

Budget class: Small

Objective: remove hard-coded personal names from automation scripts, trim AGENTS.md to a lean router, and split the pathway doc to under 200 lines.

Acceptance criteria:

- [x] `automation/change_control.py`: removed `"name: Adam Goodwin"` replacement and replaced absolute `/home/adamgoodwin` Graphify paths with `~`-relative paths.
- [x] `automation/new_build_headless.py`: removed `"name: Adam Goodwin"` replacement.
- [x] `AGENTS.md`: trimmed from 155 lines to ~77 lines (router only; Fundamentals-First/Context Hygiene/Graphify point to `CLAUDE.md`).
- [x] `docs/current-build-pathway.md`: split to under 200 lines; full history archived to `docs/archive/pathway-history.md`.

Inputs:

- `automation/change_control.py`
- `automation/new_build_headless.py`
- `AGENTS.md`
- `docs/current-build-pathway.md`

Validation:

- `python3 -m py_compile automation/change_control.py automation/new_build_headless.py` passed.
- `bash scripts/validate.sh` passed.

## Chunk Thirty-Three - Audit Tier-1 Remediation

Status: complete

Completion target: Integration complete

Budget class: Large

Objective: execute the five Tier-1 recommendations from docs/audits/repository-audit-2026-07-10.md and record the remaining tiers as a durable backlog.

Acceptance criteria:

- [x] Real validation gate: ruff (lint+format), mypy, shellcheck, PSScriptAnalyzer, and an explicit secret-hygiene step wired into `scripts/validate.sh` and `scripts/validate.ps1`, with CI installing the tools; `machine_enforcement` entries in `project-control.yaml` now map to real steps.
- [x] `docs/standards/governance-level-standard.md` (STD-ENG-009) defines levels 0-4 with a single crosswalk to risk tiers and autonomy; derive-vs-independent contradiction resolved in `docs/user-guide.md`.
- [x] One canonical doc home per rule: `AI_BOOTSTRAP.md` (86 lines) is the canonical agent-instruction source; `CLAUDE.md` (32) and `AGENTS.md` (17) are routers; DoR/DoD owned by ship-ready; four stub standards folded into parents and tombstoned.
- [x] One canonical code implementation per behavior: `automation/env_file.py` (shared .env parsing), `automation/project_naming.py` (slugify, reserved names, governance/risk tables, INITIAL_SCOPE); `new_build.sh` rewritten as a thin wrapper over `new_build_headless.py`; GUI gains reserved-name and slug-length guards and a Windows-correct PATH.
- [x] June metadata remediation executed: 40 docs given compliant headers; `python automation/governance_audit.py .` reports 0 blockers, 0 required gaps, 0 warnings (was 119); implementation plan's illegal `archived` statuses and bogus citation fixed.
- [x] Tier 2/3 recommendations and Tier-1 residuals recorded in `docs/audits/remediation-backlog-2026-07-10.md` (AUD-ENG-004).

Validation:

- `bash scripts/validate.sh` passed end-to-end on Windows Git Bash (compliance, schema, ruff, mypy, shellcheck, secret scan, 120 unit tests).
- `python automation/governance_audit.py .` exit 0, zero findings.
- `./scripts/validate.ps1` (including the Windows launcher build) run at close-out.

## Chunk Thirty-Four - GitHub Resource Efficiency Ingestion

Status: complete

Completion target: Integration complete

Budget class: Small

Objective: ingest the downloaded GitHub resource-efficiency standard as a single canonical copy and distribute a short guardrail summary to every project without generating a per-repo copy of the standard.

Owner decision: use the workspace-level `CLAUDE.md` at the code-workspace root as the distribution point instead of the per-repo generation model proposed by the source document. Guardrails, not enforced checks.

Acceptance criteria:

- [x] `docs/standards/github-resource-efficiency-standard.md` (STD-ENG-022) holds the full standard, with the source document's transmittal brief replaced by a distribution section, MUST language relaxed to guardrails, volatile GitHub product facts isolated and marked unverified, and skipped work recorded.
- [x] Guardrail summary added to the workspace-level `CLAUDE.md`, inherited by every project under the code-workspace root in a Claude Code session.
- [x] Summary mirrored in the standard itself so it is reproducible if the unversioned workspace file is lost.
- [x] Routed in `docs/standards/README.md`, `docs/context-map.md`, `START_HERE.md`, and `AI_BOOTSTRAP.md`.
- [x] Templates carry the guardrails and a pointer rather than a copy: `templates/project/AI_BOOTSTRAP.template.md`, `docs/standards/README.template.md`, `docs/context-map.template.md`.

Inputs:

- `~/Downloads/2026-07-26-github-resource-efficiency-standard.md`

Not done, deliberately:

- No machine-enforced checks. Any future check starts as a reporting control, not a blocking gate.
- No `GOVERNANCE-MANAGED` block in `automation/change_control.py`, so existing repos generated before this chunk do not receive the guardrails in their own instruction files. They are still covered in Claude Code through the workspace `CLAUDE.md`.
- The volatile GitHub product facts were not re-verified against GitHub documentation.

Validation:

- `bash scripts/validate.sh` exit 0 (compliance, schema, ruff, mypy, shellcheck, secret scan, 120 unit tests).
- `python -m unittest tests.test_scaffold_project tests.test_change_control` passed; template edits did not break scaffold or managed-upgrade expectations.
- `python automation/governance_audit.py .` — 0 blockers, 0 required gaps, 1 warning (the pre-existing Tier 2/3 carry-forward flag age, unrelated to this chunk). Report: `docs/audits/governance-audit-2026-07-26.md` (AUD-ENG-009).
