# Agent Instructions

This repository is the governance source for all projects on this machine.
It is not an application project.

## Normal Startup

For ordinary scoped work in a governed project:

1. Run `git status --short`.
2. Read the repo-local agent instructions.
3. Use `docs/context-map.md` when context routing is unclear.
4. Inspect the specific files, errors, or docs needed for the task.
5. Run targeted validation after the change.

Do not turn `START_HERE.md`, pathway docs, governance standards, Graphify, plugins, MCP servers, or provider tools into an automatic startup chain for every small edit.

## Governance Triggers

Before making material or risk-triggering code or configuration changes in any governed project:

1. Read `START_HERE.md`.
2. Review the active plan named in `START_HERE.md` (default `docs/current-build-pathway.md`).
3. Review `docs/standards/README.md` and `docs/standards/engineering-governance-by-use-case.md`.
4. Review `docs/policy/durable-development-engineering-policy.md`.
5. Review `docs/standards/ship-ready-engineering-standard.md`.
6. Run the governance check and review `project-control.yaml`.
7. Capture a timestamp with `date -Iseconds`.

Risk-triggering work: production, deployment, auth, payments, secrets, sensitive data, migrations, customer communications, external side effects, infrastructure or provider settings, destructive or autonomous actions, risk classification, governance policy changes, or release readiness.

## Required Preflight Command

When a governance trigger applies:

```bash
bash automation/governance_check.sh /path/to/project
```

If the target project does not yet contain governance files:

```bash
bash automation/bootstrap_project.sh /path/to/project <project-type>
```

## Agent Behavior Standards

- Build the smallest useful thing in the safest durable way.
- Confirm the requested work matches the project's `use_case.primary`.
- Do not override the selected `risk_tier` or `governance_level`.
- Record deviations as explicit exceptions; do not silently ignore missing governance files.
- Escalate if a request increases risk, autonomy, money handling, or sensitive data exposure.
- Work in context-window-friendly chunks with one objective, clear files, validation, and handoff notes.
- Define the target completion state: `Draft complete`, `Task complete`, `Integration complete`, `Release ready`, or `Blocked`.
- Project completion is a human decision.

For Fundamentals-First AI Coding, Context Hygiene, and Graphify Policy, see `CLAUDE.md`.

## Chunk Close-Out Protocol

1. Check `CARRY_FORWARD.md` — surface open items before proceeding.
2. Stage, commit, and push. Do this automatically unless a carry-forward flag requires a decision first.
3. Confirm the push succeeded, then suggest `/compact`.
4. Do not auto-compact. Do not skip the commit step without flagging why.

A chunk ends when: the definition-of-done in `docs/current-build-pathway.md` is met, a stop condition is reached, or the user signals done.

## Supported Project Types

- application
- website
- service
- internal-tool
- automation
- infrastructure
- documentation
- agent
