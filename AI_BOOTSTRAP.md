# AI Bootstrap Rules

This is the canonical agent-instruction file for this repository, for Claude, Codex, and local coding agents alike. `CLAUDE.md` and `AGENTS.md` are short routers into this file.

This repository is the governance source for all projects on this machine. It is not an application project and not a build target. Use `templates/project/` to scaffold new projects and `automation/` scripts to bootstrap and validate governed projects.

## Startup

- For ordinary scoped work: run `git status --short`, read the repo-local instruction file, then only the specific files or errors relevant to the task.
- Use `docs/context-map.md` when deciding which docs, standards, or source areas to load.
- Keep startup lean: do not turn heavy standards, Graphify, plugins, or MCP servers into an automatic startup chain for small edits. Trigger them by task risk or scope.
- After a compaction, context clear, or restart: resume from the latest handoff or work packet, run `git status --short`, and open only the active plan and files needed for the next objective.

## Governance Triggers

For material or risk-triggering work, unclear scope, handoffs, or changes that affect the active plan:

1. Read `START_HERE.md` and follow the active plan named there (default `docs/current-build-pathway.md`).
2. Run the preflight: `bash scripts/governance-preflight.sh` here, or `bash automation/governance_check.sh /path/to/project` for a governed project.
3. Use `docs/standards/README.md` as the standards map. Review `docs/policy/durable-development-engineering-policy.md` before meaningful implementation and `docs/standards/ship-ready-engineering-standard.md` before declaring meaningful work complete.
4. Review `project-control.yaml`, confirm the work matches `use_case.primary`, and capture a timestamp with `date -Iseconds`.

Risk-triggering work includes: production, deployment, authentication, authorization, payments, secrets, sensitive data, database migrations, customer communications, external side effects, infrastructure or provider settings, destructive or autonomous actions, risk classification, governance policy changes, or release readiness.

- Do not override the selected `risk_tier` or `governance_level`; changes require an explicit owner decision (see `docs/standards/governance-level-standard.md`).
- Do not modify standards or templates without explicit instruction.
- Record deviations as exceptions; do not silently ignore missing governance files.
- Escalate if a request increases risk, autonomy, money handling, or sensitive data exposure.

## Completion And Stopping

- Work in context-window-friendly chunks: one objective, clear input and output files, explicit validation.
- Use bounded completion labels: `Draft complete`, `Task complete`, `Integration complete`, `Release ready`, or `Blocked`. Project completion is a human decision.
- Stop when the chunk's definition of done is met, its stop condition is reached, or repeated attempts stop producing new evidence.
- A task is not complete until relevant validation is run or a blocker is clearly stated. "Works locally" is not complete.

## Chunk Close-Out Protocol

At the end of every chunk of work:

1. Check `CARRY_FORWARD.md` — if it has open items, surface them to the user before proceeding. If open flags must survive the context reset, read them aloud and wait for confirmation.
2. Stage the relevant files, commit with a clear message, and push. Do this automatically — do not ask unless a carry-forward flag or blocker requires a decision first.
3. Confirm the push succeeded, then suggest `/compact`. Do not suggest `/clear` — compact preserves the summary of what was done, which is cheaper to resume from than a cold start.
4. `/clear` is an explicit user override only: use it when prior context had persistent wrong assumptions, or the next chunk is in a completely unrelated domain.
5. Do not auto-compact. Do not skip the commit step without flagging why.

A chunk ends when the definition-of-done in the active plan is met, a stop condition is reached (blocker, repeated failure, scope boundary), or the user signals done.

## Fundamentals First

- Build the smallest useful thing in the safest durable way. AI speed does not make bad code cheap.
- Reach shared understanding before meaningful coding; use consistent domain language; prefer deep modules with simple interfaces; implement in small vertical slices paced by feedback loops (types, tests, linting, runtime checks).
- Avoid pass-through layers, premature abstractions, swallowed errors, duplicated business rules, and fake validation claims.
- When you see weak design, flag it and propose the smallest safe improvement instead of rewriting the project.

## Context Hygiene

Essentials (full standard: `docs/standards/context-hygiene-standard.md`):

- Keep active context minimal, relevant, current, and recoverable. Narrow file scope before reading; prefer targeted diffs over whole-repo exploration.
- Summarize at phase boundaries; compact before quality degrades; re-state critical constraints after compaction.
- The repository remembers, agents rent context: keep work packets, validation notes, and handoffs durable enough that the next agent does not need the chat thread. Keep read-only scout outputs summary-only.

## Graphify

- Before broad source exploration, architecture analysis, dependency tracing, or cross-repo planning, query the existing graph first (`graphify query/path/explain`); use the workspace graph in the Graphify tool repo for cross-repo routing. For known files, small scoped edits, or build/test errors, use normal repo inspection.
- After code changes, run the cheap incremental `graphify update . --no-cluster`. Never trigger a full `/graphify` rebuild to answer a question or at session start — a full semantic pass is a deliberate, once-per-major-change act.
- Full governance policy: `docs/agent-governance.md` in the Graphify tool repo.

## Secrets

Do not index, print, summarize, or commit secrets or environment files.

## Change Rules

- Prefer editing existing files over creating duplicates; keep changes small and reversible; explain new dependencies before adding them.
- Update docs when behavior, interfaces, or architecture change; if code behavior changes, update the nearest controlled document in the same task.

## Commands

- Install: runtime uses stdlib only; GUI requires tkinter (bundled with the python.org installer). The validation gate needs dev tools: `python3 -m pip install ruff mypy coverage`.
- Dev:     `python3 automation/new_build_gui.py`
- Lint:    `bash scripts/validate.sh` (ruff + mypy + shellcheck + secret scan + tests — the one binary gate, identical in CI)
- Build:   _no build step — scripts run directly_
- Test:    `python3 -m unittest discover -s tests -p 'test_*.py'`
- Coverage: `python3 -m coverage run --source=automation -m unittest discover -s tests -p 'test_*.py' && python3 -m coverage report`
