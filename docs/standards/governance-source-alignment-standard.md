# Governance Source Alignment Standard

Document ID: STD-ENG-024
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-08-31
Last Reviewed: 2026-08-31
Next Review: 2026-11-30
Document type: governance alignment standard
Audience: project owners, technical leads, coding agents, and release reviewers

## Purpose

This standard keeps governed builds aligned with useful control improvements from the
New Build Governance Agent source without making every coding session reload the full
governance repository or blindly overwrite project-local decisions.

## Core Rule

Active governed builds periodically compare their local governance package with the
current governance source. The comparison is a review step, not automatic adoption.
Local risk tiers, governance levels, exceptions, and project-specific controls remain
authoritative until an approved change updates them.

## When To Check Back

Perform an alignment review:

- when a project is first scaffolded or brought under governance
- at least every 90 days while the project is active
- before the first production release, and before later release-readiness reviews when
  the last alignment review is more than 90 days old
- after a material change in risk, autonomy, sensitive data, money movement, deployment
  model, or operating environment
- when the project owner or governance source announces a relevant control update

This is not an ordinary-startup requirement. Small, reversible work should not pause
for a governance sync merely because a session began.

## Agent Prompt Rule

At the start of material planning or release-readiness work, the agent should inspect
the project's last governance-alignment date. If the review is due or has never been
recorded, the agent should tell the user and propose a bounded alignment review. It may
continue safe in-scope work unless a missing update affects the current task or risk.

## Alignment Procedure

1. Locate the configured New Build Governance Agent source through project metadata,
   workspace instructions, or repository discovery. Do not assume a user-specific
   absolute path.
2. Record the source revision or release, comparison date, and reviewer.
3. Compare the source standards index and only the standards relevant to the project's
   current work and risk. Use a generated change-control manifest when available.
4. Classify differences as required, recommended, not applicable, or already satisfied.
5. Review proposed changes before applying them. Preserve local files through
   copy-if-missing or managed-block behavior and never silently override risk,
   governance level, owner decisions, or accepted exceptions.
6. Apply accepted updates as a separate bounded chunk with tests and rollback notes.
7. Record the outcome in `project-control.yaml`, the active pathway, or another durable
   governance record.

## Minimum Record

Each alignment review should retain:

- review date
- governance source identity and revision when available
- controls reviewed
- changes adopted, deferred, or rejected
- exceptions or owner decisions
- next review date

New projects should use the `governance_alignment` section in
`project-control.yaml`. Existing projects may use the active pathway until their
control file is upgraded.

## Current Cross-Project Controls

The standards index is the authoritative catalog. Current examples of controls worth
checking include:

- code complexity review and its advisory-to-enforced rollout
- context hygiene and bounded agent work
- ship-readiness evidence
- GitHub resource efficiency
- agent autonomy, tool permissions, and human oversight

## Failure And Unavailability

If the governance source cannot be found or accessed, record that the review was not
completed and continue only when the current work remains safe under the local
controls. Do not search arbitrary locations, download an unverified substitute, or
weaken local controls to make the check pass.

## Exceptions

A project may use a different review cadence or source when it records the reason,
owner, compensating control, and next review point. Offline or archived projects do
not need recurring reviews until work resumes.

## Review Cadence

Review this standard quarterly during its initial rollout and at least annually after
the process is stable.
