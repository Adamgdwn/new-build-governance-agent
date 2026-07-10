# Governance Audit — New Build Agent

Document ID: AUD-ENG-002
Date: 2026-06-16
Timestamp: 2026-06-16T22:31:44-06:00
Scope: /home/adamgoodwin/code/agents/New Build Agent
Status: active
Owner: Project Owner

> Remediation executed 2026-07-10 — see governance-audit-2026-07-10.md for the clean run.

---

## Executive Summary

Automated governance audit of `New Build Agent`. 3 positive finding(s). 0 blocker(s), 57 required gap(s), 62 warning(s).

**Conclusion:** ATTENTION — required gaps or blockers need resolution before next release.

---

## Validation Run

Checks performed:

- Document metadata presence (Status, Owner, date field) in first 30 lines of every docs/*.md
- Superseded docs reference their replacement
- At most one active pathway / build-plan document
- Active pathway updated within last 30 days
- Build plan / pathway / deployment docs have a Status field
- Standards, policies, and processes have Document ID fields
- CARRY_FORWARD.md open flags not stale (>7 days)

---

## Positive Findings

- All superseded docs reference their replacement.
- Single active pathway document: `docs/current-build-pathway.md`.
- No stale carry-forward flags.

---

## Findings

### Required Gaps

- [ ] `docs/CHANGELOG.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/adr-template.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/agent-inventory.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/architecture.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/archive/pathway-history.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/deployment-guide.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/domain-language.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/exception-record-template.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/manual.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/model-registry.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/policy/durable-development-engineering-policy.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/policy/engineering-governance-policy.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/processes/exception-management-process.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/processes/new-build-governance-agent-consolidation-plan.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/processes/project-intake-process.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/processes/staged-promotion-workflow.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/prompt-register.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/quick-start-governance-flow.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/repository-audit-2026-05-19.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/repository-audit-2026-05-31.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/repository-audit-2026-06-07.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/risks/risk-register.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/roadmap.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/runbook.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/ai-agent-governance-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/deployment-and-release-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/documentation-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/engineering-governance-by-use-case.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/monorepo-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/repository-and-naming-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/risk-classification-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/security-and-secrets-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/standards/testing-standard.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/tool-permission-matrix.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/user-guide.md` — add `Status: <draft|active|superseded|retired>` in the first 30 lines.
- [ ] `docs/archive/pathway-history.md` is a plan/pathway/deployment doc with no `Status:` field — add one.
- [ ] `docs/deployment-guide.md` is a plan/pathway/deployment doc with no `Status:` field — add one.
- [ ] `docs/processes/new-build-governance-agent-consolidation-plan.md` is a plan/pathway/deployment doc with no `Status:` field — add one.
- [ ] `docs/standards/deployment-and-release-standard.md` is a plan/pathway/deployment doc with no `Status:` field — add one.
- [ ] `docs/standards/README.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/ai-agent-governance-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/context-hygiene-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/deployment-and-release-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/documentation-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/engineering-governance-by-use-case.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/monorepo-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/repository-and-naming-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/risk-classification-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/security-and-secrets-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/ship-ready-engineering-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/standards/testing-standard.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/policy/durable-development-engineering-policy.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/policy/engineering-governance-policy.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/processes/exception-management-process.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/processes/new-build-governance-agent-consolidation-plan.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/processes/project-intake-process.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.
- [ ] `docs/processes/staged-promotion-workflow.md` — add `Document ID: <CLASS>-ENG-<NNN>` in the front matter.

### Warnings

- [ ] `docs/CHANGELOG.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/adr-template.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/agent-inventory.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/architecture.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/archive/pathway-history.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/deployment-guide.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/domain-language.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/exception-record-template.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/manual.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/model-registry.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/policy/durable-development-engineering-policy.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/policy/engineering-governance-policy.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/processes/exception-management-process.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/processes/new-build-governance-agent-consolidation-plan.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/processes/project-intake-process.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/processes/staged-promotion-workflow.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/prompt-register.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/quick-start-governance-flow.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/repository-audit-2026-05-19.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/repository-audit-2026-05-31.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/repository-audit-2026-06-07.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/risks/risk-register.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/roadmap.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/runbook.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/ai-agent-governance-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/deployment-and-release-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/documentation-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/engineering-governance-by-use-case.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/monorepo-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/repository-and-naming-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/risk-classification-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/security-and-secrets-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/standards/testing-standard.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/tool-permission-matrix.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/user-guide.md` — add `Owner: <name>` in the first 30 lines.
- [ ] `docs/CHANGELOG.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/adr-template.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/archive/pathway-history.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/context-map.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/domain-language.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/manual.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/policy/durable-development-engineering-policy.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/policy/engineering-governance-policy.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/processes/exception-management-process.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/processes/new-build-governance-agent-consolidation-plan.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/processes/project-intake-process.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/processes/staged-promotion-workflow.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/quick-start-governance-flow.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/roadmap.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/README.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/ai-agent-governance-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/context-hygiene-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/deployment-and-release-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/documentation-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/engineering-governance-by-use-case.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/monorepo-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/repository-and-naming-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/risk-classification-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/security-and-secrets-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/ship-ready-engineering-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/standards/testing-standard.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.
- [ ] `docs/user-guide.md` — add a date field (`Last Updated: YYYY-MM-DD`) in the first 30 lines.


---

## Document Supersession

- All superseded docs reference their replacement.
- Single active pathway document: `docs/current-build-pathway.md`.
- `docs/archive/pathway-history.md` is a plan/pathway/deployment doc with no `Status:` field — add one.
- `docs/deployment-guide.md` is a plan/pathway/deployment doc with no `Status:` field — add one.
- `docs/processes/new-build-governance-agent-consolidation-plan.md` is a plan/pathway/deployment doc with no `Status:` field — add one.
- `docs/standards/deployment-and-release-standard.md` is a plan/pathway/deployment doc with no `Status:` field — add one.

---

## Recommended Remediation Order

1. Resolve all **Blockers** — these prevent release or introduce governance risk.
2. Resolve all **Required Gaps** — missing metadata, orphaned docs, missing Document IDs.
3. Address **Warnings** at your discretion — stale docs and open carry-forward flags.

---

## Audit Conclusion

ATTENTION — required gaps or blockers need resolution before next release.
Total findings: 119 (0 blocker, 57 required gap, 62 warning).

_This report was generated automatically. Review each finding and tick the checkbox when resolved._
