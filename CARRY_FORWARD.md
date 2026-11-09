# Carry-Forward Flags

Last Updated: 2026-11-08
Status: open items present

Use this file to record anything that must survive a context reset:
blockers, unresolved decisions, open risks, next-chunk prerequisites.

Clear each item when it is resolved or handed off. If this file has open items,
the coding agent will surface them before suggesting a fresh session for the next chunk.

| Flag | Added | Last Reviewed | Owner | Status | Notes |
|---|---|---|---|---|---|
| Audit Tier 2/3 backlog open | 2026-07-10 | 2026-11-08 | Project Owner | open | Tier-1 fixes from AUD-ENG-003 are done; remaining recommendations and Tier-1 residuals are detailed in `docs/audits/remediation-backlog-2026-07-10.md` (AUD-ENG-004). B-14 portability remediation was completed in commit `5e68ca6`. 2026-11-08 review: Chunk Forty removed `new_build.ps1`'s duplicate code-root routing (its slug copy remains), and Chunk Forty-Three's build playbooks address part of B-6's paved-road gap without adding the scaffolded tests or CI template. No backlog item was closed; select the next item or record exceptions in a future chunk. |
| GitHub standard distribution gaps | 2026-07-26 | 2026-11-08 | Project Owner | open | Reviewed 2026-11-08 and still applicable; the new build playbooks do not carry STD-ENG-022 guardrails. STD-ENG-022 reaches Claude Code through the unversioned workspace `CLAUDE.md` and new scaffolds through the bootstrap template. Existing repos, Codex sessions, the Linux machine, and cloud agents are not covered; the volatile product facts are unverified. Options and the `change_control.py` fallback are in the standard's Distribution and Deferred Work sections. |
| Freedom dispatcher relative cwd awaiting merge | 2026-11-08 | 2026-11-08 | Project Owner | open | `freedom.tool.yaml` keeps a portable `cwd: "."`. The dispatcher fix that resolves it against the manifest's folder is draft PR #73 in the private `the-freedom-engine-os` repository (branch `fix/relative-tool-cwd`, built from its `origin/main`). Until it merges and the dispatcher restarts, Freedom cannot launch New Build. That repository's `agent/stage-c-overnight-turnover` checkout also holds uncommitted 2026-09-05 path edits and three unpushed commits, untouched by this work. |
| AI Coding Practices knowledge base change proposal | 2026-11-08 | 2026-11-08 | Project Owner | open | `docs/proposals/2026-11-08 - AI Coding Practices Knowledge Base Change Proposal.md` lists seven items (P1 to P7) for STD-AIC-001 to STD-AIC-005, ADR-0005, and a System One entry. The knowledge base was not edited (owner decision 2026-11-08). Approve, amend, or reject each item; approved items may need matching template edits here. |
| Build-to-sale standard distribution | 2026-09-30 | 2026-11-08 | Project Owner | open | Reviewed 2026-11-08: unchanged. STD-ENG-025 exists as a single canonical copy with a workspace `CLAUDE.md` summary. Not yet done: scaffold templates (standards index, context map, pathway phase table), managed-upgrade blocks in `change_control.py`, a validated `project-control.yaml` lifecycle field (phase and last-reviewed date), and alignment reviews for existing projects intended for sale (GazeCut first). Owner decides scope and order. |
