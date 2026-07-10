# Model Registry

Last reviewed: 2026-05-31T11:06:01-06:00
Status: active
Owner: Technical Lead

| Model ID | Provider | Version | Purpose | Approved For | Owner | Last Reviewed |
| --- | --- | --- | --- | --- | --- | --- |
| M-CODEX | OpenAI | User-selected Codex session | Repository edits, audits, tests, and governance updates in this workspace. | A1 supervised coding and documentation work. | Adam Goodwin | 2026-05-31 |
| M-CLAUDE | Anthropic | User-selected Claude Code session | Alternate coding assistant for governed repo work. | A1 supervised coding and documentation work. | Adam Goodwin | 2026-05-31 |
| M-LOCAL | Local Python/Bash | System Python and shell tools | Deterministic scaffolding, validation, manifests, and promotion helpers. | Bounded local automation under repo scripts. | Adam Goodwin | 2026-05-31 |

## Model Use Rules

- AI-generated code is reviewed like human-written code.
- Model output is not authority for policy, source data, command success, or external actions.
- Material model, prompt, tool, or autonomy changes require a pathway note and validation.
