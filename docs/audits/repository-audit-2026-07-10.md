# Repository Audit — New Build Governance Agent

Document ID: AUD-ENG-003
Version: 1.0
Status: active
Owner: Project Owner
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

Scope: full repository — governance design, document control, user experience,
simplicity, code quality, deliverable builds, ship-readiness — compared against
external best practice (2024–2026 sources cited in the final section).
Method: six parallel review passes (four repo dimensions, two external
best-practice research sweeps), synthesized.

---

## Executive Summary

The framework's instincts are right and match current industry consensus:
risk-tiered controls, lean always-on checks, bounded completion labels, chunk
close-out, plan/apply separation, careful secrets posture. The repo is not a
nanny state in intent.

The problems are structural, and they cluster into five themes:

1. **Say/do gap.** The standards promise enforcement that no code performs
   (`machine_enforcement: [lint, tests, secret-scan]` runs nothing), the
   central selector `governance_level` is never defined in any standard, only
   1 of 13 standards meets the repo's own metadata standard, and the June
   audit's 119 findings are ~95% unactioned. A governance repo that does not
   follow its own governance undermines its whole message.
2. **Duplication as the systemic disease.** Agent instructions are triplicated
   (~18KB); DoR/DoD, testing, and security guidance each live in 2–4 docs;
   four risk taxonomies coexist with no crosswalk. In code, the
   "create a governed project" workflow has three divergent implementations,
   slugify has four copies, and secret-handling env-file parsing is
   copy-pasted verbatim into three modules.
3. **Nanny at the wrong layer.** The automated audit produces 119 findings that
   are almost all metadata-header nags, while zero automated checks look at
   code quality, tests, or secrets. Best practice is the inverse: deterministic
   enforcement for real invariants, advisory scoring for hygiene.
4. **Scaffolded projects get paperwork, not a paved road.** New projects
   receive governance docs but no test scaffold, no CI workflow, no lint
   config, and are missing 3 of the standards they are governed against. The
   `documentation` project type fails its own governance check out of the box.
5. **The shipped product has real ship-readiness gaps.** Unsigned Windows exe,
   update-check compares release tags while self-update pulls branch HEAD, no
   rollback/downgrade path, `chmod 0o600` on secret files is a no-op on
   Windows, and the two most secret-sensitive modules have zero tests.

**Conclusion: ATTENTION.** Strong foundations; the highest-value work is
closing the enforcement gap, de-duplicating one canonical home per rule (docs
and code), and making the scaffold a genuine paved road.

---

## What Is Genuinely Good (keep and protect)

- `automation/self_update.py` — typed, frozen dataclass, specific exception
  handling, guarded fast-forward-only merge. The model module.
- `automation/workspace_paths.py` — the one correctly shared helper.
- `new_build.ps1` → `new_build_headless.py` delegation — the correct pattern
  the bash and GUI paths should copy.
- Secrets posture by design: `getpass` prompts, redacted plans,
  `prints_secret_values: false` policy flags, live-mode guard in
  `stripe_provision.py`, master env stored outside the repo,
  `test_secret_hygiene.py` committed-secret scan.
- CI on Ubuntu + Windows (`.github/workflows/validate.yml`) with a coverage
  floor; version consistency check in `validate.ps1`.
- The GUI's plain-language wizard (purpose → audience → first result → risk),
  progressive disclosure of advanced settings, and actionable error messages.
- Promotion checks (`promotion_checks.py`) genuinely verify outcomes with
  redacted output and meaningful exit codes.
- Template placeholder hygiene: zero unsubstituted variables; sentinel
  `<fill in>` blocks are detected and flagged by the compliance tool.
- Governance concepts that match 2025–26 consensus: risk tiers, lean startup
  checks, bounded completion labels, chunk close-out protocol, exception
  process design (on paper).

---

## Findings by Dimension

### 1. Governance design

- **`governance_level` (0–4) is the declared source of truth but is defined
  nowhere.** Enforced as 0–4 by `automation/schema_validation.py:165`;
  described only in a code comment in `docs/user-guide.md:540`. No standard
  says what levels mean or which controls each requires.
- **Contradictory models:** `engineering-governance-by-use-case.md:23` and
  `engineering-governance-policy.md:21` say governance_level and risk_tier are
  independent; `user-guide.md:553,597` says level derives tier. Both cannot be
  true.
- **Four risk taxonomies, no crosswalk:** Low/Med/High/Critical
  (`risk-classification-standard.md`), the same four re-defined in
  `engineering-governance-by-use-case.md:418-425`, a 6-level agent-action
  tier model (`engineering-governance-by-use-case.md:293-302`), and numeric
  0–4.
- **Self-classification is disproportionate:** `project-control.yaml`
  declares this docs+automation repo high-risk / level 3 despite
  `handles_sensitive_data: false` and `handles_money: false` — the archetypal
  Low tier per its own `risk-classification-standard.md:11`. That choice is
  what generates the 119-item metadata burden.
- **Two-approver ceremony in a one-person repo** (document-control-standard
  and exception process name owner + technical lead; both are the same human).

### 2. Document control

- **Dogfooding compliance ~8%:** 1 of 13 standards (the document-control
  standard itself) carries the full required metadata block; 8 of 13 carry
  none. 0 of 2 policies and 4 of 5 processes lack Document ID/Status.
- **Prior audit unactioned:** `docs/audits/governance-audit-2026-06-16.md`
  (57 required gaps, 62 warnings) — nearly every item still open ~3.5 weeks
  later; no burndown, no per-item owner, no due dates, and none recorded as
  exceptions (`project-control.yaml` `exceptions: []`), which
  `document-control-standard.md:384-394` itself forbids.
- **Remediation plan violates the standard it remediates:**
  `implementation-plan-2026-06-16.md:39,45` proposes `Status: archived`, a
  value outside the allowed set; it also cites a source audit file that does
  not exist (`new-build-governance-agent-audit-2026-06-17.md`).
- **ADRs exist as a template only:** `docs/adr-template.md` is a stub, the
  `docs/decisions/` folder referenced by policy does not exist, and zero ADRs
  have been written despite consequential decisions (e.g., the consolidation).
- **Release metadata inconsistent:** `VERSION` = 0.3.0 but `docs/CHANGELOG.md`
  has only an Unreleased section; `roadmap.md` is generic boilerplate despite
  32 completed pathway chunks.
- **Staleness:** hard-coded `/home/adamgoodwin/...` Linux paths across
  CLAUDE.md, AI_BOOTSTRAP.md, START_HERE.md, context-map, runbook,
  deployment-guide — unresolvable on this Windows machine; risk register last
  reviewed 2026-05-31 against a quarterly-review requirement with no
  next-review date.

### 3. Redundancy and overlap (docs)

- Definition of Ready/Done defined twice near-verbatim
  (`durable-development-engineering-policy.md:346-377` and
  `ship-ready-engineering-standard.md:149-189`).
- Testing guidance in 3 docs; security guidance in 4 docs; required-file /
  golden-path lists in 3 places; agent-safety control lists in 4 docs.
- Fundamentals-First, Context Hygiene, and Graphify blocks byte-identical in
  CLAUDE.md and AI_BOOTSTRAP.md; Chunk Close-Out appears in CLAUDE.md (5
  steps) and AGENTS.md (4 steps) with diverging wording.
- Four thin stub standards (monorepo, deployment-and-release,
  ai-agent-governance, documentation; 1–2KB each) mostly restate the big
  three.

### 4. User experience, onboarding, simplicity

- **~12 "start here" surfaces** (README, START_HERE, AI_BOOTSTRAP, INSTALL,
  user-guide, manual, quick-start-governance-flow, CLAUDE.md, AGENTS.md,
  automation/README, context-map, current-build-pathway) with circular
  routing; `CLAUDE.md:23` points to a "canonical reading order in README.md"
  that does not exist there.
- **Material-work startup requires ~12–14 files/commands** — against the
  framework's own lean-startup claim.
- **GUI and docs describe different products:** every doc promises a
  "six questions" intake including explicit governance level; the GUI asks 5
  plain-language questions and infers governance. No doc describes the actual
  GUI flow.
- **Naming drift:** "New Build Governance Agent" (canonical per
  domain-language.md) vs folder "New Build Agent" vs `freedom.tool.yaml`
  (a term domain-language.md explicitly forbids) vs a legacy
  "Rules of Development and Deployment" path in `new_build.sh:8`.
- **README is a landing page + install guide + session log:** internal handoff
  notes ("Verified So Far", "Resume Point", frogger/bowtie test records) leak
  into the public README (`README.md:224-303`).
- `docs/manual.md` is an unfilled scaffolding template shipped as if real.

### 5. Code quality (automation layer)

- **Three divergent implementations of project creation:** bash
  (`new_build.sh`, full reimplementation), PowerShell→headless (clean), GUI
  (direct + reimplementation). Consequences: the GUI lacks the reserved-name
  and slug-length guards the CLI has (can create `con`/`nul` projects); the
  bash path hardcodes `Adam Goodwin` (`new_build.sh:217`); three different
  project-control patch behaviors; four slugify copies; three copies of the
  governance→risk table and INITIAL_SCOPE generator that already differ.
- **Secret-handling env parsing copy-pasted verbatim** across `env_sync.py`,
  `master_env.py`, `stripe_provision.py` (~120 duplicated lines) — a quoting
  bug fixed in one copy will not propagate.
- **No linter, formatter, or type checker configured anywhere** despite
  near-universal type hints; no lockfile; shell scripts validated by
  `bash -n` syntax-parse only (no shellcheck / PSScriptAnalyzer); no
  pre-commit config.
- **Untested security-sensitive modules:** `stripe_provision.py` (502 lines),
  `master_env.py` (256), plus `governance_audit.py` (483),
  `project_registry.py`, `promotion_checks.py`, `audit_projects.py`,
  `promotion_remediate.py` (~2,050 untested lines total). The 3,093-line GUI
  has a 43-line test.
- **Windows security no-op:** `os.chmod(path, 0o600)` on secret files
  (`master_env.py:119`, `env_sync.py:324`, `stripe_provision.py:101`) does
  not restrict access on NTFS; no `icacls` fallback. The GUI also builds a
  POSIX-only PATH (`new_build_gui.py:164-181`) on a Windows-first product.
- **Test anti-patterns:** `test_new_build_headless.py:79-90` reimplements the
  validation guard inside the test (tests a copy, not the code);
  `test_scaffold_project.py` asserts ~40 exact prose fragments, coupling
  tests to template wording.

### 6. Templates, scaffolding, promotion, ship-readiness

- **`machine_enforcement: [lint, tests, secret-scan]` is inert metadata** —
  `compliance_report.py` checks file presence, YAML schema, and filename
  heuristics only. Secret scanning, test-strategy verification, release
  controls, and the entire Definition of Shipped have zero automated signal.
- **Documentation-type projects fail governance out of the box:**
  `scaffold_project.py:191-195` skips deployment-guide/runbook for
  documentation projects but does not strip them from `required_docs`, so
  `compliance_report.py` returns `overall_status: failed` immediately.
- **Two divergent governance checkers:** the scaffolded
  `governance-check.template.sh` requires different files than the central
  `compliance_report.py` and does no schema validation; standalone projects
  silently run the weaker one.
- **Missing standards in the scaffold:** new projects never receive
  `testing-standard.md`, `deployment-and-release-standard.md`, or
  `security-and-secrets-standard.md` — the docs they are governed against.
- **No test/CI scaffold at all:** no `tests/`, no `.github/workflows/`, no
  lint config, no sample test in `templates/project/` — contradicting
  testing-standard.md:9 and the setup checklist.
- **Promotion pipeline is a plan generator without executors** for 4 of 5
  targets: `promotion_execute.py:271` supports only `github`;
  Vercel/Supabase/Stripe/Resend exist as prose planned_actions; per-target
  post-promotion health checks are inert strings; `promotion_execute` loads
  plans without schema validation (asymmetric with `promotion_checks`).
- **Windows deliverable:** unsigned exe (SmartScreen friction, no integrity
  guarantee); zip-not-installer requiring pre-installed Python with Tcl/Tk;
  `update_check.py` compares GitHub release tags while `self_update.py`
  fast-forwards branch HEAD (a user can be "up to date" per tag and still be
  moved to unreleased commits); no downgrade/rollback action.
- **Changelog discipline not self-applied:** everything under Unreleased at
  VERSION 0.3.0.

---

## Best-Practice Comparison (external benchmarks)

| Practice area | Consensus (sources below) | This repo today |
|---|---|---|
| Governance model | Paved road: make the right way the easy way; price deviation, don't forbid it (Spotify/Netflix, GitHub MVG) | Standards are prose gates; scaffold provides paperwork, not the paved road |
| Enforcement | Every prose rule either has an automated check or is marked judgment-only; policy-as-code (OPA/Conftest concept) | `machine_enforcement` promises checks that don't exist; audit checks metadata headers only |
| Audit output | Score, don't gate (OpenSSF Scorecard 0–10 heuristics); advisory at low tiers | 119 pass/fail metadata findings; no tier→enforcement mapping |
| Agent instruction files | <100 lines (target ~60), deletion test, one canonical home, progressive disclosure; models follow ~150–200 instructions reliably (Anthropic, HumanLayer) | ~18KB triplicated across CLAUDE.md / AGENTS.md / AI_BOOTSTRAP.md |
| Decisions | ADRs, numbered, immutable, Superseded-by lifecycle (Nygard/Fowler/AWS) | Template stub, zero ADRs, dead `docs/decisions/` reference |
| Document control | Front-matter (owner/status/last_reviewed) + git as the register; review cadence by rate-of-change | 8-field metadata block demanded, ~8% compliance, hand-maintained registers |
| Doc structure | Diátaxis separation (policy=explanation, standard=reference, procedure=how-to); ≤5 root-level docs, one entry point | Mixed-purpose mega-docs; ~10 root .md files; 12 entry surfaces |
| Definition of done | One binary, script-checkable gate run identically locally and in CI (Google PRR scaled down) | `validate.*` exists but omits lint/types/secret-scan; DoD prose in two docs |
| Release automation | Conventional Commits → release-please → SemVer + changelog + tag | Hand-edited VERSION, changelog all Unreleased |
| Template drift | Copier-style update model (answers file + 3-way merge) or version-stamp + audit diff | Copy-once scaffold; audit_projects.py partially covers; no template version stamp |
| Python baseline | uv (lockfile) + ruff + mypy + pytest + pre-commit, config in pyproject.toml | pytest+coverage only; no lock, no lint, no types checked |
| Windows shipping | Signed binaries (Azure Trusted Signing, ~$10/mo for individuals); update pinned to releases; rollback path | Unsigned exe; tag-check vs branch-HEAD-update mismatch; no rollback |

---

## Ranked Recommendations

### Tier 1 — close the say/do gap (highest value)

1. **Make the gate real.** Extend `scripts/validate.*` (and wire
   `compliance_report.py` or clearly de-scope it) to actually run: ruff
   (lint+format), mypy, pytest, the secret-hygiene scan, and shellcheck /
   PSScriptAnalyzer — one binary pass/fail gate, identical locally and in CI.
   Until then, relabel `machine_enforcement` as planned, not active.
2. **Write the missing Governance Level Standard.** Define levels 0–4, the
   controls each requires, and a single crosswalk table to Low/Med/High/
   Critical and the agent-action tiers. Make `risk-classification-standard.md`
   the sole definition; delete the duplicate re-definitions. Resolve the
   derive-vs-independent contradiction.
3. **One canonical home per rule (docs).** AI_BOOTSTRAP.md becomes the single
   agent-instruction source at <100 lines using the deletion test; CLAUDE.md
   and AGENTS.md become short pointers. Ship-ready owns DoR/DoD/DoS;
   testing-standard owns testing; security standard owns security; others
   reference. Fold the four stub standards into their parents.
4. **One canonical implementation per behavior (code).** Collapse
   `new_build.sh` onto `new_build_headless.py` (as `new_build.ps1` already
   does); route the GUI through the same path (fixes its missing validation
   guards); extract one shared `env_file.py` for the secret-handling parsers;
   single source for slugify, reserved names, and governance→risk tables.
5. **Act on findings or record exceptions.** Execute the June metadata
   remediation (fixing its illegal `archived` status to `retired` first) or
   formally record the deviation as the repo's first exception record, with
   an audit burndown (owner + due date per item). Either path restores
   integrity; silent non-compliance is the one option the standard forbids.

### Tier 2 — paved road and proportionality

6. **Scaffold a real paved road:** add to `templates/project/` a `tests/`
   folder with one passing sample test, a CI workflow template, lint/format
   config, and the three missing standards; fix the documentation-type
   `required_docs` failure; make the template governance checker delegate to
   (or mirror) `compliance_report.py`.
7. **Score, don't gate, in the audit tool:** give each check a declared
   enforcement level per risk tier (advisory/soft/hard); output a score plus
   the handful of hard failures rather than 119 equal-weight checkboxes.
8. **Right-size the repo's own classification** (or write the ADR justifying
   level 3 for a no-money/no-sensitive-data repo); collapse the two-approver
   ceremony to single-owner reality.
9. **Adopt ADRs for real:** create `docs/decisions/`, backfill the
   consolidation decision, use the Proposed→Accepted→Superseded-by lifecycle;
   require an ADR for any new governance control ("name the failure it
   prevents").
10. **Cut entry-point sprawl:** README becomes a ~150-line landing page (move
    session logs to the pathway doc); one numbered reading order that every
    entry doc defers to; delete `docs/manual.md`; resolve the two policy docs
    to one; document the GUI's actual 5-question flow; pick one product name
    and retire the "freedom" vocabulary or update domain-language.md.

### Tier 3 — product ship-readiness and hygiene

11. **Modern Python baseline:** uv lockfile committed, ruff + mypy config in
    pyproject.toml, pre-commit, CI installs with frozen lockfile; Conventional
    Commits + release-please for automated versioning/changelog; cut a 0.3.0
    changelog section now.
12. **Fix the update/rollback story:** pin `self_update` to the release tag
    that `update_check` reported (not branch HEAD); add a downgrade path;
    sign the Windows exe (Azure Trusted Signing is ~$10/month for
    individuals).
13. **Windows secret-file protection:** replace the no-op `chmod 0o600` with
    an `icacls` ACL restriction (or explicit warning) in `master_env.py`,
    `env_sync.py`, `stripe_provision.py`; add tests for both modules.
14. **Purge stale/broken references:** all `/home/adamgoodwin/...` paths,
    the nonexistent audit citation in `implementation-plan-2026-06-16.md:9`,
    the legacy path in `new_build.sh:8`, and the boilerplate roadmap.
15. **Promotion honesty:** mark Vercel/Supabase/Stripe/Resend targets
    plan-only (or wire executors); chain execute → post-promotion checks;
    schema-validate plans in `promotion_execute.load_plan`.

---

## Sources (external best practice)

Governance: Spotify paved paths (InfoQ) · Red Hat golden paths · DORA platform
engineering · GitHub Minimum Viable Governance · OPA/Conftest CI/CD · OpenSSF
Scorecard · Harmel-Law, Architecture Advice Process (O'Reilly 2024).
Document control: Fowler/Nygard ADRs · AWS & Google Cloud ADR guidance ·
Diátaxis (diataxis.fr) · GitLab docs testing · Vale/markdownlint/lychee.
AI-agent governance: Anthropic Claude Code best practices · HumanLayer
"Writing a good CLAUDE.md" and 12-Factor Agents · agents.md (Linux
Foundation).
Ship-readiness: Google SRE PRR · Cortex/getdx production-readiness guides ·
conventionalcommits.org · keepachangelog.com · release-please.
Scaffolding/tooling: Copier (copier.readthedocs.io) · uv/ruff (Astral) ·
pydevtools handbook · clig.dev · Azure Trusted Signing · Velopack/tufup.

---

## Prior-Audit Linkage

- `docs/audits/governance-audit-2026-06-16.md` (AUD-ENG-002): 119 findings,
  ~95% still open — subsumed into Recommendation 5.
- `docs/repository-audit-2026-06-07.md`: pathway handoff fixed; register
  staleness and AI_BOOTSTRAP placeholders still open.

_This audit was produced with six parallel AI review passes; findings were
cross-checked against file:line evidence. Treat individual line numbers as
approximate anchors._
