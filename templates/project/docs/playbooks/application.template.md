# Build Playbook: Application

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/application.template.md`

Read this before you design, build, or verify a feature in this project. It adds
application-specific rules to `AGENTS.md`; where the two conflict, `AGENTS.md`
and `project-control.yaml` win.

## Done looks like

- The changed flow works end to end in the running app: start it, drive the
  flow in a browser (Playwright or the project's equivalent), include the
  unhappy path, and keep the command output or screenshot as evidence. Passing
  unit tests alone do not show that a flow works.
- Acceptance criteria come from the chunk the owner approved. Do not invent,
  narrow, or loosen them.

## Before you build

1. Confirm the data model, which roles exist, and who may read or change each
   record.
2. Find the existing patterns for authentication, data access, validation, and
   error handling, and reuse them.
3. Plan the change as one vertical slice, from UI to storage, with its test.

## Build rules

- Check authorization on the server for every read and write, per record. A
  client-side check is a convenience, never a control.
- Give every table the client can reach row-level security or an equivalent
  server-side rule.
- Validate input at the boundary with a schema and return errors the user can
  act on. Do not swallow exceptions.
- Search before adding a helper, and do not leave placeholder or duplicate
  implementations behind.
- Keep service keys and secrets on the server, out of client bundles, logs, and
  screenshots.
- Database migrations are reviewed files. An agent never runs a migration
  against production.

## Verify

- Run the unit and integration tests, then the app, then the browser flow.
- Test the cases agents skip: a second user who must not see the first user's
  data, bad input, an expired session, and a slow or failed dependency.
- Read the application logs from the run for errors and warnings.

## Failure modes agents produce here

- Logic errors that pass happy-path tests.
- Tests edited or deleted until they pass. This project forbids that.
- Missing per-record authorization (one user reads another's data by changing
  an ID).
- A backend-as-a-service database exposed to the client without row-level
  security.
- Packages that do not exist, or that are not the package you meant.
  Confirm a package's registry page, maintainer, and download history before
  adding it, and commit the lockfile.

## Security

- Apply the OWASP basics to every new endpoint: injection, authentication,
  access control, and sensitive-data exposure.
- Rate-limit authentication and any expensive or AI-backed endpoint.
- Keep dependencies locked and updated deliberately.

## Where a System One model fits

Use a typed-judgment model where the app needs common sense rather than text:
routing a request to the right queue, moderation, triage, scoring, or checking
that a support reply matches the policy. Jev (TypeSafe, hosted) works
zero-shot; call it from the server only, keep its key out of the client, and
set thresholds on your own data. Laya (open weights, local) needs fine-tuning
and a held-out evaluation first, and fits only when data must stay on the
machine. Confidence never grants permission.

## Stop and ask

- Schema migrations on shared data, changes to authentication or permissions,
  payments, or anything that touches production data.
