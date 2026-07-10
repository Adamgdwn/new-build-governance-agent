# Document Control Standard

Document ID: STD-ENG-008
Version: 1.1.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-05-31
Last Reviewed: 2026-05-31
Next Review: 2027-05-31

## Purpose

This standard defines how governed documents are named, structured, versioned, reviewed, approved, timestamped, and maintained.

Use this as the portable document-control standard for governed builds. A project may adopt this standard by referencing this file from its `START_HERE.md`, `project-control.yaml`, `docs/current-build-pathway.md`, or equivalent build-session instructions.

## Applicability

This standard applies to governed project documentation, especially documents that control planning, implementation, review, operation, audit, or handoff.

It applies strongly to:

- policies
- standards
- processes
- current build pathways
- handoff notes
- audit reports
- runbooks
- risk registers
- agent registers
- model and prompt registers
- tool permission matrices
- deployment guides
- architecture decision records

For low-risk local notes, use the lightweight metadata and timestamp rules. For high-risk, production, infrastructure, money, sensitive data, or agent/tooling work, use the full controlled-document structure.

## Core Rule

Controlled documents must be easy to identify, easy to review, and easy for the next maintainer or agent to resume from.

Every controlled document should answer:

- what this document is
- who owns it
- what status it is in
- when it was last updated or reviewed
- what decision, work, validation, risk, or handoff it records
- what the next reader should do with it

## Adoption Rule

To adopt this standard in another repository without retooling:

1. Add or reference this document as the project's document-control standard.
2. Add `docs/current-build-pathway.md` or an equivalent live pathway document.
3. Require material work, decisions, validation, exceptions, audits, and handoffs to use ISO-style timestamps from `date -Iseconds`.
4. Use the document patterns in this standard for new or materially updated Markdown files.
5. Record any intentional deviation as an exception or pathway note.

Machine checks may be added later, but adoption does not require new automation.

## Markdown Structure Rules

Use predictable Markdown hierarchy:

- `#` is reserved for the document title and should appear once.
- `##` is used for primary sections.
- `###` is used for subsections inside a `##` section.
- Do not skip heading levels.
- Prefer tables for pathways, validation logs, registers, findings, and approvals.
- Prefer short sections with clear labels over long unstructured prose.
- Keep file names in `kebab-case`.
- Do not put version numbers in file names unless there is a legal, contractual, or archival reason.

Documents do not need identical headings, but documents of the same type should use the same pattern.

## Document Classes

Use these default document classes:

| Class | Meaning |
|---|---|
| `POL` | Policy |
| `STD` | Standard |
| `PRC` | Process |
| `TPL` | Template |
| `CHK` | Checklist |
| `ADR` | Architecture decision record |
| `RUN` | Runbook |
| `GUI` | User guide or quick-start guide |
| `REG` | Register or log |
| `AUD` | Audit report |
| `PATH` | Current pathway or handoff route |

## Document Identifier Format

Controlled documents should use this identifier format in the document header when practical:

```text
<CLASS>-<DOMAIN>-<NUMBER>
```

Examples:

- `POL-ENG-001`
- `STD-ENG-008`
- `PRC-ENG-001`
- `AUD-ENG-001`
- `PATH-ENG-001`

`DOMAIN` may remain `ENG` unless the project adopts a wider taxonomy. `NUMBER` should be a zero-padded sequence within the class and domain.

## Required Metadata

Controlled documents should include this metadata near the top of the file:

```text
Document ID: STD-ENG-008
Version: 1.1.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-05-31
Last Reviewed: 2026-05-31
Next Review: 2027-05-31
```

Lightweight project-local documents may use this shorter metadata when full control is unnecessary:

```text
Last Updated: 2026-05-31
Status: active
Owner: Project Owner
```

Audit reports, validation notes, and handoff notes should include a full timestamp:

```text
Timestamp: 2026-05-31T18:24:39-06:00
```

## Status Values

Use these default statuses:

- `draft`
- `active`
- `superseded`
- `retired`

Avoid vague status labels such as `done-ish`, `current enough`, or `needs love`.

## Versioning Rules

Use semantic-style document versions:

- major version for material policy or control changes
- minor version for meaningful content additions or clarifications
- patch version for typo fixes or non-substantive edits

Examples:

- `1.0.0` initial approved issue
- `1.1.0` added a required control
- `1.1.1` corrected wording only
- `2.0.0` materially changed the approval model

## Timestamp Rules

Use ISO-style timestamps for material work, decisions, exceptions, validation, release notes, audits, and handoffs.

Prefer the local command:

```bash
date -Iseconds
```

Use date-only values for review metadata, such as `Last Reviewed`, when a full timestamp would add noise. Use full timestamps for event records where sequence matters.

## Required Project Document Set

This section absorbs the retired Documentation Standard. Documentation must support delivery, operation, and handover; documents should be concise, current, and owned. Required documents may be lightweight, but they may not be absent.

Every governed project must provide:

- `README.md`
- `START_HERE.md`
- `project-control.yaml`
- architecture overview
- current build pathway
- deployment guide for deployable systems
- runbook for operable systems
- change log or release history
- risk register

Type-specific additions:

- Applications, services, and websites: environment and configuration notes, dependency and integration notes, user-facing availability or support assumptions.
- Internal tools and automations: execution and scheduling model, operational owner, failure handling notes.
- Infrastructure repositories: environment topology, state handling notes, change approval expectations.
- AI agents: model registry, prompt or instruction record, tool permission matrix, evaluation strategy, human oversight rules, rollback or kill-switch guidance.

Major architectural or governance decisions should be captured in ADR form — at minimum, decisions affecting security posture, production architecture, deployment model, data handling, agent autonomy, or external dependencies with high lock-in risk.

Required documents must state owner and last review date where practical, timestamp material work and handoffs, be written for maintainers and operators, and avoid stale promises or plans that are no longer accurate.

## Required Document Patterns

### Pathway And Handoff Documents

Use this pattern for `docs/current-build-pathway.md` and similar live work-routing documents:

```text
# Current Build Pathway

Last Updated: YYYY-MM-DD
Status: active
Owner: Technical Lead

## Purpose
## Required Work Pattern
## Chunking Standard
## Active Path
## Timestamp Rule
## Validation Log
## Next Handoff
```

The active path should use a table:

| Step | Status | Timestamp | Owner | Notes |
|---|---|---|---|---|
| Define current chunk | active | YYYY-MM-DDTHH:MM:SS-06:00 | Technical Lead | State the current work. |

The validation log should use a table:

| Timestamp | Command | Result | Notes |
|---|---|---|---|
| YYYY-MM-DDTHH:MM:SS-06:00 | `command` | pass | Record the evidence. |

### Audit Documents

Use this pattern for repository audits, standards audits, release audits, and readiness audits:

```text
# Audit Title

Date: YYYY-MM-DD
Timestamp: YYYY-MM-DDTHH:MM:SS-06:00
Scope: repository, system, release, or process audited
Classification audited: project type, use case, risk tier, governance level

## Executive Summary
## Standards Audited
## Validation Run
## Positive Findings
## Findings
## Recommended Remediation Order
## Audit Conclusion
```

Findings should be ordered by severity and include evidence, impact, and recommended fix.

### Standards And Policies

Use this pattern for standards and policies:

```text
# Standard Or Policy Name

Document ID: STD-ENG-000
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: YYYY-MM-DD
Last Reviewed: YYYY-MM-DD
Next Review: YYYY-MM-DD

## Purpose
## Applicability
## Core Rule
## Requirements
## Exceptions
## Review Cadence
```

Use `## Requirements` for mandatory rules and `## Guidance` for recommended but non-mandatory practices.

### Registers And Logs

Use this pattern for risk registers, model registries, prompt registers, tool inventories, and permission matrices:

```text
# Register Name

Last Updated: YYYY-MM-DD
Status: active
Owner: Technical Lead

## Purpose
## Register
## Review Cadence
## Open Actions
```

The register itself should use a table with owner, status, last reviewed date, and notes.

### Runbooks

Use this pattern for operational runbooks:

```text
# Runbook Name

Last Updated: YYYY-MM-DD
Status: active
Owner: Technical Lead

## Purpose
## Operating Context
## Common Commands
## Normal Operation
## Failure Handling
## Escalation
## Recovery Or Rollback
## Validation
## Handoff Notes
```

Runbooks for live systems should be reviewed at least every 6 months or after incidents.

### Architecture Decision Records

Use this pattern for ADRs:

```text
# ADR-000: Decision Title

Date: YYYY-MM-DD
Status: proposed, accepted, superseded, or retired
Owner: Technical Lead

## Context
## Decision
## Consequences
## Alternatives Considered
## Review Point
```

ADRs should be used for decisions that affect security posture, production architecture, deployment model, data handling, agent autonomy, or external dependencies with high lock-in risk.

## File Naming Rules

File names should remain human-readable and stable:

- use `kebab-case`
- include the document purpose, not the control ID
- avoid version numbers in file names
- include dates in audit/report file names when date is part of the record identity

Examples:

- `document-control-standard.md`
- `engineering-governance-policy.md`
- `project-intake-process.md`
- `current-build-pathway.md`
- `repository-audit-2026-05-31.md`

## Review Cadence

Default review cadence:

| Document Type | Minimum Review Cadence |
|---|---|
| Policies and standards | Annually |
| Processes and guides | Annually |
| Templates and checklists | When dependent controls change, and at least annually |
| Runbooks for live systems | Every 6 months, or after incidents |
| Risk registers | After material risk changes, and at least quarterly for high-risk systems |
| Agent registers and tool permissions | After each material change, and at least quarterly for high-risk systems |
| Current build pathway | During every substantial build session |
| Audit reports | At audit time, then retained as historical records |

## Approval Expectations

Use this default approval model:

| Change Type | Approval Expectation |
|---|---|
| Policy and standard changes | Project owner and technical lead |
| Process changes affecting production governance | Project owner and technical lead |
| Templates and checklists | Technical lead |
| Project-local controlled documents | Project owner or delegate, with technical lead review where risk warrants |
| Low-risk pathway notes | Technical lead or assigned agent self-review |

## Change Logging

Material changes to controlled documents should be recorded in one of:

- document revision history section
- changelog
- current build pathway validation or handoff note
- repository history with clear commit messages

Higher-risk governance documents should prefer an explicit revision history section.

## Exceptions

If a project cannot follow this standard exactly, record:

- the document or control affected
- the reason for deviation
- the compensating control
- the owner
- the review date

Do not silently ignore missing ownership, timestamps, validation evidence, or handoff notes when they matter to future work.

## Superseded Documents

When a document is replaced:

- mark the old document as `superseded`
- reference the replacement document
- retain the prior document for traceability unless there is a compelling reason not to

## Minimum Acceptance Checklist

A controlled document is acceptable when:

- the title and document purpose are clear
- ownership is explicit
- status is explicit
- dates or timestamps are present where required
- heading hierarchy is predictable
- material decisions or validation are traceable
- handoff or next action is clear when the document controls active work
- exceptions are recorded instead of hidden
