# Carry-Forward Flags

Last Updated: 2026-11-10
Status: open items present

Closed, 2026-11-10 (owner decision): the 2026-11-08 revision set is implemented, and AUD-ENG-015 is a record only, with its recommendations not adopted. No chunk is queued. The `env_sync` writer fix stays written up as Chunk Fifty-Three at `docs/current-build-pathway.md:57-91`, to run only if the owner asks for it.

Keep this file short: one or two lines per flag, pointing to where the detail lives. Refresh the next-chunk line at every close-out. Clear a flag when it is resolved or handed off.

| Flag | Added | Last Reviewed | Owner | Status | Notes |
|---|---|---|---|---|---|
| Audit Tier 2/3 backlog open | 2026-07-10 | 2026-11-10 | Project Owner | open | Open in `docs/audits/remediation-backlog-2026-07-10.md` (next review 2026-12-08): the rest of B-6, B-7 to B-12, the rest of B-13, B-15, and the Tier 1 residuals. B-8 needs an owner decision on this repository's risk tier. Since Chunk Forty-Seven, secret env writes stop when the file cannot be restricted (FAT, exFAT, some network drives); how to reverse that is in the pathway's Chunk Forty-Seven section. |
| GitHub standard distribution gaps | 2026-07-26 | 2026-11-08 | Project Owner | open | STD-ENG-022 reaches only Claude Code (through the unversioned workspace `CLAUDE.md`) and new scaffolds. Not covered: existing repos, Codex sessions, the Linux machine, cloud agents, and the build playbooks. Its volatile product facts are unverified. Options and the `change_control.py` fallback: the standard's Distribution and Deferred Work sections. |
| AI Coding Practices knowledge base change proposal | 2026-11-08 | 2026-11-10 | Project Owner | open | Owner to approve, amend or reject P1 to P7 in `docs/proposals/2026-11-08 - AI Coding Practices Knowledge Base Change Proposal.md`. The knowledge base was not edited (owner decision 2026-11-08); approved items may need matching template edits here. AUD-ENG-015 found that their content already ships, while new projects are routed to the unchanged knowledge base for the same topics, so new projects get two answers until this is decided. |
| Build-to-sale standard distribution | 2026-09-30 | 2026-11-08 | Project Owner | open | STD-ENG-025 exists only as one canonical copy plus a workspace `CLAUDE.md` summary. Not done: scaffold templates (standards index, context map, pathway phase table), managed-upgrade blocks in `change_control.py`, a validated `project-control.yaml` lifecycle field (phase, last-reviewed date), and alignment reviews of projects intended for sale (GazeCut first). Owner sets scope and order. |
