# Harness Governance

Document type: harness governance
Status: active
Profile: {{HARNESS_PROFILE}}
Topology: {{HARNESS_TOPOLOGY}}
Generated: {{GENERATED_AT}}

## Harness Intent

The builder described this harness as:

> {{HARNESS_DESCRIPTION}}

Refer to this intent when making architecture decisions, selecting models, or
reviewing whether a new AI participant belongs in this product.

## Profile: {{HARNESS_TOPOLOGY_LABEL}}

{{HARNESS_PROFILE_RULES}}

## Engineering Constraints

A coding agent starting work in this project should:

1. Read this file to understand the intended AI topology.
2. Confirm that `agent_controls.harness_profile` in `project-control.yaml`
   matches the intent above. Update it if the builder has since revised scope.
3. Apply `docs/standards/engineering-governance-by-use-case.md` to any
   AI-participant design decisions.
4. Record new AI participants in `docs/agent-inventory.md` before integrating
   them.
5. Record model choices in `docs/model-registry.md` before calling them.
6. Record prompt templates in `docs/prompt-register.md`.
7. Record tool or API permissions in `docs/tool-permission-matrix.md`.

## Open Governance Questions

Replace these placeholders with answers before writing the first AI call:

- What does a successful harness outcome look like?
- What is the failure mode that governance must prevent?
- Which participant(s) can take external actions (write, send, deploy)?
- What is the human review point before any external action?
- How are model outputs validated before they affect state?
