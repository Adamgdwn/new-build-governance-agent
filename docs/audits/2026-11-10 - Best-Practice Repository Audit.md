# Best-Practice Repository Audit — New Build Governance Agent

Document ID: AUD-ENG-015
Version: 1.0
Status: active
Owner: Project Owner
Approver: Project Owner
Effective Date: 2026-11-10
Last Reviewed: 2026-11-10
Next Review: 2026-12-08

Requested by Adam Goodwin on 2026-11-10: check that the improvements from the
2026-11-08 research, and the outside notes added on 2026-11-09, were captured
properly, and that this is genuinely a repository of best practices for
building.

Builds on AUD-ENG-003 (repository audit, 2026-07-10) and AUD-ENG-004 (its
remediation backlog).

---

## The Two Answers

**1. Were the improvements captured properly? Mostly yes, in this repository
and in new projects. Not for existing projects.**

The research is in this repository's rules and in what a new project
receives: the eight build playbooks, the harness record, the frontier-model
rules, the Jev and Laya placement, and the 2026-11-09 writing guidance. A
reviewer traced 40 items from the research record: 23 are captured faithfully,
10 partly, 5 are missing, and 2 are stated but not done. The problems that
matter:

- Existing projects receive almost none of it. Change control creates only
  missing files, never refreshes text it added before, and would offer most
  existing projects the wrong playbook.
- The research says to test changes to instruction files and templates on a
  set of tasks, for success and cost. That was not done for the refresh, and
  the always-loaded files grew: `AI_BOOTSTRAP.md` by 18%, and a new project's
  `AGENTS.md` is 7.3 KB against its own 4 KB budget.
- Proposals P1 to P7 await the owner's decision, but their content already
  ships, while new projects are told the canonical rules for the same topics
  are in the unchanged knowledge base. Until the owner decides, new projects
  get two answers.
- A few research points are missing or only partly carried over (section 1).

**2. Is this genuinely a repository of best practices for building? Not yet.
It holds good building advice, but it does not give new projects the means to
follow it, and it does not consistently follow its own rules.**

- The advice is good. The eight playbooks are specific, current and
  right-sized.
- A new project gets no tests, no CI, no lint configuration, no `.gitignore`
  and no `.env.example`. Its only check confirms that files exist, and passes
  an empty project at every governance level. Its `project-control.yaml`
  claims that lint, tests and secret scanning are machine-enforced, and its
  `AGENTS.md` names hooks and a runner that are not in this repository.
- The building advice is 2.5% of the text a new project receives; standards
  and policy are 71%. The required reading before implementation is the
  policy and two standards, not the playbook.
- AUD-ENG-003's finding that new projects get "paperwork, not a paved road" is
  unchanged. This repository's own gate has improved a great deal since July,
  but the repository still breaks several of its own rules (section 4).

Recommendations 1 to 4 are the smallest set of changes that would make the
second answer "yes".

---

## Scope, Method And Finish Line

Finish line, set before the work started: both questions answered with
evidence checked against the files, a plain verdict, and a finite list of
recommendations for the owner to accept or reject. No chunks created, and no
standards or templates changed.

Method:

- All nine project types were scaffolded at governance level 2 into a scratch
  folder with `scaffold_project.scaffold_project()`, which writes only into its
  target. Each project's own `scripts/governance-check.sh` was then run.
- Three read-only reviewers covered:
  - **Capture trace.** The list was built from the research record's own
    findings, rules and contested points and from the 2026-11-09 lists, not
    from the chunk write-ups.
  - **Quality of the building guidance.** It was judged against the
    research's nine findings, AUD-ENG-003's best-practice comparison and named
    engineering practices.
  - **The repository's own rules.** Checked against AUD-ENG-003's five themes.
- Every finding below was verified by reading the cited file or running the
  cited check. Claims that did not hold are listed at the end.

Not examined:

- whether the playbooks improve agent results (no evaluation exists);
- the external AI Coding Practices knowledge base, hooks and runner;
- other repositories, including existing governed projects;
- GitHub settings such as branch protection;
- Windows behaviour at runtime.

---

## 1. Capture Of The Research

| Area (source) | This repository's rules | What a new project gets | Existing projects | Verdict |
|---|---|---|---|---|
| Per-build-type instructions (owner request) | Standards index | All eight types get their playbook | Offered by a guessed type | Captured for new projects |
| Agent means harness, one intake choice (decision 3) | Use-case standard | Agent playbook, harness README, one GUI choice | Harness README never offered | Captured for new projects |
| Fresh session per chunk (decision 2) | `AI_BOOTSTRAP.md` | `AGENTS.md` | Managed block still says "compact or reset" | Captured; old wording ships beside it |
| Instructions plain, short and measured (Finding 2) | Stated | `AGENTS.md` is 7.3 KB / 1,003 words against "about 600 words" and 4 KB | — | Stated, not done |
| Context and sessions (Finding 3) | Stated | Stated, with "about 1M tokens" written in, undated | — | Captured; a volatile fact is frozen in |
| Verification and evidence (Finding 4) | Stated | Policy, pathway and agent playbook | — | Captured, except "a turn that ends in prose is a progress report" |
| Evaluation (Finding 5) | Use-case standard | Agent playbook | — | Captured for agent products. Missing everywhere: testing changes to instruction files and templates, and evaluating the deployment |
| Security (Finding 6) | Partly | Agent playbook carries most of it | — | Partial (below) |
| Multi-agent work, cost and caching (Findings 7, 8) | Stated | Context hygiene standard, agent playbook | — | Captured |
| Protocols: `AGENTS.md` canonical (Finding 9) | Stated | `CLAUDE.md` is the one-line import | — | Captured |
| Jev and Laya placement | Use-case standard | A section in all eight playbooks | — | Placed. Weight discussed in section 3. Missing: "neither is a coding-agent model". The model registry ships only to agent projects |
| 2026-11-09 external notes | Context hygiene standard | Identical in the template | — | Captured; deferrals recorded as the owner's decision |
| Decisions 1 and 4 (Freedom `cwd: "."`; knowledge base not edited) | Done | — | — | Captured |
| Proposals P1 to P7 (pending) | Already in `AI_BOOTSTRAP.md` | Already in templates, while projects are routed to the unchanged knowledge base | — | Ahead of the owner's decision |

Verified details:

- **Existing projects.** `automation/change_control.py` creates a file only
  when it is missing (`build_manifest`, line 668). It skips any managed block
  whose markers are present (`has_managed_instruction_guidance`, line 661), so
  text it added before is never refreshed. The context hygiene block it adds
  still says "compact or reset before quality degrades" (line 98). The harness
  README is not in its file lists. It picks the playbook through
  `infer_project_profile` (line 564), which never reads `project-control.yaml`.
  That function returns only agent, application or automation, from the
  folder name and package files. So existing website, service, internal-tool,
  infrastructure and documentation projects can never be offered their own
  playbook.
- **Measurement.** The research record (lines 145-146) says to test changes to
  `AGENTS.md`, skills and templates on a golden set for success and cost. No
  rule here applies that to this repository's own instruction files, and no
  refresh chunk measured it. Commit `c59655f` grew `AI_BOOTSTRAP.md` from 9,923
  to 11,705 bytes.
- **Size and repetition.** `templates/project/AGENTS.template.md` is 7,262
  bytes and 1,003 words. The template `project-control.yaml` sets "about 600
  words" and `agents_md_target_kb: 4` (lines 84-85), and the AGENTS template's
  line 7 adds a third size rule ("under 80 lines"). Its lines 41 and 42 both say
  project completion is a human decision, because change control's required
  fragments at lines 200 and 234 differ only in capitalisation.
- **Old guidance beside new.** The reusable prompt block in the context
  hygiene template (line 324) says "Compact or reset before quality degrades".
  The pathway template (line 47) still sizes chunks to "one agent context
  window".
- **Pending proposals.** P1 (plain language, state a rule once) is at
  `AI_BOOTSTRAP.md:60`, P4's untrusted-configuration rule at line 66, and P7's
  System One guidance is in all eight playbooks. The template context map
  (line 30) and standards index (lines 36-37, 45-46, 52) send instruction,
  chunking, hook and model-routing questions to STD-AIC-001 to 005 in the
  knowledge base. This is not a breach of the owner's decision: editing this
  repository was the refresh's stated objective, and the knowledge base is
  untouched. It is a split source until P1 to P7 are decided.
- **Research points missing or partial:**
  - The CaMeL ordering (plan before reading untrusted data) appears nowhere
    outside the research record.
  - Keeping secrets and network access outside the agent is absent from the
    Harness Engineering Controls (use-case standard, lines 345-356).
  - Three rules do not reach the `AGENTS.md` or policy a new project gets: "a
    turn that ends in prose is a progress report" (`AI_BOOTSTRAP.md:61`),
    "treat configuration from an untrusted repository as code" (line 66), and
    "prefer settings to prompt wording" (line 67).
  - "Neither Jev nor Laya is a coding-agent model" and "evaluate the
    deployment" appear nowhere.
- **Unsourced specifics.** Four specifics in the agent playbook are not in the
  research record that is meant to hold the evidence. They may be right, but
  they are unsourced here:
  - each evaluation task runs three times and passes only if all three pass
    (line 24);
  - tool search past "a few dozen" tools (line 49);
  - weekly error analysis (line 76);
  - "a score of 0% usually means the task itself is broken" (line 99).

## 2. What A New Project Actually Receives

All nine project types were generated at governance level 2.

- **Playbooks and records.** Every type receives its matching playbook (2.4 to
  7.7 KB) and passes its own check. Agent projects also receive the harness
  README, model registry, prompt register, tool permission matrix and agent
  inventory. Documentation projects correctly skip the deployment guide and
  runbook.
- **No working machinery.** None receives a `tests/` folder, a CI workflow,
  lint or format configuration, a dependency manifest or lockfile, a
  `.gitignore` or a `.env.example`. `templates/project/` holds neither of the
  last two, yet the shipped `AGENTS.md` says variable names live in
  `.env.example` (line 34).
- **A file-presence gate.** The only check, `scripts/governance-check.sh`,
  confirms that files exist and that `project-control.yaml` has its fields.
  `tests/test_compliance_report.py` requires every fresh scaffold, at every
  governance level including 4, to pass the compliance report, with no code
  and no tests.
- **Claimed enforcement:**
  - `project-control.yaml` lists `machine_enforcement: [required-file-check,
    lint, tests, secret-scan]` (template lines 44-48); only the file check
    exists.
  - `AGENTS.md` labels three rules with hooks (`guard-protected-paths`,
    `stop-validate`) and names a runner (`scripts/agent/run-chunks.mjs`). None
    of these files exists in this repository, and
    `tests/test_scaffold_project.py:73` requires the hook label.
  - The preflight template runs the project's own file check before the
    central checker (lines 8-13), so the central one is never reached.
- **Standards.** A project receives the policy, the use-case, ship-ready,
  context hygiene, complexity and alignment standards, and the index. It does
  not receive the testing or security-and-secrets standards. Its index
  (`templates/project/docs/standards/README.template.md`):
  - lists four standards retired on 2026-07-10 as current (lines 35, 40, 42,
    47);
  - lists Testing and Security with no files behind them (lines 50-51);
  - leaves the delivered Context Hygiene standard unlinked;
  - routes five AI-coding topics to the knowledge base outside the project.
- **Proportions.** Of the 138,939 bytes of text an application project
  receives, standards and policy are 99,987 (71%) and the playbook 3,524
  (2.5%). The required reading before implementation is the policy, the
  use-case standard and the ship-ready standard (69,431 bytes). The playbook
  sits under "Read when relevant" in `AGENTS.md` (lines 51-53), and the context
  map, `START_HERE.md`, the README and the manual do not route to it.
- **Undefined autonomy codes.** Agent projects get an `autonomy_level` code
  (`scaffold_project.py:162`). The template use-case standard has dropped the
  A0 to A3 definitions that this repository's copy keeps (lines 330-336).

## 3. Quality Of The Building Guidance

The playbooks are good advice. The application and infrastructure playbooks,
read in full, are short, specific to the build type and current. They cover:
- evidence-based done criteria;
- server-side authorization per record;
- reviewed migrations that an agent never runs against production;
- plan-then-apply, with a person applying;
- deletion protection and backups outside the stack;
- the failure modes agents actually produce;
- clear points to stop and ask.

A reviewer's read of all eight reached the same verdict.

Verified gaps and problems:

- **Shipping and operating is thin.**
  - No playbook names a CI gate. The only "CI" is inside the documentation
    playbook's System One section (line 55).
  - Only the infrastructure playbook mentions rollback (line 18).
  - The service playbook has no health or readiness checks and no correlation
    IDs.
  - The agent playbook names prompt injection as a risk (line 93) but has no
    kill switch or injection test set, though the use-case standard requires
    both (template lines 260, 287).
  - The service, automation, internal-tool and documentation playbooks have no
    lockfile or pinning rule.
- **Accuracy slips.**
  - The application playbook's OWASP list uses 2017 names (lines 66-67).
  - "Never in ... state" (infrastructure, line 34) cannot be met with
    Terraform-style tools, which keep some secrets in state. The rule should be
    encrypted, access-restricted remote state.
  - "Point to code by file and line ... so the page cannot drift"
    (documentation, lines 30-31) gets it backwards: line references go stale
    with every edit.
  - Documentation projects are classified as the "Static / marketing website"
    use case (`scaffold_project.py:36`).
- **The always-loaded test rule contradicts the policy.** `AGENTS.md:30` says
  "Never modify or delete an existing test file". The policy a project receives
  forbids changing a test only *to make it pass*, allows a reviewed fix (line
  198), and asks agents to "write or update a test" (lines 126, 614).
- **Jev and Laya weight.** Every playbook has a "Where a System One model fits"
  section, and in all eight it is longer than the Security section; the
  documentation playbook has no Security section at all. The research's own
  evidence is that Laya failed its adoption test and stays disconnected, and
  that Jev's figures are vendor claims. The owner asked for both to be placed
  where they add the most value. Whether that means a section in every
  playbook is the owner's decision.
- **Tool-specific text in files meant for any coding agent:**
  - `/clear` and `/compact` (`AGENTS.md:49`, `CARRY_FORWARD.md:13`);
  - a 135-word Graphify paragraph (`AGENTS.md:56`);
  - a finish report that hard-codes `npm run` commands (ship-ready template,
    lines 386-389);
  - `Runner: claude / codex / human` (pathway template, line 89).
- **Frozen facts.** "About 1M tokens ... compact automatically" (context
  hygiene template, lines 97, 181) is untrue for many local models. The
  handoff heading hard-codes the `-06:00` time zone (line 266).
- **Copies that drift.** The policy template still carries its own Definitions
  of Ready, Done and Shipped (lines 374-407) beside the ship-ready standard's
  (lines 149-196); this repository's own policy has already removed that copy.
  The template use-case standard keeps the old four-tier review table, which
  this repository's copy replaced with a pointer to the risk classification
  standard.
- **Intake.**
  - The GUI cannot create service, infrastructure or documentation projects
    (its type map, `new_build_gui.py:108-117`).
  - "Other" becomes automation in the GUI but internal-tool in headless
    (`project_naming.py:96`).
  - The GUI lists Phi-4, a small language model, under "Non-LLM AI" (line 171).

## 4. Does The Repository Follow Its Own Rules

| AUD-ENG-003 theme | Now | Evidence |
|---|---|---|
| 1. Say/do gap | Improved here; unchanged for new projects | This repository's gate runs ruff, mypy, shellcheck, the tests, a coverage floor and a secret scan in CI on Ubuntu and Windows. New projects still claim enforcement that nothing performs (section 2). |
| 2. Duplication | Improved in code; unchanged in templates and instruction files | There is now one env-file module and one naming module. The secrets rule is stated word for word in `AGENTS.md:16`, `CLAUDE.md:20` and `AI_BOOTSTRAP.md:109`, and template copies drift (section 3). |
| 3. Checks at the wrong layer | Improved here; unchanged in design | The self-audit checks only that header fields exist. It passes while 12 documents are past their own Next Review date (11 of them due 2026-10-10), including the testing, security, ship-ready, risk-classification and governance-level standards and AUD-ENG-003 itself. |
| 4. Paperwork, not a paved road | Unchanged | Section 2. One bug was fixed (documentation projects now pass their own check) and playbooks were added. |
| 5. Ship-readiness | Improved for secrets; unchanged for release and update | Secret files are owner-only on Windows, and the env modules have tests and fixes. Apart from one workflow-maintenance commit (`08ef475`), nothing has changed the update, promotion or release code since July. |

Verified defects in this repository:

1. **The cross-project audit always records zero missing files and zero
   warnings.** `automation/audit_projects.py:96-100` and
   `new_build_gui.py:2377-2380` look for `FAIL: Missing required file` and
   `WARN:` lines. The checker they run, `automation/governance_check.sh`, hands
   off to `compliance_report.py`, which prints `REQUIRED GAP:` and
   `RECOMMENDED:` lines (lines 325-341). Only pass or fail survives, through
   the exit code. `audit_projects.py` has no tests.
2. **Releases are not gated.** Pushing a `v*` tag publishes the Windows release
   asset (`build-windows-launcher.yml`, lines 43-57) without depending on the
   Validate workflow. The whole workflow, including pull-request runs, has
   `contents: write` (lines 17-18).
3. **Windows `PATH` handling.** `promotion_execute.py:44-47` and
   `promotion_checks.py:72-75` split and rejoin `PATH` on `:`, which breaks
   `C:\...` entries on Windows.
4. **The secret scan is narrow.** It covers five locations, skips everything
   under `docs`, and three of its four patterns need a leading `=`
   (`tests/test_secret_hygiene.py`). `.gitignore` ignores only `.env`.
5. **Python minimum.** The Windows gate accepts Python 3.8
   (`scripts/validate.ps1:21,30`) and the README says Python 3.8+ (line 471),
   while `pyproject.toml` requires 3.11.
6. **The approval rules do not fit a solo owner.**
   - The document control standard requires the project owner and the
     technical lead for policy and standard changes (lines 394-395).
   - The technical lead here is "codex session" (`project-control.yaml:14-16`).
   - The governance level standard (line 82) sends solo owners to a
     single-owner approval clause that the document control standard does not
     contain.
7. **Start-up documents grew.**
   - The README is 501 lines, against the July target of about 150.
   - The pathway, which agents follow for material work, is 73.7 KB.
   - `docs/manual.md` and `docs/roadmap.md` are still unfilled template text.
8. **Rotated-out secrets stay in project files.** The `env_sync` writer keeps
   the old value on `--overwrite`. Chunk Fifty-Three is ready to fix it.
9. **Wrong write locations in the manifest.** `freedom.tool.yaml` declares
   that New Build writes under `~/code/agents` and `~/code/Applications`
   (lines 5-6, 129, 135-136). That is the public default, but on this machine
   New Build writes under the numbered folders it detects.
10. **Tests check wording, not structure.** `tests/test_scaffold_project.py`
    has 119 `assertIn` calls, up from about 40 in July, and they lock in the
    hook label and the `/clear` wording in `AGENTS.md`.

---

## Recommendations

For the owner to accept, amend or reject. None of these has been added to the
pathway as a chunk. Sizes are estimates, in chunks.

Recommendations 1 to 4 are the line at which this becomes a repository of best
practices for building: a new project starts with working machinery, honest
claims, the standards it is governed by, and the building guidance first.

1. **Give new projects a paved road.** Ship a `.gitignore`, a `.env.example`, a
   sample test, and a validate script that runs the project's lint, test and
   build commands and fails while any is still `<fill in>`. Add a CI workflow
   that runs that script. (AUD-ENG-004 B-6, items 1-3.) About 2 chunks.
2. **Make new projects' claims true.** Have preflight run that validate script.
   Until hooks and a runner ship, mark `machine_enforcement` and the hook and
   runner names as planned, and stop the tests from requiring that text. About
   1 chunk, or part of recommendation 1.
3. **Ship the standards a project is governed by.**
   - Add the testing and security-and-secrets standards.
   - Remove the four retired standards from the template index, and link the
     standards that are delivered.
   - Restore the autonomy definitions.
   - Generate template copies from the canonical files, so they stop
     drifting.

   (B-6 item 4.) 1 to 2 chunks.
4. **Put the building guidance first.**
   - Make the playbook the required read before building, and the first row
     of the context map.
   - Bring `AGENTS.md` within its own 4 KB budget: fix the case-sensitive
     fragments, and move the Graphify paragraph and the vendor commands out.
   - Make its test rule match the policy.

   About 1 chunk.
5. **Close the playbook gaps.**
   - Add one short shared "ship and operate" block to every code playbook:
     CI gate, rollback, health checks, dependency scanning and lockfiles.
   - Fix the accuracy slips.
   - Source or soften the four unsourced evaluation specifics.
   - Add the missing research rules: the CaMeL ordering, secrets and network
     access outside the agent, prose-only turns, untrusted configuration,
     settings over wording, and "neither Jev nor Laya is a coding-agent
     model".

   1 to 2 chunks.
6. **Reach existing projects.** Change control should read `project_type` from
   `project-control.yaml`, offer the right playbook and the harness README, and
   refresh its own managed text through a reviewed sync. 1 to 2 chunks.
7. **Decide P1 to P7.** Until then, label the shipped text derived from them as
   pending, so new projects do not get two answers. The owner's decision, then
   about 1 chunk of template edits.
8. **Measure instruction changes, as the research says.** Run a small task set
   before and after changes to `AGENTS.md`, `AI_BOOTSTRAP.md` and the
   templates, recording success and token cost. About 1 chunk.
9. **Fix the verified defects in this repository** (section 4, items 1-5 and
   8-10): the audit parser, release gating and permissions, Windows `PATH`,
   the secret scan and `.gitignore`, the Python minimum, Chunk Fifty-Three,
   the manifest's write locations, and scaffold tests that check structure
   instead of wording. About 3 chunks.
10. **Owner decisions on weight and process.** These cover:
    - how much space Jev and Laya get in the playbooks;
    - a single-owner approval rule;
    - the 12 overdue reviews;
    - the README length;
    - the unfilled manual and roadmap.

    About 1 chunk once decided.

If all ten are accepted, the work is about 12 to 15 chunks. Recommendations 1
to 4 alone are about 5 to 6.

---

## Reviewer Claims Dropped Or Corrected

- **Dropped:** that CI's shellcheck step may be skipped. The Ubuntu job log of
  Validate run 42930877191 shows `PASS: shellcheck`.
- **Dropped:** that the README's description of the intake ("six questions")
  is wrong. Not confirmed.
- **Corrected:** the internal-tool playbook is not the only code playbook
  without a lockfile or pinning rule. Service and automation have none either.
- **Corrected:** not every secret-scan pattern needs a leading `=`. The
  private-key pattern does not.
- **Corrected:** one commit since July (`08ef475`) touched the release workflow,
  to update action versions. The release, update and promotion logic is
  unchanged.
- **Process note:** the capture reviewer ran one read-only search outside the
  repository (`find /` to depth 6, and a listing of `~/.cache`), looking for a
  tokenizer. It found nothing, opened no files and wrote nothing.
