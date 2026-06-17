# Implementation Plan — Governance Agent Hardening

Document ID: PATH-ENG-002
Date: 2026-06-16
Status: active
Owner: Adam Goodwin
Approver: Adam Goodwin

Source: audit `new-build-governance-agent-audit-2026-06-17.md` + conversation review.

## Execution Order

1 → 7 → 3 → 4a (triage) → 4b (automation) → 2 → 5 → 6

Chunk 1 first (safety), Chunk 7 second (pure template, zero risk), then feature work,
Chunk 4 split into human triage pass then automation, then GUI risk (Chunk 2), then polish (5, 6).

---

## Pre-Chunk 4 — Document triage (human decision pass)

**Risk:** None — read-only review, then a single commit of status headers  
**Status:** todo — requires owner judgment, cannot be automated

### Context
33 markdown files in `docs/` have no `Status:` field. No archive folder exists.
Getting status wrong on a live standard is worse than leaving it unmarked temporarily,
so this is a human-guided pass, not a bulk automation.

### What needs a decision for each file

| File | Likely status | Confirm? |
|---|---|---|
| `docs/repository-audit-2026-05-19.md` | archived | — |
| `docs/repository-audit-2026-06-07.md` | archived | — |
| `docs/processes/new-build-governance-agent-consolidation-plan.md` | retired (decision executed) | — |
| `docs/standards/*.md` (11 files) | active | confirm each |
| `docs/policy/*.md` (2 files) | active | confirm each |
| `docs/processes/*.md` (3 remaining) | active | confirm each |
| `docs/roadmap.md`, `docs/runbook.md`, `docs/manual.md` | active | confirm |
| `docs/agent-inventory.md`, `docs/model-registry.md`, etc. | active | confirm |
| `docs/CHANGELOG.md` | active | — |
| Templates (`docs/adr-template.md`, `docs/exception-record-template.md`) | active | — |

### What gets created
- `docs/archive/` folder
- Old audit reports moved to `docs/archive/` with `Status: archived` header
- Retired plan marked `Status: retired` in place (not moved — stays for traceability)
- All remaining docs get appropriate `Status:` header added

### Definition of done
Every `.md` in `docs/` has a `Status:` field. Archive folder exists.
Zero uncontrolled documents. Baseline is clean before Chunk 4 automation runs.

---

## Chunk 1 — Stop-ship safety patches

**Risk:** Low — bug fixes only, no refactor  
**Status:** todo

### Files

| File | Change |
|---|---|
| `automation/new_build_headless.py` | After `slug = slugify(project_name)`: reject if slug is empty, single char, contains `/`, or matches a reserved OS name. Fail with descriptive error. |
| `automation/new_build.sh` | Same slug check after slugify step (~line 66); abort with message. |
| `automation/new_build.ps1` | Same check for PowerShell path. |
| `automation/env_sync.py` | In `build_sync_plan()` after `project_target = project / target`: resolve both, call `project_target.resolve().relative_to(project.resolve())` — raise `ValueError` if it escapes. Same guard in `apply_sync()` before first write. |
| `automation/new_build_headless.py` | In `fail()`: change output to `{"status": "failed", "project_path": "", "slug": "", "files_created": [], "error": msg}` — matches `freedom.tool.yaml` schema on failure. |
| `automation/promotion_plan.py` | Replace shell string concat at ~line 114 (`"for f in " + " ".join(shell_files) + ...`) with per-file argv: `["bash", "-n", file]` for each. No `shell=True`. |

### Tests added
- Slug edge cases: `!!!`, `/`, `../../etc`, space-only, 256-char
- Env sync path traversal attempts
- Headless failure output schema matches `freedom.tool.yaml`
- Shell syntax check with filenames containing spaces

### Definition of done
All four bugs fail safely with a clear error. Tests pass. `scripts/validate.sh` passes.

---

## Chunk 7 — Chunk close-out protocol in scaffolded projects

**Risk:** Low — template and scaffold list changes only  
**Status:** todo

### Purpose
Every project created by the governance agent opens in VS Code with Claude Code already
knowing the close-out ritual: surface carry-forward flags, ask to commit and push, then
suggest `/compact` (not `/clear`) to compress context without losing the summary of what
was just done. The code is the memory; the compact summary preserves the shape of the work.

`/clear` is an explicit user override only — used when the previous context had persistent
wrong assumptions, or the next chunk is in a completely unrelated domain.

### Files

| File | Change |
|---|---|
| `templates/project/AGENTS.md` | Add "Chunk Close-Out Protocol" section (see below) |
| `templates/project/CLAUDE.md` | Mirror the same protocol section |
| `templates/project/CARRY_FORWARD.md` | New template file, scaffolded empty (see below) |
| `automation/scaffold_project.py` | Add `CARRY_FORWARD.md` to scaffolded file list |
| `automation/new_build_headless.py` | Include `CARRY_FORWARD.md` in `files_created` output |
| `automation/compliance_report.py` | Add `CARRY_FORWARD.md` to `BASELINE_REQUIRED_FILES` |
| Root `AGENTS.md` and `CLAUDE.md` (this repo) | Add the same Chunk Close-Out Protocol section |

### Chunk Close-Out Protocol section (verbatim for templates)

```markdown
## Chunk Close-Out Protocol

At the end of every chunk of work:

1. Check `CARRY_FORWARD.md` — if it has any open items, surface them to the
   user before proceeding. If there are open flags that must survive the context
   reset, read them aloud and wait for confirmation.
2. Stage the relevant files, commit with a clear message, and push. Do this
   automatically — do not ask unless a carry-forward flag or blocker requires
   a decision first.
3. Confirm the push succeeded, then suggest `/compact` to compress the context
   window. Do not suggest `/clear` — compact preserves the summary of what was
   done, which is cheaper to resume from than a cold start.
4. `/clear` is an explicit user override only: use it when prior context had
   persistent wrong assumptions, or the next chunk is in a completely unrelated
   domain.
5. Do not auto-compact. Do not skip the commit step without flagging why.

A chunk ends when:
- the current definition-of-done in `docs/current-build-pathway.md` is met, or
- a stop condition is reached (blocker, repeated failure, scope boundary), or
- the user signals done.
```

### CARRY_FORWARD.md template (verbatim)

```markdown
# Carry-Forward Flags

Last Updated: <timestamp>
Status: empty

Use this file to record anything that must survive a context reset:
blockers, unresolved decisions, open risks, next-chunk prerequisites.

Clear each item when it is resolved or handed off. If this file has open items,
the coding agent will surface them before suggesting /compact.

| Flag | Added | Owner | Status | Notes |
|---|---|---|---|---|
| (none) | — | — | — | — |
```

### Definition of done
New scaffold contains `CARRY_FORWARD.md`. `AGENTS.md` and `CLAUDE.md` templates contain
the close-out protocol. Compliance report flags missing `CARRY_FORWARD.md`. This repo's
own root `AGENTS.md` and `CLAUDE.md` contain the protocol.

---

## Chunk 3 — Governance audit module

**Risk:** Low — new module, one new GUI button  
**Status:** todo

### Purpose
A new `automation/governance_audit.py` generates a properly formatted AUD-class markdown
report (per `docs/standards/document-control-standard.md`) that a developer opens in
VS Code and works through using `- [ ]` checkboxes. Builds on `compliance_report.py`
data but adds document health checks and outputs actionable markdown.

### New file: `automation/governance_audit.py`

**Checks added on top of `compliance_report.py`:**

| Check | What it looks for |
|---|---|
| Document metadata | Each `.md` in `docs/` has `Status:`, `Owner:`, and a date field in the first 30 lines |
| Supersession markers | Docs with `Status: superseded` must reference their replacement |
| Multiple active pathways | More than one `*pathway*.md` or `*build-plan*.md` with `Status: active` |
| Stale active pathway | Active pathway doc not updated in >30 days — warning, not blocker |
| Build plan orphans | Any `*-plan.md`, `*-pathway.md`, `*-deployment*.md` without a `Status:` line |
| Document ID gaps | Files in `docs/standards/`, `docs/policy/`, `docs/processes/` missing `Document ID:` |
| CARRY_FORWARD.md staleness | Open flags added >7 days ago with no status change — warning |

**Report format** follows the AUD class pattern from `document-control-standard.md`:
- Document ID: `AUD-ENG-<sequence>`
- Sections: Executive Summary, Validation Run, Positive Findings, Findings (Blockers /
  Required Gaps / Warnings), Recommended Remediation Order, Audit Conclusion
- Each finding has a `- [ ]` checkbox with a direct, unambiguous fix instruction
- Written to `docs/audits/governance-audit-YYYY-MM-DD.md` inside the target project

**CLI:** `python3 automation/governance_audit.py <project_path> [--open]`

The `--open` flag runs `code <report_path>` after writing.

### GUI change (Governance & Release tab)
Add "Run Governance Audit" button after the existing "Preview Compliance" step.
On click: runs `governance_audit.py` on selected project, writes report, opens it in VS Code.
Shows output path in the log.

### Definition of done
Report writes valid AUD-class markdown. Checkboxes are present for every finding.
`--open` launches VS Code. GUI button is visible and functional.

---

## Chunk 4 — Document supersession enforcement

**Risk:** Medium — change_control.py modification, template changes  
**Status:** todo

### Purpose
Make it structurally impossible for old pathway, deployment, and build plan docs to
silently coexist with active ones. No files deleted — superseded docs stay for
traceability but get the correct status marker and a back-reference.

### Files

| File | Change |
|---|---|
| `automation/change_control.py` | When generating a new `docs/current-build-pathway.md` via upgrade apply: scan for any existing `*pathway*.md` or `*build-plan*.md` with `Status: active`. Rewrite each to `Status: superseded` and append `Superseded by: docs/current-build-pathway.md (<timestamp>)`. Record each supersession in the manifest. |
| `automation/governance_audit.py` | Supersession check feeds into the audit report under its own "Document Supersession" section. |
| Document Control tab (GUI) | After applying the standard, run the supersession scanner. Show summary: "N docs marked superseded, M docs missing status." |
| `templates/project/docs/current-build-pathway.md` | Add banner at top: "This is the single active pathway document. All prior pathway, deployment-plan, and build-plan documents in this repo must carry `Status: superseded` and reference this file." |

### Definition of done
Applying a governance upgrade marks all prior active pathway docs as superseded.
Audit report surfaces any docs that are missing status or have multiple active pathways.
No files are deleted by the automation.

---

## Chunk 2 — Release execution hardening

**Risk:** Medium — GUI changes, subprocess behavior  
**Status:** todo

### Files

| File | Change |
|---|---|
| `automation/new_build_gui.py` line ~2808 | Remove `"--allow-stage-all"` from `_run_execute_github`. Add `"--include-files"` built from new file-picker widget. |
| `automation/new_build_gui.py` Governance & Release tab | Add "Review Changed Files" step before Execute button: shows `git status` output in scrollable list; user checks each file; staged set passed as `--include-files`. Block Execute button until at least one file is checked. |
| `automation/promotion_checks.py` line ~165 | Add `timeout=300` to `subprocess.run()`. Add `timed_out` status path. Cap stdout/stderr at 8 KB each before storing — truncate with `[truncated]` marker. |
| `automation/promotion_checks.py` | Add `_redact_output(text)`: strips lines matching `KEY=value` env patterns before they enter the report dict. |

### Note
`promotion_execute.py` already creates a PR for non-default branches (line 192). Branch
strategy is not a gap. The real gap is `--allow-stage-all` and missing file picker.

### Definition of done
GUI Execute button requires at least one file explicitly selected. Promotion checks
time out after 5 minutes. Stdout/stderr are capped and redacted before report storage.

---

## Chunk 5 — Shipping contract

**Risk:** Low — config and docs additions  
**Status:** todo

| File | What |
|---|---|
| `pyproject.toml` | Metadata, console entry points (`new-build-gui`, `new-build-headless`, `new-build-audit`), Python `>=3.11`, optional `[dev]` extras: `pytest`, `coverage`. No new runtime deps. |
| `SECURITY.md` | Vulnerability disclosure, secret-handling expectations, no-live-tokens policy. |
| `.env.example` | Placeholder for Stripe/GitHub API vars. Currently no required vars — documents the pattern. |
| `AI_BOOTSTRAP.md` | Fill in concrete commands: Lint, Test, Build. |
| `scripts/validate.sh` | Add coverage threshold: fail if overall < 60%; fail if `promotion_execute.py` or `promotion_checks.py` < 40%. |

### Definition of done
`pip install -e .[dev]` works. `scripts/validate.sh` enforces coverage thresholds.
`SECURITY.md` and `.env.example` present.

---

## Chunk 6 — Context and token hygiene

**Risk:** Low — docs and path constants  
**Status:** todo

| File | Change |
|---|---|
| `docs/current-build-pathway.md` | Split: keep active plan (current chunk + next handoff + validation log). Archive pre-June-2026 history to `docs/archive/pathway-log-2026.md` with `Status: archived`. |
| `automation/new_build_headless.py` line 183 | Replace hard-coded `"Adam Goodwin"` with owner from governance home `project-control.yaml`, defaulting to `"Project Owner"`. |
| `automation/change_control.py` | Replace hard-coded `/home/adamgoodwin/...` Graphify paths with runtime-resolved paths via `GOVERNANCE_HOME` and `Path.home()`. |
| Root `AGENTS.md` | Trim to startup router only. Target: under 80 lines. Heavy governance text stays in the standards it already references. |

### Definition of done
`docs/current-build-pathway.md` < 200 lines. No hard-coded personal paths or names in
generated output. `AGENTS.md` is a router, not a policy doc.

---

## Summary

| Chunk | Risk | Files touched | Status |
|---|---|---|---|
| 1 — Safety patches | Low | 5 files, ~60 lines | todo |
| 7 — Chunk close-out protocol | Low | 6 templates + 2 root files | todo |
| 3 — Governance audit | Low | 1 new file + 1 GUI change | todo |
| 4 — Supersession enforcement | Medium | 2 files + 1 template | todo |
| 2 — Release hardening | Medium | 2 files + new UI widget | todo |
| 5 — Shipping contract | Low | 5 files | todo |
| 6 — Context hygiene | Low | 4 files | todo |
