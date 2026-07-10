# Prompt Register

Last reviewed: 2026-05-31T11:06:01-06:00
Status: active
Owner: Technical Lead

| Prompt ID | Agent | Purpose | Current Version | Change Type | Last Reviewed |
| --- | --- | --- | --- | --- | --- |
| P-AGENTS | All repo agents | Default repository instructions for governed work. | `AGENTS.md` current | Managed instructions | 2026-05-31 |
| P-AI-BOOTSTRAP | All AI assistants | Canonical project operating rules and validation expectations. | `AI_BOOTSTRAP.md` current | Managed instructions | 2026-05-31 |
| P-CLAUDE | Claude Code | Claude-specific reading order and operating constraints. | `CLAUDE.md` current | Managed instructions | 2026-05-31 |
| P-FREEDOM-TOOL | Freedom dispatcher | Tool invocation metadata for headless New Build Governance Agent execution. | `freedom.tool.yaml` current | Tool manifest | 2026-05-31 |

## Change Rules

- Instruction changes must preserve the start/pathway/governance preflight sequence.
- Use-case guidance must not override the selected `risk_tier` or `governance_level`.
- Prompt or instruction changes that increase autonomy, external side effects, money handling, or sensitive data exposure require explicit review.
