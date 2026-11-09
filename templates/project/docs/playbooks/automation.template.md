# Build Playbook: Automation

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/automation.template.md`

Read this before you design, build, or verify a workflow in this project. It
adds automation-specific rules to `AGENTS.md`; where the two conflict,
`AGENTS.md` and `project-control.yaml` win. These rules apply to scheduled
jobs, scripts, and workflow tools such as n8n alike.

## Done looks like

- A dry run on representative input shows exactly the actions the workflow
  would take.
- A real run against a test or staging target succeeds.
- Running it again with the same input creates no duplicate side effects.
- A failure reaches a person (an alert or a message), not just a log file.

## Before you build

1. List every trigger, every credential, and every outbound action.
2. Check for the lethal trifecta: untrusted input, private data, and an
   outbound action in the same workflow. If all three are present, add a human
   approval step or split the workflow.

## Build rules

- Authenticate every trigger. Do not expose public webhooks without
  authentication.
- Give each workflow its own credentials, scoped to what it needs.
- Deduplicate with idempotency keys so retries and replays are safe. After a
  timeout, check whether the action already happened before retrying it.
- Use bounded retries with backoff, a timeout on every step, and a place where
  failed items wait for review.
- Respect the rate limits of every service the workflow calls.
- Disable code-execution and shell nodes unless the workflow needs them.
- Keep the workflow platform patched; its own vulnerabilities expose every
  stored credential.
- Store times in UTC and convert only for display.

## Verify

- Dry run, staged real run, and duplicate re-run, as above.
- Feed it malformed, empty, and adversarial input, such as a message that
  contains instructions.

## Failure modes agents produce here

- Duplicate emails, messages, or records when a step retries.
- Workflows that combine an open trigger, stored credentials, and outbound
  messages.
- Silent failures that nobody notices for weeks.
- Time-zone and schedule drift bugs.

## Security

- Credentials stay in the platform's credential store, never in workflow
  definitions committed to git.
- Review each new connector or community node before installing it.

## Where a System One model fits

Workflows often need a fast decision: which branch this item takes, whether a
message is a refund request, or how urgent it is. A typed-judgment model makes
that decision with a probability, so the workflow can act on confident cases
and route uncertain ones to a person. Jev (TypeSafe, hosted) works zero-shot.
Laya (open weights, local) suits private or offline workflows after
fine-tuning and a held-out evaluation. Confidence never grants permission.

## Stop and ask

- Sending messages to customers or the public, moving money, and deleting
  records.
