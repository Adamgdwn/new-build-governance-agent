# Carry-Forward Flags

Last Updated: 2026-08-31
Status: open items present

Use this file to record anything that must survive a context reset:
blockers, unresolved decisions, open risks, next-chunk prerequisites.

Clear each item when it is resolved or handed off. If this file has open items,
the coding agent will surface them before suggesting /compact.

| Flag | Added | Last Reviewed | Owner | Status | Notes |
|---|---|---|---|---|---|
| Audit Tier 2/3 backlog open | 2026-07-10 | 2026-08-31 | Project Owner | open | Tier-1 fixes from AUD-ENG-003 are done; remaining recommendations and Tier-1 residuals are detailed in `docs/audits/remediation-backlog-2026-07-10.md` (AUD-ENG-004). B-14 portability remediation was completed in commit `5e68ca6`; select the next item from the backlog or record exceptions in a future chunk. |
| GitHub standard distribution gaps | 2026-07-26 | 2026-08-31 | Project Owner | open | Reviewed and still applicable. STD-ENG-022 reaches Claude Code through the unversioned workspace `CLAUDE.md` and new scaffolds through the bootstrap template. Existing repos, Codex sessions, the Linux machine, and cloud agents are not covered; the volatile product facts are unverified. Options and the `change_control.py` fallback are in the standard's Distribution and Deferred Work sections. |
