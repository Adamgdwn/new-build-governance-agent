# AI Coding Practices Knowledge Base Change Proposal

Document type: change proposal
Status: draft
Owner: Adam Goodwin (Project Owner)
Last Updated: 2026-11-08
Audience: Adam Goodwin, as approver of the AI Coding Practices knowledge base

## Purpose

The AI Coding Practices knowledge base (POL-AIC-001, STD-AIC-001 to STD-AIC-005,
and ADR-0001 to ADR-0005, approved 2026-09-02) is the canonical home for how
agents are instructed, how work is chunked and run unattended, how rules are
enforced, and which model does what. Research on 2026-11-08 found guidance that
has moved since that approval.

This document proposes changes. Nothing in the knowledge base has been edited
(owner decision, 2026-11-08). Evidence and sources are in
`docs/research/2026-11-08 - Frontier AI Engineering Practice Research.md`.

Each item is independent: approve, amend, or reject it, and record the outcome
in the knowledge base's change log.

## Items that confirm current decisions

These need no change. They are recorded so the approval has the evidence.

- ADR-0001 (`AGENTS.md` canonical for both tools) still holds. Claude Code reads
  `AGENTS.md` only when no `CLAUDE.md` exists, so the one-line `@AGENTS.md`
  import remains necessary. Codex reads `AGENTS.md` files from the repository
  root down, the nearest file wins, and its default size cap is 32 KiB.
- ADR-0003 (hooks enforce rules instead of prose) matches all three labs:
  rules with no exceptions belong in hooks, deny rules, sandbox, or managed
  settings.
- ADR-0004 (independent fresh-context verifier) matches lab and practitioner
  guidance: a reviewer that sees only the diff or output is effective, and
  authors should review their own output first.

## Proposed changes

### P1. STD-AIC-001 Agent Instruction File Standard: instruction style

Add:

- Write rules in plain language with the reason, and state each rule once.
  Anthropic, OpenAI, and Google now all report that emphatic capitals and
  repeated warnings make current models over-apply a rule.
- Do not describe the repository's architecture or file layout in instruction
  files. Include only what an agent cannot work out from the repository:
  commands, traps, unrecorded decisions, and anything corrected twice.
  Anthropic's current Claude Code guidance lists architecture descriptions
  under "what you can stop doing", and a 2026 study of agent context files
  found they raised cost by more than 20% while rarely improving success.
- For GPT-6-era Codex: state each approval rule once, say explicitly that the
  user's instructions override skills, and remove blanket rules such as
  "always run tests" in favour of the chunk's named validation.

### P2. STD-AIC-002 Chunk Specification Standard: the reason for fresh sessions

Keep the fresh session per chunk (ADR-0002), but update its rationale. Context
capacity is no longer the reason: current models have about 1M tokens of
context and compact automatically. The reason is that each chunk starts clean
from a written definition of done, which matches Anthropic's current advice to
start a fresh session to build from a finished specification.

Add:

- Within a chunk, prefer automatic or focused compaction to a reset. After two
  failed corrections, clear the session and restate the task.
- Every chunk's definition of done names a pass/fail check and the evidence to
  capture (the command and its output, a screenshot, or a check result).

### P3. STD-AIC-003 Unattended Execution Standard: run contracts

Add:

- Before any unattended run, record the definition of done, the check that
  proves it, the scope, turn and spend caps, and who signs off.
- A turn that ends with text and no tool call is a progress report, not
  completion. Continue it automatically at most two or three times, then stop
  and report.
- Overnight and Ralph-style loops can produce more output than anyone can
  review. Limit them to new projects or bounded tasks with review capacity
  reserved.
- Claude Code's auto mode approves actions with a classifier. In Anthropic's
  own testing it missed some overeager actions, so it is a judgment aid, not a
  boundary; hard rules stay in hooks, deny rules, and the sandbox.

### P4. STD-AIC-004 Hook Enforcement Standard: untrusted configuration

Add:

- Agent configuration in a cloned repository (`.claude/settings.json`,
  `.mcp.json`, hooks) can execute code; a 2025 vulnerability did exactly that
  before it was patched. Review that configuration before trusting a
  repository, as you would any script.
- Pin MCP servers, skills, and plugins by version (and hash where supported),
  and review each update before adopting it. At least one popular MCP server
  turned malicious in a later version, and a 2026 audit found critical issues
  in a material share of published skills.

### P5. STD-AIC-005 Model And Effort Routing Standard: current lineup and settings

Update (volatile; dated 2026-11-08, re-verify before encoding):

- Claude: Fable 5.1 (released 2026-09-01), Opus 5.5 (2026-09-22),
  Sonnet 5.5 (2026-09-28), and Haiku 5.5 (2026-10-07), all with 1M-token
  context. Claude Code defaults the 5.5 models to medium effort.
- OpenAI: the GPT-6 family (Astra, 6.1 Sol, 6.1 Terra, and Luna).
  Google: Gemini 4 Argon and Gemini 3.8 Flash.

Add:

- Use the effort setting, not prompt wording such as "think hard", to control
  reasoning depth. Several 2025 techniques now return errors on current Claude
  models: thinking budgets, response prefill, and forced tool choice on some
  models.
- Keep the orchestrating or planning agent on a strong model; weaker primary
  models are poor at knowing when to escalate. Route exploration, summaries,
  and classification to smaller models, or to System One judgment models where
  a typed answer is enough.

### P6. ADR-0005 Measure Graphify Before Keeping It: what to measure

Add to the measurement: compare task success and token cost with and without
graph context on the same tasks. The Thoughtworks Technology Radar notes that
agents sometimes perform worse with graph context than with plain search,
which makes the measurement more important, not less.

### P7. New entry: System One models in the toolkit

Record that typed-judgment ("System One") models are not coding-agent models.
TypeSafe's own documentation says Jev is not a replacement for the model behind
a coding agent. Their place is inside products and harnesses (routing,
screening, verification, context selection, trace classification) and in CI
as semantic lints. Laya, the open-weights local alternative, needs fine-tuning
and a held-out evaluation before use; Adam's 2026-10-10 qualification rejected
its base checkpoint for zero-shot request routing.

## After approval

Approved items may need matching edits to this repository's generated
templates (`templates/project/AGENTS.template.md` and the context map and
standards index templates). Make them through the Governance Source Alignment
Standard so project-level decisions are preserved.
