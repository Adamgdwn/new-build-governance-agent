# Engineering Governance Policy

Document ID: POL-ENG-001
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This policy establishes the default governance model for software, automation, infrastructure, and AI systems developed under this framework.

The policy exists to ensure:

- consistent build quality
- controlled risk
- traceable decisions
- secure handling of sensitive information
- repeatable deployment and operational practices

## Policy Statement

All projects shall follow the standards in this repository by default.

All meaningful software changes shall also follow [Durable Development Engineering Policy](durable-development-engineering-policy.md). That policy is the default code engineering standard for implementation quality, testing, review, security, deployment, observability, documentation, and AI-assisted development.

Projects shall use [Engineering Governance By Use Case](../standards/engineering-governance-by-use-case.md) to choose appropriate controls for the project type. Use-case guidance informs implementation controls, but `risk_tier` and `governance_level` in `project-control.yaml` remain the source of truth unless explicitly changed.

Projects shall use [Ship-Ready Engineering Standard](../standards/ship-ready-engineering-standard.md) before declaring meaningful work complete. That standard separates Definition of Ready, Definition of Done, and Definition of Shipped so good code becomes a verified product increment with evidence.

Projects may deviate from a standard only when:

- the deviation is justified by project context, risk, or technical constraint
- the deviation is documented in an approved exception record
- compensating controls are defined where needed
- the exception has a review date

## Governance Principles

- Production-grade mindset from the start.
- Controls scaled by risk.
- Consistency preferred over novelty.
- Documentation should support action, not bureaucracy.
- Automation should enforce what can be checked reliably.
- Human review remains mandatory for exceptions, high-risk decisions, and production releases of sensitive systems.

## Scope

This policy applies to:

- web applications
- backend services and APIs
- internal tools
- public websites
- AI agents
- scripts and automations
- infrastructure and deployment code
- documentation-focused repositories
- mono-repositories containing any of the above

## Accountability

Each project must have, at minimum:

- a project owner
- a technical lead

The same person may hold both roles temporarily, but both responsibilities must still be covered.

## Mandatory Control Areas

Each project must address:

- naming and repository structure
- required documentation
- risk classification
- testing strategy
- durable development engineering policy
- security and secrets handling
- deployment and release controls
- operations and support readiness
- exception management

Agent-based systems must also address:

- model and prompt traceability
- tool permission boundaries
- evaluation coverage
- human oversight rules
- rollback and incident handling

## Exceptions

Exceptions are permitted, not ignored.

Any exception must include:

- what standard is being deviated from
- why the deviation is needed
- what risk it creates
- what compensating controls exist
- who approved it
- when it must be reviewed

## Enforcement

Enforcement should be layered:

1. policy and standards
2. templates and checklists
3. CI and repository validation
4. release approval workflow
5. optional agent-based governance

## Review Cadence

This policy should be reviewed at least annually or after any major incident, regulatory change, or material shift in operating model.
