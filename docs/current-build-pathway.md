# Current Build Pathway

Last Updated: 2026-11-08
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

## Chunk Forty-Six - Documentation Scaffold Passes Its Own Compliance Check

Status: complete

Completion target: Task complete

Budget class: Small

Timestamp: 2026-11-08T21:01:34-06:00

Source: AUD-ENG-004 item B-6 (the documentation-type sub-item), chosen by the owner on 2026-11-08 as the next chunk.

Objective: a freshly scaffolded `documentation` project passes its own compliance report. The scaffold deliberately skips `docs/deployment-guide.md` and `docs/runbook.md` for documentation projects, but the generated `project-control.yaml` still listed both as required, so `compliance_report.py` returned `failed` at every governance level.

Acceptance criteria:

- [x] `automation/scaffold_project.py` keeps the skipped docs and the generated `required_docs` list in step: one table names the operational docs and the types that skip them, and the list is trimmed only when the scaffold writes `project-control.yaml`. Existing control files are kept as they are.
- [x] Regression test: every project type at every governance level passes its own compliance report straight after scaffolding.
- [x] Structural tests: documentation projects neither get nor require the two docs, other types get and require both, and an existing documentation `project-control.yaml` is left unchanged.
- [x] Backlog bookkeeping: the B-6 documentation sub-item recorded as done, B-14 closed, and the review dates current.
- [x] `bash scripts/validate.sh` with the pinned tools exits 0, and the governance audit stays clean.

Stop condition: stop before any template edit, any other B-6 sub-item, or any change to how `change_control.py` treats existing projects.

Findings:

- Before the fix, a probe of all 45 type and level combinations found documentation as the only failing type, failing at all five levels. The new tests failed on exactly those six cases before the fix and pass after it.
- The scaffolded `scripts/governance-check.sh` already treated the two docs as optional for documentation projects. Only the compliance report, which reads `required_docs`, disagreed.
- `change_control.py` offers both docs to every project type, documentation included, so a promoted documentation project stays consistent when it accepts them. The only documentation project found in the workspace, `home-assistant-manager`, has both docs and is unaffected.
- Not fixed (out of scope): `compliance_report.required_files_from_control` adds the AI register files only for `project_type: agent`, not legacy `agentic-harness`. Those projects still pass, because the scaffold creates the files, but their check is less strict.

Validation:

- `bash scripts/validate.sh` with the pinned tools (ruff 0.15.21, mypy 2.2.0, coverage 7.15.0) exit 0: 158 tests, coverage 36%.
- CLI check: `scaffold_project.py <dir> documentation`, then `compliance_report.py <dir>` exits 0 with 0 required gaps (exit 1 before the fix).
- `python3 automation/governance_audit.py .`: 0 blockers, 0 required gaps, 0 warnings. `graphify update . --no-cluster` exit 0.

## 2026-11-08 Frontier Refresh Plan

Owner request, 2026-11-08: research current AI engineering practice (the AI Engineer channel, frontier-lab guidance, independent practitioners), write per-build-type instructions that agents can be given, refresh this repository's rules for current frontier models, place Jev and Laya where they add the most value, treat a harness as what people mean by "agent", and finish the unfinished 2026-09-05 path work.

Owner decisions, Adam Goodwin, 2026-11-08:

- Fix the Freedom dispatcher so `freedom.tool.yaml` keeps a portable `cwd: "."`.
- Align this repository's own chunk close-out with the fresh-session-per-chunk pattern (ADR-0002 in the AI Coding Practices knowledge base). This resolves the matching carry-forward flag.
- Merge the intake's "AI helper" and "agentic harness" choices into one "AI agent (harness)" choice.
- Frontier updates to AI Coding Practices topics go into a dated change proposal for that knowledge base. The knowledge base itself is not edited.

| Chunk | Objective | Budget class | Status |
|---|---|---|---|
| Forty | Workspace paths and preview routing | Small | complete |
| Forty-One | Freedom dispatcher resolves a relative `cwd` (the-freedom-engine-os) | Tiny | complete (draft PR #73 awaiting merge) |
| Forty-Two | One "AI agent (harness)" intake choice | Medium | complete |
| Forty-Three | Build-type agent playbooks | Large | complete |
| Forty-Four | Frontier AI engineering research record, including Jev and Laya | Medium | complete |
| Forty-Five | Frontier-model rules refresh and knowledge-base change proposal | Large | complete |

## Chunk Forty-Five - Frontier-Model Rules Refresh

Status: complete

Completion target: Integration complete

Budget class: Large

Timestamp: 2026-11-08T20:31:59-06:00

Objective: bring this repository's own rules and the generated standards up to date for current frontier models, align this repository's chunk close-out with the fresh-session pattern (owner decision 2026-11-08), and propose matching changes to the AI Coding Practices knowledge base without editing it.

Acceptance criteria:

- [x] `AI_BOOTSTRAP.md` and `CLAUDE.md`: chunk close-out ends with a fresh session for the next chunk, and within a chunk relies on automatic compaction rather than resets. The stated reason is a clean start from a written definition of done, not context capacity. A "Working With Frontier Models" section covers plain-language rules, evidence of completion, deterministic checks first, hooks for hard rules, the role of subagents, package and configuration trust, and model settings over prompt wording.
- [x] Context Hygiene Standard and its template: subagents justified by parallelism, isolation, or independent review rather than capacity; compaction guidance for 1M-token models.
- [x] Engineering Governance By Use Case and its template: Harness Engineering Controls under AI Agents With Tools (Rule of Two, tripwires versus boundaries, bound approvals and caps, supply-chain pinning, evaluation sets as data, retesting at model releases, trace logging, System One rules).
- [x] Durable Development Policy and its template: working with current coding agents.
- [x] Harness README template (decisions table, Rule of Two question) and model registry template (exact model IDs, settings, eval set, re-evaluation before switching).
- [x] Build playbooks gained the AI Engineer findings: checking before retrying after a timeout, recording state before external changes, prompt-cache ordering, effort-for-cost trade-offs, credentials and egress outside the agent, and proof a reviewer can check.
- [x] README screenshots retaken from the current GUI on a virtual display, with updated alt text.
- [x] `docs/proposals/2026-11-08 - AI Coding Practices Knowledge Base Change Proposal.md`: seven items for owner review. The knowledge base was not edited.
- [x] Carry-forward: fresh-context and screenshot flags cleared, the proposal flagged, and the three standing flags reviewed with what changed.

Finding during research: Anthropic's current guidance says context resets are no longer needed to save room on 1M-token models, and lists "subagents to protect context" under things to stop doing. Fresh sessions remain recommended between unrelated tasks and when starting a build from a written specification, which is what a chunk is. The owner's close-out decision stands on that basis.

Validation:

- `bash scripts/validate.sh` with the pinned tools exit 0 (154 tests, coverage 36%); governance audit 0 blockers, 0 required gaps, 0 warnings.

## Chunk Forty-Four - Frontier AI Engineering Research Record

Status: complete

Completion target: Task complete

Budget class: Medium

Timestamp: 2026-11-08T20:30:23-06:00

Objective: keep the evidence behind the 2026-11-08 rule changes in the repository, so later agents can check why a rule exists without the chat thread.

Acceptance criteria:

- [x] `docs/research/2026-11-08 - Frontier AI Engineering Practice Research.md` records method, limits, findings by theme, contested points, volatile facts with dates, what changed in the repository, and sources.
- [x] The AI Engineer channel is covered from real transcripts: 24 of 30 shortlisted 2026 talks, each listed with its link.
- [x] Jev and Laya are compared from TypeSafe's live documentation, Laya's published limits, and Adam's 2026-10-10 Laya qualification, with placement rules for harnesses, products, CI, and large data.

Known gaps:

- YouTube rate-limited caption downloads, so 20 of the 24 talks were summarised from the channel's own ai.engineer transcripts by reader agents without a second check. The AlixPartners and Ramp talks were not retrieved; McKinsey was retrieved but not analysed.
- OpenAI's "Harness engineering" post returned HTTP 403; its claims come from secondary sources and the author's talk.

Validation:

- Every source link in the record came from the research notes; the one speaker attribution questioned during review was checked against the transcript notes.

## Chunk Forty-Three - Build-Type Agent Playbooks

Status: complete

Completion target: Integration complete

Budget class: Large

Timestamp: 2026-11-08T20:18:42-06:00

Objective: give coding agents type-specific instructions they can be handed for each kind of build, delivered with every new project and offered to existing ones, grounded in the 2026-11-08 research (frontier-lab guidance, independent practitioners, security and evaluation sources, TypeSafe documentation, and Laya's published limits).

Acceptance criteria:

- [x] Eight playbooks in `templates/project/docs/playbooks/`: agent (harness), application, website, service, internal tool, automation, infrastructure, and documentation. Each covers what done looks like, preparation, build rules, verification, the failure modes agents produce in that build type, security, where a System One model fits (Jev hosted, Laya local), and when to stop and ask.
- [x] Written for current frontier models: plain language with reasons, no emphatic capitals, deterministic checks before model judgment, and evidence-based completion.
- [x] The scaffold delivers the matching playbook as `docs/build-playbook.md` (legacy `agentic-harness` gets the agent playbook), and the generated `AGENTS.md` routes to it.
- [x] `automation/change_control.py propose` offers the playbook to existing projects. A fresh scaffold still yields an empty upgrade manifest.
- [x] One type-to-playbook table (`PLAYBOOK_BY_TYPE` in `automation/project_naming.py`) serves both the scaffold and change control.
- [x] The standards index and README route to the playbooks. They are guidance inside existing standards, not new controls.

Also fixed: change control treated only `agent`, not legacy `agentic-harness`, as an agent project, so v0.3.0 harness projects were not offered their AI registers.

Validation:

- Throwaway `application` and `agent` projects scaffolded from the new templates: the application's own `scripts/governance-check.sh` exited 0, the agent passed schema validation, and `change_control.py propose` on the fresh agent project produced 0 actions.
- New tests: every project type has a playbook template; the scaffold delivers the matching playbook; `AGENTS.md` routes to it; change control offers the right playbook and AI registers to existing projects.
- `bash scripts/validate.sh` exit 0 (154 tests, coverage 36%); governance audit 0 blockers, 0 required gaps.

## Chunk Forty-Two - One AI Agent (Harness) Intake Choice

Status: complete

Completion target: Task complete

Budget class: Medium

Timestamp: 2026-11-08T20:11:35-06:00

Objective: carry out the owner decision that an agent is a harness. The intake offers one "An AI agent (harness)" choice instead of separate "AI helper" and "agentic harness" choices, and every agent project gets the harness record, from every entry point.

Finding: the v0.3.0 harness feature was only partly wired. A project the GUI created with type `agentic-harness` failed its own `project-control.yaml` schema check, `change_control.py` mapped it to the web-application use case, headless routed it to the applications folder (fixed in Chunk Forty), and the Freedom manifest could not request it.

Acceptance criteria:

- [x] GUI: one agent purpose, which always shows the AI-topology step. The old `harness` value is kept only as an alias for the canonical `agent` type.
- [x] `agent` stays the one canonical project type, already wired through schema, compliance, change control, and Freedom. `agentic-harness` is accepted as a legacy v0.3.0 type and validates.
- [x] Every agent project gets `docs/harness/README.md` and a `harness_profile`. When the topology was not asked (headless, terminal, or advanced settings), it is recorded as `undecided` with instructions to choose before the first model call, rather than guessed.
- [x] Headless, `new_build.sh`, `new_build.ps1`, and `freedom.tool.yaml` accept an optional harness topology and description, and the terminal launchers ask the topology question for agent builds.
- [x] README describes the single choice.

Not done, deliberately:

- The README screenshots still show the v0.3.0 choices. A carry-forward flag tracks retaking them.
- The harness README template's content is refreshed in Chunk Forty-Five, not here.
- The PowerShell prompt was not executed locally (no PowerShell on this machine).

Validation:

- `bash scripts/validate.sh` exit 0 (150 tests, coverage 36%); governance audit 0 blockers, 0 required gaps.
- Focused suites for GUI, scaffold, schema, headless, and change control: 53 tests passed, with new tests for the single choice, the legacy alias, undecided and chosen topologies, topology rejection, and legacy harness schema validity.
- A dry run of `bash automation/new_build.sh --build-type agent` asked the topology question, previewed `~/01. Code/03. Agents/topology-probe`, and created nothing.

## Chunk Forty-One - Freedom Dispatcher Relative Tool Working Directory

Status: complete (delivered as a draft pull request; merging is the owner's decision)

Completion target: Task complete

Budget class: Tiny

Timestamp: 2026-11-08T20:04:39-06:00

Objective: let `freedom.tool.yaml` keep a portable `cwd: "."` by having the Freedom dispatcher resolve a relative `cwd` against the manifest's own folder, instead of restoring an absolute workstation path in this public repository.

Acceptance criteria:

- [x] `the-freedom-engine-os` dispatcher: `invoke_subprocess` takes an optional `manifest_dir`, filled by `main.py` from `registry.get_manifest_path()`. Absolute paths, a missing `cwd`, and tools without a recorded manifest path behave as before.
- [x] Built in an isolated worktree from that repository's `origin/main`. Its active `agent/stage-c-overnight-turnover` checkout, which holds uncommitted 2026-09-05 path edits and three unpushed commits, was not touched.
- [x] That repository's rules were followed: governance preflight passed, and a testing summary was added under `docs/live-tests/`.
- [x] `freedom.tool.yaml` documents the relative `cwd` contract.

Validation:

- `test_dispatcher_cwd.py`: 5 tests passed, including a real subprocess.
- The dispatcher engine ran New Build's real manifest with `--plan` appended and returned `status: planned`. Without the manifest folder it reproduced the original defect. Nothing was created.
- Delivered as draft PR #73 (`fix/relative-tool-cwd`). The live FastAPI service run is held, because a real create would scaffold a project. A carry-forward flag tracks the merge.

## Chunk Forty - Workspace Paths And Preview Routing

Status: complete

Completion target: Task complete

Budget class: Small

Timestamp: 2026-11-08T19:59:12-06:00

Objective: finish the 2026-09-05 home-folder path work so New Build works with numbered workspace folders (`01. Code`, `03. Agents`, `02. Applications`) without hard-coding one machine's layout, and make the terminal previews impossible to drift from the real routing.

Context: the 2026-09-05 edits were found uncommitted on a base eight commits behind `origin/main`. They are preserved unchanged on the local branch `wip/2026-09-05-path-migration` (`564a23a`). On synced `main`, importing the GUI tried to create `~/code/Applications`, which on this workstation resolves through the temporary `code` alias to a stray `~/01. Code/Applications`. The sandbox blocked it and the GUI test module errored.

Acceptance criteria:

- [x] `automation/workspace_paths.py` ignores a numeric ordering prefix when recognising code-root and category folders, reuses an existing category folder (real folders before aliases), and treats the parent of a category folder as the code root. Public defaults stay `~/code/agents` and `~/code/Applications`.
- [x] Resolving paths never creates folders. The GUI creates missing category folders in `main()` at launch, not at import, and its folder pickers default to the detected code root.
- [x] `new_build_headless.py --plan` runs the same validation and routing as a real build and writes nothing. `new_build.sh` and `new_build.ps1` preview through it and no longer carry their own code-root logic.
- [x] Headless routes `agentic-harness` projects to the agents folder, matching the GUI (`AGENT_PROJECT_TYPES` in `automation/project_naming.py`).
- [x] `master_env.py` registry gating from the preserved branch is re-applied: `set` and `merge` accept only keys already reviewed into the master registry.
- [x] README, INSTALL, architecture, and automation reference describe the detection rules.

Not done, deliberately:

- The path edits on the preserved branch were not merged. Upstream commit `5e68ca6` had already replaced the `change_control.py` Graphify block and the runbook path with portable versions, and the remaining edits hard-coded one workstation's layout.
- The PowerShell create path was not executed locally (no PowerShell on this machine). The Windows CI job parses it with PSScriptAnalyzer and smoke-tests `-Version` only.

Validation:

- A dry run on this workstation previewed `/home/adamgoodwin/01. Code/03. Agents/preview-probe` for a harness through `bash automation/new_build.sh`, aborted at the confirmation prompt, and created nothing (no stray `Applications` folder).
- New tests cover prefix detection, alias preference, side-effect-free resolution, `--plan` (no writes, harness routing, validation failure), and harness routing.
- `bash scripts/validate.sh` with the pinned `requirements-dev.txt` tools (ruff 0.15.21, mypy 2.2.0, coverage 7.15.0) exit 0: compliance (0 required gaps), schema, ruff lint and format, mypy, shellcheck, secret scan, 141 unit tests, coverage 35% against the 25% floor.

## Chunk Thirty-Nine - Build-To-Sale Lifecycle Standard

Status: complete

Completion target: Integration complete

Budget class: Small

Timestamp: 2026-09-30T10:43:32-06:00

Objective: make the owner-supplied Build-to-Sale Operating System a cross-project standard, so projects intended for sale carry market validation, pre-sale, commercial readiness and a funding, credits and partners search alongside the existing engineering controls.

Owner decision: Adam Goodwin, 2026-09-30, approved cross-project use after it was first applied to Span OS, and asked that the lifecycle include a search for grants, loans, hosting credits and partners.

Acceptance criteria:

- [x] `docs/standards/build-to-sale-lifecycle-standard.md` (STD-ENG-025) holds adoption rules in Part A (scope, relationship to existing standards, core rules, funding/credits/partners track, agent boundaries, document locations) and the source framework as Part B, with headings shifted one level and text otherwise unchanged.
- [x] The standards index, context map and governance-source alignment examples route to it. It is not a mandatory startup read.
- [x] The workspace-level `CLAUDE.md` carries a short summary, following the STD-ENG-022 distribution pattern.
- [x] A carry-forward flag records the deferred distribution work.

Not done, deliberately:

- No scaffold template, managed-upgrade block, `project-control.yaml` field or schema change. The owner decides scope and order (carry-forward flag).
- No alignment review of existing projects. Span OS applied the framework directly on 2026-09-30; GazeCut and others have not been reviewed.

Validation:

- `PYTHON=py bash scripts/validate.sh` exit 0: compliance (0 required gaps), schema, lint, secret scan, 129 unit tests.
- `py automation/governance_audit.py .`: 0 blockers, 0 required gaps, 3 warnings (existing carry-forward flags due for review). Report: `docs/audits/governance-audit-2026-09-30.md`.

## Chunk Thirty-Eight - AI Coding Best Practices Fold-In

Status: complete

Completion target: Integration complete

Budget class: Medium

Timestamp: 2026-09-02T15:21:24-06:00

Objective: fold the plan-once, run-chunks pattern approved in the AI Coding Best Practices knowledge base (POL-AIC-001, STD-AIC-001 to 005, ADR-0001 to 0005, approved by the owner on 2026-09-02) into the generated project templates without changing this repository's standards.

Owner decision: Adam Goodwin, 2026-09-02, approved folding the pattern into the templates.

Acceptance criteria:

- [x] `CLAUDE.template.md` is the one-line import `@AGENTS.md`. `AGENTS.template.md` is the single canonical instruction file in the STD-AIC-001 shape (What this is, Start, Commands, Rules, Finish a chunk, Read when relevant), 55 lines, and still carries every phrase the scaffold tests and the managed-block fragments require. `AI_BOOTSTRAP.template.md` holds commands only, with the `- Lint:`, `- Test:`, and `- Build:` lines the compliance report reads.
- [x] `docs/current-build-pathway.template.md` uses runner-readable chunks (`### P-NN - Title`, `Status: Ready`, `Runner:`, `Files:` allow-list) and the plan-once, approve-once, fresh-session-per-chunk work pattern.
- [x] `START_HERE.template.md`, `docs/context-map.template.md`, `docs/standards/README.template.md`, and `project-control.template.yaml` route to the AIC standards by name (canonical copies stay in the knowledge base) and tighten the instruction-file budgets (AGENTS.md 4 KB, CLAUDE.md 1 KB).
- [x] `automation/change_control.py` skips managed-block appends to `CLAUDE.md` and `AI_BOOTSTRAP.md` when `CLAUDE.md` is an import-only file, so an upgrade cannot double-load guidance in the new layout. Two new tests cover it, and a freshly scaffolded project now yields an empty upgrade manifest.
- [x] `README.md` and `docs/user-guide.md` describe the generated instruction files as they now are.

Not done, deliberately:

- The runner itself (`scripts/agent/`, hook wiring) is not scaffolded. It stays pinned in the knowledge base under `reference/agent-runner/` with the adoption process PRC-AIC-002, to avoid a third copy that drifts.
- This repository's own `AGENTS.md`, `CLAUDE.md`, and `AI_BOOTSTRAP.md` still follow the compact-after-chunk close-out. See the new carry-forward flag.
- The template `AGENTS.md` is 961 words against the STD-AIC-001 target of about 600, because the scaffold tests mandate the full Graphify policy text and ten governance phrases. Projects slim their own copy.
- No standard in `docs/standards/` was changed.

Validation:

- `PYTHON=py bash scripts/validate.sh` exit 0: compliance (0 required gaps), schema, ruff lint and format, mypy, shellcheck, secret scan, 129 unit tests.
- A throwaway `application` project scaffolded from the new templates: `bash automation/governance_check.sh` exit 0, 0 required gaps, 5 recommended items (command placeholders and optional files).
- `python automation/governance_audit.py .`: 0 blockers, 0 required gaps, 0 warnings. Report: `docs/audits/governance-audit-2026-09-02.md`.

## Chunk Thirty-Seven - Public Documentation And GitHub Metadata

Status: complete

Completion target: Release ready

Budget class: Tiny

Objective: make the new complexity and periodic governance-alignment controls visible in the public documentation and GitHub repository information.

Acceptance criteria:

- [x] The public README explains both controls in plain language and links directly to their canonical standards.
- [x] The user guide, project manual, generated README/manual, and automation reference describe the new scaffolded controls consistently.
- [x] The GitHub repository description and topics surface code quality, cyclomatic complexity, and the 90-day alignment behavior.
- [x] The additions remain under `Unreleased`; no version tag or GitHub Release is created without a separate version decision.

Validation:

- Focused scaffold, change-control, and schema tests passed (11 tests).
- `bash automation/governance_check.sh .` passed with zero required gaps.
- `scripts/validate.ps1` passed completely: ruff, mypy, PowerShell analysis, shellcheck, secret scan, 127 tests, launcher smoke tests, and Windows package build.
- GitHub repository metadata was read back after update and showed the new description plus `code-quality` and `cyclomatic-complexity` topics.

Completed: 2026-08-31T13:49:39-06:00

## Chunk Thirty-Six - Complexity Controls And Governance Alignment

Status: complete

Completion target: Integration complete

Budget class: Small

Objective: add plain-language cyclomatic-complexity controls and a lightweight periodic check-back from governed builds to this governance source.

Acceptance criteria:

- [x] A controlled complexity standard defines the metric's limits, advisory bands, test companion, anti-gaming rule, rollout, and exception evidence.
- [x] A higher-level alignment standard prompts active builds every 90 days and before relevant release work without becoming an ordinary-startup check.
- [x] Source instructions, project templates, the workspace umbrella, and managed upgrades carry concise prompts.
- [x] New project controls default complexity to advisory mode and record governance-source cadence without overriding local risk or governance decisions.
- [x] Schema, scaffold, and change-control tests cover the new controls and distribution paths.

Known baseline: Ruff C901 currently reports 13 existing functions above 10, ranging from 11 to 37. They remain advisory and are not an authorization for unrelated refactoring.

Stop condition: stop after validation and distribution are proven; do not refactor existing complexity findings or promote the advisory control to a blocking gate without a separate decision.

Validation:

- `python -m unittest tests.test_schema_validation tests.test_scaffold_project tests.test_change_control` passed (11 tests).
- Full `unittest` suite passed (127 tests); coverage remained above the enforced floor at 34%.
- Ruff lint and format checks passed; the advisory C901 report retained the 13-finding baseline with no new finding from this chunk.
- Governance preflight and audit passed with zero required gaps; audit report `AUD-ENG-010` was refreshed.
- Local mypy execution remains blocked by Windows Application Control as recorded in risk `R-009`; the unchanged CI gate remains authoritative for mypy.

## Chunk Thirty-Five - Repository Audit And Portability Remediation

Status: complete

Completion target: Task complete

Budget class: Small

Objective: audit the governance source, refresh stale control records, and remove verified portability failures without expanding into the strategic Tier 2/3 backlog.

Acceptance criteria:

- [x] Governance preflight and automated audit have no blockers or required gaps.
- [x] Active/generated guidance contains no user-specific operational filesystem paths; historical audit and archive records remain unchanged.
- [x] Architecture and generated guidance describe current module boundaries and portable discovery paths.
- [x] Open carry-forward flags can record a review date without being falsely treated as abandoned.
- [x] CI installs one pinned validation toolchain and cancels superseded runs within a bounded timeout.
- [x] Risk, change, backlog, carry-forward, and pathway records reflect the 2026-08-31 review.
- [x] Focused tests pass; any full-gate limitation is recorded without weakening enforcement.

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
| Chunk Thirty-Five - Repository Audit And Portability Remediation | complete | 2026-08-31 | Audit/control records refreshed, portable Graphify discovery added, the validation toolchain pinned, and current GitHub Actions bounded and upgraded; CI and Windows packaging passed. |
| Chunk Thirty-Six - Complexity Controls And Governance Alignment | complete | 2026-08-31T13:24:17-06:00 | STD-ENG-023 and STD-ENG-024 added; advisory complexity controls and 90-day check-back prompts distributed through source instructions, scaffolds, managed upgrades, and the workspace umbrella. |
| Chunk Thirty-Seven - Public Documentation And GitHub Metadata | complete | 2026-08-31T13:49:39-06:00 | Public and generated documentation now explain the controls; GitHub description and topics surface the addition without creating an unapproved version release. |
| Chunk Thirty-Nine - Build-To-Sale Lifecycle Standard | complete | 2026-09-30T10:43:32-06:00 | STD-ENG-025 added as a single canonical copy with a workspace `CLAUDE.md` summary; scaffold and upgrade distribution deferred to a carry-forward flag. |
| Chunk Forty - Workspace Paths And Preview Routing | complete | 2026-11-08T19:59:12-06:00 | Numbered workspace folders detected without hard-coding a layout; side-effect-free path resolution; launchers preview through `new_build_headless.py --plan`; harness routing matches the GUI; master env registry gating re-applied. |
| Chunk Forty-One - Freedom Dispatcher Relative Tool Working Directory | complete | 2026-11-08T20:04:39-06:00 | Dispatcher resolves a relative tool `cwd` against the manifest folder; delivered as draft PR #73 in the-freedom-engine-os. |
| Chunk Forty-Two - One AI Agent (Harness) Intake Choice | complete | 2026-11-08T20:11:35-06:00 | One agent choice that always asks the AI topology; every agent project gets a harness record; v0.3.0 harness projects now pass schema validation. |
| Chunk Forty-Three - Build-Type Agent Playbooks | complete | 2026-11-08T20:18:42-06:00 | Eight agent-facing playbooks delivered as `docs/build-playbook.md` by project type and offered to existing projects through change control. |
| Chunk Forty-Four - Frontier AI Engineering Research Record | complete | 2026-11-08T20:30:23-06:00 | Dated research record: AI Engineer talks, lab guidance, practitioner, evaluation, and security sources, and the Jev and Laya placement analysis. |
| Chunk Forty-Five - Frontier-Model Rules Refresh | complete | 2026-11-08T20:31:59-06:00 | Fresh-session close-out here; frontier-model rules in AI_BOOTSTRAP, context hygiene, use-case standard, policy, and harness templates; knowledge-base change proposal for owner review. |
| Chunk Forty-Six - Documentation Scaffold Passes Its Own Compliance Check | complete | 2026-11-08T21:01:34-06:00 | One table drives the documentation type's skipped docs and its `required_docs`; every type at every governance level now passes its own compliance report; audit backlog B-14 closed. |

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
