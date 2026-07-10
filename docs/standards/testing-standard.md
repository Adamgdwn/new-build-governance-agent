# Testing Standard

Document ID: STD-ENG-021
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This standard defines minimum testing expectations across project types.

## Principles

- Every project must have an intentional test strategy.
- Testing should be strong enough to reduce release risk without becoming ceremonial.
- Higher-risk systems require stronger evidence.

## Minimum Expectations By Risk

### Low

- basic validation appropriate to the artifact
- linting or static checks where applicable
- manual verification steps documented if automated tests are not justified

### Medium

- automated tests for core logic where applicable
- documented regression checks
- deployment validation steps

### High

- automated tests across critical flows
- integration testing for key dependencies
- release-blocking checks in CI

### Critical

- strong automated coverage for business-critical flows
- pre-release validation in production-like conditions
- negative-path and failure-mode testing
- explicit sign-off before production deployment

## Project-Type Guidance

### Applications and APIs

Should include a combination of:

- unit tests
- integration tests
- end-to-end or journey tests for critical flows

### Websites

Should include:

- build validation
- content and link checks where practical
- form or conversion-path validation if applicable

### Scripts and Automations

Should include:

- safe dry-run behavior where possible
- idempotency validation for repeatable tasks
- failure-mode handling tests for impactful automations

### AI Agents

Should include:

- deterministic prompt and policy checks where possible
- evaluation sets for key tasks
- tool-use safety tests
- regression evaluation after model or prompt changes

## Allowed Exceptions

If a project has limited automation, the gap must be justified and paired with compensating controls such as:

- documented manual test scripts
- smaller release scope
- stronger review gates

