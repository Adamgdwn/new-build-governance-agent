# Governance Source Alignment Standard

Document type: governance alignment standard
Status: active
Owner: Project owner or human technical lead
Audience: project owners, technical leads, coding agents, and release reviewers

## Purpose

This standard keeps the project aligned with useful control improvements from the New
Build Governance Agent source without making every session reload the governance
repository or blindly overwrite local decisions.

## Core Rule

Periodically compare the local governance package with the current governance source.
The comparison is a review step, not automatic adoption. Local risk tiers, governance
levels, exceptions, and project-specific controls remain authoritative until an
approved change updates them.

## When To Check Back

Review alignment:

- when the project is first scaffolded or brought under governance
- at least every 90 days while active
- before the first production release, and before later release-readiness reviews when
  the last review is more than 90 days old
- after a material change in risk, autonomy, sensitive data, money movement, deployment
  model, or operating environment
- when the owner or governance source announces a relevant control update

This is not an ordinary-startup requirement.

## Agent Prompt Rule

At the start of material planning or release-readiness work, inspect the last
governance-alignment date. If it is due or absent, tell the user and propose a bounded
alignment review. Continue safe in-scope work unless a missing update affects the
current task or risk.

## Procedure

1. Locate the configured governance source without assuming a user-specific path.
2. Record its revision or release, the date, and the reviewer.
3. Compare the source standards index and only the standards relevant to current work
   and risk. Use a generated change-control manifest when available.
4. Classify differences as required, recommended, not applicable, or already satisfied.
5. Review before applying; never silently override local controls or owner decisions.
6. Apply accepted updates as a bounded, validated chunk.
7. Record the result and next review date in `project-control.yaml`, the active pathway,
   or another durable governance record.

## Failure And Exceptions

If the source is unavailable, record that the review was not completed and continue
only when local controls remain sufficient for the work. A different cadence or source
requires a recorded owner, rationale, compensating control, and next review point.
Offline or archived projects do not need recurring reviews until work resumes.
