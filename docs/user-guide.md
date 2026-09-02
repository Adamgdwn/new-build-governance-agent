# User Guide

Last Updated: 2026-08-31
Status: active
Owner: Technical Lead

This guide covers how to use the framework day-to-day: creating projects, validating governance, customising templates, and understanding what each file does.

---

## Agent flow

```mermaid
flowchart TD
    A([Launch]) --> B{Interface}
    B -->|Terminal| C["bash automation/new_build.sh"]
    B -->|Desktop GUI| D["automation/launch_gui.sh"]
    C & D --> E

    subgraph intake [" Step 1 — Intake "]
        E["Project name\nfree text · auto-slugified to directory name"] --> F

        F{Build type} -->|app| F1[application]
        F -->|agent| F2[agent]
        F -->|tool| F3[internal-tool]
        F -->|other| F4[automation]

        F1 & F2 & F3 & F4 --> G

        G["Stack\nfree text description of your tech stack\ne.g. python / fastapi   react / node   not specified"] --> H

        H["Builder model\nclaude · codex · local · hybrid\nRecorded in project-control.yaml and INITIAL_SCOPE.md"] --> I

        I{Governance level} -->|0-1| I1[risk_tier: low]
        I -->|2| I2[risk_tier: medium]
        I -->|3| I3[risk_tier: high]
        I -->|4| I4[risk_tier: critical]

        I1 & I2 & I3 & I4 --> J

        J{Capture scope brief now?} -->|yes| K["Problem statement\nPrimary user or consumer\nMVP description\nWritten to INITIAL_SCOPE.md"]
        J -->|no| L[Skip — fill in before first session]
    end

    K & L --> M

    subgraph routing [" Step 2 — Route "]
        M["Slugify name\nlowercase · spaces and underscores become dashes"] --> N{Type}
        N -->|agent| O["~/code/agents/slug/"]
        N -->|"app · tool · other"| P["~/code/Applications/slug/"]
    end

    O & P --> Q

    subgraph confirm [" Step 3 — Confirm "]
        Q{Directory\nalready exists?} -->|yes| R["Warn: existing files\nwill not be overwritten"]
        Q -->|no| S["Show plan\nname · type · governance level · risk tier · full path"]
        R --> S
        S -->|no| T([Abort — nothing written])
        S -->|yes| U[Proceed]
    end

    U --> V

    subgraph scaffold [" Step 4 — bootstrap_project.sh "]
        V["Copy templates\ncopy-if-missing — safe on existing projects"] --> W["Core files\nREADME · CLAUDE · AGENTS · AI_BOOTSTRAP\nproject-control.yaml\ndocs: architecture · context-map · current-build-pathway\ndurable engineering policy · standards map · risk-register · CHANGELOG\nadr-template · exception-record-template\ndeployment-guide · runbook\nscripts/governance-preflight.sh"]
        W --> X["Patch project-control.yaml\nproject name · type · governance level · risk tier"]
        X --> Y{Agent project?}
        Y -->|yes| Z["Add agent-specific docs\nagent-inventory · model-registry\nprompt-register · tool-permission-matrix"]
        Y -->|no| AA[Standard doc set only]
    end

    Z & AA --> AB

    subgraph post [" Step 5 — Post-scaffold "]
        AB["Create extra directories\ndocs/adr · docs/specs · docs/runbooks · archive"] --> AC["Fill project-control.yaml\nowner name · builder model"]
        AC --> AD["Write INITIAL_SCOPE.md\nclassification table · build approach\nscope brief · first-session checklist"]
    end

    AD --> AE([Project ready\nOpen in your editor · fill in AI_BOOTSTRAP.md commands])
```

---

## Creating a new project

### Project root and categories

New Build Governance Agent keeps generated projects in the same two categories on every machine:

| Category | Created under | Used for |
|---|---|---|
| Agent projects | `<project-root>/agents` | AI agents and agentic systems |
| Applications | `<project-root>/Applications` | apps, tools, automations, and other builds |

By default, `<project-root>` is inferred from the install location. If the agent is installed inside a folder named `code` or `01. Code Projects`, that parent folder is used. Otherwise, the default is `~/code`.

Define `NEW_BUILD_CODE_ROOT` before launch when the generated projects should live somewhere else:

```powershell
$env:NEW_BUILD_CODE_ROOT = "C:\Users\you\01. Code Projects"
```

```bash
export NEW_BUILD_CODE_ROOT="$HOME/code"
```

Create the category folders before first use if they do not already exist. The launchers also create them automatically when they can.

### Windows and version-update roadmap

Windows support and version updates should be added in small, reviewable chunks. The goal is that a user can clone the repository from GitHub on Windows, run the framework without WSL, and later keep the checkout current without guessing which files or commands matter.

Execution should follow this timestamped chunk ledger:

| Chunk | Scope | Status | Completion timestamp | Notes |
|---:|---|---|---|---|
| 1 | Windows-first launch support | complete | 2026-06-01T11:07:02-06:00 | Added PowerShell entry points, avoided normal-use WSL requirements, normalized first-run paths, and added Windows CI validation. |
| 2 | Version source of truth | complete | 2026-06-01T11:36:57-06:00 | Added `VERSION`, version helper commands, GUI version display, release documentation, and version tests. |
| 3 | Read-only update checks | complete | 2026-06-01T12:00:28-06:00 | Added `automation/update_check.py` and launcher flags that compare local `VERSION` against GitHub releases or semantic version tags; reports current, behind, ahead, or unable to check without changing files. |
| 4 | Guarded self-update | complete | 2026-06-01T12:17:12-06:00 | Added explicit self-update commands that refuse dirty, detached, missing-upstream, ahead, or diverged checkouts and update only by `git merge --ff-only`. |
| 5 | Windows validation hardening | complete | 2026-06-01T12:38:41-06:00 | Expanded `scripts/validate.ps1` with agent-specific required-file checks and Windows launcher smoke tests for version, update-check, and self-update failure reporting. |
| 6 | GUI update affordances | complete | 2026-06-01T13:05:20-06:00 | Added Agent Updates controls to the GUI; the Update button is offered only after a dry-run confirms a safe fast-forward is possible. |
| 7 | Windows EXE package | complete | 2026-06-05T17:37:22-06:00 | Added a reviewable Windows `.exe` launcher, Windows package build script, CI artifact workflow, and tag-based GitHub Release asset publishing. |

Keep this ledger current when a chunk starts or completes. Every completed chunk should have an ISO timestamp from `date -Iseconds` or the Windows equivalent.

### Terminal (Linux/macOS)

```bash
bash automation/new_build.sh
```

### PowerShell (Windows)

```powershell
.\automation\new_build.ps1
```

### Double-click GUI (Windows)

For non-technical Windows users, download `NewBuildGovernanceAgent-Windows.zip` from GitHub Releases, unzip it, and double-click:

```text
NewBuildGovernanceAgent.exe
```

The `.exe` starts the desktop GUI through the same guarded PowerShell launcher used by technical users. It is a launcher for the unpacked package, so keep it in the unzipped folder with the `automation`, `docs`, `scripts`, and `templates` directories.

Build the Windows package from source on Windows:

```powershell
.\scripts\build-windows-launcher.ps1
```

The build creates:

```text
dist\windows\NewBuildGovernanceAgent.exe
dist\NewBuildGovernanceAgent-Windows.zip
```

The launcher walks you through six questions:

1. **Project name** — free text. The directory name is auto-derived (lowercased, spaces become dashes).
2. **Build type** — `app`, `agent`, `tool`, or `other`.
3. **Expected stack** — free text, e.g. `python / fastapi` or `not specified`.
4. **Primary builder model** — `claude`, `codex`, `local`, or `hybrid`. Recorded in `project-control.yaml` and `INITIAL_SCOPE.md`.
5. **Governance level** — choose `0` through `4`, where `0` is full autonomy and `4` is critical controls.
6. **Capture scope brief?** — if `yes`, you answer three more questions (problem, primary user, MVP) and the answers are written into `INITIAL_SCOPE.md`.

Before creating anything, the launcher shows you a confirmation summary. Type `no` to abort with no changes made.

### Desktop GUI

Windows PowerShell:

```powershell
.\automation\launch_gui.ps1
```

Linux/macOS:

```bash
python3 automation/new_build_gui.py
```

Same questions as the terminal version, with a live path preview beneath the project name field. The output panel streams bootstrap progress in real time.

For a desktop menu entry or `.desktop` launcher, use `automation/launch_gui.sh` instead of
calling the Python file directly. The wrapper preserves `PATH`, sets `GOVERNANCE_HOME`, and
handles repo paths that contain spaces more reliably.

### Installed version

The installed version comes from the repository `VERSION` file.

Linux/macOS:

```bash
bash automation/new_build.sh --version
python3 automation/version.py --plain
```

Windows PowerShell:

```powershell
.\automation\new_build.ps1 -Version
py -3 automation\version.py --plain
```

The GUI also shows the installed version in the header.

### Update check

The update check is read-only. It compares the local `VERSION` file against the latest semantic version available from GitHub releases or tags and reports one of:

- `current` — the local version matches the latest published semantic version.
- `behind` — a newer published version exists.
- `ahead` — the local checkout is newer than the latest published semantic version.
- `unable_to_check` — GitHub could not be reached, or no semantic version release/tag exists yet.

Linux/macOS:

```bash
python3 automation/update_check.py
bash automation/new_build.sh --check-updates
python3 automation/new_build_headless.py --check-updates
```

Windows PowerShell:

```powershell
.\automation\new_build.ps1 -CheckUpdates
py -3 automation\update_check.py
```

This command does not pull, merge, reset, checkout, write files, or update the repository.

### Self-update

The self-update command is guarded. It fetches the current branch's upstream remote, then updates only when Git can fast-forward cleanly.

It refuses to update when:

- the working tree has modified, staged, or untracked files
- the checkout is detached
- the current branch has no upstream tracking branch
- the local branch is ahead of its upstream
- the local branch has diverged from its upstream
- Git cannot fetch the upstream remote

Linux/macOS:

```bash
python3 automation/self_update.py --dry-run
python3 automation/self_update.py
bash automation/new_build.sh --self-update
```

Windows PowerShell:

```powershell
py -3 automation\self_update.py --dry-run
.\automation\new_build.ps1 -SelfUpdate
```

The update path uses `git fetch --prune --tags <remote>` followed by `git merge --ff-only <upstream>`. It does not reset, stash, rebase, force-pull, change branches, or overwrite local work.

### GUI update controls

The desktop GUI includes an Agent Updates control in the Governance & Release workflow.

- `Check` runs the version check and a self-update dry run.
- `Update` remains disabled unless the dry run reports `would_update`.
- If the repo is dirty, detached, missing an upstream, ahead, diverged, or already current, the GUI shows the status but does not offer the update action.
- After a successful GUI update, restart the GUI so the running app loads the updated code.

---

## What gets created

Every project receives:

| File | Purpose |
|------|---------|
| `README.md` | Project description (from template — fill in) |
| `START_HERE.md` | First file for agents; current plan and handoff pointer |
| `CLAUDE.md` | One line, `@AGENTS.md`; Claude Code imports the canonical file |
| `AGENTS.md` | Canonical instructions for Claude Code, Codex, and other coding agents (under 80 lines) |
| `AI_BOOTSTRAP.md` | Project commands only — fill in the Commands section |
| `INITIAL_SCOPE.md` | Timestamped intake answers, classification, and first-session checklist |
| `project-control.yaml` | Governance level, risk tier, owner, project type, and required controls |
| `docs/architecture.md` | Architecture overview |
| `docs/context-map.md` | Compact routing map for task-specific agent context loads |
| `docs/current-build-pathway.md` | Live build path, chunk plan, timestamp rule, and validation log |
| `docs/domain-language.md` | Shared vocabulary for domain terms used consistently across code, docs, tests, UI, prompts, and runbooks |
| `docs/policy/durable-development-engineering-policy.md` | Durable engineering policy for code health, testing, security, review, release, and AI-assisted development |
| `docs/standards/README.md` | Standards map for coding and release sessions; points agents to required and supporting engineering standards |
| `docs/standards/engineering-governance-by-use-case.md` | Use-case controls guide; informs work without overriding selected risk tier or governance level |
| `docs/standards/ship-ready-engineering-standard.md` | Ship-readiness gate that separates Definition of Ready, Definition of Done, and Definition of Shipped with evidence expectations |
| `docs/standards/context-hygiene-standard.md` | Lean startup, context tiers, budget classes, scoped reads, compaction, and handoff guidance |
| `docs/standards/code-complexity-control-standard.md` | Plain-language cyclomatic-complexity review bands, test companion, anti-gaming guidance, rollout stages, and exception evidence |
| `docs/standards/governance-source-alignment-standard.md` | Bounded periodic comparison with this governance source, using review-before-apply safeguards that preserve local decisions |
| `docs/risks/risk-register.md` | Risk log |
| `docs/CHANGELOG.md` | Change history |
| `docs/adr-template.md` | Template for Architecture Decision Records |
| `docs/exception-record-template.md` | Template for documenting governance exceptions |
| `scripts/governance-preflight.sh` | Local validation script |

For `app`, `tool`, and `other` projects (anything deployable):

| File | Purpose |
|------|---------|
| `docs/deployment-guide.md` | Deployment steps and rollback procedure |
| `docs/runbook.md` | Operational runbook |

For `agent` projects, also:

| File | Purpose |
|------|---------|
| `docs/agent-inventory.md` | What the agent does and its boundaries |
| `docs/model-registry.md` | Models in use, versions, purposes |
| `docs/prompt-register.md` | Prompts used, their inputs/outputs, owners |
| `docs/tool-permission-matrix.md` | Tools the agent can call and under what conditions |

---

## First steps after creation

Open `INITIAL_SCOPE.md`. It has a checklist:

- [ ] Read `START_HERE.md`
- [ ] Use `docs/context-map.md` to route task-specific docs and source reads
- [ ] Review `docs/current-build-pathway.md`
- [ ] Review `docs/standards/README.md`
- [ ] Review `docs/standards/engineering-governance-by-use-case.md`
- [ ] Review `docs/policy/durable-development-engineering-policy.md`
- [ ] Review `docs/standards/ship-ready-engineering-standard.md`
- [ ] Review `docs/domain-language.md` and add project-specific terms as they become important
- [ ] Fill in the `## Commands` section of `AI_BOOTSTRAP.md` (install, dev, lint, build, test commands)
- [ ] Confirm the governance level in `project-control.yaml` — the default is `2`
- [ ] Add a first ADR if you made architecture decisions during intake
- [ ] Run `bash scripts/governance-preflight.sh` before material or risk-triggering work

The `AI_BOOTSTRAP.md` Commands section is the most important thing to fill in before your first AI session. Without it, the AI has to guess how to build, test, and run the project.

Keep active work in `docs/current-build-pathway.md` as small, timestamped chunks with a budget class and validation evidence. That gives the next agent a narrow resume point instead of forcing a full repo reread.

## Complexity and governance-alignment controls

Generated projects start with cyclomatic complexity in advisory mode for changed code. The number is a smoke alarm, not a verdict:

- **1–10:** ordinary review.
- **11–20:** discuss whether the function has too many responsibilities, deep nesting, difficult state transitions, or untested branches.
- **21+:** make a coherent refactor or record why the branch-heavy design is clearer, who accepted it, and which focused tests control the risk.

Do not split a function into shallow pass-through wrappers merely to lower its score. Generated parsers, protocol handlers, state machines, and other inherently branch-heavy code can be reasonable exceptions when their structure and tests make the behavior clear. See `docs/standards/code-complexity-control-standard.md` in the generated project for the full control.

Generated projects also record a governance-source alignment cadence in `project-control.yaml`. At material planning or release-readiness work, an agent checks the last review date and prompts for a bounded comparison when the date is absent or more than 90 days old. The comparison is not part of ordinary startup, applies only relevant changes after review, and must not overwrite the project's selected risk tier, governance level, exceptions, or owner decisions. Record the source revision, review date, outcome, and next review point after each comparison.

---

## Adding governance to an existing project

Existing-project upgrades must be treated as a safety review first and a compliance update second. The goal is to bring the repo up to current governance standards without jeopardizing product code, user-authored docs, selected risk level, secrets, or release state.

Run `bootstrap_project.sh` directly against any existing directory:

```bash
bash automation/bootstrap_project.sh /path/to/existing-project application 2
```

On Windows, use the Python scaffolder directly:

```powershell
py -3 automation\scaffold_project.py C:\path\to\existing-project application 2
```

It uses a **copy-if-missing** pattern — it will never overwrite files that already exist. Run it safely on a project that already has a `README.md` or `project-control.yaml`; only the missing files will be added.

For a reviewable upgrade path, generate a manifest first:

```bash
python3 automation/change_control.py propose --project /path/to/existing-project
```

Apply the manifest only after reviewing it:

```bash
python3 automation/change_control.py apply --manifest /path/to/manifest.json
```

This is the safest way to fold new governance baseline files, such as `START_HERE.md`, `docs/current-build-pathway.md`, `docs/policy/durable-development-engineering-policy.md`, `docs/standards/README.md`, `docs/standards/ship-ready-engineering-standard.md`, `docs/standards/code-complexity-control-standard.md`, and `docs/standards/governance-source-alignment-standard.md`, into existing builds.

The manifest flow also brings existing agent instruction files forward without rewriting them. If `AGENTS.md`, `AI_BOOTSTRAP.md`, or `CLAUDE.md` already exists but does not point agents at the current pathway, durable engineering policy, use-case governance, complexity controls, periodic source alignment, or fundamentals-first AI coding guidance, the manifest proposes append-only managed blocks. Each block is wrapped in `GOVERNANCE-MANAGED-START` / `GOVERNANCE-MANAGED-END` comments so the change is obvious and reversible.

### Existing-repo safety verification

Before applying a governance upgrade to an existing repo:

1. Confirm the repo is on a branch or has a clean rollback point with `git status --short`.
2. Generate a manifest with `python3 automation/change_control.py propose --project /path/to/existing-project`.
3. Review every manifest action and verify it only creates missing governance files or appends marked managed instruction blocks.
4. Verify the manifest does not overwrite product files, remove user content, change secrets, install dependencies, push to git, or alter external services.
5. Verify the manifest does not change the existing `risk_tier` or `governance_level` unless the user explicitly requested that change.

After applying the manifest:

```bash
bash automation/governance_check.sh /path/to/existing-project
python3 automation/change_control.py propose --project /path/to/existing-project
git -C /path/to/existing-project status --short
```

The second proposal should show no repeated governance actions. The git status review should show only the expected governance files and managed instruction block changes. If anything else changed, stop and review before continuing.

Project types: `application` `website` `service` `internal-tool` `automation` `infrastructure` `documentation` `agent`

Governance levels: `0` full autonomy, `1` light guardrails, `2` standard supervised,
`3` strict review, `4` critical controls. The levels are defined in
`docs/standards/governance-level-standard.md`. `risk_tier` (`low`, `medium`,
`high`, or `critical`) is set independently; when only one of the two values is
supplied, the tooling fills in the recommended default for the other.

---

## Optional: asking an agent to commit and push

This section is owner coaching, not a required governance control.

Keep it if you want practical prompts for asking Codex, Claude Code, or another coding agent to publish work to GitHub. Remove or ignore it if you want the shared project docs to stay strictly product-facing.

To opt out during an agent session, say:

```text
Do not add personal coaching tips. Keep GitHub guidance limited to project operations.
```

When asking an agent to publish work to GitHub, be explicit about the GitHub path you want.

Default safe request:

```text
Commit these changes, push a branch, and open or update a draft PR.
```

Use this for normal feature work, standards changes, release prep, dependency changes, workflow changes, or anything that benefits from review and CI before landing on `main`.

Direct-main request:

```text
Commit these changes and push main directly.
```

Use this only when you intentionally want the agent to bypass the normal PR path. Direct `main` pushes can be appropriate for owner-approved local governance updates, urgent fixes, or solo-maintainer work, but the agent should still:

1. Check `git status --short --branch`.
2. Confirm the changed files match the requested scope.
3. Run the relevant validation commands.
4. Commit with a clear message.
5. Push the branch the owner explicitly named.
6. Report the commit hash, branch, validation, and any GitHub rule bypass notice.

Useful optional GitHub requests:

- "Summarize the open PRs and tell me what needs attention."
- "Create GitHub issues for the remaining cleanup items."
- "Turn this idea into a scoped issue with acceptance criteria."
- "Check the failing GitHub Actions run and explain the root cause."
- "Address the actionable review comments on this PR."
- "Update the PR title and body so GitHub reflects what changed."
- "Prepare a release draft with validation notes and rollback guidance."

If the working tree contains unrelated changes, the agent should not stage everything silently. It should identify the mixed scope and ask what belongs in the commit.

---

## Validating a project

### Quick check (file presence only)

```bash
bash automation/check_required_files.sh /path/to/project
```

Reports which required files are present or missing.

### Full governance check

```bash
bash automation/governance_check.sh /path/to/project
```

Checks required files, validates `project-control.yaml` fields, and reports categorized compliance findings:

| Category | Meaning | Blocks? |
|---|---|---|
| `Required gaps` | Missing files or invalid control fields required by the selected governance level and project policy | Yes |
| `Recommended improvements` | Useful controls suggested by use case, setup needs, or software fundamentals | No |
| `Design quality warnings` | Signals such as vague names, shallow structure, or missing feedback loops that deserve review | No |
| `Owner decisions needed` | Governance mismatch warnings or risk decisions that need owner confirmation | No by default |
| `Accepted exceptions` | Known accepted gaps recorded in `project-control.yaml` or exception records | No by default |

The selected `risk_tier` and `governance_level` remain unchanged unless the owner explicitly approves a change.

For machine-readable output:

```bash
python3 automation/compliance_report.py /path/to/project --json
```

### Fundamentals-first governance

Generated projects include fundamentals-first AI coding guidance in `AGENTS.md`, the single canonical instruction file. `CLAUDE.md` imports it and `AI_BOOTSTRAP.md` holds commands only, so the guidance is loaded once per session.

The guidance tells AI and human builders to:

- reach shared understanding before meaningful coding
- use consistent domain language
- prefer deep modules with simple interfaces over shallow pass-through layers
- let feedback loops set the pace
- design interfaces deliberately
- flag weak design and propose the smallest safe improvement

This guidance scales by risk. Low-risk prototypes may stay lightweight, while high-risk systems, AI agents, automations, private-data systems, money-related work, destructive tools, and deployment workflows receive stronger controls and clearer owner-decision prompts.

### Repository validation on Windows

```powershell
.\scripts\validate.ps1
```

This runs the Windows-friendly validation path: required file checks, project-control schema validation, Python compile checks, PowerShell syntax checks, optional shell syntax checks when Bash is available, unit tests, and Windows launcher smoke tests.

### Per-project preflight

Each scaffolded project includes its own preflight script:

```bash
bash /path/to/project/scripts/governance-preflight.sh
```

Run this before significant or risk-triggering changes, release readiness checks,
or as a pre-commit hook. New scaffolds also
include `scripts/governance-check.sh`, so the preflight works without relying on
`GOVERNANCE_HOME`.

---

## Understanding project-control.yaml

This file is the single source of truth for a project's governance classification. Key fields:

```yaml
project_name: my-app
project_type: application     # application | website | service | internal-tool |
                              # automation | infrastructure | documentation | agent
risk_tier: medium             # low | medium | high | critical
governance_level: 2           # 0 full autonomy ... 4 critical controls

owner:
  name: Your Name

technical_lead:
  name: claude session        # or codex, local, hybrid

agent_controls:
  applicable: false           # set to true for agent projects
  autonomy_level: A0          # A0 = human-in-the-loop, A1 = supervised, A2 = autonomous

quality_controls:
  cyclomatic_complexity:
    mode: advisory
    review_above: 10
    refactor_or_exception_above: 20
    scope: changed-code

governance_alignment:
  source: New Build Governance Agent
  mode: review-before-apply
  review_cadence_days: 90
  last_reviewed: ""           # fill after the first comparison
```

Change `governance_level` if the project evolves. A prototype that becomes a production system should usually move toward `3` or `4`, and `risk_tier` should usually be reclassified upward at the same time. The two fields are set independently; justify any deliberate mismatch in `project-control.yaml` notes. See `docs/standards/governance-level-standard.md` for the level definitions and the level-to-tier crosswalk.

---

## Recording an exception

When you knowingly deviate from the framework — skipping a document, using a non-standard structure, deferring a security control — record it instead of silently ignoring it.

Copy `docs/exception-record-template.md`, fill it in, and save it as `docs/exceptions/YYYY-MM-DD-short-title.md`.

An exception record needs:
- What was deviated from
- Why the deviation is justified
- Who approved it
- When it will be resolved (or that it's permanent)

---

## Customising templates

Templates live in `templates/project/`. Edit them to match your organisation's defaults before bootstrapping new projects.

Common customisations:

- **`AI_BOOTSTRAP.template.md`** — add default commands for your typical stack
- **`CLAUDE.template.md`** — add project-wide rules you always want Claude to follow
- **`project-control.template.yaml`** — change the default owner name, governance level, autonomy level, or risk tier
- **`docs/architecture.template.md`** — add sections specific to your architecture patterns
- **`docs/domain-language.template.md`** — add default vocabulary entries for your organisation or product family

Changes to templates only affect new projects. Existing projects are unaffected.

---

## Governance Levels

| Level | Meaning | Default risk tier |
|-------|---------|-------------------|
| `0` | Full autonomy | `low` |
| `1` | Light guardrails | `low` |
| `2` | Standard supervised | `medium` |
| `3` | Strict review | `high` |
| `4` | Critical controls | `critical` |

The framework stores both `governance_level` and `risk_tier`, and the two are set independently. The 0-4 level is the primary selection; the tier column above is the recommended default pairing, applied automatically when only one value is supplied. The full level definitions, required controls, and the crosswalk to agent-action tiers live in `docs/standards/governance-level-standard.md`.

---

## Working with AI assistants

### Claude

`CLAUDE.md` is automatically read at the start of every Claude Code session in the project directory. It contains one line, `@AGENTS.md`, which imports the canonical rule file. Do not add a `.claude/CLAUDE.md`; Claude Code would load both.

`AGENTS.md` is where the rules live: what the project is, how a session starts, the owner-authorization boundaries, the governed read-only paths, the commit format, and how a chunk is finished. Keep it under 80 lines.

`AI_BOOTSTRAP.md` is where you put the actual commands to install, run, lint, test, and build the project, one per line. The compliance report reads the `- Lint:`, `- Test:`, and `- Build:` lines.

### Other assistants (Codex, Cursor, etc.)

Codex reads `AGENTS.md` natively, and so do most other coding agents. Point any assistant that does not at `AGENTS.md` at the start of each session. The same file serves every tool, so there is nothing to keep in sync.

Generated instruction files also include fundamentals-first AI coding guidance. The important behavior is simple: before meaningful coding, reach shared understanding, use consistent domain language, work in small validated slices, and flag weak design with the smallest safe improvement instead of broad rewrites.

---

## Governance maturity path

The framework is designed to grow in layers:

| Layer | Description |
|-------|-------------|
| 1. Templates | ✅ Done — all projects start with a consistent structure |
| 2. Local validation | ✅ Done — `governance_check.sh` and `governance-preflight.sh` |
| 3. CI enforcement | Add `governance_check.sh` as a CI step |
| 4. Schema validation | Validate `project-control.yaml` against a schema |
| 5. Metrics and drift | Track which projects are missing controls over time |
| 6. Governing agent | AI-assisted compliance scoring and exception expiry reminders |

Start at layer 1 and add layers as the team grows or risk increases.
