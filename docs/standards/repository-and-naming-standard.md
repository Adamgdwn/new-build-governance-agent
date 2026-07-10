# Repository and Naming Standard

Document ID: STD-ENG-017
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This standard defines naming conventions and repository structure expectations for consistency across project types.

## Naming Principles

- Names must be understandable, concise, and durable.
- Consistency is preferred, but naming may vary by artifact type when there is a good reason.
- Abbreviations should be avoided unless they are widely understood.

## Default Naming Conventions

### Repository Names

Use a type-appropriate convention:

- application and website repositories: `kebab-case`
- service and API repositories: `kebab-case`
- infrastructure repositories: `kebab-case`
- documentation repositories: `kebab-case`
- script files: `snake_case` or `kebab-case`, chosen once per repository
- environment variables: `UPPER_SNAKE_CASE`
- code symbols: follow language conventions

Examples:

- `customer-portal`
- `billing-api`
- `marketing-site`
- `ops-automation`

### AI Agent Naming

Use human-readable role-oriented names in documentation, and stable machine-safe identifiers in code and config.

Examples:

- display name: `Deployment Governance Agent`
- identifier: `deployment-governance-agent`

## Required Top-Level Repository Structure

Every repository should include, where applicable:

- `README.md`
- `.gitignore`
- `docs/`
- `tests/` or type-appropriate test location
- `scripts/` for operational or helper scripts
- `.github/` or equivalent CI folder when automation exists

Each project must also contain or generate:

- `START_HERE.md`
- `project-control.yaml`
- `docs/current-build-pathway.md`
- `docs/policy/durable-development-engineering-policy.md`
- `docs/standards/README.md`
- `docs/standards/engineering-governance-by-use-case.md`
- `docs/standards/ship-ready-engineering-standard.md`
- `docs/standards/context-hygiene-standard.md`
- deployment and runbook documentation if deployable

## Preferred Common Layout

Use one common layout unless the technology stack strongly suggests otherwise.

Example:

```text
repo-name/
  README.md
  START_HERE.md
  project-control.yaml
  docs/
    architecture.md
    current-build-pathway.md
    policy/durable-development-engineering-policy.md
    standards/README.md
    standards/engineering-governance-by-use-case.md
    standards/ship-ready-engineering-standard.md
    standards/context-hygiene-standard.md
    deployment-guide.md
    runbook.md
    adr/
    risks/
  src/
  tests/
  scripts/
  .github/
```

## Permitted Deviations

Deviation from the preferred structure is acceptable when:

- the framework or platform has a dominant convention
- the repository is a monorepo
- the project type is documentation-only
- generated structure is imposed by a trusted vendor tool

Any significant deviation should be documented.

## Monorepo Handling

This section absorbs the retired Monorepo Standard.

Monorepos are supported when:

- the root defines shared governance controls
- each governed application or service has local ownership and documentation
- release boundaries are clear
- secrets and deployments are scoped to the correct subproject

The monorepo root should include a root `README.md`, a root `project-control.yaml`, shared standards or conventions, CI and enforcement configuration, and ownership boundaries.

Each independently deployable or governed subproject should include a local `README.md`, local documentation as needed, an explicit owner, a risk classification, and a release boundary.

Preferred structure:

```text
monorepo/
  README.md
  project-control.yaml
  apps/
    customer-portal/
    marketing-site/
  services/
    billing-api/
  agents/
    deployment-governance-agent/
  packages/
  docs/
```

Control rules:

- Shared controls may be centralized.
- Risk and release decisions must remain traceable per governed subproject.
- A high-risk subproject may require stronger controls than the rest of the monorepo.
