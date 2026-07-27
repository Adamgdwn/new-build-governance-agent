# GitHub Resource Efficiency Standard

Document ID: STD-ENG-022
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-26
Last Reviewed: 2026-07-26
Next Review: 2026-10-26
Audience: coding agents, human coders, reviewers, and project owners

## Purpose

Maximize the useful employment of GitHub while minimizing avoidable storage,
bandwidth, compute, maintenance, and billing costs.

GitHub should be used heavily for durable source control, collaboration,
security, traceability, automation, and genuine software distribution. It should
not become the default warehouse for generated binaries, mutable datasets,
caches, logs, or repeated build output.

## Governing Principle

> Use GitHub for durable source code, collaboration, security, traceability,
> automation, and intentional software releases. Route every file and workload
> to the lowest-cost GitHub facility appropriate to its purpose and lifecycle.
> No coding agent should create or expand recurring GitHub costs without
> explicit operator approval.

Required security, validation, evidence, and release controls must not be
removed merely to reduce cost. The objective is to eliminate duplication and
waste, not necessary assurance.

## How This Standard Is Distributed

This file is the single canonical copy. It is deliberately **not** generated
into every governed repository.

- A short guardrail summary lives in the workspace-level `CLAUDE.md` at the root
  of the code workspace (`01. Code Projects/CLAUDE.md`). Every project under that
  root inherits it in a Claude Code session without carrying a local copy.
- That summary points here for the detail. Agents read this file when a task
  actually touches repository storage, LFS, Actions, artifacts, caches,
  Packages, releases, runners, or GitHub billing.
- These are guardrails, not hard rails. They are guidance an agent applies with
  judgment and departs from openly, not a blocking gate. Nothing here is wired
  into `scripts/validate.*` or a preflight check.

Known limits of this distribution model, accepted on 2026-07-26:

- Workspace `CLAUDE.md` is read by Claude Code. Codex sessions read `AGENTS.md`
  and will not pick up the summary unless an equivalent is added for them.
- The summary is machine-local to the Windows workspace. It does not travel to
  the Linux machine, to cloud agents, or to a cloned repo on someone else's
  machine.
- If those gaps start to matter, the fallback is the mechanism already used for
  other shared rules: a `GOVERNANCE-MANAGED` block distributed through
  `automation/change_control.py`, which lands the same summary in each repo's
  `AI_BOOTSTRAP.md`.

## 1. Spending Authority

- No agent should enable a paid GitHub feature, increase or remove a spending
  limit, select a paid or larger runner, purchase storage, or permit an overage
  without explicit operator approval.
- Every metered GitHub product should have a deliberate finite budget. A `$0`
  stop limit is appropriate when service interruption is preferable to an
  unexpected charge.
- Unlimited or unbounded metered spending is not acceptable.
- Before requesting approval for GitHub spending, report:
  - the operational use case;
  - the free or cheaper alternatives considered;
  - the expected initial and monthly cost;
  - the expected storage, bandwidth, or runtime growth;
  - the proposed budget ceiling;
  - the retention and cleanup policy; and
  - the rollback method.
- If cost status is unclear, treat the feature as potentially paid until its
  current billing behavior is verified from official GitHub documentation.
- Never change a billing setting merely to make a workflow pass.

## 2. Storage Classification

Before adding a nontrivial file or generated output, classify it by purpose:

| Content | Correct default location |
| --- | --- |
| Source code, configuration, schemas, documentation, and small durable assets | Git |
| Genuine versioned software deliverables | GitHub Releases |
| Temporary build, test, diagnostic, or review output | Short-lived Actions artifacts |
| Reusable downloaded dependencies | Bounded Actions cache |
| Published libraries and container images | GitHub Packages with a retention policy |
| Generated, mutable, high-volume, replaceable, or backup data | Ignored local or approved external storage |

Rules:

- Generated files, dependency folders, caches, logs, database dumps, graph
  outputs, installers, APKs, archives, test recordings, and replaceable build
  output should not be committed to Git or Git LFS.
- GitHub should not be used as a general backup system, data lake, media
  archive, or arbitrary bulk-file store.
- Review `.gitignore`, `.gitattributes`, build configuration, and workflow
  artifact paths before a tool begins generating large output.
- A file should not be stored in more than one GitHub facility without a
  documented need. A release binary should not also be committed to Git or LFS.
- Repository size should target less than 1 GiB. Crossing 1 GiB warrants an
  investigation and a growth plan. Intentionally approaching or exceeding 5 GiB
  warrants explicit operator review.

## 3. Large-File Review Gate

- Any new or materially changed non-text file larger than 10 MiB should get a
  storage-classification review before it is committed or uploaded.
- The review should identify:
  - whether the file is a source, deliverable, transient artifact, dependency,
    package, dataset, or backup;
  - whether it can be regenerated;
  - its current size and expected change frequency;
  - expected annual version growth;
  - download frequency and bandwidth impact;
  - required retention; and
  - the least-cost appropriate storage location.
- The 10 MiB threshold is an internal early-warning control, not GitHub's
  maximum file-size limit.
- Do not split, compress, rename, or encode a file merely to evade a size or
  approval rule.

## 4. Git LFS Policy

- Running `git lfs track`, broadening an LFS pattern, or adding a new class of
  LFS object requires explicit operator approval.
- Use Git LFS only when a binary must genuinely be version-controlled, cannot be
  economically regenerated, and is not better distributed as a release or
  package.
- Generated binaries, APKs, installers, datasets, graph snapshots, database
  exports, model output, logs, caches, archives, and routine build artifacts
  should never be routed automatically into Git LFS.
- Before approving LFS, estimate full-file version growth. Each modified version
  is another complete stored object.
- GitHub Actions should not download LFS objects unless the particular job reads
  their contents. Jobs that do not need them should keep LFS checkout disabled.
- LFS objects should not be included in automatically generated source archives
  unless a documented distribution requirement justifies the bandwidth.
- Removing an LFS-tracked file from the current branch is not proof that
  historical LFS storage has been reclaimed.
- LFS history rewrites, force pushes, object purges, and GitHub Support cleanup
  are separate destructive operations requiring a scoped plan, backups, impact
  analysis, and explicit approval.

## 5. Releases and Actions Artifacts

### GitHub Releases

- Use GitHub Releases for authentic operator-facing or customer-facing software
  deliverables associated with an intentional version or milestone.
- Do not use Releases as a billing workaround, general file share, backup
  location, or arbitrary blob store.
- Upload a release deliverable once. Do not also commit it to Git or LFS.
- Do not create a release for every routine CI run or internal checkpoint.
- Apply a clear versioning and retention policy to prereleases and obsolete
  release candidates.

### Actions Artifacts

- Upload an Actions artifact only when a person or downstream job is expected to
  consume it.
- Default artifact retention should be one to seven days.
- Retention longer than seven days needs a documented operational, audit, or
  regulatory reason.
- Promote release deliverables that must be retained to a GitHub Release rather
  than leaving them as long-lived workflow artifacts.
- Do not upload dependency folders, caches, complete workspaces, redundant logs,
  or duplicate outputs.
- Prefer uploading targeted failure diagnostics conditionally instead of large
  diagnostic bundles on every successful run.
- Artifact names should identify the workflow, platform when relevant, commit or
  version, and purpose, so stale output can be recognized safely.

## 6. GitHub Actions Compute Efficiency

- Workflows should run only for relevant events, branches, paths, and changes.
- Equivalent validation should not run twice through overlapping `push`,
  `pull_request`, scheduled, or chained-workflow triggers.
- Superseded pull-request and branch runs should use concurrency controls with
  cancellation when cancellation is safe.
- Inexpensive checks should run before expensive builds, integration tests, or
  deployment preparation.
- Jobs should fail fast when continuing cannot produce useful evidence.
- Every job should have a reasonable timeout.
- Standard Linux runners are the default. Windows, macOS, ARM, larger, or other
  specialized runners are appropriate only when they prove an actual supported
  platform or required behavior.
- Test matrices should cover intentional compatibility targets rather than every
  possible combination.
- Paid larger runners require explicit cost approval even for a public
  repository.
- Prefer a shallow checkout. Fetch full history or tags only when the job uses
  them.
- Prefer sparse checkout when a job requires only a bounded part of a large
  repository.
- Keep LFS download disabled unless required.
- Draft pull requests may run inexpensive safety checks, but expensive
  validation should normally wait until the change is ready for review, unless
  early execution reduces real development risk.
- Scheduled workflows should have a named owner, documented purpose, justified
  frequency, timeout, and removal condition.
- CI should not commit generated output back into a branch in a way that
  triggers an uncontrolled workflow loop.
- Do not adopt self-hosted runners solely because GitHub does not charge Actions
  minutes for them. Hardware, electricity, maintenance, availability, isolation,
  and security costs all count.

## 7. Cache Discipline

- Cache only downloaded dependencies or expensive reproducible inputs that
  measurably reduce total workflow time or network use.
- Prefer package-manager caching provided by the relevant setup action.
- Build cache keys from dependency lockfiles and only the platform information
  that changes cache compatibility.
- Avoid cache keys that create a completely new large cache for every commit.
- Do not cache the entire repository, complete workspace, generated application,
  release binary, or large output without evidence that the runtime savings
  exceed the storage and churn cost.
- Keep cache scope and size bounded. Investigate repeated eviction and cache
  thrashing rather than automatically increasing the storage limit.
- Increasing a repository's cache allowance above the included amount requires
  explicit operator approval and a cost estimate.
- Untrusted workflow contexts should not receive write access to trusted caches.

## 8. Packages and Container Images

- Use GitHub Packages only for artifacts genuinely consumed through a package
  manager or container registry.
- Every package or image workflow should define:
  - which versions are permanent;
  - how many development or prerelease versions are retained;
  - when untagged or superseded versions are removed; and
  - who approves deletion of published versions.
- Do not publish a new package version when the content and dependency identity
  are unchanged.
- Do not delete public packages casually; downstream projects may depend on them.
- Package deletion and retention automation should preserve protected releases
  and require a recoverability review.

## 9. Pull Requests, Branches, and Automated Updates

- Prefer focused pull requests that validate only the affected surface while
  preserving required integration coverage.
- Delete merged branches unless a documented workflow requires them.
- Group compatible Dependabot updates to reduce review overhead and repeated CI
  runs.
- Keep security updates enabled where supported. Economic optimization must not
  suppress vulnerability awareness.
- Avoid bot configurations that repeatedly rebase, force-push, or reopen changes
  without new information.
- Do not use empty commits or repeated reruns as the normal way to retry
  unreliable CI. Diagnose and fix the underlying instability.

## 10. Budgets, Alerts, and Review Cadence

- Enable included-usage alerts and budget alerts for all applicable metered
  products.
- Where supported, alert before exhaustion: a first warning at or below 75%,
  another at 90%, and a final warning at 100%.
- Treat a 75% warning as an investigation trigger and a 90% warning as an
  immediate containment trigger.
- Review at least monthly:
  - Git LFS storage and bandwidth;
  - Actions minutes;
  - Actions artifact storage and retention;
  - Actions cache size and churn;
  - GitHub Packages storage and bandwidth;
  - Codespaces or cloud development usage when enabled;
  - current budgets and alerts; and
  - repositories with unusual size or workflow growth.
- Record material findings, approved exceptions, and remediation status in a
  durable repository or account-level cost-control record.
- Prefer retention policies and automated lifecycle controls over emergency
  deletion.

## 11. Destructive Cleanup Boundary

- Cost efficiency does not grant standing authority to delete data.
- Before deleting artifacts, caches, packages, releases, branches, tags, LFS
  objects, or Git history:
  - resolve the exact target;
  - establish whether it is reproducible or recoverable;
  - identify downstream users and dependencies;
  - create a backup when appropriate;
  - document the expected cost benefit; and
  - obtain the level of approval required by repository governance.
- History rewriting, force pushing, and LFS purging always require explicit
  operator approval.

## 12. Exceptions and Completion

- Any exception to this standard should record:
  - owner;
  - repository and affected resource;
  - reason;
  - alternatives considered;
  - estimated cost and growth;
  - approved ceiling;
  - retention period;
  - review or expiry date; and
  - rollback or removal condition.
- Do not declare a GitHub cost-efficiency task complete until the affected
  storage class, workflow behavior, retention, budget boundary, and relevant
  validation have been checked.
- Report both growth prevented going forward and historical usage that remains.
- Never imply that removing a current file, workflow, or pointer automatically
  erased historical billable storage.

## Guardrail Summary

This is the block mirrored into the workspace-level `CLAUDE.md`:

> Keep Git for source, config, docs, and small durable assets. Generated output
> — build artifacts, dependency folders, caches, logs, datasets, installers,
> APKs, archives, graph output, database dumps — belongs in `.gitignore`, a
> release, or outside GitHub. Classify any new non-text file over ~10 MiB before
> committing it. Ask before anything that creates or grows a recurring GitHub
> cost: a paid feature, `git lfs track` or a broader LFS pattern, a larger or
> paid runner, a raised cache or retention limit, a changed budget. In Actions,
> use relevant triggers, cheap checks first, a timeout on every job, cancelled
> superseded runs, shallow checkout, and LFS checkout off unless the job reads
> the objects. Upload artifacts only when something downstream consumes them,
> with 1–7 day retention. Deleting to save cost is its own decision, and
> removing a file today does not reclaim what history already stores.

## Volatile GitHub Product Facts

These informed the thresholds above and were current at drafting on 2026-07-26.
They were **not** independently re-verified during ingestion. Verify against
official GitHub documentation before relying on a specific number, and do not
treat them as durable policy.

- Git LFS uses metered storage and bandwidth. Modified files create complete
  additional objects, and LFS downloads by GitHub Actions consume the repository
  owner's bandwidth:
  [Git Large File Storage billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs).
- GitHub recommends repositories remain ideally below 1 GiB and strongly
  recommends remaining below 5 GiB. Git warns for files above 50 MiB and GitHub
  blocks files above 100 MiB:
  [About large files on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
- Release assets have a per-file size limit but no total release-size or
  bandwidth quota:
  [About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
- Actions minutes and stored artifacts can be metered for private repositories.
  Larger runners are always charged, and artifact storage shares an allowance
  with GitHub Packages:
  [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
- Actions cache storage has a separate included allowance per repository, with
  eviction behavior and possible billing above configured free limits:
  [Dependency caching reference](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching).
- Actions artifacts and logs default to a retention period that can be reduced
  globally or per artifact:
  [Removing workflow artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts).
- Workflow concurrency can cancel superseded runs:
  [Control workflow concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency).
- Budgets and alerts are available for metered GitHub products:
  [Budgets and alerts](https://docs.github.com/en/billing/concepts/budgets-and-alerts).
- Dependabot can group compatible updates to reduce separate pull requests:
  [Multi-ecosystem updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/multi-ecosystem-updates).

## Deferred Work

Not built, and intentionally so:

- Machine-enforced checks (rejecting committed build output, flagging large
  files, LFS pattern changes, missing timeouts, unbounded cache keys, paid
  runner labels). Any such check should start as a reporting control and only
  become blocking after existing repositories are inventoried and approved
  exceptions are recorded.
- Distribution to Codex sessions and to the Linux machine.
- Verification of the volatile product facts above.
