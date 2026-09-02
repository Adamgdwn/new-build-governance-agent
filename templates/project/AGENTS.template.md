# Agent Instructions

Last Updated: YYYY-MM-DD
Status: draft
Owner: Project Owner

Canonical instructions for Claude Code, Codex, and any other coding agent. `CLAUDE.md` imports this file. Keep it under 80 lines; put detail in `docs/` and link it. `AI_BOOTSTRAP.md` holds the project commands only.

## What this is

<Stack, production surface, and data or money boundaries in two or three sentences.> Risk tier and governance level are set in `project-control.yaml`; confirm the work matches `use_case.primary` and do not override the selected `risk_tier` or `governance_level`. Product and data boundaries: `docs/context-map.md`.

## Start

1. `git status --short` (lean startup). Preserve changes from other sessions.
2. Active work is the active plan named by `START_HERE.md`, default `docs/current-build-pathway.md`. Take the first chunk with `Status: Ready`, one chunk per session. Read only the files that chunk names and what they import.
3. `START_HERE.md` is orientation only. `CARRY_FORWARD.md` lists open items only. `docs/context-map.md` routes everything else. The repository remembers. Agents rent context.
4. Unattended execution, when the runner is installed: `node scripts/agent/run-chunks.mjs`.

## Commands

- `AI_BOOTSTRAP.md` lists install, dev, lint, typecheck, test, and build commands one per line.
- Governance preflight: `bash scripts/governance-preflight.sh`. Required before risk-triggering work: production, deployment, authentication, authorization, payments, secrets, sensitive data, database migrations, customer communications, external side effects, infrastructure or provider settings, destructive actions, autonomous tool use, risk classification, governance policy changes, or release readiness. Proceed only after preflight passes or every gap is accepted as a recorded exception.
- Capture a timestamp with `date -Iseconds` for material work, decisions, validation, and handoffs.

## Rules

A rule that a hook enforces names the hook. Hooks live in `scripts/agent/hooks/` when the runner is installed; until then the rule is still the rule.

- Never modify or delete an existing test file. New test files are fine when the chunk asks for them. If validation fails, fix the code. (hook: guard-protected-paths)
- `docs/standards/`, `docs/policy/`, `project-control.yaml`, database migrations, and `.env*` are read-only unless the chunk lists them under `Files:`. (hook: guard-protected-paths)
- A chunk is not finished until its Validation commands pass. (hook: stop-validate)
- Owner authorization first for: <new payment surfaces, new data stores, tool-using AI, customer-facing messaging, and anything else the owner names here>.
- Secrets: do not index, print, summarize, or commit secrets or environment files, and never log or screenshot secret values. Variable names live in `.env.example`.
- Stage only the chunk's files. Commit as `P-NN: title`. Push when the chunk is ready to share and no `CARRY_FORWARD.md` flag needs a decision first.
- `docs/standards/README.md` is the standards map. Read `docs/policy/durable-development-engineering-policy.md` before meaningful implementation: build the smallest useful thing in the safest durable way, and treat "works locally" as incomplete until validation, security and privacy impact, documentation, and rollback are addressed.
- Fundamentals-First AI Coding: AI speed does not make bad code cheap. Reach shared understanding first, use consistent domain language, prefer deep modules with simple interfaces, let types, tests, linting, and runtime checks set the pace, and flag weak design with the smallest safe improvement rather than a rewrite.
- Complexity is a review signal, not a verdict: in changed code, 11-20 prompts a design and branch-test look, 21+ needs a coherent refactor or a recorded exception. Do not add shallow wrappers to lower a score. See `docs/standards/code-complexity-control-standard.md`.
- Periodic governance alignment: at material planning or release-readiness work, if the last alignment date is absent or more than 90 days old, prompt for a bounded comparison with the governance source and preserve local controls and owner decisions. This is not an ordinary-startup requirement. See `docs/standards/governance-source-alignment-standard.md`.
- Context Hygiene: narrow file scope before reading, prefer targeted diffs over whole-repo exploration, keep scout outputs summary-only, and use `docs/standards/context-hygiene-standard.md` for long sessions and handoffs. After a compaction, context clear, or fresh restart, resume from the pathway and `CARRY_FORWARD.md`, then `git status --short`.
- Completion labels are bounded: `Draft complete`, `Task complete`, `Integration complete`, `Release ready`, or `Blocked`. Project completion is a human decision. Do not declare meaningful work complete without the evidence `docs/standards/ship-ready-engineering-standard.md` asks for.
- Stop when the chunk's definition of done is met, when its stop condition is reached, or when repeated attempts stop producing new evidence; project completion is a human decision, so report the bounded state and stop.

## Finish a chunk

1. Validation green: the chunk's Validation commands, or `node scripts/agent/validate.mjs` when the runner is installed.
2. In the pathway, inside that chunk only: tick met criteria, record Known gaps, set `Status: Review`. The runner or the owner sets `Done`.
3. Update `CARRY_FORWARD.md` only if an open item changed. Commit, then push per the rule above.
4. Start the next chunk in a fresh session (`/clear`), not `/compact`. The pathway and `CARRY_FORWARD.md` are the handoff. Compact only mid-chunk when context is degrading.

## Read when relevant

- `docs/context-map.md`: routing by task. `docs/architecture.md`, `docs/risks/risk-register.md`, and `docs/domain-language.md` when the task touches them.
- `docs/standards/README.md`: which standards apply and where the source text lives. `docs/standards/engineering-governance-by-use-case.md` is control guidance only, never a reason to change tier or level.
- Graphify Policy: an optional orientation tool, never a startup step. The canonical policy is `docs/agent-governance.md` in the installed Graphify tool repository. Query the repo-local graph before broad source exploration or architecture analysis; use `graphify global path` and `graphify global list` to find the configured global graph for cross-repo routing rather than hard-coding a provider or a user-specific filesystem layout. Use normal inspection for known files, build or test errors, small scoped edits, and routine docs checks. Set up a new repo with `graphify-setup-project /path/to/repo`; full semantic repo graphs come from `/graphify /path/to/repo` in Claude Code as a deliberate once-per-major-change act. Do not trigger a full `/graphify` rebuild to answer a question, at session start, or after a context clear. After code changes run `graphify update . --no-cluster`. Measure use before keeping any Graphify hooks.
