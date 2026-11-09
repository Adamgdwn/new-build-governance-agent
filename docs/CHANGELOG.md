# Change Log

Last Updated: 2026-11-08
Status: active
Owner: Technical Lead

## Unreleased

- 2026-11-08: Added the frontier AI engineering research record (Chunk Forty-Four), the evidence behind the 2026-11-08 playbooks and rule changes: 24 AI Engineer channel talks from transcripts, current Anthropic, OpenAI, and Google guidance, practitioner, evaluation, and security sources, and where Jev (hosted) and Laya (local) typed-judgment models add value.
- 2026-11-08: Added build-type agent playbooks (Chunk Forty-Three): eight instruction files for coding agents (AI agent harness, application, website, service, internal tool, automation, infrastructure, documentation) covering done-criteria, build rules, verification, typical agent failure modes, security, where Jev or Laya fits, and when to stop and ask. New projects receive the matching playbook as `docs/build-playbook.md`; existing projects are offered it by `change_control.py propose`. Change control now treats legacy `agentic-harness` projects as agent projects.
- 2026-11-08: Merged the intake's "AI helper" and "agentic harness" choices into one "An AI agent (harness)" choice (Chunk Forty-Two). Every agent project now gets `docs/harness/README.md` and a harness profile, with the topology recorded as `undecided` when it was not asked. Headless, both terminal launchers, and the Freedom manifest accept an optional harness topology and description. Fixed v0.3.0 harness projects failing their own schema check and being mapped to the web-application use case by change control.
- 2026-11-08: Fixed workspace paths after the home-folder migration (Chunk Forty). Folder names may carry a numeric ordering prefix (`01. Code`, `03. Agents`), existing category folders are reused instead of creating a parallel `Applications` folder, and a checkout installed inside a category folder treats the folder above it as the code root. Importing the GUI no longer creates folders. The terminal launchers preview through a new `new_build_headless.py --plan` dry run, so the preview always matches the real routing, and headless now routes `agentic-harness` projects to the agents folder as the GUI does. `master_env.py set` and `merge` accept only keys already reviewed into the master registry.

- Added the Build-To-Sale Lifecycle Standard (STD-ENG-025): lifecycle phase status, evidence-based phase exits, validation instruments, P0-P3 priority, four definitions of done, and a funding, credits and partners track, with the owner-supplied Build-to-Sale Operating System as Part B. Single canonical copy with a short workspace `CLAUDE.md` summary; scaffold and upgrade distribution deferred (Chunk Thirty-Nine).
- Folded the approved AI Coding Best Practices pattern into the generated project templates: one canonical `AGENTS.md` (Claude Code imports it through a one-line `CLAUDE.md`), a commands-only `AI_BOOTSTRAP.md`, runner-readable pathway chunks (`### P-NN`, `Status: Ready`, `Runner:`, `Files:`), the plan-once, approve-once, fresh-session-per-chunk work pattern, AIC standards routed by name in the context map and standards index, and a change-control guard that never appends managed blocks to import-only instruction files. Standards in this repository are unchanged (Chunk Thirty-Eight).
- Updated the public README, user guide, project manual, generated project documentation, automation reference, and GitHub repository metadata so the new complexity and periodic alignment controls are visible from the project landing page.
- Added the Code Complexity Control Standard with plain-language guidance, advisory 1-10/11-20/21+ bands, test-linked review, anti-gaming rules, optional validated project controls, and scaffold/change-control distribution.
- Added the Governance Source Alignment Standard and a lightweight 90-day prompt so active builds periodically compare relevant local controls with this source without making governance sync an ordinary-startup requirement or silently overwriting project decisions.
- Pinned the validation toolchain in `requirements-dev.txt`, wired CI to that single source, upgraded official actions to their Node 24-compatible majors, and added bounded timeouts, superseded-run cancellation, and seven-day package retention after repeated CI drift failures.
- Made carry-forward staleness use an explicit last-reviewed date while retaining compatibility with existing five-column files.
- Made same-day governance-audit reruns retain their existing document ID instead of consuming a new sequence number.
- Removed user-specific Graphify and repository paths from active docs, generated instructions, and managed instruction upgrades.
- Refreshed the architecture component map to separate scaffolding, compliance, change control, and audit responsibilities.
- Reviewed the risk register and recorded the local toolchain constraints that currently prevent the full gate from completing outside CI.
- Refreshed the public README, user guide, quick-start governance flow, project manual, and generated README/manual templates so the latest governance baseline points to lean startup, `docs/context-map.md`, budget classes, and risk-triggered preflight.
- Integrated the cost-effective agentic coding and context-window management standard into context hygiene, context routing, project controls, generated templates, managed upgrade blocks, and focused tests; the downloaded standard is explicitly not a new mandatory startup read.
- Integrated the Codex startup preflight lean-out plan into context hygiene, live/generated agent instructions, managed upgrade blocks, and pathway guidance; the downloaded plan is explicitly not a new mandatory startup read.
- Refreshed the GitHub landing description and GUI screenshot to show that the agent now provides practical guidance alongside governance.
- Added the Context Hygiene Standard as a generated supporting standard for agent context windows, token budgets, scoped repository reads, compaction, and handoffs, with scaffold, recommended compliance, and upgrade manifest wiring.
- Added optional user-guide tips for asking coding agents to commit, push, open pull requests, or intentionally push `main`.
- Added a generated `docs/standards/README.md` standards index so future coding sessions can find the full engineering standard set from one entry point.
- Added the Ship-Ready Engineering Standard as a standalone generated baseline document, with scaffold, governance check, and upgrade manifest wiring.
- Added a Windows `.exe` launcher package path for non-technical users, including a C# launcher, package build script, GitHub Actions artifact workflow, and tag-based release asset publishing.
- Initial project setup.
