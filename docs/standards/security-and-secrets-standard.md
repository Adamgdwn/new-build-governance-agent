# Security and Secrets Standard

Document ID: STD-ENG-019
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This standard defines baseline controls for secrets, sensitive data, and secure delivery.

## Principles

- Sensitive access must be intentional, minimal, and reviewable.
- Secrets must never be embedded in source control.
- Data handling controls must scale with sensitivity and risk.

## Required Controls

Every project must address:

- secret storage and rotation method
- environment segregation
- least-privilege access
- dependency management
- logging and sensitive data exposure rules
- backup and recovery expectations where applicable

## Secrets Rules

- Secrets must be stored in approved secret managers or protected environment systems.
- Example placeholder files such as `.env.example` may be committed, but not real secret values.
- Production credentials must not be shared through chat, code comments, or untracked local files intended for long-term use.
- Control-plane credentials and project runtime credentials must be tracked as
  separate classes of secret.
- Control-plane credentials grant automation the ability to create or modify
  provider-side resources, such as Supabase projects, Vercel projects and env
  vars, Stripe products and webhooks, or Resend domains. These credentials must
  have the narrowest practical scope and explicit approval before use.
- Project runtime credentials are generated for one application or environment,
  such as API URLs, publishable keys, service-role keys, database URLs, and
  webhook signing secrets. These values must be synced only into projects that
  require them.
- Local automation may read from a private master env file only when the workflow is
  governed, redacted, and scoped to the target project.
- Project env sync must copy only required keys, preserve existing project values by
  default, and require an explicit privileged flag before copying service-role keys,
  database URLs, access tokens, webhook secrets, or similar admin credentials.
- Provider provisioning must record the generated project identifiers and runtime
  credentials back into the private master env or an approved secret manager,
  then create a redacted governance record of what changed.
- Stripe provisioning must be manifest-driven, test-mode-first, and approved
  before live mode. Prefer restricted API keys for automation. Full secret keys
  should be reserved for tasks that cannot be completed with a restricted key.
- Generated real env files must be excluded from source control and permissioned for
  the local owner only.

## Sensitive Data Rules

Projects that handle money, personal data, or privileged business data must define:

- data categories handled
- where data is stored
- retention expectations
- masking or redaction needs
- access boundaries

## Secure Delivery Expectations

At medium risk and above, projects should include:

- secret scanning
- dependency vulnerability review
- access review for deployment credentials

At high risk and above, projects should also include:

- explicit security review during project setup
- documented incident response contact or owner

At critical risk, projects should also include:

- stronger approval controls for privileged changes
- periodic review of permissions and integrations
