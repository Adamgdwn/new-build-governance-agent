# Build Playbook: Infrastructure

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/infrastructure.template.md`

Read this before you change infrastructure or deployment code in this project.
It adds infrastructure rules to `AGENTS.md`; where the two conflict,
`AGENTS.md` and `project-control.yaml` win.

## Done looks like

- The `plan` or diff is saved and a person has reviewed it.
- Format, validation, lint, and policy-as-code checks pass.
- The change was applied to a non-production environment first.
- The rollback or restore path was exercised, not just written down.

## Before you build

1. Confirm which environments and accounts the change touches.
2. Confirm that remote state is in use, locked, and current.

## Build rules

- An agent never runs apply or destroy against production or shared
  environments. It prepares the plan; a person applies it.
- Turn on deletion protection for stateful resources, and keep backups outside
  the stack that manages them.
- Grant least-privilege IAM. Wildcard permissions or open ingress
  (`0.0.0.0/0`) need a recorded exception.
- Pin provider and module versions.
- Keep secrets in a secret manager, never in variables files, state, or code.
- Keep changes small enough to review in one sitting.
- Detect drift before changing a resource that might have been edited by hand.

## Verify

- Save the plan output and read every change, delete, and replace line.
- Run the security scanner, then review what it reports. A change made only to
  satisfy a scanner is not a fix.

## Failure modes agents produce here

- Destroying resources because the state file was stale or the wrong
  workspace was selected.
- Broad IAM roles or open security groups. These pass `plan` because `plan`
  checks syntax and effect, not intent.
- Fixes that silence a scanner without removing the risk.
- Hard-coded secrets and unpinned modules.

## Security

- Use separate credentials per environment, and keep production credentials
  out of agent sessions entirely.
- Policy-as-code is the control; prose rules such as "do not touch
  production" are not.

## Where a System One model fits

A typed-judgment model can add a tripwire on top of deterministic policy, for
example a yes/no check on whether a plan deletes or replaces a stateful
resource, so the review highlights it. It never replaces policy checks or human
review. Jev (TypeSafe, hosted) works zero-shot; Laya (open weights, local)
needs fine-tuning and a held-out evaluation first.

## Stop and ask

- Every apply to a shared or production environment, DNS changes, IAM
  changes, and anything that raises recurring cost.
