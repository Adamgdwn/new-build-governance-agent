# Engineering Standards Index

Document ID: STD-ENG-016
Document type: standards index
Status: active
Owner: Project owner or human technical lead
Last Updated: 2026-08-31
Audience: coding agents, human coders, reviewers, project owners, and release reviewers

## Purpose

This is the first standards file a coding session should read when it needs the engineering rules for a governed build.

It points to the standards that define what good code means, how controls scale by use case and risk, and what evidence is required before work can be called ship-ready.

## Required Coding Session Reading

For meaningful implementation work, read these in order:

1. [Durable Development Engineering Policy](../policy/durable-development-engineering-policy.md)
2. [Engineering Governance By Use Case](engineering-governance-by-use-case.md)
3. [Ship-Ready Engineering Standard](ship-ready-engineering-standard.md)

Together, these answer:

- What makes code durable and maintainable?
- What controls fit this type of project?
- What evidence proves the work is ready for a real user?
- What completion state can be honestly claimed without rushing the broader project?

## Supporting Engineering Standards

Use these when the work touches the matching area:

| Standard | Use When |
|---|---|
| [Code Complexity Control Standard](code-complexity-control-standard.md) | Reviewing branch-heavy code, choosing cyclomatic-complexity thresholds, adding focused test evidence, or recording a complexity exception. |
| [Context Hygiene Standard](context-hygiene-standard.md) | Managing long agent sessions, context windows, token budgets, compaction, scoped repo reads, or handoffs. |
| [Document Control Standard](document-control-standard.md) | Creating or maintaining durable docs, handoffs, records, standards, pathway logs, ADRs, audits, or runbooks. Also owns the required project document set. |
| [GitHub Resource Efficiency Standard](github-resource-efficiency-standard.md) | Changing repository storage, `.gitignore`, Git LFS, Actions workflows, artifacts, caches, Packages, releases, runners, or GitHub billing. Guardrails only; the short summary lives in the workspace-level `CLAUDE.md`. |
| [Governance Source Alignment Standard](governance-source-alignment-standard.md) | Checking whether an active project is due to compare its local controls with this governance source. |
| [Governance Level Standard](governance-level-standard.md) | Selecting or interpreting `governance_level` 0-4, or mapping levels to risk tiers and agent-action tiers. |
| [Repository And Naming Standard](repository-and-naming-standard.md) | Naming repositories, files, modules, directories, common project structure, or monorepo layout. |
| [Risk Classification Standard](risk-classification-standard.md) | Classifying risk tier, sensitive surfaces, or escalation needs. Sole definition of the Low/Medium/High/Critical tiers. |
| [Security And Secrets Standard](security-and-secrets-standard.md) | Handling secrets, auth, permissions, private data, external credentials, or trust boundaries. |
| [Testing Standard](testing-standard.md) | Choosing test levels, writing validation evidence, or judging test adequacy. |

Retired standards (kept as tombstones; content merged into their parents on 2026-07-10):

- `ai-agent-governance-standard.md` → [Engineering Governance By Use Case](engineering-governance-by-use-case.md)
- `deployment-and-release-standard.md` → [Ship-Ready Engineering Standard](ship-ready-engineering-standard.md)
- `documentation-standard.md` → [Document Control Standard](document-control-standard.md)
- `monorepo-standard.md` → [Repository And Naming Standard](repository-and-naming-standard.md)

## Context Routing

Use `docs/context-map.md` before broad repository reading when the right files or
standards are unclear. It routes task types to the smallest useful context set.

## Coding Agent Rule

Do not rely on memory from a previous chat to know the engineering standards. Read this index, then open the standards relevant to the current task.

If a project only contains a subset of these standards, use the local files first. When this repository is available as the governance source, use the standards here as the source of truth for missing or older project-local copies.
