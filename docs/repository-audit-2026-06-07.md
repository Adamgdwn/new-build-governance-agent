# Repository Standards Audit - 2026-06-07

Date: 2026-06-07
Timestamp: 2026-06-07T10:09:10-06:00
Status: retired
Owner: Project Owner
Scope: whole repository standards audit
Classification audited: `project_type: agent`, primary use case `AI agent with tools`, secondary use case `Infrastructure / deployment code`, `risk_tier: high`, `governance_level: 3`
Auditor: Codex session

## Executive Summary

The repository is in good baseline shape for continued development. Required governance files are present, the local validation suite passes, the current scaffold and upgrade pathways are tested, and recent standards additions are discoverable through the standards index and agent instructions.

The audit did not find required-file gaps or obvious committed secret values. The main remaining issues are evidence and control-quality gaps:

- Stripe provisioning is still too trusting for a restricted money-handling helper.
- Promotion planning can report misleading local-compliance gaps even when governance validation passes.
- Prompt/tool/register review metadata and handoff records are stale after recent material instruction and guidance changes.
- `AI_BOOTSTRAP.md` still has placeholder command entries, so agent-readable validation commands are weaker than the actual repo validation path.
- The repo lacks `SECURITY.md` and `.env.example`, both recommended by the repo's compliance model and relevant to a high-risk governance tool with secret/env helpers.

## Standards Audited

- `START_HERE.md`
- `docs/current-build-pathway.md`
- `docs/standards/README.md`
- `docs/policy/durable-development-engineering-policy.md`
- `docs/standards/engineering-governance-by-use-case.md`
- `docs/standards/ship-ready-engineering-standard.md`
- `docs/standards/ai-agent-governance-standard.md`
- `docs/standards/security-and-secrets-standard.md`
- `docs/standards/testing-standard.md`
- `docs/standards/deployment-and-release-standard.md`
- `docs/standards/document-control-standard.md`
- `docs/standards/context-hygiene-standard.md`
- `docs/standards/repository-and-naming-standard.md`
- `project-control.yaml`

## Validation Run

| Timestamp | Command | Result | Notes |
|---|---|---|---|
| 2026-06-07T10:09:10-06:00 | `git status --short --branch` | pass | Working tree was clean before audit work. |
| 2026-06-07T10:09:10-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 required gaps; 5 recommended improvements; 1 design quality warning. |
| 2026-06-07T10:09:10-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file check, schema validation, Python compile, shell syntax, and 38 unittests passed. |
| 2026-06-07T10:09:10-06:00 | `python3 automation/compliance_report.py /home/adamgoodwin/code/agents/New\ Build\ Agent --json` | pass | Machine-readable report returned `overall_status: passed` with 0 required gaps. |
| 2026-06-07T10:10:19-06:00 | `python3 automation/promotion_plan.py --project /home/adamgoodwin/code/agents/New\ Build\ Agent` | partial | Plan generated, but local-compliance stage reported misleading `needs_work` items. |
| 2026-06-07T10:10:34-06:00 | `python3 automation/promotion_checks.py --plan <generated-plan> --stage pre_promotion_checks` | pass | Generated pre-promotion checks passed. |
| 2026-06-07T10:09:10-06:00 | targeted `rg`, `find`, and file review scans | pass with findings | Reviewed placeholders, secret-like paths, stale metadata, generated templates, promotion, env, Stripe, CI, and agent control records. |

Local PowerShell validation could not be run because `pwsh` is not installed in this environment. The repo delegates PowerShell validation to the Windows CI job.

## Positive Findings

- Required governance files are present and validation passes.
- The repo is correctly classified as a high-risk AI agent/tooling project, and the selected risk tier/governance level remain explicit in `project-control.yaml`.
- The standards index now includes durable development, use-case governance, ship-readiness, context hygiene, and supporting standards.
- Fresh scaffold and existing-project upgrade behavior are covered by tests, including context hygiene and managed instruction guidance.
- `promotion_checks.py` now prefers safe `argv` execution and does not rely on arbitrary `shell=True` execution from plan JSON.
- `promotion_execute.py` requires explicit file inclusion or explicit full-tree approval and blocks secret-like paths.
- Secret hygiene tests scan controlled code for obvious real secret values.
- GitHub Actions cover Linux and Windows validation, and the Windows launcher package workflow is present.
- The tool permission matrix and agent inventory document the main local automation surfaces and approval expectations.

## Findings

### High: Stripe provisioning does not fail closed on invalid or placeholder manifests

Evidence:

- `automation/stripe_provision.py:101-108` only verifies that the manifest is a JSON object.
- `automation/stripe_provision.py:135-137` creates a default webhook URL of `https://example.com/api/stripe/webhook`.
- `automation/stripe_provision.py:319`, `automation/stripe_provision.py:345`, and `automation/stripe_provision.py:370` assume required fields such as product `name`, price `unit_amount`, and webhook `url`.
- `automation/stripe_provision.py:456-460` applies a plan after checking only the live-mode flag.

Impact:

Stripe provisioning is a restricted helper that can create products, prices, and webhooks and write generated values into the private master env. For a high-risk governance tool, malformed manifests and placeholder URLs should be rejected before any provider call. The current shape can fail late, create unintended Stripe resources, or create a webhook endpoint pointed at a placeholder URL.

Recommended fix:

Add a `validate_manifest()` / `validate_plan()` path used by both `plan` and `apply`. Require valid mode, product keys/names, price keys/env names/amounts/currency/intervals, safe lookup keys, webhook URL format, non-placeholder host, event names, and secret env names. Make `apply` fail closed when validation fails, and add tests for placeholder URL refusal, missing required fields, and live/test key mismatch behavior.

### High: Promotion local-compliance status can be misleading

Evidence:

- `automation/promotion_plan.py:362-369` uses `change_control.build_manifest()` actions as the local-compliance source of truth.
- Generated audit plan at `2026-06-07T10:10:19-06:00` reported missing items: `scripts/governance-check.sh`, `AGENTS.md`, and `AGENTS.md`.
- In the same audit, `automation/governance_check.sh`, `scripts/validate.sh`, and `automation/compliance_report.py --json` all passed with 0 required gaps.

Impact:

Promotion planning is release evidence. A plan that reports `needs_work` for a repo that passes governance validation can confuse operators, block promotion unnecessarily, or hide real gaps among false positives. The duplicate `AGENTS.md` entries also make the plan less reviewable.

Recommended fix:

Have `promotion_plan.py` use the categorized compliance report as the local-compliance source of truth, not raw upgrade-manifest actions. If managed instruction append opportunities remain useful, report them separately as recommendations. De-duplicate missing items and include finding categories in the promotion plan.

### Medium: Prompt, tool, and control registers are stale after material changes

Evidence:

- `docs/prompt-register.md:3-10` still shows `Last reviewed: 2026-05-31T11:06:01-06:00` and per-prompt review dates of `2026-05-31`.
- `docs/tool-permission-matrix.md:3-18` still shows `Last reviewed: 2026-05-31T11:06:01-06:00`.
- `docs/agent-inventory.md`, `docs/model-registry.md`, `docs/architecture.md`, `docs/deployment-guide.md`, `docs/runbook.md`, and `docs/risks/risk-register.md` also have May 31 review metadata.
- Since then, material instruction/guidance changes were made, including ship-ready guidance, standards index, context hygiene, GUI update affordances, Windows launcher packaging, and GitHub publishing guidance.

Impact:

The AI Agent Governance Standard requires prompt, model, and tool changes to be traceable. The current pathway records many changes, but the register metadata makes it look as if prompt/tool records have not been reviewed since before recent material changes. This weakens auditability and handoff quality.

Recommended fix:

Update prompt register, tool permission matrix, model registry, agent inventory, architecture, runbook, deployment guide, and risk register review timestamps where the current content has been reviewed. Add entries or notes for the context hygiene managed instructions and GitHub direct-main publishing path where relevant.

### Medium: Agent-readable command guidance still contains placeholders

Evidence:

- `AI_BOOTSTRAP.md:61-67` still contains `<fill in>` for Install, Dev, Lint, Build, and Test.
- The compliance report flags missing concrete lint, test, and build commands.

Impact:

The repo has a real validation command, but `AI_BOOTSTRAP.md` does not expose it in the canonical commands block. New agents may waste context or choose weaker checks. This conflicts with the testing standard's intentional strategy and the context hygiene standard's preference for refreshable, targeted guidance.

Recommended fix:

Fill in repo-specific commands. Suggested minimum:

- Install: `No install required for baseline validation; Python 3.12 and Tkinter are expected.`
- Dev: `python3 automation/new_build_gui.py`
- Lint: `bash scripts/validate.sh`
- Build: `bash scripts/validate.sh`
- Test: `python3 -m unittest discover -s tests -p 'test_*.py'`

If a distinct lint/build command is desired later, add it and update `scripts/validate.sh`.

### Medium: Security onboarding files are incomplete for a high-risk governance tool

Evidence:

- Compliance report recommends missing `.env.example`.
- Compliance report recommends missing `SECURITY.md`.
- The repo includes secret/env and provider-adjacent helpers: `automation/master_env.py`, `automation/env_sync.py`, and `automation/stripe_provision.py`.
- `.gitignore` correctly ignores `.env`, `data/`, and build/runtime artifacts, but does not provide a safe placeholder env contract.

Impact:

The Security and Secrets Standard requires projects to address secret storage, rotation, least privilege, logging exposure, dependency management, and incident owner expectations. The docs describe many of these controls, but a GitHub-visible `SECURITY.md` and safe `.env.example` would make the security posture easier for future agents, users, and contributors to follow.

Recommended fix:

Add `SECURITY.md` with vulnerability reporting, no-secret-reporting guidance, local secret handling, and escalation owner. Add `.env.example` with safe placeholder keys only, or explicitly document that this repo does not require runtime env values for baseline validation and provider credentials remain in `/home/adamgoodwin/code/.env.master`.

### Medium: Current pathway handoff and validation log are stale

Evidence:

- `docs/current-build-pathway.md:567-569` still says the ship-ready standard and README OS guidance are the latest handoff context and does not mention context hygiene, the GitHub landing refresh, or this audit.
- The validation log near `docs/current-build-pathway.md:561-565` ends at 2026-06-06 despite 2026-06-07 validation and pushes being recorded in chunk summaries above.

Impact:

The current pathway is supposed to be the durable handoff route. Stale handoff text makes future agents reread more history than necessary and weakens context hygiene.

Recommended fix:

Update `docs/current-build-pathway.md` with this audit chunk, the latest validation evidence, and a concise next handoff that names context hygiene, current findings, and the recommended remediation order.

### Low: Runtime artifact directory name triggers the design-quality warning

Evidence:

- Compliance report flags `data` as a suspicious generic name.
- `data/` is an ignored runtime artifact location used for registry, logs, exports, and reports.

Impact:

This is not a current blocker. The directory has a real purpose, but the generic name creates a recurring warning.

Recommended fix:

Either accept this as a documented exception or rename the runtime artifact root to a more specific path such as `.new-build-governance-agent/` or `runtime/new-build-governance-agent/`. If keeping `data/`, record the rationale in the risk register or compliance notes.

## Recommended Remediation Order

1. Harden `automation/stripe_provision.py` with manifest/plan validation and placeholder URL refusal.
2. Fix `automation/promotion_plan.py` local-compliance reporting to use categorized compliance output and remove false positives.
3. Update `AI_BOOTSTRAP.md` command entries with the actual repo validation commands.
4. Refresh prompt/tool/model/agent/runbook/risk review metadata and add notes for recent guidance/control changes.
5. Add `SECURITY.md` and `.env.example` or document an explicit accepted exception for each.
6. Update `docs/current-build-pathway.md` handoff and validation log.
7. Decide whether to accept or rename the `data/` runtime artifact path.

## Audit Conclusion

The repository is not blocked for normal governed development: required governance files exist, validation passes, CI exists, and no obvious committed secrets were found. It is not yet lock-down clean for high-risk release evidence because a few control surfaces still produce misleading or incomplete evidence.

The highest-value next chunk is to fix promotion/Stripe evidence quality first. That will make the repo's own release path more trustworthy and reduce ambiguity for future agents.
