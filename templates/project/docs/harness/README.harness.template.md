# Harness Governance

Document type: harness governance
Status: active
Profile: {{HARNESS_PROFILE}}
Topology: {{HARNESS_TOPOLOGY}}
Generated: {{GENERATED_AT}}

An agent is a model plus its harness: the loop, tools, context, memory,
permissions, and checks around the model. This file records this project's
harness decisions. `docs/build-playbook.md` holds the working instructions for
building and verifying it.

## Harness Intent

The builder described this harness as:

> {{HARNESS_DESCRIPTION}}

Refer to this intent when making architecture decisions, selecting models, or
reviewing whether a new AI participant belongs in this product.

## Profile: {{HARNESS_TOPOLOGY_LABEL}}

{{HARNESS_PROFILE_RULES}}

## Harness Decisions

Record each decision here, or in an ADR linked from here, before the first
model call:

| Decision | Choice | Why |
| --- | --- | --- |
| Build or adopt the harness (agent SDK, hosted agent runtime, or workflow tool) | | |
| Models and their effort settings (detail in `docs/model-registry.md`) | | |
| Tools and their permissions (detail in `docs/tool-permission-matrix.md`) | | |
| Where state lives between sessions (files, database, memory store) | | |
| Human gates before external actions | | |
| Evaluation set location and pass rule | | |
| Where traces are logged and who reads them | | |
| Caps on tokens, cost, retries, depth, and wall time | | |
| System One models used to route, screen, verify, or select context, if any | | |

## Engineering Constraints

A coding agent starting work in this project should:

1. Read this file and `docs/build-playbook.md` to understand the intended AI
   topology and how to build it.
2. Confirm that `agent_controls.harness_profile` in `project-control.yaml`
   matches the intent above. Update it if the builder has since revised scope.
3. Apply `docs/standards/engineering-governance-by-use-case.md`, including its
   Harness Engineering Controls, to any AI-participant design decision.
4. Record new AI participants in `docs/agent-inventory.md` before integrating
   them.
5. Record model choices in `docs/model-registry.md` before calling them.
6. Record prompt templates in `docs/prompt-register.md`.
7. Record tool or API permissions in `docs/tool-permission-matrix.md`.

## Open Governance Questions

Replace these placeholders with answers before writing the first AI call:

- What does a successful harness outcome look like, and which eval tasks show it?
- What is the failure mode that governance must prevent?
- Which participant(s) can take external actions (write, send, deploy)?
- Does any one session combine untrusted input, sensitive data, and an
  external action? If so, where is the human gate, or how is the work split?
- What is the human review point before any external action?
- How are model outputs validated before they affect state?
