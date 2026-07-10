# Agent Instructions

This repository is the governance source for all projects on this machine.
It is not an application project and not a build target.

`AI_BOOTSTRAP.md` is the canonical agent-instruction file for all agents
(Claude, Codex, Cursor, local). Read it before material or risk-triggering
work; it owns the startup ritual, governance triggers, completion labels,
and the Chunk Close-Out Protocol.

Tool-agnostic essentials:

- Start ordinary scoped work with `git status --short` and only the files relevant to the task.
- Preflight for governance-triggering work: `bash automation/governance_check.sh /path/to/project` (bootstrap missing governance files with `bash automation/bootstrap_project.sh /path/to/project <project-type>`).
- Do not override the selected `risk_tier` or `governance_level`; record deviations as exceptions.
- Do not index, print, summarize, or commit secrets or environment files.
- Supported project types: application, website, service, internal-tool, automation, infrastructure, documentation, agent.
