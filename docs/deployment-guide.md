# Deployment Guide

Last reviewed: 2026-05-31T11:06:01-06:00
Status: draft
Owner: Technical Lead

## Environments

This is primarily a local governance tool.

| Environment | Description |
|---|---|
| dev | Local working checkout of this repository. |
| staging | A branch or copied workspace used to validate scaffold, compliance, and promotion behavior before merging. |
| prod | The trusted local checkout and any published GitHub branch/PR used as the source for future builds. |

## Release Workflow

1. Read `START_HERE.md` and `docs/current-build-pathway.md`.
2. Run `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent`.
3. Run `bash scripts/validate.sh`.
4. Review `git status --short` and confirm the intended file set.
5. Generate a promotion plan if publishing externally: `python3 automation/promotion_plan.py --project .`.
6. Run pre-promotion checks from the plan.
7. Publish through a reviewed GitHub execution step or a manual commit/PR.
8. Record validation and handoff notes in `docs/current-build-pathway.md`.

## Windows Release Package

The Windows package gives non-technical users a double-click launcher.

Build it locally on Windows:

```powershell
.\scripts\build-windows-launcher.ps1
```

Outputs:

```text
dist\windows\NewBuildGovernanceAgent.exe
dist\NewBuildGovernanceAgent-Windows.zip
```

GitHub Actions also builds the package on pull requests and pushes. When a semantic version tag such as `v0.3.0` is pushed, the `Build Windows Launcher` workflow publishes `NewBuildGovernanceAgent-Windows.zip` as a GitHub Release asset.

The executable is a launcher for the unpacked package. It starts `automation\launch_gui.ps1` and expects the `automation`, `docs`, `scripts`, and `templates` directories to remain beside it in the unzipped folder.

## Versioning

`VERSION` is the source of truth for the installed New Build Governance Agent version.

Rules:

- Keep `VERSION` as a single-line semantic version.
- Keep `freedom.tool.yaml` `version` aligned with `VERSION`.
- Use `automation/version.py` for command-line version reporting.
- Use `automation/update_check.py` for read-only comparison against GitHub releases or semantic version tags.
- Use `automation/self_update.py` for guarded fast-forward self-updates.
- Record version-source changes in `docs/current-build-pathway.md` with a completion timestamp.
- Do not combine self-update behavior with GUI update controls unless the active chunk explicitly allows it.

Useful commands:

```bash
python3 automation/version.py
python3 automation/version.py --plain
python3 automation/version.py --json
python3 automation/update_check.py
python3 automation/update_check.py --json
python3 automation/self_update.py --dry-run
python3 automation/self_update.py
bash automation/new_build.sh --version
bash automation/new_build.sh --check-updates
bash automation/new_build.sh --self-update
python3 automation/new_build_headless.py --version
python3 automation/new_build_headless.py --check-updates
```

The update check is informational only. It must not pull, merge, reset, checkout, write files, or modify the local repository.

The self-update command may modify the local checkout, but only by fast-forwarding the current branch from its configured upstream. It must refuse dirty worktrees, detached checkouts, missing upstreams, local-ahead branches, and diverged histories.

## Rollback

- For local documentation/script changes, use git revert or a follow-up correction commit.
- For generated project scaffolds, remove newly created files or directories only after confirming they are not user-authored.
- For change-control applies, remove created files or marked managed blocks if rollback is required.
- For GitHub publish execution, use the rollback commands emitted in the execution report.
- For env/Stripe actions, restore previous env values or Stripe configuration from recorded plan/report context.

## Validation

Minimum validation before release:

- governance check
- Python compile checks and tests
- shell syntax checks
- fresh scaffold smoke test for changed templates or bootstrap behavior
- change-control idempotency check for changed compliance manifests
- secret scan by pattern or approved scanner

High-risk changes require explicit review of affected tool permissions, rollback path, and user-facing documentation.
