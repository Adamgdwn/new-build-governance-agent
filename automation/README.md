# Automation

Scripts for scaffolding, governance checking, and project intake.

---

## new_build.sh / new_build.ps1 — New Build Governance Agent

Interactive launcher. Asks intake questions, classifies the project,
scaffolds the correct structure, and writes a scope file.

On Windows, the release package includes `NewBuildGovernanceAgent.exe` for non-technical users. The `.exe` launches the desktop GUI from the unpacked package. The repository also includes PowerShell launchers for technical users. They work from either a cloned checkout or a downloaded ZIP copy, but guarded self-update requires a cloned checkout with an upstream branch.

**Run it on Linux/macOS:**
```bash
bash automation/new_build.sh
```

**Run it on Windows PowerShell:**
```powershell
.\automation\new_build.ps1
```

**Open the Windows GUI by double-click:**
```text
NewBuildGovernanceAgent.exe
```

**What it asks:**
- Project name
- Build type: app / agent / tool / other
- Expected stack
- Primary builder model: claude / codex / local / hybrid
- Governance level: 0 / 1 / 2 / 3 / 4
- Whether to capture a scope brief now

**Validate on Windows:**
```powershell
.\scripts\validate.ps1
```

The Windows validator covers required governance files, project-control schema, Python compilation, PowerShell syntax, optional shell syntax when Bash is available, unit tests, and launcher smoke tests.

**What it creates:**
```
~/code/agents/<slug>/          (for agents)
~/code/Applications/<slug>/    (for apps and tools)
  ├── README.md
  ├── START_HERE.md
  ├── CLAUDE.md
  ├── AGENTS.md
  ├── AI_BOOTSTRAP.md
  ├── INITIAL_SCOPE.md         ← timestamped intake answers + first-session checklist
  ├── project-control.yaml
  ├── docs/
  │   ├── adr/
  │   ├── specs/
  │   ├── runbooks/
  │   ├── architecture.md
  │   ├── current-build-pathway.md
  │   ├── domain-language.md
  │   ├── policy/durable-development-engineering-policy.md
  │   ├── standards/README.md
  │   ├── standards/engineering-governance-by-use-case.md
  │   ├── standards/ship-ready-engineering-standard.md
  │   ├── standards/context-hygiene-standard.md
  │   ├── manual.md
  │   ├── roadmap.md
  │   ├── risks/risk-register.md
  │   └── ...
  ├── scripts/governance-check.sh
  ├── scripts/governance-preflight.sh
  └── archive/
```

**Notes:**
- Uses the cross-platform Python scaffolding engine. `bootstrap_project.sh` remains as the Linux/macOS shell entry point.
- Will not overwrite existing files if the directory already exists.
- Agents should use lean startup for ordinary scoped work, then read `START_HERE.md` and follow `docs/current-build-pathway.md` for material work, unclear scope, handoffs, or active-plan changes.
- Use-case classification is written to `project-control.yaml` for control selection guidance, but it does not override the chosen governance level or risk tier.
- Coding sessions should use `docs/standards/README.md` as the standards map before opening task-specific standards.
- Meaningful implementation work should also follow `docs/policy/durable-development-engineering-policy.md`.
- Meaningful finish reports and releases should use `docs/standards/ship-ready-engineering-standard.md` to prove Definition of Shipped with evidence.
- Long agent sessions, handoffs, scoped file reads, compaction, and token budgets should use `docs/standards/context-hygiene-standard.md`.
- Domain terms should be kept consistent in `docs/domain-language.md` across code, docs, tests, UI, prompts, and runbooks.
- Generated agent instructions include fundamentals-first AI coding guidance: shared understanding, consistent domain language, deep modules, feedback loops, deliberate interfaces, and smallest safe improvements.
- Fill in the `## Commands` section of `AI_BOOTSTRAP.md` before the first coding session.

---

## scaffold_project.py / bootstrap_project.sh — Project Scaffolder

Creates a governed project structure from templates.

```bash
bash bootstrap_project.sh /path/to/project <type> [governance-level]
```

```powershell
py -3 automation/scaffold_project.py C:\path\to\project application 2
```

Types: `application` `website` `service` `internal-tool` `automation`
       `infrastructure` `documentation` `agent`

Governance levels: `0` full autonomy, `1` light guardrails, `2` standard supervised,
`3` strict review, `4` critical controls (default: 2). The scaffolder derives
the compatibility `risk_tier` from this selection.

Called automatically by `new_build.sh`, `new_build.ps1`, and the GUI. Can also be run directly to bootstrap
an existing ungoverned project (safe — will not overwrite existing files).

---

## launch_gui.sh / launch_gui.ps1 — Desktop Launcher Wrapper

Desktop-safe wrapper for menu entries, `.desktop` launchers, and Windows PowerShell.

```bash
bash automation/launch_gui.sh
```

```powershell
.\automation\launch_gui.ps1
```

Use this for desktop integration instead of calling `python3 automation/new_build_gui.py`
directly. It preserves a stable `PATH`, sets `GOVERNANCE_HOME`, and avoids failures
caused by repo paths that contain spaces.

---

## build-windows-launcher.ps1 — Windows EXE Package

Builds the double-click Windows launcher and package.

```powershell
.\scripts\build-windows-launcher.ps1
```

Outputs:

```text
dist\windows\NewBuildGovernanceAgent.exe
dist\NewBuildGovernanceAgent-Windows.zip
```

The executable is a small C# launcher built from `windows\NewBuildGovernanceAgentLauncher.cs`. It finds `automation\launch_gui.ps1`, starts it with a process-scoped execution-policy bypass, and shows a Windows error dialog if the full package or Python/Tkinter support is missing.

The package ZIP includes tracked repository files plus `NewBuildGovernanceAgent.exe` at the top level, so non-technical Windows users can unzip and double-click.

---

## governance_check.sh — Governance Validator

Checks a project for required governance files, valid `project-control.yaml` fields, and categorized compliance findings.

```bash
bash governance_check.sh /path/to/project
```

The output separates:

- `Required gaps`: blocking missing files or invalid control fields
- `Recommended improvements`: advisory setup, documentation, or feedback-loop improvements
- `Design quality warnings`: advisory naming or structure signals
- `Owner decisions needed`: governance mismatch or risk confirmations
- `Accepted exceptions`: already recorded exceptions

Only required gaps fail the command. Advisory findings are meant to guide review without automatically changing the selected `risk_tier` or `governance_level`.

Run this after bootstrapping, or from the project's own preflight script:
```bash
bash scripts/governance-preflight.sh
```

New scaffolds also include `scripts/governance-check.sh`, so the local preflight works
without requiring `GOVERNANCE_HOME` to be configured.

For JSON output, call the categorized reporter directly:

```bash
python3 automation/compliance_report.py /path/to/project --json
```

---

## check_required_files.sh — Minimal File Check

Lightweight check for required file presence only. Missing files are reported as required gaps. Subset of `governance_check.sh`.

```bash
bash check_required_files.sh /path/to/project
```

---

## schema_validation.py — Schema Validation

Validates `project-control.yaml` and generated promotion plan JSON without adding
third-party dependencies.

**Examples:**
```bash
python3 automation/schema_validation.py --project /path/to/project
python3 automation/schema_validation.py --promotion-plan data/new-build-governance-agent/exports/promotion-demo-20260408T000000Z.json
```

The repository validation script runs the project-control schema check automatically.
Promotion plans are also validated when generated and before checks execute.

---

## version.py — Installed Version

Reads the repository `VERSION` file and prints the installed New Build Governance Agent version.

**Examples:**
```bash
python3 automation/version.py
python3 automation/version.py --plain
python3 automation/version.py --json
bash automation/new_build.sh --version
python3 automation/new_build_headless.py --version
```

On Windows:

```powershell
.\automation\new_build.ps1 -Version
py -3 automation\version.py --plain
```

Keep `freedom.tool.yaml` `version` aligned with `VERSION`.

---

## update_check.py — Read-Only Update Check

Compares the local `VERSION` file against the latest semantic version available from GitHub releases or tags. It reports `current`, `behind`, `ahead`, or `unable_to_check` and does not modify the working tree.

**Examples:**
```bash
python3 automation/update_check.py
python3 automation/update_check.py --json
bash automation/new_build.sh --check-updates
python3 automation/new_build_headless.py --check-updates
```

On Windows:

```powershell
.\automation\new_build.ps1 -CheckUpdates
py -3 automation\update_check.py
```

This check is intentionally informational.

---

## self_update.py — Guarded Self-Update

Fetches the current branch's upstream remote and updates only when Git can perform a clean fast-forward merge. It refuses dirty worktrees, detached checkouts, missing upstreams, local-ahead branches, and diverged histories.

**Examples:**
```bash
python3 automation/self_update.py --dry-run
python3 automation/self_update.py
bash automation/new_build.sh --self-update
```

On Windows:

```powershell
py -3 automation\self_update.py --dry-run
.\automation\new_build.ps1 -SelfUpdate
```

The updater uses `git fetch --prune --tags <remote>` and `git merge --ff-only <upstream>`. It does not reset, stash, rebase, force-pull, change branches, or overwrite local work.

---

## GUI Update Controls

The desktop GUI shows Agent Updates in the Governance & Release workflow. The Check button runs the version check and a self-update dry run. The Update button is enabled only when the dry run reports that a safe fast-forward is available.

The GUI does not offer self-update when the checkout is dirty, detached, missing an upstream, ahead, diverged, failed, or already up to date.

---

## project_registry.py — Local Project Inventory

Stores a local record of successful project scaffolds and audit results.

**Examples:**
```bash
python3 automation/project_registry.py list
python3 automation/project_registry.py register --project-name demo --slug demo --path ~/code/agents/demo --project-type agent --risk-tier medium --governance-level 2 --builder codex --stack python
```

---

## audit_projects.py — Workspace Governance Audit

Scans `~/code/agents` and `~/code/Applications` for governed projects, runs `governance_check.sh`, and records the audit result in the local registry.

**Run it:**
```bash
python3 automation/audit_projects.py
python3 automation/audit_projects.py --json
```

---

## change_control.py — Structured Upgrade Manifests

Generates and applies reviewable upgrade manifests for governed project drift.
Use this for existing builds when new baseline files or instruction guidance are added. It creates only missing files and appends clearly marked managed instruction blocks when an existing instruction file is missing the current governance contract.

**Examples:**
```bash
python3 automation/change_control.py propose --project ~/code/agents/my-project
python3 automation/change_control.py apply --manifest data/new-build-governance-agent/exports/upgrade-my-project-20260408T000000Z.json
```

**Document-control standard update:**
```bash
python3 automation/change_control.py propose-document-control --project ~/code/agents/my-project
python3 automation/change_control.py apply --manifest data/new-build-governance-agent/exports/document-control-my-project-20260408T000000Z.json
```

The document-control update syncs only `docs/standards/document-control-standard.md`.

**Existing-repo safety rule:**

Before apply, review the manifest and confirm it only creates missing governance files or appends marked managed instruction blocks. It must not overwrite product files, remove user content, change secrets, install dependencies, push to git, alter external services, or change the selected `risk_tier` / `governance_level` unless the user explicitly requested that change.

After apply, verify the upgrade did not jeopardize the repo:

```bash
bash automation/governance_check.sh /path/to/project
python3 automation/change_control.py propose --project /path/to/project
git -C /path/to/project status --short
```

The second proposal should have no repeated actions, and git status should show only expected governance file additions or managed instruction block updates.

**Non-destructive behavior:**
- Existing files are not overwritten.
- Existing instruction files such as `AGENTS.md`, `AI_BOOTSTRAP.md`, and `CLAUDE.md` are only appended to when they are missing the current `START_HERE.md` / `docs/current-build-pathway.md` guidance or durable engineering policy guidance.
- Appended instruction guidance is wrapped in `GOVERNANCE-MANAGED-START` / `GOVERNANCE-MANAGED-END` comments so it is easy to review or remove.

---

## promotion_plan.py — External Sync Planning

Generates a staged promotion plan for GitHub, Vercel, Supabase, Stripe, Resend, and similar targets. Plans include local pre-checks, provider provisioning needs, environment sync guidance, approval-and-execute guidance, post-checks, and rollback readiness notes.

**Example:**
```bash
python3 automation/promotion_plan.py --project ~/code/Applications/frogger
```

---

## env_sync.py — Governed Environment Sync

Creates a redacted plan for copying only the environment variables a project appears
to need from a private local master env file, then applies that plan into the
project's env file when approved.

This is the second half of the automation path. The first half is provider
provisioning: account-level or organization-level credentials in the master env
allow New Build Governance Agent to create or configure resources in systems such as
Supabase, Vercel, Stripe, and Resend. The generated project credentials are then
stored back in the master env and synced into the project that needs them.

**Examples:**
```bash
python3 automation/env_sync.py plan --project ~/code/Applications/frogger --include-code-refs
python3 automation/env_sync.py apply --plan data/new-build-governance-agent/exports/env-sync-frogger-20260408T000000Z.json
python3 automation/env_sync.py apply --plan data/new-build-governance-agent/exports/env-sync-frogger-20260408T000000Z.json --include-privileged
```

**Governance behavior:**
- Defaults to `~/code/.env.master` as the source and `.env.local` as the target.
- Treats account/org control-plane values and project runtime values as separate layers.
- Reads `.env.example`, `.env.local.example`, `.env.template`, and optional code references.
- Does not print secret values in the plan or command output.
- Preserves existing target values unless `--overwrite` is passed.
- Requires `--include-privileged` before copying service-role keys, tokens,
  passwords, database URLs, webhook secrets, and similar admin credentials.
- Writes target env files with owner-only `600` permissions.

---

## stripe_provision.py — Governed Stripe Provisioning

Creates and applies a redacted, manifest-driven plan for Stripe products, prices,
and webhook endpoints. This is for provider-side setup before project env sync.

**Examples:**
```bash
python3 automation/stripe_provision.py init --project ~/code/Applications/frogger
python3 automation/stripe_provision.py plan --project ~/code/Applications/frogger
python3 automation/stripe_provision.py apply --plan data/new-build-governance-agent/exports/stripe-frogger-test-20260408T000000Z.json
python3 automation/stripe_provision.py apply --plan data/new-build-governance-agent/exports/stripe-frogger-live-20260408T000000Z.json --allow-live
```

**Manifest shape:**
```json
{
  "project_slug": "frogger",
  "mode": "test",
  "currency": "cad",
  "provision_prices": true,
  "products": [
    {
      "key": "starter",
      "name": "Frogger Starter",
      "prices": [
        {
          "key": "starter_monthly",
          "env": "STRIPE_PRICE_STARTER",
          "lookup_key": "frogger_starter_monthly",
          "unit_amount": 900,
          "interval": "month"
        }
      ]
    }
  ],
  "webhook": {
    "url": "https://example.com/api/stripe/webhook",
    "secret_env": "STRIPE_WEBHOOK_SECRET",
    "events": ["checkout.session.completed", "customer.subscription.updated"]
  }
}
```

**Governance behavior:**
- Uses `STRIPE_RESTRICTED_KEY` first, then `STRIPE_SECRET_KEY` if needed.
- Refuses live-mode apply unless `--allow-live` is passed.
- Uses lookup keys and project metadata to avoid duplicate products/prices.
- Creates or updates webhook endpoints by URL.
- Writes generated price IDs and newly-created webhook secrets back to
  `~/code/.env.master` without printing secret values.
- Existing Stripe webhook secrets cannot be retrieved from Stripe; if an endpoint
  already exists, keep or rotate the secret manually.

---

## master_env.py — Master Env Population Helper

Inspects and populates the private master env file without printing secret values.
Use this before `env_sync.py` when you are collecting provider credentials from
Supabase, Vercel, Stripe, Resend, OpenAI, Anthropic, and similar systems.

The master env should hold both:
- **Control-plane credentials**: account/org tokens that allow governed automation
  to create or configure provider resources, such as `SUPABASE_ACCESS_TOKEN`,
  `SUPABASE_ORG_ID`, `VERCEL_TOKEN`, `VERCEL_TEAM_ID`, `STRIPE_SECRET_KEY`, or
  `STRIPE_RESTRICTED_KEY`. Populate these first when the goal is to let AI
  building agents create provider-side resources on your behalf.
- **Project runtime credentials**: URLs, project refs, publishable keys,
  service-role keys, database URLs, webhook secrets, and other values generated
  for one specific app or environment.

**Examples:**
```bash
python3 automation/master_env.py status
python3 automation/master_env.py status --control-plane
python3 automation/master_env.py missing --priority
python3 automation/master_env.py missing --control-plane
python3 automation/master_env.py set SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
python3 automation/master_env.py merge --source ~/Downloads/provider.env
```

**Governance behavior:**
- Defaults to `~/code/.env.master`.
- Prompts with hidden input by default for `set`.
- Does not print secret values.
- Preserves existing values unless `--overwrite` is passed.
- Writes the master env file with owner-only `600` permissions.
- Keeps the master env outside individual project folders so one app does not
  accidentally own or commit organization-level provider access.

---

## promotion_checks.py — Guided Pre/Post Checks

Runs the local pre-promotion or post-promotion checks defined in a generated promotion plan and writes a JSON report.

**Examples:**
```bash
python3 automation/promotion_checks.py --plan data/new-build-governance-agent/exports/promotion-frogger-20260408T000000Z.json
python3 automation/promotion_checks.py --plan data/new-build-governance-agent/exports/promotion-frogger-20260408T000000Z.json --stage post_promotion_checks
```

---

## promotion_remediate.py — Local Test Tool Repair

Repairs missing local test tooling for a selected project, currently focused on installing `pytest` into the detected project Python environment before rerunning checks.

**Example:**
```bash
python3 automation/promotion_remediate.py --plan data/new-build-governance-agent/exports/promotion-frogger-20260408T000000Z.json --tool pytest
```

---

## promotion_execute.py — Approved External Execution

Executes the approved GitHub publish step from a generated promotion plan, stages an explicit reviewed file set, commits, pushes the current branch, and writes a rollback-aware execution report.

**Example:**
```bash
python3 automation/promotion_execute.py --plan data/new-build-governance-agent/exports/promotion-frogger-20260408T000000Z.json --target github --include-file README.md --include-file docs/current-build-pathway.md --commit-message "Promote frogger"
```

To stage the full working tree after reviewing `git status --short`, pass:

```bash
python3 automation/promotion_execute.py --plan data/new-build-governance-agent/exports/promotion-frogger-20260408T000000Z.json --target github --allow-stage-all --commit-message "Promote frogger"
```

---

## Recommended additions (future)

- Schema validation for `project-control.yaml`
- Naming convention checks
- Exception expiry alerts
- Release readiness validation
- Agent governance compliance scoring

---

## Consolidation plan

The current plan is to keep `New Build Governance Agent` as the primary product and absorb the useful backend/controller concepts from the separate `New Project Setup Agent` prototype.

See:

- `docs/processes/new-build-governance-agent-consolidation-plan.md`
