# Current Build Pathway

Last Updated: 2026-11-09
Status: active
Owner: Technical Lead

## Purpose

This document is the live path from current plan to completed build. It keeps agent work small, timestamped, and easy to resume.

## Required Work Pattern

For ordinary scoped work, use lean startup:

1. Check `git status --short`.
2. Read the short repo-local agent instructions.
3. Use `docs/context-map.md` when context routing is unclear.
4. Inspect only the specific files, errors, or docs needed for the task.
5. Run targeted validation after the change.

For material or risk-triggering work sessions:

1. Start from `START_HERE.md`.
2. Run the governance preflight for the target project.
3. Review `docs/standards/README.md`.
4. Review `docs/standards/engineering-governance-by-use-case.md`.
5. Review `docs/policy/durable-development-engineering-policy.md`.
6. Review `docs/standards/ship-ready-engineering-standard.md`.
7. Review `project-control.yaml` and open exceptions.
8. Capture a timestamp with `date -Iseconds`.
9. Define the next build chunk in this document.
10. Complete and validate that chunk before expanding scope.
11. Update this document with status, validation, and the next chunk.

Risk-triggering work includes production, deployment, authentication, authorization, payments, secrets, sensitive data, database migrations, customer communications, external side effects, infrastructure or provider settings, destructive actions, autonomous tool use, risk classification, governance policy changes, or release readiness.

## Chunking Standard

Each build chunk should be small enough to fit comfortably in an agent context window.

A good chunk has:

- one objective
- a budget class: Tiny, Small, Medium, Large, or Strategic
- clear input files or documents: a `Read first:` list with line ranges, plus `Facts:` that save reads
- clear output files or behavior
- explicit validation steps
- a timestamped status note

Use second-level Markdown headings for active and planned chunks:

```md
## Chunk One - Short Objective
## Chunk Two - Short Objective
```

## Chunk Fifty-Two - The Env Writer Finds Keys The Way The Reader Does

Status: ready · Completion target: Task complete · Budget class: Small

Source: found by Chunk Fifty-One and recorded in AUD-ENG-004 B-13. It is the default next item. If the owner names another item, do that instead (alternates at the end).

Objective: `env_file.update_env_values` finds a key's existing line the way `parse_env_file` reads it. Then `set` and `merge` without `--overwrite` keep a value written as `export KEY=v`, on an indented line or as `KEY = v`, instead of appending a second line that wins.

Read first:

- `automation/env_file.py:25-26` (`_ASSIGNMENT_RE`), `:62-79` (`parse_env_file`) and `:274-316` (`update_env_values`).
- `tests/test_env_file.py:100-169` (`UpdateEnvValuesTests`; the test at `:150-161` keeps an untouched `export` line verbatim).
- `tests/test_master_env.py:282-300`: the keep and overwrite tests to copy for the user-level check.

Facts:

- Repro, run on scratch files at Chunk Fifty-One: with a master holding `export SHARED_KEY=old`, `master_env.py --master <file> set SHARED_KEY --value new` printed `added` and appended `SHARED_KEY=new` under `# ===== Added by master_env.py =====`. `parse_env_file` then returned `new`, because the last line wins. `  INDENTED_KEY=keep` and `SPACED_KEY = keep2` behaved the same.
- `parse_env_file` strips the line, splits it at the first `=`, removes an `export ` prefix and strips the key. `_ASSIGNMENT_RE` (`^([A-Za-z_][A-Za-z0-9_]*)=(.*)$`) matches only a bare `KEY=` at the start of the line.
- Only `master_env.py` and `stripe_provision.py` call `update_env_values`; `env_sync.py` has its own writer.
- When rewriting a matched line, keep the text before `=` (the `export ` prefix and any indentation), so a file that a shell sources keeps working.

Acceptance criteria:

- [ ] An `env_file` test that fails first: an `export` line, an indented line and a `KEY = v` line are each filled when blank, kept without `overwrite`, and rewritten in place with it. Each keeps its prefix, and no key gains a second line.
- [ ] A `master_env` test: `set` without `--overwrite` on `export SHARED_KEY=<fake>` prints `skipped`, keeps the value, and leaves one line for the key.
- [ ] The local gate passes; Validate passes on both OSes.

Validation: as for Chunk Fifty-One. Run `PYTHON=$V/bin/python3 bash scripts/validate.sh`, where `V` is a venv with `requirements-dev.txt` installed (reuse a matching `/tmp/claude-1000/*New-Build-Agent/*/scratchpad/devvenv`). Then push to `main`, take the run id from `gh run list --commit <sha>`, and run `timeout 15m gh run watch <id> --exit-status`. If the ubuntu-latest total, rounded down, is above 43, raise `fail_under` to it.

Stop condition: stop when the criteria pass. Change only how `update_env_values` matches and rewrites an existing line, not how `parse_env_file` reads values or the file format. If the fix needs more than that, record it in B-13 and stop. Do not start the `validate.ps1` coverage step or the test anti-pattern fixes. Do not edit standards or templates.

Close-out: mark this section complete with findings and validation. Add its row to Recent Completed Work, and update B-13 (`docs/audits/remediation-backlog-2026-07-10.md:183-263`), `docs/CHANGELOG.md` and `CARRY_FORWARD.md`. If no chunk is ready, define the next one here in this same compact form, then point `CARRY_FORWARD.md` at it.

Alternates, only if the owner names one: tests for `governance_audit.py`, `project_registry.py`, `audit_projects.py` or `promotion_remediate.py` (the rest of B-13's test item); the `validate.ps1` coverage step (B-13), so the Windows gate enforces the same floor; or the B-13 test anti-pattern fixes.

## Chunk Fifty-One - Tests For The Master Env Commands

Status: complete · Completion target: Task complete · Budget class: Medium

Timestamp: 2026-11-09T21:41:21-06:00

Source: chunk 51, the default set at the Chunk Forty-Nine close-out: AUD-ENG-004 B-13's next open work item, tests for the secret-sensitive modules. `master_env.py` was the last of the two it names.

Objective: `automation/master_env.py` gets tests for its four commands, with no real env file. It had 115 statements and 36% coverage. It reads and writes the master env file and must never print a value.

Acceptance criteria:

- [x] `tests/test_master_env.py` (22 tests, 19 of them new) covers `status` for named keys, `--control-plane` and the default list; `missing` with no flag, `--priority` and `--control-plane`; `set` with `--value`, a hidden prompt, `--visible`, a blank answer, a value kept without `--overwrite`, and `--overwrite`; `merge --key`, including its refusal; and `main` refusing `set --value` with two keys and running a command.
- [x] No test prints a value or reads a real env file. Every test checks stdout and stderr for each fake value, and every master is a temporary file. A module guard points the parser's `--master` default at a temporary path, so a test that forgets `--master` cannot reach the real file.
- [x] `fail_under` rose from 41 to 43. `master_env.py` is 99% covered (118 statements, one missed: the `__main__` call) locally and on ubuntu-latest.
- [x] The local gate passes; Validate passes on both OSes.

Findings:

- One bug, fixed with tests that failed first. `set` wrote a value containing a line break across several lines. The value read back cut short, and a continuation line such as `QmFzZTY0ZmFrZTE=` read back as a key with a blank value, which a plain `missing` printed: part of the secret, on stdout. The way in was `--value`, for example with a PEM key for `GITHUB_APP_PRIVATE_KEY`. Before the fix, the four line-break checks (three `--value` cases and one prompted case) failed with `2 != 0`. `set` now refuses any value that `splitlines()` would split, with exit 2 and before anything is written, and names only the key. A prompt reads one line, but `splitlines()` also splits at characters such as a carriage return, so prompted values are checked too.
- Found, not fixed, and recorded in B-13: `env_file.update_env_values` finds a key's line with a regex that matches only a bare `KEY=` at the start of a line, while `parse_env_file` also reads `export KEY=`, indented lines and `KEY = v`. For such a line, `set` or `merge` without `--overwrite` appends a second line, prints `added`, and the new value wins on read. The fix belongs in the shared writer, which `stripe_provision.py` also uses, so it is Chunk Fifty-Two rather than a fix here.
- Also recorded in B-13: `merge` with a missing `--source` merges nothing and exits 0, and with a missing `--master` creates a master holding only the header. The env writer has no line-break guard of its own.
- The commands are tested through the real parser (`build_parser().parse_args`), so the flag names are covered too.
- Local and ubuntu-latest per-file counts match except for one line and one branch in `workspace_paths.py`, as at Chunk Forty-Nine, so the exact local total (43.25%) stands in for CI's.

Known gaps:

- `scripts/validate.ps1` still has no coverage step, so the floor is enforced only on ubuntu-latest (B-13).

Validation: the fail-first run showed only the four line-break checks failing. The local gate then passed (216 tests, 2 skipped; total 43.25%). Validate run 42750867354 passed on ubuntu-latest (218 tests, 2 skipped; total 43%: 4,616 statements, 2,532 missed) and windows-latest (218 tests, 6 skipped). Build Windows Launcher run 42750867646 passed. `graphify update . --no-cluster` exit 0.

## Chunk Forty-Nine - First Tests For The Stripe Provisioning Module

Status: complete · Completion target: Task complete · Budget class: Medium

Timestamp: 2026-11-09T21:23:40-06:00

Source: chunk 49, the default set at the Chunk Forty-Eight close-out: AUD-ENG-004 B-13's next open work item (tests for the secret-sensitive modules), starting with the one that had none.

Objective: `automation/stripe_provision.py` gets its first tests, with no network access and no real key. It had 235 statements and 0% coverage. It writes Stripe price ids and a new webhook signing secret into the master env file.

Acceptance criteria:

- [x] `tests/test_stripe_provision.py` (23 tests) covers `flatten_params` nesting; key selection by mode, including the refusal; `build_plan` naming the key variable but never its value; create-versus-reuse in `ensure_product`, `ensure_price` and `ensure_webhook`; and `apply_plan`. Price ids and a new webhook secret land in a temporary master env, an existing webhook leaves the env value alone and returns the secret note, and the result reports `secret_values_printed: False`.
- [x] `StripeClient.request` is tested for GET query versus POST body encoding. An HTTP error becomes a `RuntimeError` whose message does not contain the key.
- [x] No test reaches the network or reads a real env file: a module-level guard makes `urlopen` fail, and every master env is a temporary file.
- [x] `fail_under` rose from 25 to 41, the ubuntu-latest total rounded down. `stripe_provision.py` is 86% covered (243 statements, 30 missed) locally and on ubuntu-latest.
- [x] The local gate passes; Validate passes on both OSes.

Findings:

- Two bugs, each fixed with a test that failed first:
  - A mode other than exactly `test` or `live` skipped both the key filter and the `--allow-live` check. A manifest or plan with `"mode": "Live"` used the first key set, live or not, without `--allow-live`. The apply-time test failed with "a Stripe client was built" and the plan-time test with "ValueError not raised". `check_mode` now refuses any other mode in `build_plan` and `stripe_key_for_mode`.
  - Without `secret_env` in the manifest, the plan said a new webhook's secret would go to `STRIPE_WEBHOOK_SECRET`, but apply dropped it. The API returns that secret only when it creates the endpoint. The test failed with `None != 'whsec_fake5'`. Plan and apply now share one default, `DEFAULT_WEBHOOK_SECRET_ENV`.
- Still untested in the module: the `init` and `plan` commands, `write_plan`, `write_manifest_template`, and `load_manifest`'s error paths.
- The criteria's tkinter note no longer holds. Local and ubuntu-latest per-file counts match except for one line in `workspace_paths.py`, so the exact local total (41.70%) stands in for CI's.
- Fake keys are short (`sk_test_fake1`). The module checks only the `_test_` or `_live_` marker, and short values stay clear of the hygiene test and GitHub secret scanning.

Known gaps:

- `scripts/validate.ps1` has no coverage step, so the floor is enforced only on ubuntu-latest (B-13).

Validation: the local gate passed (197 tests, 2 skipped; total 41.70%). Validate run 42748834389 passed on ubuntu-latest (199 tests, 2 skipped; total 42%: 4,613 statements, 2,599 missed) and windows-latest (199 tests, 5 skipped). Build Windows Launcher run 42748834120 passed.

## Chunk Fifty - Token-Efficient Handover And Agent Writing Guidance

Status: complete · Completion target: Task complete · Budget class: Medium

Timestamp: 2026-11-09T20:29:23-06:00

Source: owner request 2026-11-09. Part A writes the token-efficient handover down as guidance, not a rule. Part B adds compact agent-writing guidance. After reviewing another agent's compression notes, the owner approved Part B with their useful points folded in, deferred the rest, and had the chunk run straight away.

Objective: new projects, and coding agents from any vendor, receive both parts as guidance through the context hygiene standard (recommended, not required) and the project templates. No rule file changes.

Acceptance criteria:

- [x] Part A: the standard and its template copy gain Hand Over Through The Next Ready Chunk, and a Next-Chunk Handover Template beside the Handoff Summary Template.
- [x] Part B: both gain Write Compactly For Agents. It includes the external notes' list of what must survive, the uncertainty labels, one statement per rule, and compressing only text that is loaded repeatedly. Its evidence sentence is generic, so the template copy reads correctly in any project.
- [x] The pathway template gains optional `Read first:` and `Facts:` fields in the P-01 skeleton and the Chunking Standard list, and this pathway's Chunking Standard names them.
- [x] The `CARRY_FORWARD` template gains a `Next chunk:` line and the one-or-two-lines note, and its `/compact` reference is now `/clear`.
- [x] Step 4 of the `AGENTS` template's "Finish a chunk" list points to the new section, without adding a mandatory step.
- [x] The standards index and both context maps route "writing text that agents read" to the standard.
- [x] `AI_BOOTSTRAP.md`, `CLAUDE.md`, the playbooks and the managed blocks are unchanged.
- [x] Tests cover the new headings, the fields and the carry-forward line, and the local gate passes. Validate on both OSes is checked on the pushed commit.

Findings:

- The research record (`docs/research/2026-11-09 - Token-Efficient Agent Writing Research.md`) now compares the external notes and keeps the evidence. Its own guidance list became a pointer to the standard, so each rule is stated once.
- Compression pays only for text that is loaded every session. A one-time pass over a 3,600-token rules block repays itself in 12 to 24 sessions; a handover would need 28 to 59 reads to repay one load of a compression skill.
- Deferred by the owner: a compression tool, the Jev or Laya checking layer, and separate compressed copies of documents.

Known gaps:

- The `AGENTS` template is 7.3 KB, against the 6 KB `agents_md_target_kb`. It was already over before this chunk.
- Existing projects receive the guidance only at their alignment review, because change control adds only missing files and blocks.

Validation: the local gate passed (174 tests, 2 skipped; total coverage 37%). Validate runs on the pushed commit.

## Chunk Forty-Eight - Exact Single-Entry Windows Access List For Secret Files

Status: complete · Completion target: Task complete · Budget class: Medium

Timestamp: 2026-11-09T18:05:57-06:00

Source: AUD-ENG-004 item B-13, its first open work item, as defined at the Chunk Forty-Seven close-out. The owner started the chunk on 2026-11-09.

Objective: on Windows, every secret file written by `write_private_text` ends with exactly one access entry, the current user's, and writes still fail closed. The old `icacls <file> /inheritance:r /grant:r *<SID>:F` kept explicit entries, such as the SYSTEM, Administrators and Owner Rights copies a file receives in a folder without auto-inheritance (CI runs 42556335162 and 42557263741).

Acceptance criteria:

- [x] On windows-latest, a new file and a rewritten file that already holds an explicit entry each end with exactly one entry: the current user's, allow, no flags, `FA`. This holds in a normally inheriting folder, a `tempfile.mkdtemp` folder, and a plain `os.mkdir` folder. The rewrite test first adds a BUILTIN\Users entry and confirms it is there.
- [x] A failed restriction still raises `SecretFileProtectionError` and writes nothing; POSIX behaviour is unchanged.
- [x] The local gate passes; Validate passes on both OSes.

Decision: candidate 1, `SetNamedSecurityInfoW` through `ctypes`. One call replaces the whole list with a protected one-entry list built from the SDDL `D:P(A;;FA;;;<SID>)`, and no step in between widens access. Not chosen:

- `icacls /restore` needs a crafted ACL file whose integrity then matters, in a UTF-16 format with names relative to the folder.
- `icacls /reset` first would expose a rewritten file that already holds secrets, and the existing-file rule forbids emptying it first.

Findings:

- `SetNamedSecurityInfoW` receives the list without its descriptor, so the `P` in the SDDL text does not reach the file. `PROTECTED_DACL_SECURITY_INFORMATION` blocks inheritance; the branch tests pin it (`0x80000004`, with `DACL_SECURITY_INFORMATION`).
- A NULL list would grant everyone full control, so the helper refuses to apply one (tested).
- `ctypes` defines `WinDLL`, `get_last_error` and `FormatError` only on Windows. They sit in one `sys.platform`-guarded loader, `_load_security_api`, which the branch tests replace with a fake on every OS. Linux mypy skips the loader's body. `mypy --platform win32` checks it (a probe confirmed it catches a deliberate type error), and `validate.ps1` runs mypy on Windows.
- `env_file.py` coverage on Linux fell from 100% to 90%. The uncovered lines (153-172) are that loader, which only the windows-latest job runs, without measuring coverage.
- Unchanged: the `whoami` step, the fail-closed contract, and the error's manual `icacls` hint. That hint leaves explicit entries in place; the next successful write removes them.
- Mutation check: five regressions each failed the every-OS tests. They were dropping the protected flag, passing a NULL list on, skipping the free, ignoring the error code, and granting read instead of full control.
- Standards: `security-and-secrets-standard.md:59` (real env files permissioned for the local owner only) now holds exactly on Windows. `:88` (periodic permission review) applies at critical risk; this repository is high tier.

Validation:

- Preflight: 0 required gaps, 1 existing design warning. `python3 automation/governance_audit.py .`: 0 blockers, 0 required gaps, 0 warnings (AUD-ENG-014).
- Gate with the pinned tools: exit 0; ruff and mypy passed; 174 tests run, 2 skipped (the real-Windows tests); total coverage 37%. `mypy --platform win32 automation`: no issues.
- Windows CI: Validate run 42727149869 on `e3c17b0` passed on ubuntu-latest and windows-latest. On Windows, ruff and mypy passed and 176 tests ran with 4 skipped. Those 4 are exactly the POSIX-only tests, so both real-Windows tests ran and passed. The Windows launcher build (run 42727149861) passed.
- `graphify update . --no-cluster`: exit 0.

## Chunk Forty-Seven - Secret Env Files Restricted To The Owner On Windows

Status: complete

Completion target: Task complete

Budget class: Medium

Timestamp: 2026-11-08T21:24:23-06:00

Source: AUD-ENG-004 item B-13, its first two work items. This was the carry-forward's suggested next item; the owner started the chunk on 2026-11-08.

Objective: the secret env files this repository writes are restricted to the current user on every platform, so no other ordinary user or group keeps access. On Windows, `os.chmod(path, 0o600)` changes only the read-only flag. `.env.master` and project env files therefore kept whatever access their folder granted, and outside the user profile that can include every local user.

Acceptance criteria:

- [x] One helper in `automation/env_file.py`. `write_private_text` creates a missing file owner-only (`O_CREAT | O_EXCL`, mode 0600), restricts it with `restrict_to_owner`, and only then writes the content. On Windows, `restrict_to_owner` runs `icacls <file> /inheritance:r /grant:r *<SID>:F` with the SID that `whoami /user` reports. Both tools are called by their System32 path, without a shell.
- [x] Both secret writers use it: `write_env_lines` (behind `master_env.py` and `stripe_provision.py`) and `env_sync.apply_sync`. The `apply_sync` merge loop is unchanged.
- [x] The write fails closed. When the restriction fails, `SecretFileProtectionError` is raised with a fix hint, a file the call created is removed, and an existing file keeps its content.
- [x] Tests cover:
  - POSIX modes: 0600 from creation even with umask 0, and an existing 0644 file becomes 0600.
  - Restriction before any content is written, and the refused-write paths.
  - The Windows branch, with mocked tools, on every OS.
  - Windows-only tests that read the resulting access-control list back with `icacls /save`, in a folder with normal inheritance and in a `tempfile.mkdtemp` folder.
  - The first tests of `apply_sync`'s write path.
- [x] Backlog, changelog, runbook, and carry-forward updated.

Stop condition: stop before the coverage-floor ratchet, the `validate.ps1` coverage step, tests for the other untested modules, the test anti-pattern fixes, and any edit to STD-ENG-019 or the templates.

Decision (fail closed): the backlog also allowed a warning instead of a refusal. Refusing matches what POSIX already did when `chmod` failed. It also matches STD-ENG-019, which says generated real env files must be "permissioned for the local owner only". Consequence: on a drive without access-control lists (FAT32, exFAT, some network shares), env writes now stop with a fix hint, where before they succeeded unprotected. Reversing this is an owner decision.

Findings:

- The backlog's three `chmod` sites had already narrowed to two. `master_env.py` and `stripe_provision.py` write through `env_file.update_env_values`, so the only direct calls left were `env_file.py:82` and `env_sync.py:291`.
- POSIX had a related gap. Content was written before `chmod` ran, so a new file briefly held secrets at the default mode (0644 under the usual umask). The new order closes it.
- `apply_sync`'s write path had no test before this chunk. `env_sync.py` coverage rose from 38% to 53%.
- Known limit, confirmed in CI: `icacls /inheritance:r` removes only inherited entries. Explicit entries stay: ones another tool added to an existing file, and copies a new file receives from a parent folder whose list is not auto-inherited.
  - CI run 42556335162 showed the second case: a file created in a `tempfile.mkdtemp` folder kept explicit SYSTEM, Administrators, and Owner Rights entries next to the user's. Python 3.12.4+ creates those folders with a protected list without auto-inheritance.
  - Run 42557263741 showed that such parents are not rare. On the runner, even a plain `os.mkdir` folder under the temp directory passed explicit copies (SYSTEM, Administrators, and the user).
  - Those entries are the Windows equivalent of root, so the outcome is acceptable. Where the parent passes only inherited entries (tested in a folder reset with `icacls /reset`), only the user's entry remains (run 42557576490).
  - Exact single-entry replacement is now a B-13 work item. Running `icacls /reset` first was not used, because it would briefly re-open an already-protected file on every rewrite.
- Mutation check: five deliberate regressions each failed the new tests: bypassing the helper, writing before restricting, creating with mode 0666, keeping inheritance on Windows, and a plain write in `env_sync`.
- For the owner: STD-ENG-019's Next Review date (2026-10-10) has passed. The standard was not edited.

Validation:

- `bash scripts/validate.sh` with the pinned tools exit 0: 173 tests run, coverage 37%. The 3 Windows-only tests are skipped on Linux and are not counted in that total (176 test cases). `env_file.py` has 100% coverage, its Windows branch included.
- CLI checks on throwaway files: `env_sync.py apply` under umask 000 wrote a 0600 `.env.local`, and `master_env.py set` changed a 0644 master to 0600.
- `python3 automation/governance_audit.py .`: 0 blockers, 0 required gaps, 0 warnings. `graphify update . --no-cluster` exit 0.
- Windows CI: run 42556335162 on `a2ac691` failed, with 175 tests run, 2 failures, and 4 skipped. Both failures were the real-Windows tests' strict "exactly one entry" assertion meeting the `mkdtemp` case above. `whoami`, `icacls`, and every existing env test passed through real `icacls`. The fix-forward commit asserts the actual property and adds the normal-inheritance case.
- Windows CI: run 42557263741 on `ba5197b` failed, with 176 tests run, 2 failures, and 4 skipped. Both failures were the new precondition check: a plain `os.mkdir` folder under the runner's temp directory did not pass inherited entries. The kept-entries test passed. The next commit resets its test folder with `icacls /reset` first.
- Windows CI: run 42557576490 on `e320d6f` passed, with 176 tests run and 4 skipped (the POSIX-only tests). All three real-Windows tests passed. A file in a normally inheriting folder has exactly one entry, for the current user, and still has one after a rewrite. In `mkdtemp` and plain-mkdir folders, nothing but SYSTEM, Administrators, or Owner Rights sits beside the user. Ubuntu and the Windows launcher build also passed.
- 2026-11-09: this chunk's start-up spent about 12 minutes reading before its first edit, because no Chunk Forty-Seven had been defined. The handover is now Chunk Forty-Eight (above), a ready section, and `CARRY_FORWARD.md` points to it in one line.

## Chunk Forty-Six - Documentation Scaffold Passes Its Own Compliance Check

Status: complete

Completion target: Task complete

Budget class: Small

Timestamp: 2026-11-08T21:01:34-06:00

Source: AUD-ENG-004 item B-6 (the documentation-type sub-item), chosen by the owner on 2026-11-08 as the next chunk.

Objective: a freshly scaffolded `documentation` project passes its own compliance report. The scaffold deliberately skips `docs/deployment-guide.md` and `docs/runbook.md` for documentation projects, but the generated `project-control.yaml` still listed both as required, so `compliance_report.py` returned `failed` at every governance level.

Acceptance criteria:

- [x] `automation/scaffold_project.py` keeps the skipped docs and the generated `required_docs` list in step: one table names the operational docs and the types that skip them, and the list is trimmed only when the scaffold writes `project-control.yaml`. Existing control files are kept as they are.
- [x] Regression test: every project type at every governance level passes its own compliance report straight after scaffolding.
- [x] Structural tests: documentation projects neither get nor require the two docs, other types get and require both, and an existing documentation `project-control.yaml` is left unchanged.
- [x] Backlog bookkeeping: the B-6 documentation sub-item recorded as done, B-14 closed, and the review dates current.
- [x] `bash scripts/validate.sh` with the pinned tools exits 0, and the governance audit stays clean.

Stop condition: stop before any template edit, any other B-6 sub-item, or any change to how `change_control.py` treats existing projects.

Findings:

- Before the fix, a probe of all 45 type and level combinations found documentation as the only failing type, failing at all five levels. The new tests failed on exactly those six cases before the fix and pass after it.
- The scaffolded `scripts/governance-check.sh` already treated the two docs as optional for documentation projects. Only the compliance report, which reads `required_docs`, disagreed.
- `change_control.py` offers both docs to every project type, documentation included, so a promoted documentation project stays consistent when it accepts them. The only documentation project found in the workspace, `home-assistant-manager`, has both docs and is unaffected.
- Not fixed (out of scope): `compliance_report.required_files_from_control` adds the AI register files only for `project_type: agent`, not legacy `agentic-harness`. Those projects still pass, because the scaffold creates the files, but their check is less strict.

Validation:

- `bash scripts/validate.sh` with the pinned tools (ruff 0.15.21, mypy 2.2.0, coverage 7.15.0) exit 0: 158 tests, coverage 36%.
- CLI check: `scaffold_project.py <dir> documentation`, then `compliance_report.py <dir>` exits 0 with 0 required gaps (exit 1 before the fix).
- `python3 automation/governance_audit.py .`: 0 blockers, 0 required gaps, 0 warnings. `graphify update . --no-cluster` exit 0.

## 2026-11-08 Frontier Refresh Plan

Owner request, 2026-11-08: research current AI engineering practice (the AI Engineer channel, frontier-lab guidance, independent practitioners), write per-build-type instructions that agents can be given, refresh this repository's rules for current frontier models, place Jev and Laya where they add the most value, treat a harness as what people mean by "agent", and finish the unfinished 2026-09-05 path work.

Owner decisions, Adam Goodwin, 2026-11-08:

- Fix the Freedom dispatcher so `freedom.tool.yaml` keeps a portable `cwd: "."`.
- Align this repository's own chunk close-out with the fresh-session-per-chunk pattern (ADR-0002 in the AI Coding Practices knowledge base). This resolves the matching carry-forward flag.
- Merge the intake's "AI helper" and "agentic harness" choices into one "AI agent (harness)" choice.
- Frontier updates to AI Coding Practices topics go into a dated change proposal for that knowledge base. The knowledge base itself is not edited.

| Chunk | Objective | Budget class | Status |
|---|---|---|---|
| Forty | Workspace paths and preview routing | Small | complete |
| Forty-One | Freedom dispatcher resolves a relative `cwd` (the-freedom-engine-os) | Tiny | complete (draft PR #73 awaiting merge) |
| Forty-Two | One "AI agent (harness)" intake choice | Medium | complete |
| Forty-Three | Build-type agent playbooks | Large | complete |
| Forty-Four | Frontier AI engineering research record, including Jev and Laya | Medium | complete |
| Forty-Five | Frontier-model rules refresh and knowledge-base change proposal | Large | complete |

## Chunk Forty-Five - Frontier-Model Rules Refresh

Status: complete

Completion target: Integration complete

Budget class: Large

Timestamp: 2026-11-08T20:31:59-06:00

Objective: bring this repository's own rules and the generated standards up to date for current frontier models, align this repository's chunk close-out with the fresh-session pattern (owner decision 2026-11-08), and propose matching changes to the AI Coding Practices knowledge base without editing it.

Acceptance criteria:

- [x] `AI_BOOTSTRAP.md` and `CLAUDE.md`: chunk close-out ends with a fresh session for the next chunk, and within a chunk relies on automatic compaction rather than resets. The stated reason is a clean start from a written definition of done, not context capacity. A "Working With Frontier Models" section covers plain-language rules, evidence of completion, deterministic checks first, hooks for hard rules, the role of subagents, package and configuration trust, and model settings over prompt wording.
- [x] Context Hygiene Standard and its template: subagents justified by parallelism, isolation, or independent review rather than capacity; compaction guidance for 1M-token models.
- [x] Engineering Governance By Use Case and its template: Harness Engineering Controls under AI Agents With Tools (Rule of Two, tripwires versus boundaries, bound approvals and caps, supply-chain pinning, evaluation sets as data, retesting at model releases, trace logging, System One rules).
- [x] Durable Development Policy and its template: working with current coding agents.
- [x] Harness README template (decisions table, Rule of Two question) and model registry template (exact model IDs, settings, eval set, re-evaluation before switching).
- [x] Build playbooks gained the AI Engineer findings: checking before retrying after a timeout, recording state before external changes, prompt-cache ordering, effort-for-cost trade-offs, credentials and egress outside the agent, and proof a reviewer can check.
- [x] README screenshots retaken from the current GUI on a virtual display, with updated alt text.
- [x] `docs/proposals/2026-11-08 - AI Coding Practices Knowledge Base Change Proposal.md`: seven items for owner review. The knowledge base was not edited.
- [x] Carry-forward: fresh-context and screenshot flags cleared, the proposal flagged, and the three standing flags reviewed with what changed.

Finding during research: Anthropic's current guidance says context resets are no longer needed to save room on 1M-token models, and lists "subagents to protect context" under things to stop doing. Fresh sessions remain recommended between unrelated tasks and when starting a build from a written specification, which is what a chunk is. The owner's close-out decision stands on that basis.

Validation:

- `bash scripts/validate.sh` with the pinned tools exit 0 (154 tests, coverage 36%); governance audit 0 blockers, 0 required gaps, 0 warnings.

## Chunk Forty-Four - Frontier AI Engineering Research Record

Status: complete

Completion target: Task complete

Budget class: Medium

Timestamp: 2026-11-08T20:30:23-06:00

Objective: keep the evidence behind the 2026-11-08 rule changes in the repository, so later agents can check why a rule exists without the chat thread.

Acceptance criteria:

- [x] `docs/research/2026-11-08 - Frontier AI Engineering Practice Research.md` records method, limits, findings by theme, contested points, volatile facts with dates, what changed in the repository, and sources.
- [x] The AI Engineer channel is covered from real transcripts: 24 of 30 shortlisted 2026 talks, each listed with its link.
- [x] Jev and Laya are compared from TypeSafe's live documentation, Laya's published limits, and Adam's 2026-10-10 Laya qualification, with placement rules for harnesses, products, CI, and large data.

Known gaps:

- YouTube rate-limited caption downloads, so 20 of the 24 talks were summarised from the channel's own ai.engineer transcripts by reader agents without a second check. The AlixPartners and Ramp talks were not retrieved; McKinsey was retrieved but not analysed.
- OpenAI's "Harness engineering" post returned HTTP 403; its claims come from secondary sources and the author's talk.

Validation:

- Every source link in the record came from the research notes; the one speaker attribution questioned during review was checked against the transcript notes.

## Chunk Forty-Three - Build-Type Agent Playbooks

Status: complete

Completion target: Integration complete

Budget class: Large

Timestamp: 2026-11-08T20:18:42-06:00

Objective: give coding agents type-specific instructions they can be handed for each kind of build, delivered with every new project and offered to existing ones, grounded in the 2026-11-08 research (frontier-lab guidance, independent practitioners, security and evaluation sources, TypeSafe documentation, and Laya's published limits).

Acceptance criteria:

- [x] Eight playbooks in `templates/project/docs/playbooks/`: agent (harness), application, website, service, internal tool, automation, infrastructure, and documentation. Each covers what done looks like, preparation, build rules, verification, the failure modes agents produce in that build type, security, where a System One model fits (Jev hosted, Laya local), and when to stop and ask.
- [x] Written for current frontier models: plain language with reasons, no emphatic capitals, deterministic checks before model judgment, and evidence-based completion.
- [x] The scaffold delivers the matching playbook as `docs/build-playbook.md` (legacy `agentic-harness` gets the agent playbook), and the generated `AGENTS.md` routes to it.
- [x] `automation/change_control.py propose` offers the playbook to existing projects. A fresh scaffold still yields an empty upgrade manifest.
- [x] One type-to-playbook table (`PLAYBOOK_BY_TYPE` in `automation/project_naming.py`) serves both the scaffold and change control.
- [x] The standards index and README route to the playbooks. They are guidance inside existing standards, not new controls.

Also fixed: change control treated only `agent`, not legacy `agentic-harness`, as an agent project, so v0.3.0 harness projects were not offered their AI registers.

Validation:

- Throwaway `application` and `agent` projects scaffolded from the new templates: the application's own `scripts/governance-check.sh` exited 0, the agent passed schema validation, and `change_control.py propose` on the fresh agent project produced 0 actions.
- New tests: every project type has a playbook template; the scaffold delivers the matching playbook; `AGENTS.md` routes to it; change control offers the right playbook and AI registers to existing projects.
- `bash scripts/validate.sh` exit 0 (154 tests, coverage 36%); governance audit 0 blockers, 0 required gaps.

## Chunk Forty-Two - One AI Agent (Harness) Intake Choice

Status: complete

Completion target: Task complete

Budget class: Medium

Timestamp: 2026-11-08T20:11:35-06:00

Objective: carry out the owner decision that an agent is a harness. The intake offers one "An AI agent (harness)" choice instead of separate "AI helper" and "agentic harness" choices, and every agent project gets the harness record, from every entry point.

Finding: the v0.3.0 harness feature was only partly wired. A project the GUI created with type `agentic-harness` failed its own `project-control.yaml` schema check, `change_control.py` mapped it to the web-application use case, headless routed it to the applications folder (fixed in Chunk Forty), and the Freedom manifest could not request it.

Acceptance criteria:

- [x] GUI: one agent purpose, which always shows the AI-topology step. The old `harness` value is kept only as an alias for the canonical `agent` type.
- [x] `agent` stays the one canonical project type, already wired through schema, compliance, change control, and Freedom. `agentic-harness` is accepted as a legacy v0.3.0 type and validates.
- [x] Every agent project gets `docs/harness/README.md` and a `harness_profile`. When the topology was not asked (headless, terminal, or advanced settings), it is recorded as `undecided` with instructions to choose before the first model call, rather than guessed.
- [x] Headless, `new_build.sh`, `new_build.ps1`, and `freedom.tool.yaml` accept an optional harness topology and description, and the terminal launchers ask the topology question for agent builds.
- [x] README describes the single choice.

Not done, deliberately:

- The README screenshots still show the v0.3.0 choices. A carry-forward flag tracks retaking them.
- The harness README template's content is refreshed in Chunk Forty-Five, not here.
- The PowerShell prompt was not executed locally (no PowerShell on this machine).

Validation:

- `bash scripts/validate.sh` exit 0 (150 tests, coverage 36%); governance audit 0 blockers, 0 required gaps.
- Focused suites for GUI, scaffold, schema, headless, and change control: 53 tests passed, with new tests for the single choice, the legacy alias, undecided and chosen topologies, topology rejection, and legacy harness schema validity.
- A dry run of `bash automation/new_build.sh --build-type agent` asked the topology question, previewed `~/01. Code/03. Agents/topology-probe`, and created nothing.

## Chunk Forty-One - Freedom Dispatcher Relative Tool Working Directory

Status: complete (delivered as a draft pull request; merging is the owner's decision)

Completion target: Task complete

Budget class: Tiny

Timestamp: 2026-11-08T20:04:39-06:00

Objective: let `freedom.tool.yaml` keep a portable `cwd: "."` by having the Freedom dispatcher resolve a relative `cwd` against the manifest's own folder, instead of restoring an absolute workstation path in this public repository.

Acceptance criteria:

- [x] `the-freedom-engine-os` dispatcher: `invoke_subprocess` takes an optional `manifest_dir`, filled by `main.py` from `registry.get_manifest_path()`. Absolute paths, a missing `cwd`, and tools without a recorded manifest path behave as before.
- [x] Built in an isolated worktree from that repository's `origin/main`. Its active `agent/stage-c-overnight-turnover` checkout, which holds uncommitted 2026-09-05 path edits and three unpushed commits, was not touched.
- [x] That repository's rules were followed: governance preflight passed, and a testing summary was added under `docs/live-tests/`.
- [x] `freedom.tool.yaml` documents the relative `cwd` contract.

Validation:

- `test_dispatcher_cwd.py`: 5 tests passed, including a real subprocess.
- The dispatcher engine ran New Build's real manifest with `--plan` appended and returned `status: planned`. Without the manifest folder it reproduced the original defect. Nothing was created.
- Delivered as draft PR #73 (`fix/relative-tool-cwd`). The live FastAPI service run is held, because a real create would scaffold a project. A carry-forward flag tracks the merge.

## Chunk Forty - Workspace Paths And Preview Routing

Status: complete

Completion target: Task complete

Budget class: Small

Timestamp: 2026-11-08T19:59:12-06:00

Objective: finish the 2026-09-05 home-folder path work so New Build works with numbered workspace folders (`01. Code`, `03. Agents`, `02. Applications`) without hard-coding one machine's layout, and make the terminal previews impossible to drift from the real routing.

Context: the 2026-09-05 edits were found uncommitted on a base eight commits behind `origin/main`. They are preserved unchanged on the local branch `wip/2026-09-05-path-migration` (`564a23a`). On synced `main`, importing the GUI tried to create `~/code/Applications`, which on this workstation resolves through the temporary `code` alias to a stray `~/01. Code/Applications`. The sandbox blocked it and the GUI test module errored.

Acceptance criteria:

- [x] `automation/workspace_paths.py` ignores a numeric ordering prefix when recognising code-root and category folders, reuses an existing category folder (real folders before aliases), and treats the parent of a category folder as the code root. Public defaults stay `~/code/agents` and `~/code/Applications`.
- [x] Resolving paths never creates folders. The GUI creates missing category folders in `main()` at launch, not at import, and its folder pickers default to the detected code root.
- [x] `new_build_headless.py --plan` runs the same validation and routing as a real build and writes nothing. `new_build.sh` and `new_build.ps1` preview through it and no longer carry their own code-root logic.
- [x] Headless routes `agentic-harness` projects to the agents folder, matching the GUI (`AGENT_PROJECT_TYPES` in `automation/project_naming.py`).
- [x] `master_env.py` registry gating from the preserved branch is re-applied: `set` and `merge` accept only keys already reviewed into the master registry.
- [x] README, INSTALL, architecture, and automation reference describe the detection rules.

Not done, deliberately:

- The path edits on the preserved branch were not merged. Upstream commit `5e68ca6` had already replaced the `change_control.py` Graphify block and the runbook path with portable versions, and the remaining edits hard-coded one workstation's layout.
- The PowerShell create path was not executed locally (no PowerShell on this machine). The Windows CI job parses it with PSScriptAnalyzer and smoke-tests `-Version` only.

Validation:

- A dry run on this workstation previewed `/home/adamgoodwin/01. Code/03. Agents/preview-probe` for a harness through `bash automation/new_build.sh`, aborted at the confirmation prompt, and created nothing (no stray `Applications` folder).
- New tests cover prefix detection, alias preference, side-effect-free resolution, `--plan` (no writes, harness routing, validation failure), and harness routing.
- `bash scripts/validate.sh` with the pinned `requirements-dev.txt` tools (ruff 0.15.21, mypy 2.2.0, coverage 7.15.0) exit 0: compliance (0 required gaps), schema, ruff lint and format, mypy, shellcheck, secret scan, 141 unit tests, coverage 35% against the 25% floor.

## Chunk Thirty-Nine - Build-To-Sale Lifecycle Standard

Status: complete

Completion target: Integration complete

Budget class: Small

Timestamp: 2026-09-30T10:43:32-06:00

Objective: make the owner-supplied Build-to-Sale Operating System a cross-project standard, so projects intended for sale carry market validation, pre-sale, commercial readiness and a funding, credits and partners search alongside the existing engineering controls.

Owner decision: Adam Goodwin, 2026-09-30, approved cross-project use after it was first applied to Span OS, and asked that the lifecycle include a search for grants, loans, hosting credits and partners.

Acceptance criteria:

- [x] `docs/standards/build-to-sale-lifecycle-standard.md` (STD-ENG-025) holds adoption rules in Part A (scope, relationship to existing standards, core rules, funding/credits/partners track, agent boundaries, document locations) and the source framework as Part B, with headings shifted one level and text otherwise unchanged.
- [x] The standards index, context map and governance-source alignment examples route to it. It is not a mandatory startup read.
- [x] The workspace-level `CLAUDE.md` carries a short summary, following the STD-ENG-022 distribution pattern.
- [x] A carry-forward flag records the deferred distribution work.

Not done, deliberately:

- No scaffold template, managed-upgrade block, `project-control.yaml` field or schema change. The owner decides scope and order (carry-forward flag).
- No alignment review of existing projects. Span OS applied the framework directly on 2026-09-30; GazeCut and others have not been reviewed.

Validation:

- `PYTHON=py bash scripts/validate.sh` exit 0: compliance (0 required gaps), schema, lint, secret scan, 129 unit tests.
- `py automation/governance_audit.py .`: 0 blockers, 0 required gaps, 3 warnings (existing carry-forward flags due for review). Report: `docs/audits/governance-audit-2026-09-30.md`.

## Chunk Thirty-Eight - AI Coding Best Practices Fold-In

Status: complete

Completion target: Integration complete

Budget class: Medium

Timestamp: 2026-09-02T15:21:24-06:00

Objective: fold the plan-once, run-chunks pattern approved in the AI Coding Best Practices knowledge base (POL-AIC-001, STD-AIC-001 to 005, ADR-0001 to 0005, approved by the owner on 2026-09-02) into the generated project templates without changing this repository's standards.

Owner decision: Adam Goodwin, 2026-09-02, approved folding the pattern into the templates.

Acceptance criteria:

- [x] `CLAUDE.template.md` is the one-line import `@AGENTS.md`. `AGENTS.template.md` is the single canonical instruction file in the STD-AIC-001 shape (What this is, Start, Commands, Rules, Finish a chunk, Read when relevant), 55 lines, and still carries every phrase the scaffold tests and the managed-block fragments require. `AI_BOOTSTRAP.template.md` holds commands only, with the `- Lint:`, `- Test:`, and `- Build:` lines the compliance report reads.
- [x] `docs/current-build-pathway.template.md` uses runner-readable chunks (`### P-NN - Title`, `Status: Ready`, `Runner:`, `Files:` allow-list) and the plan-once, approve-once, fresh-session-per-chunk work pattern.
- [x] `START_HERE.template.md`, `docs/context-map.template.md`, `docs/standards/README.template.md`, and `project-control.template.yaml` route to the AIC standards by name (canonical copies stay in the knowledge base) and tighten the instruction-file budgets (AGENTS.md 4 KB, CLAUDE.md 1 KB).
- [x] `automation/change_control.py` skips managed-block appends to `CLAUDE.md` and `AI_BOOTSTRAP.md` when `CLAUDE.md` is an import-only file, so an upgrade cannot double-load guidance in the new layout. Two new tests cover it, and a freshly scaffolded project now yields an empty upgrade manifest.
- [x] `README.md` and `docs/user-guide.md` describe the generated instruction files as they now are.

Not done, deliberately:

- The runner itself (`scripts/agent/`, hook wiring) is not scaffolded. It stays pinned in the knowledge base under `reference/agent-runner/` with the adoption process PRC-AIC-002, to avoid a third copy that drifts.
- This repository's own `AGENTS.md`, `CLAUDE.md`, and `AI_BOOTSTRAP.md` still follow the compact-after-chunk close-out. See the new carry-forward flag.
- The template `AGENTS.md` is 961 words against the STD-AIC-001 target of about 600, because the scaffold tests mandate the full Graphify policy text and ten governance phrases. Projects slim their own copy.
- No standard in `docs/standards/` was changed.

Validation:

- `PYTHON=py bash scripts/validate.sh` exit 0: compliance (0 required gaps), schema, ruff lint and format, mypy, shellcheck, secret scan, 129 unit tests.
- A throwaway `application` project scaffolded from the new templates: `bash automation/governance_check.sh` exit 0, 0 required gaps, 5 recommended items (command placeholders and optional files).
- `python automation/governance_audit.py .`: 0 blockers, 0 required gaps, 0 warnings. Report: `docs/audits/governance-audit-2026-09-02.md`.

## Chunk Thirty-Seven - Public Documentation And GitHub Metadata

Status: complete

Completion target: Release ready

Budget class: Tiny

Objective: make the new complexity and periodic governance-alignment controls visible in the public documentation and GitHub repository information.

Acceptance criteria:

- [x] The public README explains both controls in plain language and links directly to their canonical standards.
- [x] The user guide, project manual, generated README/manual, and automation reference describe the new scaffolded controls consistently.
- [x] The GitHub repository description and topics surface code quality, cyclomatic complexity, and the 90-day alignment behavior.
- [x] The additions remain under `Unreleased`; no version tag or GitHub Release is created without a separate version decision.

Validation:

- Focused scaffold, change-control, and schema tests passed (11 tests).
- `bash automation/governance_check.sh .` passed with zero required gaps.
- `scripts/validate.ps1` passed completely: ruff, mypy, PowerShell analysis, shellcheck, secret scan, 127 tests, launcher smoke tests, and Windows package build.
- GitHub repository metadata was read back after update and showed the new description plus `code-quality` and `cyclomatic-complexity` topics.

Completed: 2026-08-31T13:49:39-06:00

## Chunk Thirty-Six - Complexity Controls And Governance Alignment

Status: complete

Completion target: Integration complete

Budget class: Small

Objective: add plain-language cyclomatic-complexity controls and a lightweight periodic check-back from governed builds to this governance source.

Acceptance criteria:

- [x] A controlled complexity standard defines the metric's limits, advisory bands, test companion, anti-gaming rule, rollout, and exception evidence.
- [x] A higher-level alignment standard prompts active builds every 90 days and before relevant release work without becoming an ordinary-startup check.
- [x] Source instructions, project templates, the workspace umbrella, and managed upgrades carry concise prompts.
- [x] New project controls default complexity to advisory mode and record governance-source cadence without overriding local risk or governance decisions.
- [x] Schema, scaffold, and change-control tests cover the new controls and distribution paths.

Known baseline: Ruff C901 currently reports 13 existing functions above 10, ranging from 11 to 37. They remain advisory and are not an authorization for unrelated refactoring.

Stop condition: stop after validation and distribution are proven; do not refactor existing complexity findings or promote the advisory control to a blocking gate without a separate decision.

Validation:

- `python -m unittest tests.test_schema_validation tests.test_scaffold_project tests.test_change_control` passed (11 tests).
- Full `unittest` suite passed (127 tests); coverage remained above the enforced floor at 34%.
- Ruff lint and format checks passed; the advisory C901 report retained the 13-finding baseline with no new finding from this chunk.
- Governance preflight and audit passed with zero required gaps; audit report `AUD-ENG-010` was refreshed.
- Local mypy execution remains blocked by Windows Application Control as recorded in risk `R-009`; the unchanged CI gate remains authoritative for mypy.

## Chunk Thirty-Five - Repository Audit And Portability Remediation

Status: complete

Completion target: Task complete

Budget class: Small

Objective: audit the governance source, refresh stale control records, and remove verified portability failures without expanding into the strategic Tier 2/3 backlog.

Acceptance criteria:

- [x] Governance preflight and automated audit have no blockers or required gaps.
- [x] Active/generated guidance contains no user-specific operational filesystem paths; historical audit and archive records remain unchanged.
- [x] Architecture and generated guidance describe current module boundaries and portable discovery paths.
- [x] Open carry-forward flags can record a review date without being falsely treated as abandoned.
- [x] CI installs one pinned validation toolchain and cancels superseded runs within a bounded timeout.
- [x] Risk, change, backlog, carry-forward, and pathway records reflect the 2026-08-31 review.
- [x] Focused tests pass; any full-gate limitation is recorded without weakening enforcement.

Stop condition: stop before any risk-tier/governance-level decision, dependency adoption, provider change, or broader backlog item that requires owner direction.

## Recent Completed Work

| Step | Status | Timestamp | Notes |
|------|--------|-----------|-------|
| Chunk Twenty-Three - Graphify Policy Consolidation | complete | 2026-06-12T15:54:47-06:00 | Consolidated Graphify guidance across live instructions, templates, managed upgrade blocks, tests, and handoff files. |
| Chunk Twenty-Four - Graphify Folder Consolidation | complete | 2026-06-12T17:50:14-06:00 | Single master Graphify Tool folder; removed duplicate root graphify-out/; updated all paths. |
| Chunk Twenty-Five - Completion States And Stop Rules | complete | 2026-06-12T18:58:28-06:00 | Honest completion states, human-owned project completion, anti-loop stop rules, managed upgrade guidance. |
| Chunk Twenty-Six - Lean Startup And Preflight Integration | complete | 2026-06-13T09:13:03-06:00 | Lean startup integrated into context hygiene, live/generated instructions, and managed upgrade blocks. |
| Chunk Twenty-Seven - Cost-Effective Agentic Context Integration | complete | 2026-06-13T10:18:57-06:00 | Repo-memory, budget classes, context-map, summary-only scouts integrated without new mandatory startup reads. |
| Chunk Twenty-Eight - Governance Package Documentation Closeout | complete | 2026-06-13T10:25:50-06:00 | Public docs, generated docs, and shared handoffs updated for lean startup and cost-effective context. |
| Chunk Twenty-Nine - Token-Friendly Startup Tightening | complete | 2026-06-16T18:28:42-06:00 | Lean startup clarified; START_HERE.md made conditional; no-full-rebuild-after-clear rule propagated. |
| Chunk Thirty - Compaction Restart Efficiency | complete | 2026-06-16T19:05:02-06:00 | Active-plan routing indirect through START_HERE.md; post-compaction restart guidance added. |
| Chunk Thirty-One - Housekeeping | complete | 2026-06-16 | Hard-coded personal names removed from automation; AGENTS.md trimmed to router; pathway split. |
| Chunk Thirty-Two - Document Supersession Enforcement | complete | 2026-06-16 | Supersession scanner in change_control.py; Document Supersession section in audit report; GUI summary; template banner. |
| Chunk Thirty-Four - GitHub Resource Efficiency Ingestion | complete | 2026-07-26T20:22:46-06:00 | STD-ENG-022 added as a single canonical copy; guardrail summary distributed through the workspace-level CLAUDE.md and the project bootstrap template; no per-repo standard copy, no enforced checks. |
| Chunk Thirty-Five - Repository Audit And Portability Remediation | complete | 2026-08-31 | Audit/control records refreshed, portable Graphify discovery added, the validation toolchain pinned, and current GitHub Actions bounded and upgraded; CI and Windows packaging passed. |
| Chunk Thirty-Six - Complexity Controls And Governance Alignment | complete | 2026-08-31T13:24:17-06:00 | STD-ENG-023 and STD-ENG-024 added; advisory complexity controls and 90-day check-back prompts distributed through source instructions, scaffolds, managed upgrades, and the workspace umbrella. |
| Chunk Thirty-Seven - Public Documentation And GitHub Metadata | complete | 2026-08-31T13:49:39-06:00 | Public and generated documentation now explain the controls; GitHub description and topics surface the addition without creating an unapproved version release. |
| Chunk Thirty-Nine - Build-To-Sale Lifecycle Standard | complete | 2026-09-30T10:43:32-06:00 | STD-ENG-025 added as a single canonical copy with a workspace `CLAUDE.md` summary; scaffold and upgrade distribution deferred to a carry-forward flag. |
| Chunk Forty - Workspace Paths And Preview Routing | complete | 2026-11-08T19:59:12-06:00 | Numbered workspace folders detected without hard-coding a layout; side-effect-free path resolution; launchers preview through `new_build_headless.py --plan`; harness routing matches the GUI; master env registry gating re-applied. |
| Chunk Forty-One - Freedom Dispatcher Relative Tool Working Directory | complete | 2026-11-08T20:04:39-06:00 | Dispatcher resolves a relative tool `cwd` against the manifest folder; delivered as draft PR #73 in the-freedom-engine-os. |
| Chunk Forty-Two - One AI Agent (Harness) Intake Choice | complete | 2026-11-08T20:11:35-06:00 | One agent choice that always asks the AI topology; every agent project gets a harness record; v0.3.0 harness projects now pass schema validation. |
| Chunk Forty-Three - Build-Type Agent Playbooks | complete | 2026-11-08T20:18:42-06:00 | Eight agent-facing playbooks delivered as `docs/build-playbook.md` by project type and offered to existing projects through change control. |
| Chunk Forty-Four - Frontier AI Engineering Research Record | complete | 2026-11-08T20:30:23-06:00 | Dated research record: AI Engineer talks, lab guidance, practitioner, evaluation, and security sources, and the Jev and Laya placement analysis. |
| Chunk Forty-Five - Frontier-Model Rules Refresh | complete | 2026-11-08T20:31:59-06:00 | Fresh-session close-out here; frontier-model rules in AI_BOOTSTRAP, context hygiene, use-case standard, policy, and harness templates; knowledge-base change proposal for owner review. |
| Chunk Forty-Six - Documentation Scaffold Passes Its Own Compliance Check | complete | 2026-11-08T21:01:34-06:00 | One table drives the documentation type's skipped docs and its `required_docs`; every type at every governance level now passes its own compliance report; audit backlog B-14 closed. |
| Chunk Forty-Seven - Secret Env Files Restricted To The Owner On Windows | complete | 2026-11-08T21:24:23-06:00 | `write_private_text` restricts secret env files before writing (mode 0600 on POSIX, `icacls` on Windows) and fails closed; on Windows, explicit entries copied from some parent folders remain (Chunk Forty-Eight). |
| Chunk Forty-Eight - Exact Single-Entry Windows Access List For Secret Files | complete | 2026-11-09T18:05:57-06:00 | One `SetNamedSecurityInfoW` call (ctypes) replaces a secret file's whole Windows access list with one protected entry for the current user. Explicit entries from parent folders or other tools are removed; writes still fail closed. |
| Chunk Fifty - Token-Efficient Handover And Agent Writing Guidance | complete | 2026-11-09T20:29:23-06:00 | The context hygiene standard and project templates now carry the next-chunk handover and compact agent-writing guidance as guidance, not rules. Another agent's compression notes were compared; the compression tool and the Jev or Laya checking layer are deferred. |
| Chunk Forty-Nine - First Tests For The Stripe Provisioning Module | complete | 2026-11-09T21:23:40-06:00 | 23 tests take `stripe_provision.py` from 0% to 86% covered, with no network or real key. Two fixes: a mode such as `Live` no longer skips the `--allow-live` check, and apply no longer drops a new webhook secret when the manifest names no `secret_env`. Coverage floor 25 to 41. |
| Chunk Fifty-One - Tests For The Master Env Commands | complete | 2026-11-09T21:41:21-06:00 | 19 new tests take `master_env.py` from 36% to 99% covered, with temporary files only. Fix: `set` refuses a value with a line break, which used to read back as a blank key that `missing` printed. An env writer bug found here is ready as Chunk Fifty-Two. Coverage floor 41 to 43. |

Full history: `docs/archive/pathway-history.md`

## Chunk Thirty - Compaction Restart Efficiency

Status: complete

Completion target: Task complete

Budget class: Small

Objective: make turnovers after compaction, context clear, and fresh restarts faster by routing agents through the latest handoff/work packet and the active plan named by `START_HERE.md` instead of hardcoding historical pathway reads.

Acceptance criteria:

- [x] Source instructions route material work to the active plan named by `START_HERE.md`, defaulting to `docs/current-build-pathway.md`.
- [x] Generated project templates inherit the same active-plan indirection.
- [x] Context hygiene source and template include a concise post-compaction/context-clear restart checklist.
- [x] Existing-project managed instruction upgrades carry the restart guidance.
- [x] Focused tests cover the new active-plan and restart guidance.

Validation:

- `python3 -m unittest tests.test_scaffold_project tests.test_change_control` passed.
- `bash automation/governance_check.sh .` passed with 0 required gaps.
- `bash scripts/validate.sh` passed with 38 tests.

## Chunk Thirty-One - Housekeeping

Status: complete

Completion target: Task complete

Budget class: Small

Objective: remove hard-coded personal names from automation scripts, trim AGENTS.md to a lean router, and split the pathway doc to under 200 lines.

Acceptance criteria:

- [x] `automation/change_control.py`: removed `"name: Adam Goodwin"` replacement and replaced absolute `/home/adamgoodwin` Graphify paths with `~`-relative paths.
- [x] `automation/new_build_headless.py`: removed `"name: Adam Goodwin"` replacement.
- [x] `AGENTS.md`: trimmed from 155 lines to ~77 lines (router only; Fundamentals-First/Context Hygiene/Graphify point to `CLAUDE.md`).
- [x] `docs/current-build-pathway.md`: split to under 200 lines; full history archived to `docs/archive/pathway-history.md`.

Inputs:

- `automation/change_control.py`
- `automation/new_build_headless.py`
- `AGENTS.md`
- `docs/current-build-pathway.md`

Validation:

- `python3 -m py_compile automation/change_control.py automation/new_build_headless.py` passed.
- `bash scripts/validate.sh` passed.

## Chunk Thirty-Three - Audit Tier-1 Remediation

Status: complete

Completion target: Integration complete

Budget class: Large

Objective: execute the five Tier-1 recommendations from docs/audits/repository-audit-2026-07-10.md and record the remaining tiers as a durable backlog.

Acceptance criteria:

- [x] Real validation gate: ruff (lint+format), mypy, shellcheck, PSScriptAnalyzer, and an explicit secret-hygiene step wired into `scripts/validate.sh` and `scripts/validate.ps1`, with CI installing the tools; `machine_enforcement` entries in `project-control.yaml` now map to real steps.
- [x] `docs/standards/governance-level-standard.md` (STD-ENG-009) defines levels 0-4 with a single crosswalk to risk tiers and autonomy; derive-vs-independent contradiction resolved in `docs/user-guide.md`.
- [x] One canonical doc home per rule: `AI_BOOTSTRAP.md` (86 lines) is the canonical agent-instruction source; `CLAUDE.md` (32) and `AGENTS.md` (17) are routers; DoR/DoD owned by ship-ready; four stub standards folded into parents and tombstoned.
- [x] One canonical code implementation per behavior: `automation/env_file.py` (shared .env parsing), `automation/project_naming.py` (slugify, reserved names, governance/risk tables, INITIAL_SCOPE); `new_build.sh` rewritten as a thin wrapper over `new_build_headless.py`; GUI gains reserved-name and slug-length guards and a Windows-correct PATH.
- [x] June metadata remediation executed: 40 docs given compliant headers; `python automation/governance_audit.py .` reports 0 blockers, 0 required gaps, 0 warnings (was 119); implementation plan's illegal `archived` statuses and bogus citation fixed.
- [x] Tier 2/3 recommendations and Tier-1 residuals recorded in `docs/audits/remediation-backlog-2026-07-10.md` (AUD-ENG-004).

Validation:

- `bash scripts/validate.sh` passed end-to-end on Windows Git Bash (compliance, schema, ruff, mypy, shellcheck, secret scan, 120 unit tests).
- `python automation/governance_audit.py .` exit 0, zero findings.
- `./scripts/validate.ps1` (including the Windows launcher build) run at close-out.

## Chunk Thirty-Four - GitHub Resource Efficiency Ingestion

Status: complete

Completion target: Integration complete

Budget class: Small

Objective: ingest the downloaded GitHub resource-efficiency standard as a single canonical copy and distribute a short guardrail summary to every project without generating a per-repo copy of the standard.

Owner decision: use the workspace-level `CLAUDE.md` at the code-workspace root as the distribution point instead of the per-repo generation model proposed by the source document. Guardrails, not enforced checks.

Acceptance criteria:

- [x] `docs/standards/github-resource-efficiency-standard.md` (STD-ENG-022) holds the full standard, with the source document's transmittal brief replaced by a distribution section, MUST language relaxed to guardrails, volatile GitHub product facts isolated and marked unverified, and skipped work recorded.
- [x] Guardrail summary added to the workspace-level `CLAUDE.md`, inherited by every project under the code-workspace root in a Claude Code session.
- [x] Summary mirrored in the standard itself so it is reproducible if the unversioned workspace file is lost.
- [x] Routed in `docs/standards/README.md`, `docs/context-map.md`, `START_HERE.md`, and `AI_BOOTSTRAP.md`.
- [x] Templates carry the guardrails and a pointer rather than a copy: `templates/project/AI_BOOTSTRAP.template.md`, `docs/standards/README.template.md`, `docs/context-map.template.md`.

Inputs:

- `~/Downloads/2026-07-26-github-resource-efficiency-standard.md`

Not done, deliberately:

- No machine-enforced checks. Any future check starts as a reporting control, not a blocking gate.
- No `GOVERNANCE-MANAGED` block in `automation/change_control.py`, so existing repos generated before this chunk do not receive the guardrails in their own instruction files. They are still covered in Claude Code through the workspace `CLAUDE.md`.
- The volatile GitHub product facts were not re-verified against GitHub documentation.

Validation:

- `bash scripts/validate.sh` exit 0 (compliance, schema, ruff, mypy, shellcheck, secret scan, 120 unit tests).
- `python -m unittest tests.test_scaffold_project tests.test_change_control` passed; template edits did not break scaffold or managed-upgrade expectations.
- `python automation/governance_audit.py .` — 0 blockers, 0 required gaps, 1 warning (the pre-existing Tier 2/3 carry-forward flag age, unrelated to this chunk). Report: `docs/audits/governance-audit-2026-07-26.md` (AUD-ENG-009).
