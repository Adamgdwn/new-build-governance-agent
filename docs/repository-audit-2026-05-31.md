# New Build Governance Agent Standards Audit

Date: 2026-05-31
Timestamp: 2026-05-31T10:53:42-06:00
Status: retired
Owner: Project Owner
Scope: `New Build Governance Agent` repository only
Classification audited: `project_type: agent`, `use_case.primary: AI agent with tools`, secondary use case `Infrastructure / deployment code`, `risk_tier: high`, `governance_level: 3`

## Executive Summary

The build passes the current machine governance baseline and the new use-case governance standard is integrated without overriding the selected risk level. The scaffold and change-control paths now preserve user-selected `risk_tier` and `governance_level`, while adding use-case guidance as control-selection context.

The main audit gap at audit time was not file presence. It was evidence quality. Several high-risk agent and infrastructure controls existed as placeholder documents, and `project-control.yaml` declared machine enforcement for lint, tests, and secret scanning that was not yet backed by committed tooling or CI.

Overall status at audit time: conditionally acceptable for local governed development, not yet strong enough for unattended agent operation or production-grade release automation.

## Remediation Update

Timestamp: 2026-05-31T11:13:32-06:00

The main audit fixes have now been implemented in this working tree:

- Agent inventory, model registry, prompt register, tool permission matrix, architecture, deployment guide, runbook, and risk register now contain real operating records instead of placeholders.
- `scripts/validate.sh` now runs governance checks, required-file checks, Python compile checks, shell syntax checks, and the committed unit test suite.
- `.github/workflows/validate.yml` now runs the same validation script for pushes and pull requests on hosted GitHub.
- Focused unit tests cover change-control idempotency and risk preservation, env sync redaction/privileged-key handling, promotion-check discovery, explicit Git staging, and secret hygiene.
- `freedom.tool.yaml` no longer passes Supabase provider credentials to the headless scaffold tool.
- `automation/promotion_execute.py` now requires either `--include-file` entries or explicit `--allow-stage-all`, blocks secret-like paths, and records staged files in the report.
- `automation/promotion_plan.py` now detects Python compile, shell syntax, and unittest checks for this repo, and `automation/promotion_checks.py` prefers argv-based execution.

## Standards Audited

- `docs/policy/engineering-governance-policy.md`
- `docs/policy/durable-development-engineering-policy.md`
- `docs/standards/engineering-governance-by-use-case.md`
- `docs/standards/ai-agent-governance-standard.md`
- `docs/standards/risk-classification-standard.md`
- `docs/standards/testing-standard.md`
- `docs/standards/security-and-secrets-standard.md`
- `docs/standards/deployment-and-release-standard.md`
- `docs/standards/repository-and-naming-standard.md`

## Validation Run

| Command | Result | Notes |
|---|---|---|
| `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings. |
| `bash automation/check_required_files.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | Required-file baseline includes durable policy and use-case standard. |
| `python3 -m py_compile $(find automation -maxdepth 1 -name '*.py' -print)` | pass | Python syntax passed for automation entry points. |
| `for f in $(find automation scripts templates/project/scripts -name '*.sh' -print); do bash -n "$f"; done` | pass | Shell syntax passed. |
| `bash scripts/validate.sh` | pass | Runs governance, required files, Python compile, shell syntax, unittest, and secret-hygiene tests. |
| `python3 automation/promotion_checks.py --plan <generated-plan> --stage pre_promotion_checks` | pass | Generated checks now include governance preflight, Python compile, shell syntax, and unittest. |
| Fresh `website 1` scaffold | pass | Preserved `risk_tier: low` and `governance_level: 1`; added `use_case.primary`. |
| Existing-project change-control apply/idempotency check | pass | Added use-case standard and managed guidance; second proposal had no actions. |
| Promotion pre-check generated from plan | pass | Audit-time result detected only governance preflight; remediated result below detects governance preflight, Python compile, shell syntax, and unittest. |

## Positive Findings

- `project-control.yaml` now clearly records use-case classification without overriding selected risk: `project-control.yaml:3`.
- Required governance files are present and checked, including the durable engineering policy and use-case standard.
- Bootstrap and change-control paths are copy-if-missing and preserve existing files.
- The use-case standard explicitly says `risk_tier` and `governance_level` remain source-of-truth unless explicitly changed.
- Secret scan by pattern found no obvious committed secret values. Matches were policy text, placeholder env names, or code references.
- `.gitignore` excludes `.env`, Python cache files, logs, and New Build Governance Agent runtime exports.

## Findings

### High: Agent governance records are placeholders

Status: remediated on 2026-05-31.

Evidence:

- `docs/agent-inventory.md:5` contains `Example Agent`.
- `docs/model-registry.md:5` contains `Example provider` and `YYYY-MM-DD`.
- `docs/prompt-register.md:5` contains `Example Agent`.
- `docs/tool-permission-matrix.md:5` contains `Example API`.

Why it matters:

The project is classified as an agent with tool/infrastructure responsibilities. The AI agent governance standard requires real agent inventory, model registry, prompt register, tool permission matrix, oversight rules, and rollback or disable procedure.

Recommended fix:

Replace placeholders with the real New Build Governance Agent control surface: GUI, headless/Freedom invocation, promotion planning/checking/execution, environment sync, master env handling, and Stripe provisioning. Include allowed/prohibited actions, approval requirements, and disable/rollback behavior.

### High: Core operating docs are still scaffold-thin

Status: remediated on 2026-05-31.

Evidence:

- `docs/architecture.md:5` still says to describe the system.
- `docs/deployment-guide.md:5` still says to describe environments.
- `docs/runbook.md:5` still says to describe operational purpose.
- `docs/risks/risk-register.md:5` has blank tier/owner fields and an example risk.

Why it matters:

For a high-risk agent/infrastructure governance tool, architecture, deployment, runbook, and risk register need to explain real trust boundaries, external actions, credential handling, rollback, and likely failures.

Recommended fix:

Promote the factual architecture and risk content from the older repository audit into the live controlled docs, then add current use-case and durable-policy changes.

### High: Declared machine enforcement is stronger than actual enforcement

Status: remediated on 2026-05-31 with `scripts/validate.sh`, focused unit tests, secret hygiene coverage, and a GitHub Actions validation workflow.

Evidence:

- `project-control.yaml:40` declares `required-file-check`, `lint`, `tests`, and `secret-scan`.
- No `tests/` directory, `.github/` workflow, `pyproject.toml`, `requirements.txt`, `package.json`, `SECURITY.md`, `CONTRIBUTING.md`, or `CODEOWNERS` was found.
- Current automated validation is mostly governance checks, `py_compile`, shell syntax, and targeted smoke checks.

Why it matters:

The testing and supply-chain standards allow risk-scaled controls, but the project is high risk and includes scripts that can write files, sync env values, provision Stripe, and push to GitHub.

Recommended fix:

Add a minimal test suite for `change_control.py`, bootstrap/render behavior, env parsing/redaction, and promotion-plan safety. Add a simple CI or local validation script that runs governance, syntax, tests, and secret-scan equivalents.

### Medium: Freedom tool manifest passes through a broad Supabase service-role key

Status: remediated on 2026-05-31; headless scaffolding now declares no provider env passthrough.

Evidence:

- `freedom.tool.yaml:37` passes `SUPABASE_URL`.
- `freedom.tool.yaml:39` passes `SUPABASE_SERVICE_ROLE_KEY`.
- `freedom.tool.yaml:123` says this tool writes a project tree and `freedom.tool.yaml:125` says it does not modify Supabase.

Why it matters:

The use-case standard requires least-privilege tool scopes for AI agents. Passing a service-role key to a scaffolding tool appears broader than its stated side effects.

Recommended fix:

Remove `SUPABASE_SERVICE_ROLE_KEY` from `env_passthrough` unless a current code path requires it. If retained, document why, what can use it, and what prevents accidental database writes.

### Medium: GitHub execution stages all local changes

Status: remediated on 2026-05-31; execution now requires an explicit file list or explicit full-tree approval and records staged files.

Evidence:

- `automation/promotion_execute.py:117` runs `git add -A`.
- The repo currently has many modified and untracked files from ongoing governance updates.

Why it matters:

For a high-risk governance tool, external publication should be scoped to reviewed files. `git add -A` can publish unrelated or accidental local changes if the operator misses them.

Recommended fix:

Make GitHub execution consume an explicit file manifest or require a reviewed file list before staging. At minimum, record the staged file list in the execution report before commit.

### Medium: Pre-promotion checks are too narrow for this repo

Status: remediated on 2026-05-31; generated pre-promotion checks now include governance preflight, Python compile, shell syntax, and unittest for this repo.

Evidence:

- Generated pre-promotion checks detected and ran only `bash scripts/governance-preflight.sh`.
- Separate manual audit commands were needed for Python compile and shell syntax.

Why it matters:

The repository's own promotion flow should discover the available Python and shell validations for this automation-heavy project.

Recommended fix:

Teach `promotion_plan.py` or `promotion_checks.py` to add repo-local Python compile and shell syntax checks when automation scripts are present.

## Use-Case Compliance Summary

| Use-case control | Status | Notes |
|---|---|---|
| Explicit tool inventory | Partial | File exists, but content is placeholder. |
| Least-privilege tool scopes | Partial | Some scripts are conservative; Freedom env passthrough is too broad. |
| Human approval for destructive/external actions | Partial | Promotion execution is explicit, but file staging is broad. |
| Dry-run mode | Partial | Change-control and promotion planning support plans; not every external action has equivalent dry-run evidence. |
| Tool argument validation | Partial | Some CLIs validate paths and choices; not documented in tool matrix. |
| Action logging | Partial | GUI logs and reports exist, but runbook does not document retention/review. |
| Recovery plan | Weak | Runbook and risk register are placeholders. |
| Prompt injection / policy override resistance | Weak | New policy language exists, but no eval/test evidence. |

## Recommended Remediation Order

1. Replace placeholder agent, model, prompt, and tool-permission documents with real records.
2. Fill architecture, runbook, deployment guide, and risk register with current factual system behavior.
3. Add a local validation script and minimal test suite for the high-risk automation paths.
4. Remove or justify `SUPABASE_SERVICE_ROLE_KEY` passthrough in `freedom.tool.yaml`.
5. Constrain GitHub execution staging to an explicit reviewed file set.
6. Expand promotion checks so this repo's generated pre-checks include Python compile and shell syntax validation.

## Audit Conclusion

The framework direction is sound and the new standards are now integrated coherently. The build is fit for continued local development with supervised execution.

The next quality step is to turn the currently present-but-placeholder control documents into real operating records, then back the declared `lint`, `tests`, and `secret-scan` controls with executable checks.
