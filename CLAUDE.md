# Claude project instructions

This repository is the governance source for all projects on this machine.
It is not an application project and not a build target.

`AI_BOOTSTRAP.md` is the canonical agent-instruction file. This file holds only
the always-on session rules; when they conflict, `AI_BOOTSTRAP.md` wins.

Always-on rules:

- For ordinary scoped work, start with `git status --short`, this file, and the specific files or errors relevant to the task.
- For material or risk-triggering work, unclear scope, handoffs, or changes that affect the active plan: read `START_HERE.md` and follow `AI_BOOTSTRAP.md`.
- Use `docs/context-map.md` when deciding which docs, standards, or source areas to load, and `docs/standards/README.md` as the standards map.
- Keep startup lean: trigger heavy governance, Graphify, plugin, MCP, and release checks by task risk or scope, not on every edit.
- Use bounded completion labels: `Draft complete`, `Task complete`, `Integration complete`, `Release ready`, or `Blocked`. Project completion is a human decision.
- Stop when the current chunk's definition of done is met, when its stop condition is reached, or when repeated attempts stop producing new evidence.
- Build the smallest useful thing in the safest durable way, and do not treat "works locally" as complete.
- Do not override the selected `risk_tier` or `governance_level`.
- Do not modify standards or templates without explicit instruction.
- Do not index, print, summarize, or commit secrets or environment files.
- Use templates in `templates/project/` to scaffold new projects and scripts in `automation/` to bootstrap and validate governed projects.
- The canonical reading order is in `README.md` (Reading Order section).

## Chunk Close-Out Protocol

Follow the canonical 5-step protocol in `AI_BOOTSTRAP.md` (Chunk Close-Out
Protocol). In short: at the end of every chunk, check `CARRY_FORWARD.md` and
surface any open items first, then stage, commit, and push automatically,
confirm the push succeeded, and suggest `/compact` (not `/clear`). Do not
auto-compact, and do not skip the commit step without flagging why. A chunk
ends when the active plan's definition-of-done is met, a stop condition is
reached, or the user signals done.
