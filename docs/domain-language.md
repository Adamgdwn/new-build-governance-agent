# Domain Language

Last Updated: 2026-07-10
Status: active
Owner: Technical Lead
Document type: shared vocabulary
Audience: project owner, builders, AI coding agents, reviewers, and operators
Purpose: define the terms used consistently across code, docs, tests, UI, prompts, runbooks, and release notes.

## Purpose

This file defines the shared vocabulary for the project.

Important domain terms should be named consistently across labels, database tables, functions, services, tests, docs, prompts, and runbooks.

When a term changes, update this file and the affected code or documentation in the same chunk where practical.

## Terms

| Term | Meaning | Avoid Saying | Code/Docs Usage |
|---|---|---|---|
| New Build Governance Agent | The governance framework and tooling in this repository. | freedom tool, governance helper, scaffolder only | Product name, README, release notes, launcher labels. |
| governed project | A project that has this framework's baseline files, `project-control.yaml`, required docs, and validation scripts. | repo, thing, generated app | Docs, automation messages, user guide. |
| project-control.yaml | The source of truth for project type, use case, risk tier, governance level, owner, and required controls. | config file, yaml, settings | Governance checks, scaffold output, user guide. |
| risk_tier | The selected risk tier recorded in `project-control.yaml`. | detected risk, severity | Governance docs and compliance output. |
| governance_level | The selected 0-4 governance level recorded in `project-control.yaml`. | mode, strictness, maturity | Intake, project control, validation reports. |
| use_case.primary | The primary use-case classification recorded in `project-control.yaml`. | project kind, category only | Use-case governance, intake, scaffolded control docs. |
| build chunk | A small, reviewable unit of work with one objective, clear files, validation, and handoff notes. | task blob, phase, batch | `docs/current-build-pathway.md`. |
| pathway | The current build route and handoff record in `docs/current-build-pathway.md`. | plan doc, notes | Agent instructions and user guide. |
| required gap | A missing control required by the selected governance level or project policy. | warning, nice-to-have | Governance and compliance output. |
| recommended improvement | A suggested control or quality improvement based on use case, design quality, or risk signals. | required gap | Advisory output and owner review notes. |
| accepted exception | A documented, approved deviation with rationale, compensating control, and review point. | ignored gap, skipped rule | Exception records and validation notes. |

## Naming Guidance

Use domain-specific names. A name should explain the responsibility it owns.

Challenge vague names when they hide unclear responsibility:

- `manager`
- `helper`
- `utils`
- `thing`
- `stuff`
- `data`
- `processor`
- `handler`
- `misc`
- `temp`
- `common`
- `general`

Prefer names that point to the actual domain concept, boundary, or behavior.

## Agent Guidance

When terminology is vague or inconsistent, the agent should:

1. Flag the naming issue.
2. Explain the risk to comprehension, tests, prompts, or future changes.
3. Recommend the smallest safe naming improvement.
4. Keep related code, docs, tests, UI, and prompts aligned when the owner accepts the change.

Do not rename broadly just for style. Improve names when the change fits the active chunk or the owner approves the refactor.
