# Manual

Last Updated: 2026-08-31
Status: active
Owner: Technical Lead

## What This Project Is

Describe the project in operator-friendly terms.

## How To Work In This Repo

For ordinary scoped work, start lean:

1. Check `git status --short`.
2. Read `START_HERE.md` and the short repo-local agent instructions.
3. Use `docs/context-map.md` to choose only the docs and source areas needed for the task.
4. Review `docs/current-build-pathway.md` for the active chunk, completion target, stop condition, and validation expectations.
5. Run task-relevant validation.

For material or risk-triggering work, add the full governance path:

1. Review `docs/standards/README.md`.
2. Review `docs/standards/engineering-governance-by-use-case.md`.
3. Review `docs/policy/durable-development-engineering-policy.md`.
4. Review `docs/standards/ship-ready-engineering-standard.md`.
5. Run `bash scripts/governance-preflight.sh`.
6. Review `project-control.yaml`.
7. Capture a timestamp with `date -Iseconds`.
8. Confirm the current roadmap and runbook still match reality.
9. Update docs when behavior or operating expectations change.

## Ongoing Quality And Alignment Controls

- Treat cyclomatic complexity as a review signal: 1–10 receives ordinary review, 11–20 prompts design and branch-test review, and 21+ requires a coherent refactor or documented exception by default. Do not create shallow wrappers just to lower a score.
- At material planning or release readiness, check `governance_alignment.last_reviewed` in `project-control.yaml`. If it is absent or more than 90 days old, prompt for a bounded review of relevant updates from the governance source.
- Review governance updates before applying them. Never silently replace the project's risk tier, governance level, exceptions, or owner decisions.

## Expected Outputs

- working code or deliverables
- current operational documentation
- a maintained roadmap
- timestamped build pathway updates for material work
- scoped context and budget notes for meaningful chunks
- reviewable governance records

## Operator Notes

Capture practical operating tips, common gotchas, and handoff guidance.
