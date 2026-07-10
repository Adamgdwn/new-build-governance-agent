# Staged Promotion Workflow

Document ID: PRC-ENG-003
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This workflow separates local compliance work from any external push or deployment action.

The intent is:

- make local structure and governance compliant first
- prepare target-specific rollout plans second
- require explicit approval for GitHub, Vercel, Supabase, Stripe, Resend, or other external systems

## Stages

1. Local compliance

- repair or add required docs and governance files
- review manifests before applying local structure changes
- confirm the repo is in a stable local state

2. Prepare external sync

- inspect project signals for GitHub, Vercel, Supabase, Stripe, and Resend relevance
- generate a reviewable promotion plan with pre-checks, post-checks, and rollback notes
- list the target-specific checks, environment needs, and rollback expectations
- distinguish provider provisioning from project env sync
- use control-plane credentials only for approved provider-side creation or
  configuration, then store generated project credentials back into the private
  master env or approved secret manager
- for Stripe, define products, prices, and webhook endpoints in a billing
  manifest before applying any provider-side changes

3. Approve and execute per target

- run the pre-promotion checks before approval

- approve provider provisioning separately from project env sync
- approve GitHub separately
- approve Vercel separately
- approve Supabase separately
- approve Stripe separately
- approve Resend separately
- keep rollback notes attached to each target before execution

4. Post-promotion verification and rollback readiness

- re-run local checks after an approved promotion
- confirm target-specific health or smoke checks
- review rollback notes before any external change is considered safe

## Safety Rules

- local structural changes can be more autonomous than external actions
- external actions are never one-click by default
- control-plane credentials, generated project credentials, environment variables,
  and deployment links must be reviewed explicitly
- target-specific execution should be blocked until the plan is reviewed

## Current Tooling

Generate a promotion plan with:

```bash
python3 automation/promotion_plan.py --project /path/to/project
```

This creates a plan file under `data/new-build-governance-agent/exports/`.

Prepare Stripe resources with a manifest-driven plan:

```bash
python3 automation/stripe_provision.py init --project /path/to/project
python3 automation/stripe_provision.py plan --project /path/to/project
python3 automation/stripe_provision.py apply --plan /path/to/stripe-plan.json
```

Live Stripe provisioning requires an explicit flag:

```bash
python3 automation/stripe_provision.py apply --plan /path/to/stripe-live-plan.json --allow-live
```

Run the guided checks with:

```bash
python3 automation/promotion_checks.py --plan /path/to/plan.json
python3 automation/promotion_checks.py --plan /path/to/plan.json --stage post_promotion_checks
```

If the checks require manual review because local test tooling is missing, repair that tooling with:

```bash
python3 automation/promotion_remediate.py --plan /path/to/plan.json --tool pytest
```

Execute the approved GitHub publish step with:

```bash
python3 automation/promotion_execute.py --plan /path/to/plan.json --target github --include-file README.md --include-file docs/current-build-pathway.md --commit-message "Promote project"
```

After reviewing `git status --short`, use `--allow-stage-all` only when the full working tree is the intended reviewed file set.

This writes an execution report that records the staged files, previous commit, new commit, pushed branch, and rollback commands.
