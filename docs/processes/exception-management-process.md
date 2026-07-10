# Exception Management Process

Document ID: PRC-ENG-002
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This process governs how deviations from standards are requested, approved, tracked, and reviewed.

## When An Exception Is Required

An exception record is required when a project intentionally does not meet a default standard and the deviation matters for quality, security, traceability, or operations.

## Minimum Record

Each exception must capture:

- exception identifier
- affected project
- affected standard
- deviation summary
- business or technical justification
- risk introduced
- compensating controls
- owner
- technical lead approver
- project owner approver
- approval date
- review or expiry date
- status

## Lifecycle

1. Identify the needed deviation.
2. Assess the risk and define compensating controls.
3. Record the exception.
4. Approve it before relying on it in production.
5. Review it by the stated date.
6. Close, renew, or replace it.

## Approval Rule

Exceptions require approval by:

- project owner
- technical lead

For higher-risk projects, the same people may serve both operational and approval roles only temporarily. As the organization matures, these should separate.

## Review Triggers

Exceptions must be reviewed early if:

- project risk increases
- scope materially changes
- an incident exposes the weakness
- a practical compliant path becomes available

