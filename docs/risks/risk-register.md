# Risk Register

Last reviewed: 2026-05-31T11:35:07-06:00
Status: active
Owner: Technical Lead

## Current Risk Classification

- Tier: high
- Owner: Adam Goodwin
- Governance level: 3
- Primary use case: AI agent with tools
- Secondary use case: Infrastructure / deployment code

## Key Risks

| ID | Risk | Likelihood | Impact | Controls | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | Placeholder or stale governance files create false confidence. | Medium | High | Required docs, current build pathway, standards audit, validation log. | Adam Goodwin | Active |
| R-002 | Existing-project upgrades accidentally overwrite user work. | Low | High | Copy-if-missing behavior, managed instruction blocks, manifest review before apply, post-apply governance check, second proposal idempotency check, and git status review. | Adam Goodwin | Controlled |
| R-003 | Use-case standard is interpreted as overriding selected risk. | Low | Medium | Explicit notes in standard, project-control, bootstrap guidance, and agent instructions. | Adam Goodwin | Controlled |
| R-004 | GitHub publish stages unrelated local changes. | Low | High | Require explicit file selection or explicit full-tree approval; block secret-like paths; record staged files in execution report. | Adam Goodwin | Controlled |
| R-005 | Privileged env values are copied or printed accidentally. | Low | Critical | Redacted plans, no secret printing, privileged flag for admin keys, `.env` ignored. | Adam Goodwin | Controlled |
| R-006 | Stripe provisioning affects live money-handling configuration unintentionally. | Low | Critical | Test-mode-first, `--allow-live` gate, manifest-driven plan, no secret printing. | Adam Goodwin | Controlled |
| R-007 | Agent/tool permissions drift from documented intent. | Medium | High | Tool permission matrix, agent inventory, prompt register, pathway updates for material changes. | Adam Goodwin | Active |
| R-008 | Declared machine enforcement exceeds actual tests/CI. | Low | High | Local validation script, focused tests, secret-hygiene coverage, and GitHub Actions validation workflow are committed. | Adam Goodwin | Controlled |
