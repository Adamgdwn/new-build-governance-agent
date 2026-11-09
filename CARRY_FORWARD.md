# Carry-Forward Flags

Last Updated: 2026-11-09
Status: open items present

Next chunk: Chunk Forty-Eight (48), ready at `docs/current-build-pathway.md:57-95`. Start there. It lists the files to read, the gate and the stop condition.

Keep this file short: one or two lines per flag, pointing to where the detail lives. Refresh the next-chunk line at every close-out. Clear a flag when it is resolved or handed off.

| Flag | Added | Last Reviewed | Owner | Status | Notes |
|---|---|---|---|---|---|
| Audit Tier 2/3 backlog open | 2026-07-10 | 2026-11-08 | Project Owner | open | Open in `docs/audits/remediation-backlog-2026-07-10.md` (next review 2026-12-08): the rest of B-6, B-7 to B-12, the rest of B-13, B-15, and the Tier 1 residuals. B-8 needs an owner decision on this repository's risk tier. Since Chunk Forty-Seven, secret env writes stop when the file cannot be restricted (FAT, exFAT, some network drives); how to reverse that is in the pathway's Chunk Forty-Seven section. |
| GitHub standard distribution gaps | 2026-07-26 | 2026-11-08 | Project Owner | open | STD-ENG-022 reaches only Claude Code (through the unversioned workspace `CLAUDE.md`) and new scaffolds. Not covered: existing repos, Codex sessions, the Linux machine, cloud agents, and the build playbooks. Its volatile product facts are unverified. Options and the `change_control.py` fallback: the standard's Distribution and Deferred Work sections. |
| Freedom dispatcher relative cwd awaiting merge | 2026-11-08 | 2026-11-08 | Project Owner | open | Freedom cannot launch New Build until draft PR #73 (`the-freedom-engine-os`, branch `fix/relative-tool-cwd`) merges and the dispatcher restarts. The PR is mergeable and passed its Quality Gate. Its Security Visibility check fails on npm audit drift (69 advisories: 2 critical, 29 high), not on the PR's files; with no branch protection it does not block a merge, but the advisories need triage there. Leave that repository's `agent/stage-c-overnight-turnover` checkout alone (uncommitted 2026-09-05 path edits, three unpushed commits). |
| AI Coding Practices knowledge base change proposal | 2026-11-08 | 2026-11-08 | Project Owner | open | Owner to approve, amend or reject P1 to P7 in `docs/proposals/2026-11-08 - AI Coding Practices Knowledge Base Change Proposal.md`. The knowledge base was not edited (owner decision 2026-11-08); approved items may need matching template edits here. |
| Build-to-sale standard distribution | 2026-09-30 | 2026-11-08 | Project Owner | open | STD-ENG-025 exists only as one canonical copy plus a workspace `CLAUDE.md` summary. Not done: scaffold templates (standards index, context map, pathway phase table), managed-upgrade blocks in `change_control.py`, a validated `project-control.yaml` lifecycle field (phase, last-reviewed date), and alignment reviews of projects intended for sale (GazeCut first). Owner sets scope and order. |
