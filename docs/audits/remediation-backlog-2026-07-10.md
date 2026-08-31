# Remediation Backlog — Repository Audit 2026-07-10

Document ID: AUD-ENG-004
Version: 1.0
Status: active
Owner: Project Owner
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-08-31
Next Review: 2026-09-30

Source: `docs/audits/repository-audit-2026-07-10.md` (AUD-ENG-003).
Scope: the Tier 2 and Tier 3 recommendations from that audit, expanded into
actionable work items. Tier 1 (recommendations 1–5) was executed on
2026-07-10; residual gaps from that execution are recorded in the final
section of this document.

Status legend per item: `open` | `in-progress` | `done` | `exception`.
When an item is closed, set its status and add the closing commit hash.

---

## Tier 2 — paved road and proportionality

### B-6. Scaffold a real paved road (audit rec 6) — open

**What:** New projects created from `templates/project/` receive governance
paperwork but none of the working machinery that makes compliance easy.

**Work items:**
- Add `templates/project/tests/` with one passing sample test (e.g.
  `test_smoke.py` asserting the project imports / a trivial invariant), so
  `pytest`/`unittest` runs green from minute one.
- Add a CI workflow template (`templates/project/.github/workflows/validate.yml`
  or a `.template` variant) mirroring this repo's validate gate, substituted
  during scaffold.
- Add lint/format config to the scaffolded `pyproject.toml` (ruff section)
  so scaffolded projects inherit the same gate this repo now runs.
- Copy the three missing standards into scaffolded projects:
  `testing-standard.md`, `deployment-and-release-standard.md` (or its
  post-consolidation parent), `security-and-secrets-standard.md` — projects
  are governed against docs they never receive.
- Fix the documentation-type failure: `automation/scaffold_project.py`
  (~lines 104–121, 191–195) skips deployment-guide/runbook for
  `documentation` projects but leaves them in `required_docs`, so
  `compliance_report.py` returns `overall_status: failed` out of the box.
  Strip skipped docs from the generated `required_docs` list.
- Unify the two divergent governance checkers: make the scaffolded
  `templates/project/scripts/governance-check.template.sh` delegate to (or
  generate its file list from) the same source `compliance_report.py` uses,
  instead of maintaining a second, weaker list by hand.

**Why:** the paved-road model (Spotify/Netflix, GitHub MVG) makes the right
way the easy way; today the scaffold makes governance the hard way.

### B-7. Score, don't gate, in the audit tool (audit rec 7) — open

**What:** `automation/governance_audit.py` emits ~119 equal-weight pass/fail
findings, almost all metadata-header nags, with no severity model.

**Work items:**
- Give every check a declared enforcement level per risk tier:
  `hard` (fails the run), `soft` (warns, counted), `advisory` (scored only).
- Output a single score (OpenSSF-Scorecard-style 0–10) plus only the hard
  failures as blocking output; move the long tail to a report file.
- Map enforcement level to the project's `risk_tier`/`governance_level` via
  the crosswalk in `docs/standards/governance-level-standard.md` — metadata
  headers should be advisory at Low tier, hard only where the tier demands it.

**Why:** deterministic enforcement for real invariants, advisory scoring for
hygiene — the inverse of today's arrangement (119 nags, zero code checks;
the code checks now exist in `scripts/validate.*`, so the audit tool should
stop pretending to be the gate).

### B-8. Right-size the repo's own classification (audit rec 8) — open

**What:** `project-control.yaml` declares this docs+automation repo
high-risk / governance level 3 despite `handles_sensitive_data: false` and
`handles_money: false` — the archetypal Low tier per
`risk-classification-standard.md`. That self-classification is what
generated the 119-item metadata burden.

**Work items:**
- Either lower `risk_tier`/`governance_level` to match the crosswalk default,
  or write an ADR justifying level 3 for a no-money/no-sensitive-data repo
  (the "governance source for all projects" argument is defensible — but it
  must be written down, not implied).
- Collapse the two-approver ceremony (owner + technical lead — the same
  human) to single-owner reality in `document-control-standard.md` and the
  exception process: one named approver, with the dual-approval requirement
  reserved for projects that actually have two people. STD-ENG-009
  (Governance Level Standard, level 4) now carries the same "where those are
  distinct people" carve-out added 2026-07-13 — keep the two documents in
  sync when this is finalized.

### B-9. Adopt ADRs for real (audit rec 9) — open

**What:** `docs/adr-template.md` is a stub, the `docs/decisions/` folder
referenced by policy does not exist, and zero ADRs exist despite
consequential decisions.

**Work items:**
- Create `docs/decisions/` with the Nygard numbering convention
  (`0001-....md`) and the Proposed → Accepted → Superseded-by lifecycle.
- Backfill at minimum: the doc-consolidation decision (2026-07-10), the
  self-classification decision (B-8), and the update-channel decision (B-12).
- Add a policy line: any NEW governance control requires an ADR naming the
  failure it prevents ("name the failure" test) — this is the structural
  guard against nanny-state growth.

### B-10. Cut entry-point sprawl (audit rec 10) — partially addressed, open

**What:** ~12 "start here" surfaces with circular routing. The 2026-07-10
Tier-1 work consolidated the agent-instruction triangle (CLAUDE.md /
AGENTS.md / AI_BOOTSTRAP.md) and added a canonical reading order; the rest
remains:

**Work items:**
- README.md: reduce to a ~150-line landing page; move the internal session
  logs ("Verified So Far", "Resume Point", frogger/bowtie test records,
  ~lines 224–303) into `docs/current-build-pathway.md` or an archive.
- Delete or fill `docs/manual.md` — it is an unfilled scaffolding template
  shipped as if real (it is also on the `validate.*` required-files list, so
  removing it requires updating both validate scripts and
  `check_required_files.sh`).
- Resolve the two policy docs (`durable-development-engineering-policy.md`
  and `engineering-governance-policy.md`) to one, or write one paragraph in
  each defining the boundary.
- Document the GUI's actual 5-question flow — every doc promises a
  "six questions" intake including explicit governance level; the GUI asks 5
  plain-language questions and infers governance. Fix user-guide.md and
  README.md to describe the shipped product.
- Pick one product name: "New Build Governance Agent" (canonical per
  domain-language.md) vs folder "New Build Agent" vs `freedom.tool.yaml`
  (vocabulary domain-language.md explicitly forbids). Rename
  `freedom.tool.yaml` or update domain-language.md — one or the other.
- `docs/roadmap.md` is generic boilerplate despite 32 completed pathway
  chunks — write a real one or fold it into the pathway doc.

---

## Tier 3 — product ship-readiness and hygiene

### B-11. Modern Python baseline (audit rec 11) — partially addressed, open

Done 2026-07-10: ruff (lint + format) AND mypy configured in pyproject.toml
and enforced in `scripts/validate.*` + CI; `pyproject.toml` version aligned
with `VERSION` (0.3.0).
Remaining:
- Adopt `uv` with a committed lockfile; CI installs with `--frozen`.
- Tighten mypy: it currently runs in default mode; the GUI's untyped
  function bodies are not checked (`--check-untyped-defs`, then stricter
  flags module by module, starting with the secret-sensitive modules).
- Add a `pre-commit` config running ruff + the secret scan so violations
  never reach CI.
- Adopt Conventional Commits + release-please (or a manual equivalent):
  cut a `0.3.0` section in `docs/CHANGELOG.md` now (everything currently
  sits under Unreleased at VERSION 0.3.0).

### B-12. Fix the update/rollback story and sign the exe (audit rec 12) — open

**What:** `automation/update_check.py` (~80–109) compares GitHub *release
tags*, while `automation/self_update.py` (~104–141) fast-forwards *branch
HEAD* — a user can be "up to date" per tag and still be moved to unreleased
commits, and there is no downgrade path.

**Work items:**
- Pin `self_update` to the release tag that `update_check` reported
  (checkout tag, not merge branch HEAD), or explicitly declare a
  branch-following update channel in both tools and the docs.
- Add a rollback action: record the pre-update ref; expose
  `--rollback` to return to it.
- Sign `dist/windows/NewBuildGovernanceAgent.exe` — Azure Trusted Signing
  is ~$10/month for individuals and removes SmartScreen friction; wire
  signing into `scripts/build-windows-launcher.ps1`.
- Longer term: evaluate Velopack or tufup for installer + delta updates
  instead of the zip-plus-git model.

### B-13. Windows secret-file protection + tests (audit rec 13) — open

**What:** `os.chmod(path, 0o600)` on secret files (`master_env.py` ~119,
`env_sync.py` ~324, `stripe_provision.py` ~101) is a no-op on NTFS.

**Work items:**
- On Windows, replace/augment with an `icacls` ACL restriction
  (`icacls <file> /inheritance:r /grant:r "%USERNAME%:F"`), or at minimum
  emit an explicit warning that the file is not OS-protected.
- Put the platform branch in ONE place — `automation/env_file.py` (created
  2026-07-10) is the natural home for a `restrict_permissions(path)` helper.
- Add unit tests for `master_env.py` and `stripe_provision.py` (502 and 256
  untested lines of the two most secret-sensitive modules); also
  `governance_audit.py`, `project_registry.py`, `audit_projects.py`,
  `promotion_remediate.py` (~2,050 untested lines total).
- Ratchet the coverage floor: it is now REAL (CI installs coverage as of
  2026-07-10) but set at 25% — the honest measured baseline; the old 60%
  floor had never actually executed (nor had the per-file 40% targets for
  promotion_execute/promotion_checks, now set at their measured 25%/15%).
  Raise `fail_under` in pyproject.toml and the per-file targets in
  `scripts/validate.sh` as each module above gains tests.
- Add a coverage step to `scripts/validate.ps1`: coverage is currently
  enforced only in the bash gate, so a Windows-only developer first learns of
  a coverage regression from Ubuntu CI rather than the local gate. Mirror the
  `coverage run`/`coverage report` block (reading the same pyproject floor) so
  both gates are symmetric.
- Fix test anti-patterns while there: `tests/test_new_build_headless.py`
  (~79–90) reimplements the validation guard inside the test (tests a copy,
  not the code — import the real function); `tests/test_scaffold_project.py`
  asserts ~40 exact prose fragments, coupling tests to template wording —
  assert structure/keys instead.

### B-14. Purge stale/broken references (audit rec 14) — in progress

Done 2026-07-10: `/home/adamgoodwin/...` paths removed from the
agent-instruction files edited in Tier 1; legacy path removed from
`new_build.sh`; the nonexistent audit citation in
`docs/processes/implementation-plan-2026-06-16.md` corrected and its
illegal `archived` statuses fixed to `retired`.
Remaining:
- Sweep remaining `/home/adamgoodwin` hits: `docs/runbook.md`,
  `docs/deployment-guide.md`, and anything else `grep -r "adamgoodwin" .`
  finds.
- Risk register: last reviewed 2026-05-31 against a quarterly requirement
  with no next-review date — review it and stamp the next date.

### B-15. Promotion honesty (audit rec 15) — open

**What:** the promotion pipeline is a plan generator without executors for
4 of 5 targets; `automation/promotion_execute.py` (~271) supports only
`github`; Vercel/Supabase/Stripe/Resend exist as prose `planned_actions`;
per-target post-promotion health checks are inert strings.

**Work items:**
- Mark Vercel/Supabase/Stripe/Resend targets explicitly `plan-only` in the
  plan output and user-facing docs, OR wire real executors — do not imply
  execution capability that does not exist.
- Chain `promotion_execute` → `promotion_checks` automatically after a
  successful execute, so post-promotion verification is not a separate
  manual step.
- Schema-validate plans in `promotion_execute.load_plan` (today it loads
  without validation — asymmetric with `promotion_checks`, which validates).

---

## Tier 1 residuals (from the 2026-07-10 execution)

Recorded here so the Tier-1 close-out is honest. The five Tier-1
recommendations were executed on 2026-07-10 (real validate gate; Governance
Level Standard STD-ENG-009; canonical instruction/doc homes; canonical code
implementations; metadata remediation to a clean audit run). These edges were
deliberately deferred:

- **Templates still carry the old duplicated blocks.** The repo-level
  instruction files were canonicalized, but `templates/project/`
  (`AGENTS.template.md`, `CLAUDE.template.md`, `AI_BOOTSTRAP.template.md`,
  the policy template with its DoR/DoD copy) still ships the pre-consolidation
  text to new projects. Fold into B-6 (paved-road scaffold rework).
- **`new_build.ps1` keeps its own PowerShell slugify/reserved-name copy.**
  It was the audit's "model pattern" and headless re-validates everything it
  submits, so behavior is safe — but porting it to call
  `automation/project_naming.py slug` would remove the last duplicate.
- **`env_sync.apply_sync` keeps a bespoke merge loop** — its rewrite
  semantics genuinely differ from the shared `env_file.update_env_values`;
  unifying them would change behavior. Documented divergence, not drift.
- **mypy runs in default (non-strict) mode**; GUI untyped function bodies are
  unchecked. Tightening is B-11.
- **shellcheck runs at default severity, PSScriptAnalyzer at Error severity**;
  both skip-with-notice when absent locally and are guaranteed by CI installs.
  Both are currently clean.
- **`docs/deployment-guide.md` is `Status: draft`, not `active`** — the audit
  tool name-matches "deployment" as a plan document and allows only one
  active plan doc (the pathway). Durable fix: rename the file or refine
  `_is_pathway_or_plan` in `automation/governance_audit.py`.
- **Historical records left as records:** older repository audits and the
  June audit still reference the four retired stub standards as they stood;
  `INSTALL.md` / `automation/README.md` / parts of `docs/user-guide.md` still
  describe the pre-wrapper `new_build.sh` in places (interface is
  compatible; wording refresh folded into B-10).
- **No maximum slug length was added** (only the existing 2-char minimum) —
  adding a cap would change accepted inputs without audit direction.

---

## Review cadence

Review this backlog monthly (Next Review above). When an item closes, mark
it `done` with the commit hash; when a deliberate decision is made NOT to do
an item, mark it `exception` and record it in `project-control.yaml`
`exceptions:` per the document-control standard — silent staleness is the
one option the standard forbids.
