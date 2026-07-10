# Agent Inventory

Last reviewed: 2026-05-31T11:06:01-06:00
Status: active
Owner: Technical Lead

| Agent ID | Name | Purpose | Autonomy | Model | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| NBGA-001 | New Build Governance Agent GUI | Desktop workflow for scaffolding, auditing, compliance planning, release planning, checks, and selected publish execution. | A1 | Local Python/Tkinter orchestration; user-selected AI assistants may operate the repo. | Adam Goodwin | Active |
| NBGA-002 | New Build Governance Agent Headless Tool | JSON/stdin tool invoked by `freedom.tool.yaml` to create governed project scaffolds. | A1 | Local Python subprocess wrapper. | Adam Goodwin | Active |
| NBGA-003 | Compliance Manifest Agent | Generates and applies copy-if-missing governance manifests for existing projects. | A1 | `automation/change_control.py` | Adam Goodwin | Active |
| NBGA-004 | Promotion Planning Agent | Generates staged external rollout plans without pushing, deploying, billing, sending, or migrating. | A0 | `automation/promotion_plan.py` | Adam Goodwin | Active |
| NBGA-005 | Promotion Check Runner | Runs approved pre/post promotion checks from a generated plan. | A1 | `automation/promotion_checks.py` | Adam Goodwin | Active |
| NBGA-006 | GitHub Publish Executor | Commits and pushes approved local changes and may open a draft PR. | A1 | `automation/promotion_execute.py` with GitHub CLI | Adam Goodwin | Restricted |
| NBGA-007 | Environment Sync Planner/Applier | Creates redacted env sync plans and writes selected runtime env values into project env files. | A1 | `automation/env_sync.py` | Adam Goodwin | Restricted |
| NBGA-008 | Master Env Manager | Inspects, sets, and merges local master env entries without printing secret values. | A1 | `automation/master_env.py` | Adam Goodwin | Restricted |
| NBGA-009 | Stripe Provisioning Helper | Plans and applies Stripe product, price, and webhook setup from a manifest. Test-mode-first; live mode requires explicit flag. | A1 | `automation/stripe_provision.py` | Adam Goodwin | Restricted |

## Oversight Rules

- Default autonomy is A1: propose, plan, or execute bounded local actions after user approval.
- External or destructive actions require explicit operator approval at the command boundary.
- The active `risk_tier` and `governance_level` in `project-control.yaml` remain source of truth.
- Generated plans and reports are review artifacts; they do not imply approval to execute.

## Disable Or Rollback

- Stop GUI/headless execution by closing the process or removing the tool manifest from the dispatcher.
- Revert scaffold or compliance additions by removing created files or managed instruction blocks.
- Revert GitHub publish actions using the rollback commands emitted by `promotion_execute.py`.
- Restore environment files from backups or prior env snapshots; generated secret values are not printed in reports.
