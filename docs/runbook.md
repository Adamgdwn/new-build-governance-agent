# Runbook

Last reviewed: 2026-08-31T12:16:25-06:00
Status: active
Owner: Technical Lead

## Purpose

New Build Governance Agent supports local governed project creation, existing-project compliance upgrades, project audits, promotion planning, local validation, env sync planning, and selected external execution.

## Common Failures

| Symptom | First checks | Recovery |
|---|---|---|
| Governance preflight fails | Read missing file/warning output. Check `project-control.yaml`. | Add missing governance files through `bootstrap_project.sh` or `change_control.py`; record exceptions when a gap is intentional. |
| Fresh scaffold missing a file | Inspect `automation/bootstrap_project.sh` and `templates/project`. | Add the template and copy step, then run a temporary scaffold validation. |
| Existing-project upgrade repeats actions | Inspect managed block fragments in `automation/change_control.py`. | Align template/instruction wording with fragment detection and rerun idempotency check. |
| GUI fails from desktop launcher | Run `bash automation/launch_gui.sh` in a terminal. | Verify Python with Tkinter and `GOVERNANCE_HOME`/`PATH` setup. |
| Promotion checks skip tests | Inspect generated promotion plan checks. | Add repo-specific validation command or update `promotion_plan.py` detection. |
| GitHub execution fails | Read execution report, `gh auth status`, `git status --short`. | Fix auth/branch/remote or use manual commit/PR; do not retry blindly. |
| Env sync would copy privileged values | Review redacted plan entries. | Re-run without privileged flag or explicitly approve `--include-privileged`. |
| Stripe apply fails | Read redacted Stripe report and Stripe dashboard state. | Keep test mode first; restore/rotate webhook secrets or re-run with corrected manifest. |

## Operational Checks

- `bash automation/governance_check.sh .`
- `bash scripts/validate.sh`
- `python3 automation/audit_projects.py --json`
- `python3 automation/promotion_plan.py --project /path/to/project`

## Escalation

Escalate to Adam Goodwin before:

- increasing autonomy above A1
- copying privileged secrets
- applying live Stripe changes
- pushing or publishing broad unreviewed file sets
- modifying production data, permissions, deployment settings, or money-handling configuration

## Recovery Notes

Keep generated plans and reports long enough to recover the decision trail. Runtime artifacts under `data/new-build-governance-agent/exports/` are ignored by git by default, so copy important reports into controlled docs when they become durable evidence.
