# Build Playbook: Backend Service

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/service.template.md`

Read this before you design, build, or verify an endpoint or integration in
this project. It adds service-specific rules to `AGENTS.md`; where the two
conflict, `AGENTS.md` and `project-control.yaml` win.

## Done looks like

- Contract tests against the API's schema (OpenAPI or the project's
  equivalent) pass.
- The service runs locally and the changed endpoint answers real requests,
  including unauthorized, malformed, and oversized ones.
- Timeouts, retries, and failures of each dependency are handled and logged.

## Before you build

1. Write or update the contract first: request and response schemas, errors,
   and who may call the endpoint.
2. Find the existing patterns for authentication, data access, logging, and
   outbound calls, and reuse them.

## Build rules

- Authenticate every endpoint, and authorize each request per object, not
  just per route.
- Make writes that may be retried idempotent (an idempotency key or a natural
  unique key).
- Give every outbound call a timeout and bounded retries with backoff.
- Bound resource use: paginate lists, cap payload sizes, and rate-limit
  expensive endpoints.
- Never pass model output, or any other untrusted text, into SQL, a shell, a
  template engine, or `eval`. Use parameterized queries and validate against a
  schema.
- Log in a structured format, and keep secrets and personal data out of logs.
  Escape user-controlled values so log lines cannot be forged.
- Database migrations are reviewed files. An agent never runs a migration
  against production.

## Verify

- Run contract and integration tests, using real dependencies in containers
  where practical.
- Give coding agents read-only access to logs and metrics so they can debug
  without changing anything.

## Failure modes agents produce here

- Insecure direct object references: the route checks login, not ownership.
- Retries that create duplicate records or charges.
- Model output reaching a query or a shell.
- Unbounded queries and payloads.
- Log injection.

## Security

- Least-privilege service credentials, one set per service.
- Dependencies locked; confirm a new package exists and is the one you meant.

## Where a System One model fits

Use a typed-judgment model to route or triage inbound messages, webhooks, or
tickets, and to check extracted fields against their source before a write. A
good shape is: a cheap extractor proposes values, Jev checks each one, and
only failed checks escalate to a person or a reasoning model. Laya (open
weights, local) fits only when data must stay on the machine, after
fine-tuning and a held-out evaluation. Confidence never grants permission.

## Stop and ask

- Breaking API changes, data migrations, new external integrations, and new
  credentials.
