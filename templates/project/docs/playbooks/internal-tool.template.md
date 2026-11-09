# Build Playbook: Internal Tool

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/internal-tool.template.md`

Read this before you design, build, or verify a feature in this project. It adds
internal-tool rules to `AGENTS.md`; where the two conflict, `AGENTS.md` and
`project-control.yaml` win.

## Done looks like

- The tool runs end to end on representative input, and its output is checked
  against what was expected.
- At least one automated smoke test exists and passes.
- The README says how to run it, what it changes, and who owns it.

## Before you build

1. Confirm who will run the tool, on which machines, and with what access.
2. List what the tool reads and what it changes.

## Build rules

- Anything that changes data gets a dry-run mode that shows the changes first,
  and destructive actions ask for confirmation.
- Use least-privilege credentials: scoped tokens, never a shared admin account.
- Read secrets from the environment or a secret store, never from code or
  command-line arguments, where process listings expose them.
- Make re-runs safe: a second run should not duplicate the first run's effects.
- Handle partial failure, and report what succeeded and what did not.
- Log what the tool changed.

## Verify

- Run it on representative input, then with bad or empty input, then a second
  time to check that a re-run is safe.

## Failure modes agents produce here

- Secrets committed to the repository. Internal repositories leak more secrets
  than public ones because nobody expects them to be read.
- Service accounts with far more access than the tool needs.
- No owner and no tests, so the tool quietly rots.
- Paths and settings that only work on the author's machine.

## Security

- Scan for secrets before committing.
- Keep the tool's permissions to what its documented actions need.

## Where a System One model fits

A typed-judgment model can route requests, pick the intended value from
candidates your code has already found (for example with a regular
expression), or lint documents and configs against your conventions. Jev
(TypeSafe, hosted) works zero-shot; Laya (open weights, local) needs
fine-tuning and a held-out evaluation first.

## Stop and ask

- Access to production data, or permissions that cover the whole organization.
