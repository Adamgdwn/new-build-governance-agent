# Risk Classification Standard

Document ID: STD-ENG-018
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This standard defines the default risk model used to scale controls across projects.

## Risk Tiers

### Low

Typical examples:

- documentation-only repositories
- low-impact internal scripts
- prototypes with no production data and no external users

Minimum expectations:

- core documentation
- basic linting or validation where relevant
- backup or recovery plan if project state matters

### Medium

Typical examples:

- internal tools
- public websites with forms but no sensitive regulated data
- non-critical business automations

Additional expectations:

- defined test strategy
- staging or equivalent validation environment
- access and secret management controls
- release checklist before production changes

### High

Typical examples:

- customer-facing applications
- revenue-affecting systems
- API services with authenticated access
- agentic systems that can take impactful actions

Additional expectations:

- stronger test coverage and integration checks
- formal deployment guide and runbook
- incident handling path
- rollback procedure
- explicit approval before production release

### Critical

Typical examples:

- systems handling money movement
- systems processing sensitive personal data
- infrastructure or automation with broad privileged access
- agents capable of autonomous external actions with material risk

Additional expectations:

- separation of duties where feasible
- mandatory release approvals
- auditable change and deployment history
- stronger access controls
- mandatory security review
- disaster recovery expectations and recovery objectives

## Risk Factors

Risk tier should be assigned using the highest applicable factor:

- financial impact
- sensitive or regulated data exposure
- external customer impact
- operational blast radius
- privilege level
- degree of autonomy
- legal or contractual exposure
- recovery complexity

## Reclassification

Projects must be reclassified when:

- money flow is introduced
- sensitive data scope changes
- autonomous actions are added
- deployment targets or user populations materially expand
- the project becomes operationally critical

## Required Project Record

Each project should capture its risk classification in `project-control.yaml` and in project documentation.

