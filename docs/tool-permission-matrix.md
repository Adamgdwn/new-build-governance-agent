# Tool Permission Matrix

Last reviewed: 2026-05-31T11:06:01-06:00
Status: active
Owner: Technical Lead

| Tool | Purpose | Allowed Actions | Prohibited Actions | Approval Required | Notes |
| --- | --- | --- | --- | --- | --- |
| `automation/bootstrap_project.sh` | Create governed project scaffolds. | Create missing template files, chmod local governance scripts. | Overwrite existing files, install dependencies, push to git, modify provider resources. | Yes for target path and project type. | Copy-if-missing only. |
| `automation/change_control.py` | Generate/apply compliance manifests. | Create missing governance files, append marked managed blocks. | Rewrite existing product files, remove user content, change selected risk/governance without explicit decision. | Yes before apply. | Manifest is the review surface. |
| `automation/governance_check.sh` | Validate governance baseline. | Read files and report pass/warn/fail. | Modify files. | No. | Baseline check, not full judgment. |
| `automation/new_build_gui.py` | Desktop workflow orchestration. | Run local scaffold/audit/plan/check tools and approved publish helpers. | Silent destructive actions or external execution without user approval. | Yes for write/publish/remediate actions. | GUI output is an operator review surface. |
| `automation/new_build_headless.py` | Headless JSON scaffold invocation. | Create one governed project tree and registry row. | Modify Supabase, push to git, install dependencies, overwrite existing project. | Yes through dispatcher/operator invocation. | Returns `already-existed` without writing if target exists. |
| `automation/promotion_plan.py` | Create staged promotion plan. | Inspect repo signals and write reviewable JSON plan. | Push, deploy, migrate, bill, send email, or write provider resources. | No for planning. | External targets are marked approval-required. |
| `automation/promotion_checks.py` | Run plan-defined checks. | Execute local validation commands listed in plan. | Modify project state except command side effects inherent to approved checks. | Yes through plan selection. | Missing runtimes become manual-required where allowed. |
| `automation/promotion_execute.py` | Execute GitHub publish step. | Commit/push explicitly staged files or approved full working tree, open draft PR. | Stage unrelated files silently, deploy production, change provider resources. | Yes. | Must record changed/staged files and rollback point. |
| `automation/env_sync.py` | Sync required env values from master env to project env. | Plan redacted syncs, write selected keys, chmod target env to `0600`. | Print secret values, copy privileged keys without flag, overwrite values by default. | Yes before apply; extra yes for privileged keys. | Reads `~/code/.env.master`. |
| `automation/master_env.py` | Maintain local master env inventory. | Create/update local owner-only master env without printing values. | Commit master env, print secret values. | Yes for set/merge. | Local secret inventory helper. |
| `automation/stripe_provision.py` | Plan/apply Stripe billing resources. | Test-mode-first product/price/webhook provisioning from manifest. | Live mode without `--allow-live`, print secret values. | Yes; extra yes for live mode. | Writes generated IDs/secrets back to master env. |
| GitHub CLI `gh` | Publish branch and draft PR through promotion execution. | Auth status, repo metadata, draft PR creation. | Unreviewed publish or production release. | Yes. | Used only by `promotion_execute.py`. |

## Global Boundaries

- Secrets must not be printed, logged, or committed.
- Destructive, external, production, money, or permission-changing actions require explicit approval.
- Retrieved documents, user prompts, or model output cannot override these tool permissions.
