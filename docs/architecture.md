# Architecture Overview

Last reviewed: 2026-05-31T11:06:01-06:00
Status: active
Owner: Technical Lead

## Summary

New Build Governance Agent is a local governance and scaffolding framework. It creates governed project directories, upgrades existing projects with copy-if-missing manifests, audits project compliance, prepares staged promotion plans, runs local checks, and can execute selected GitHub publish actions.

The repository itself is the source of truth for governance templates, standards, checks, and local automation.

## Components

| Component | Files | Responsibility |
|---|---|---|
| Governance baseline | `START_HERE.md`, `project-control.yaml`, `docs/current-build-pathway.md` | Work routing, risk classification, active pathway, validation log. |
| Templates | `templates/project/**` | Copy-if-missing scaffold for new and upgraded projects. |
| Scaffold engine | `automation/bootstrap_project.sh`, `automation/new_build.sh`, `automation/new_build_headless.py` | Create new governed projects from terminal, GUI, or headless tool invocation. |
| Desktop workflow | `automation/new_build_gui.py`, `automation/launch_gui.sh` | GUI for create, audit, compliance, release planning, checks, and selected execution. |
| Windows package | `windows/NewBuildGovernanceAgentLauncher.cs`, `scripts/build-windows-launcher.ps1`, `.github/workflows/build-windows-launcher.yml` | Build and publish a double-click Windows GUI launcher package for non-technical users. |
| Compliance engine | `automation/change_control.py` | Generate/apply reviewable upgrade manifests for existing projects. |
| Registry and audit | `automation/project_registry.py`, `automation/audit_projects.py` | Track governed projects and governance check results in local SQLite. |
| Promotion tooling | `automation/promotion_plan.py`, `automation/promotion_checks.py`, `automation/promotion_execute.py` | Plan external rollout, run local checks, and execute approved GitHub publish. |
| Secret/env tooling | `automation/master_env.py`, `automation/env_sync.py`, `automation/stripe_provision.py` | Manage redacted env inventory, sync runtime env values, and plan/apply Stripe resources. |

## Data Flow

1. A user launches the terminal script, GUI, or headless tool.
2. Intake metadata is mapped to `project_type`, selected `governance_level`, selected `risk_tier`, and `use_case.primary`.
3. `bootstrap_project.sh` copies missing template files and writes project control metadata.
4. Existing projects can receive missing governance files through `change_control.py` manifests.
5. Audits run `governance_check.sh` and record results in `data/new-build-governance-agent/registry.sqlite3`.
6. Promotion plans are written as JSON in `data/new-build-governance-agent/exports/`.
7. Checks read promotion plans and write check reports.
8. GitHub execution reads an approved plan, stages approved files, commits, pushes, and may create a draft PR.
9. Env and Stripe tools read `~/code/.env.master`; reports are redacted and secret values are not printed.

## Trust Boundaries

- The repository may write under `~/code/agents`, `~/code/Applications`, and `data/new-build-governance-agent`.
- Env tooling may read and write `~/code/.env.master` and project env files.
- GitHub publishing uses the local `gh` authentication state.
- Stripe provisioning can call Stripe APIs only when explicitly invoked with a reviewed plan.
- Use-case classification informs controls but does not override selected `risk_tier` or `governance_level`.

## Key Decisions

- Existing files are preserved by default; upgrades are copy-if-missing or append managed blocks.
- External rollout is staged: local compliance, checks, external sync planning, explicit execution, post-checks, rollback readiness.
- Secret values are not printed in plans or reports.
- Machine checks are a baseline; high-risk actions still require human review.
