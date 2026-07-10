# New Build Governance Agent Repository Audit

Date: 2026-05-19
Status: retired
Owner: Project Owner
Scope: `New Build Governance Agent` repository only
Auditor context: repository access, limited product context, no secret values inspected or reported

## Executive Summary

New Build Governance Agent is a useful and coherent local governance tool. Its strongest pattern is the staged approach: scaffold locally, record governance metadata, generate reviewable plans, run checks, then execute only selected external actions. The repo has a clear product direction and several sensible safety choices, especially around not overwriting existing governance files and not printing secret values from the new environment tooling.

The main risk is that the architecture has started to outgrow its surfaces. The desktop GUI and Freedom/headless manifest still describe a project-scaffolding agent, while the codebase now includes master-env sync and Stripe provisioning. Those newer control-plane capabilities are currently CLI-first and plan-text-first, not governed through the desktop/headless entry points the product is meant to use.

The second major risk is execution breadth. A few flows still run broad command strings or stage every local change. That is tolerable for a personal prototype, but not for an agent-governed build tool holding control-plane credentials. These are fixable with smaller hardening passes; no rewrite is justified.

## Repo Map

### Languages And Frameworks

- Python 3 standard library automation, including `argparse`, `sqlite3`, `subprocess`, `tkinter`, `urllib`, and JSON file workflows.
- Bash shell scripts for launch, scaffolding, and governance checks.
- Markdown/YAML governance documentation and templates.
- No package manager manifest was found in this repo: no `pyproject.toml`, `requirements.txt`, or `package.json`.

### Entry Points

- Desktop launch: `automation/launch_gui.sh` finds a Python with Tkinter, sets `GOVERNANCE_HOME`, fixes `PATH`, and execs `automation/new_build_gui.py` (`automation/launch_gui.sh:5-58`).
- GUI app: `automation/new_build_gui.py` is the main desktop experience. It is currently 1,887 lines and handles project discovery, UI state, subprocess orchestration, and report display.
- Terminal project creation: `automation/new_build.sh`.
- Headless/Freedom tool invocation: `freedom.tool.yaml` calls `automation/new_build_headless.py` through stdin JSON (`freedom.tool.yaml:30-41`).
- Scaffolding engine: `automation/bootstrap_project.sh` copies templates and updates `project-control.yaml` (`automation/bootstrap_project.sh:67-143`).
- Registry: `automation/project_registry.py` stores projects and audit records in SQLite (`automation/project_registry.py:14-23`, `automation/project_registry.py:26-60`).
- Promotion planning/checks/execution: `automation/promotion_plan.py`, `automation/promotion_checks.py`, and `automation/promotion_execute.py`.
- New environment/provider tooling: `automation/master_env.py`, `automation/env_sync.py`, and `automation/stripe_provision.py`.

### Major Modules

- `automation/new_build_gui.py`: desktop app and orchestration surface.
- `automation/new_build_headless.py`: headless project creation wrapper for the Freedom dispatcher.
- `automation/bootstrap_project.sh`: template copy and baseline governance scaffold.
- `automation/change_control.py`: creates and applies missing-governance-file manifests without overwriting existing files.
- `automation/audit_projects.py`: scans `~/code/agents` and `~/code/Applications`, runs governance checks, records results.
- `automation/promotion_plan.py`: detects local project signals and creates staged external rollout plans.
- `automation/promotion_checks.py`: runs pre/post checks from promotion plans.
- `automation/promotion_execute.py`: executes GitHub commit/push/PR flow from an approved plan.
- `automation/master_env.py`: redacted status/set/merge helper for `~/code/.env.master`.
- `automation/env_sync.py`: redacted env sync planner and applier from master env into project env.
- `automation/stripe_provision.py`: manifest-driven Stripe product/price/webhook planner and applier.

### Data Flow

1. User or another agent invokes GUI, terminal script, or Freedom tool.
2. Project metadata is collected and mapped to a governance type/risk tier.
3. `bootstrap_project.sh` creates a governed project directory from `templates/project`.
4. `new_build_headless.py` and GUI flows register created projects in `data/new-build-governance-agent/registry.sqlite3`.
5. Existing projects can be audited by `audit_projects.py`, with results recorded in the same SQLite registry.
6. Promotion plans are generated as JSON under `data/new-build-governance-agent/exports/`.
7. Promotion checks read those plans and write check-report JSON under exports.
8. GitHub execution reads a plan, stages changes, commits, pushes, and optionally opens a draft PR.
9. New provider/env tooling reads `~/code/.env.master`, writes redacted plans, and can write generated values back to the master env or project env files.

### Tests And Verification

Facts:

- No `tests/` directory or `def test_` style test suite was found.
- Existing verification is mostly smoke-level:
  - `python3 -m py_compile automation/*.py` passes.
  - `bash automation/governance_check.sh .` passes with 0 warnings.
  - `promotion_plan.py` can emit check commands based on project signals (`automation/promotion_plan.py:59-159`).
- `project-control.yaml` declares `lint`, `tests`, and `secret-scan` controls (`project-control.yaml:31-35`), but this repo does not currently provide a test suite or secret-scan runner.

Judgment:

- For a local prototype, compile checks and governance checks are a reasonable starting point.
- For a tool intended to drive provider accounts and agent automation, the absence of unit/integration tests is now a material risk.

### Docs

The repo has a large governance-doc surface. Some docs are useful operating references, especially `README.md`, `automation/README.md`, and `docs/processes/staged-promotion-workflow.md`. Other first-class docs are still placeholder-thin: several are only 6 to 23 lines, including `docs/CHANGELOG.md`, `docs/agent-inventory.md`, `docs/model-registry.md`, `docs/prompt-register.md`, `docs/tool-permission-matrix.md`, `docs/manual.md`, `docs/architecture.md`, and `docs/runbook.md`.

### Build And Deployment Assumptions

- The app assumes Linux-style local paths and Adam's workspace roots: `~/code/agents`, `~/code/Applications`, and `~/code/.env.master`.
- Desktop launch assumes a Tkinter-capable Python is installed (`automation/launch_gui.sh:12-56`).
- Freedom integration previously assumed a specific absolute repository path for invoking `automation/new_build_headless.py` (`freedom.tool.yaml:30-35`).
- Provider setup currently assumes local control-plane credentials live in a private master env file and are not printed.

## Positive Findings

- The staged promotion model is clear and conservative: local compliance, pre-checks, external sync planning, approval, post-checks, rollback readiness (`automation/promotion_plan.py:310-363`).
- Generated external target plans default to no automatic external execution (`automation/promotion_plan.py:304-308`).
- Scaffolding and change-control flows avoid overwriting existing files by default (`automation/bootstrap_project.sh:74-84`, `automation/change_control.py:166-177`).
- `env_sync.py` avoids printing values in plans, does not overwrite project env values by default, gates privileged keys, and writes env files with `600` permissions (`automation/env_sync.py:222-227`, `automation/env_sync.py:271-308`).
- `master_env.py` prompts secret values without echo by default and writes the master env with `600` permissions (`automation/master_env.py:173-177`, `automation/master_env.py:112-115`).
- `stripe_provision.py` has a useful test-mode-first shape and refuses live apply unless `--allow-live` is provided (`automation/stripe_provision.py:251-256`, `automation/stripe_provision.py:456-459`).
- The desktop launcher is practical: it handles thin desktop environments, paths with spaces, `PATH`, and Tkinter detection (`automation/launch_gui.sh:5-58`).

## Prioritized Findings

### 1. New Control-Plane Tools Are Not Yet Governed Through The Desktop Or Headless Surfaces

Severity: High
Type: product/architecture gap

Facts:

- The GUI constants wire promotion plan/check/remediate/execute scripts, but not `master_env.py`, `env_sync.py`, or `stripe_provision.py` (`automation/new_build_gui.py:24-27`).
- The GUI can generate a promotion plan and run checks (`automation/new_build_gui.py:1640-1718`), but provider/env tools are only included as command strings inside plan JSON (`automation/promotion_plan.py:322-334`).
- The Freedom tool still describes scaffolding only and explicitly says it does not modify Supabase (`freedom.tool.yaml:123-126`).
- The automation docs explain env sync and Stripe provisioning mostly through terminal examples (`automation/README.md:165-207`).

Judgment:

This conflicts with the intended operating model: New Build Governance Agent should be the governance surface that other agents or desktop actions use, not a set of commands the user must run manually.

Recommendation:

- Add a desktop/headless "External Setup" or "Provider Setup" flow that exposes read-only status, plan generation, and gated apply operations for env sync and Stripe.
- Update `freedom.tool.yaml` to declare the real side effects and parameters once those actions are supported.

Expected benefit:

- Makes the agent match the user's workflow: launch from desktop or agent, review, approve, and execute without terminal copy/paste.

Effort:

- Medium. The backend scripts exist; the work is mostly orchestration, UI state, reports, and policy gates.

Risk of not fixing:

- High. Users and other agents will believe the system governs provider automation, while the actual path remains manual and easy to bypass.

Suggested first step:

- Add GUI buttons for `Master Env Status`, `Env Sync Plan`, `Stripe Manifest Init`, and `Stripe Plan`. Keep apply disabled or confirmation-gated until the report review path is polished.

### 2. Promotion Checks Execute Plan Commands With `shell=True`

Severity: High
Type: security/robustness

Facts:

- `promotion_checks.py` reads command strings from a JSON plan and runs them with `shell=True` (`automation/promotion_checks.py:105-138`).
- Current generated commands are simple internal strings such as `bash scripts/governance-preflight.sh`, `npm run lint`, and `python3 -m pytest -q` (`automation/promotion_plan.py:63-139`).
- The plan JSON is a file input, so it can be edited or generated by another process before checks run.

Judgment:

The current plan generator is benign, but the runner trusts the plan too much. For an agent-controlled workflow, command strings plus `shell=True` create an unnecessary command-injection and accidental-execution surface.

Recommendation:

- Represent checks as argv arrays instead of shell strings, or map known check names to a small whitelist of runner functions.
- Reject unknown commands unless a human explicitly approves manual mode.

Expected benefit:

- Removes a major injection class and makes check behavior auditable.

Effort:

- Medium. Requires changing plan shape or adding a compatibility parser.

Risk of not fixing:

- High if plans can be influenced by another agent, stale export, or user edit.

Suggested first step:

- Add `argv` beside existing `command` in `promotion_plan.py`, prefer `argv` in `promotion_checks.py`, and fall back to old `command` only for known safe strings.

### 3. GitHub Execution Stages All Local Changes

Severity: High
Type: security/release safety

Facts:

- `promotion_execute.py` records changed files from `git status --porcelain` (`automation/promotion_execute.py:91-95`).
- It then runs `git add -A` (`automation/promotion_execute.py:117-118`).
- It supports only the `github` target today (`automation/promotion_execute.py:206-220`).

Judgment:

This is too broad for an automation tool. If a target repo has unrelated local edits, generated files, or poorly ignored env files, the tool will stage them all. The result is especially risky when combined with provider credentials and project env work.

Recommendation:

- Add a pre-commit guard that blocks secret-looking paths and files, even if the target repo's `.gitignore` is wrong.
- Require a reviewed changed-file list before staging.
- Prefer staging the explicit file set captured by the plan or by a fresh status review, not `git add -A`.

Expected benefit:

- Prevents accidental commits of secrets, local state, and unrelated work.

Effort:

- Low to medium.

Risk of not fixing:

- High. A single bad publish could leak credentials or bundle unrelated project changes into a promotion commit.

Suggested first step:

- Block `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `secrets.*`, and known local state paths before `git add`, then switch staging to an explicit list.

### 4. Stripe Provisioning Needs Stronger Validation Before Live Use

Severity: Medium-high
Type: provider integration risk

Facts:

- `load_manifest()` only validates that the manifest is a JSON object (`automation/stripe_provision.py:101-108`).
- The default manifest uses `https://example.com/api/stripe/webhook` as a placeholder webhook URL (`automation/stripe_provision.py:135-139`).
- Prices assume required fields such as `unit_amount` are present (`automation/stripe_provision.py:336-358`).
- Product search interpolates manifest values directly into a Stripe search query (`automation/stripe_provision.py:302-304`).
- Stripe HTTP errors include the raw response body in the raised exception (`automation/stripe_provision.py:198-200`).
- Existing webhook secrets are not retrievable, which the code records as a note (`automation/stripe_provision.py:421-424`).

Judgment:

The script has the right shape for governed provisioning, but it should be stricter before it is trusted for repeated project setup. Misconfigured billing resources are hard to unwind cleanly, especially in live mode.

Recommendation:

- Add manifest schema validation for mode, products, prices, currency, amount, lookup keys, env names, webhook URL, and event names.
- Refuse apply when the webhook URL is still `example.com`.
- Escape or constrain values used in Stripe search queries.
- Sanitize Stripe error bodies before writing reports or GUI output.

Expected benefit:

- Reduces duplicate products/prices, bad live endpoints, and accidental exposure of provider error details.

Effort:

- Medium.

Risk of not fixing:

- Medium-high. Test-mode mistakes are tolerable; live-mode mistakes can create confusing billing state or broken checkout/webhook flows.

Suggested first step:

- Add a `validate_manifest()` function called by both `plan` and `apply`, and make `apply` fail closed on placeholder URLs or missing required fields.

### 5. Environment File Parsing/Writing Is Duplicated

Severity: Medium
Type: maintainability/secret-handling correctness

Facts:

- `parse_env_value`, `parse_env_file`, and `format_env_value` exist independently in `master_env.py`, `env_sync.py`, and `stripe_provision.py` (`automation/master_env.py:67-99`, `automation/env_sync.py:93-125`, `automation/stripe_provision.py:34-67`).
- `master_env.py` and `stripe_provision.py` also each have their own update/write logic (`automation/master_env.py:118-148`, `automation/stripe_provision.py:69-98`).

Judgment:

This duplication is understandable while prototyping, but env-file behavior is now security-sensitive. Divergence around quoting, comments, multiline values, or private keys could corrupt secrets or produce hard-to-debug project envs.

Recommendation:

- Factor shared env parsing, formatting, and update behavior into a small internal module such as `automation/lib/envfile.py`.
- Add tests around comments, quotes, spaces, empty values, and private-key-shaped values.

Expected benefit:

- One behavior for all secret file operations, with tests.

Effort:

- Low to medium.

Risk of not fixing:

- Medium. The risk is subtle corruption or inconsistent behavior, not immediate breakage.

Suggested first step:

- Extract the current best implementation from `env_sync.py`, import it from the other scripts, and add pytest cases using temporary files.

### 6. No Automated Test Suite For The Agent Itself

Severity: Medium
Type: quality/release confidence

Facts:

- No `tests/` directory was found.
- `project-control.yaml` says tests and secret-scan are required controls (`project-control.yaml:31-35`).
- `python3 -m py_compile automation/*.py` passes, and governance check passes, but those do not exercise behavior deeply.

Judgment:

The codebase now has enough side-effecting behavior that compile checks are not enough. Most high-value tests can be local and cheap.

Recommendation:

- Add a small pytest suite around pure functions and tmpdir-based workflows:
  - env parse/format/update
  - promotion target detection
  - manifest generation/apply create-if-missing behavior
  - Stripe manifest validation once added
  - `promotion_checks.py` command gating once hardened

Expected benefit:

- Safer refactors and faster confidence before adding more provider automation.

Effort:

- Medium.

Risk of not fixing:

- Medium. Bugs will surface during real desktop/provider workflows instead of in local verification.

Suggested first step:

- Add `pyproject.toml` or a tiny `requirements-dev.txt` with pytest, then write tests for env-file behavior and promotion-plan generation.

### 7. The GUI Is A Monolith And Is Already Drifting From Backend Capability

Severity: Medium
Type: maintainability/product drift

Facts:

- `automation/new_build_gui.py` is 1,887 lines.
- It owns UI construction, project discovery, state, subprocess calls, report parsing, and output formatting.
- New scripts for master env, env sync, and Stripe are not wired into the GUI constants or workflows (`automation/new_build_gui.py:24-27`, `automation/new_build_gui.py:1640-1843`).

Judgment:

The size itself is not the bug. The drift is the bug. New backend capabilities can land without becoming part of the primary user experience.

Recommendation:

- Extract command wrappers and report models from the GUI incrementally.
- Add new tabs/panels by calling those wrappers instead of embedding more subprocess logic directly in the view code.

Expected benefit:

- Lower risk of adding provider flows and easier testing of orchestration outside Tkinter.

Effort:

- Medium, done incrementally.

Risk of not fixing:

- Medium. Every new capability increases GUI complexity and makes desktop behavior harder to trust.

Suggested first step:

- Create `automation/command_runner.py` for subprocess environment, command execution, and JSON report loading. Move the existing promotion/check execution calls there first.

### 8. Docs Are Useful, But Some First-Class Docs Have Not Earned Their Place Yet

Severity: Medium-low
Type: documentation quality

Facts:

- `README.md` and `automation/README.md` are meaningful and current.
- Several first-class docs are very thin: `docs/CHANGELOG.md`, `docs/agent-inventory.md`, `docs/model-registry.md`, `docs/prompt-register.md`, and `docs/tool-permission-matrix.md` are each 6 lines.
- `README.md` says the GUI can guide external plan generation and GitHub publish (`README.md:72-87`), while provider provisioning is still terminal/planned-command oriented.

Judgment:

Templates are valuable, but placeholder docs can create false confidence in governance completeness.

Recommendation:

- Separate "active operating docs" from "template/stub docs".
- Mark intentionally empty docs as stubs with owners and next-update triggers, or move them back into templates until populated.

Expected benefit:

- Clearer operating picture for humans and agents.

Effort:

- Low.

Risk of not fixing:

- Medium-low. The risk is planning noise and misplaced confidence rather than immediate runtime failure.

Suggested first step:

- Add a docs index that labels each doc as `active`, `template`, or `stub`, then update or demote the 6-line files.

### 9. Local Runtime State Is Correctly Ignored, But Cleanup Should Be Part Of The Maintenance Pass

Severity: Low
Type: repo hygiene

Facts:

- `.gitignore` ignores `__pycache__/`, `*.py[cod]`, `data/new-build-governance-agent/exports/`, `data/new-build-governance-agent/logs/`, and `data/new-build-governance-agent/registry.sqlite3` (`.gitignore:1-27`).
- Ignored `automation/__pycache__/` and `data/` artifacts are present in the working tree.

Judgment:

This is not a code-health problem because the ignore rules are correct. It is still noisy for audits and backups.

Recommendation:

- Keep the ignore rules.
- Optionally clean ignored runtime artifacts when preparing releases or snapshots.

Expected benefit:

- Cleaner local repo operations and less audit noise.

Effort:

- Low.

Risk of not fixing:

- Low.

Suggested first step:

- Add a documented cleanup command or `make clean-local` equivalent if a build tool is introduced.

## What Should Stay

- Keep the staged promotion model. It is the right abstraction for this repo.
- Keep create-if-missing behavior for scaffolding and governance upgrades.
- Keep local SQLite registry for now. It is simple and fits the single-machine workflow.
- Keep `~/code/.env.master` outside the repo as the master secret inventory.
- Keep `600` permissions on generated env files.
- Keep live provider actions gated separately from plan generation.
- Keep the desktop launcher wrapper; it solves real environment problems.

## What Should Change First

1. Wire env/Stripe planning into the GUI as review-only flows.
2. Remove `shell=True` from promotion checks or gate it behind a whitelist.
3. Add secret/path guards before GitHub execution stages files.
4. Add Stripe manifest validation and placeholder URL blocking.
5. Extract shared env-file handling and add tests around it.

## What Deserves Deeper Investigation Before Action

- The exact UX contract between New Build Governance Agent, Freedom, and future agents: which operations are view-only, plan-only, approval-gated apply, or fully automated?
- Provider permission boundaries: whether Stripe, Supabase, Vercel, GitHub, Resend, and Cloudflare should use global tokens, restricted tokens, per-project generated credentials, or a mix.
- Desktop packaging: whether a `.desktop` file exists elsewhere and whether launch logs are enough for support.
- Secret scanning: whether to add a local scanner before any GitHub execute operation or rely on target repos' hooks.
- Registry lifecycle: whether local SQLite is enough or whether multi-agent coordination needs a lock/audit-log layer.

## Verification Performed During Audit

- `python3 -m py_compile automation/*.py`: passed.
- `bash automation/governance_check.sh .`: passed with 0 warnings.
- Repository file map, script references, docs length, ignored runtime artifacts, and test discovery were inspected with local shell commands.

## Bottom Line

This repo is healthy enough to keep building on. The right next move is not a rewrite; it is a hardening pass around the places where local governance turns into execution: provider setup, env sync, checks, and GitHub publishing. The core idea is sound. The system now needs its primary desktop/headless interfaces to catch up with its new backend power.
