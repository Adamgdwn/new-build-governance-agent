# Frontier AI Engineering Practice Research

Document type: research record
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Audience: Adam Goodwin, coding agents, and reviewers changing this repository's rules, templates, and playbooks

## Purpose

On 2026-11-08 Adam asked for research across AI engineering channels,
transcripts, tips, and code, to write per-build-type instructions for coding
agents, to bring this repository's rules up to date for current frontier
models, to find where Jev and Laya add the most value, and to treat harnesses
as what people mean when they ask for an agent. This record holds the evidence
behind those changes. It is not a startup read; load it when a rule's
reasoning is in question.

## Method and limits

Four evidence streams, gathered on 2026-11-08:

1. The AI Engineer YouTube channel (`youtube.com/@aiDotEngineer`): 24 of 30
   shortlisted 2026 talks analysed from full transcripts. Four came from
   YouTube captions; YouTube then rate-limited downloads, so 20 came from the
   channel's own corrected transcripts on ai.engineer, summarised by reader
   agents without a second check against the source. Not retrieved: the
   AlixPartners ("Claude Code Looked Right but Missed $800K") and Ramp
   (agent testing) talks. Retrieved but not analysed: McKinsey.
2. Frontier-lab primary sources: Anthropic engineering posts and Claude
   documentation, OpenAI and Codex documentation, Google Gemini documentation,
   and the protocol specifications (MCP, AGENTS.md, Agent Skills,
   OpenTelemetry GenAI conventions). OpenAI's "Harness engineering" post
   returned HTTP 403, so its claims here come from secondary summaries and
   the author's AI Engineer talk.
3. Independent practitioners, evaluation, and security sources.
4. TypeSafe's live documentation for Jev, the Laya project's own README and
   model cards, and Adam's 2026-10-10 Laya qualification in the Offline Local
   Agent project.

Claims below name their source. Vendor statistics are marked as vendor
claims. Facts likely to change are collected under Volatile facts with their
dates. Research notes and transcripts were kept outside the repository.

## Findings

### 1. An agent is a model plus a harness

- The industry vocabulary moved from prompt engineering (2024) to context
  engineering (2025) to harness engineering (2026). The harness is the loop,
  tools, context, memory, permissions, and checks around the model, and most
  of the leverage and most of the failures live there (Anthropic engineering
  posts 2024-12 to 2026-04; Martin Fowler's site, 2026-04; Mitchell Hashimoto,
  2026-02; AI Engineer talks by Lopopolo, Katz, and others).
- Start simple: one agent and a few tools, adding a component only when it
  measurably helps (Anthropic "Building effective agents"; OpenAI "A practical
  guide to building agents").
- Every harness component encodes an assumption about what the model cannot
  do. Retest at each model release and remove what is no longer load-bearing
  (Anthropic, 2026-03 and 2026-04). Models are absorbing coding scaffolding;
  Cursor deleted parts of its harness (AI Engineer, "Is the Agent Harness
  Dead?").
- Hosted harnesses now exist: Claude Managed Agents (2026-04) and OpenAI's
  Agents API (2026-09). Building your own versus driving a first-party harness
  is a genuine disagreement (see Contested points).

### 2. Instructions: plain, short, measured

- All three labs now say emphatic wording backfires. Claude Code's
  documentation says piling on emphasis makes Claude over-apply a rule;
  Anthropic replaces "CRITICAL: You MUST use this tool" with "Use this tool
  when..."; OpenAI reserves absolute words for true invariants; Google warns
  against overly persuasive language.
- Shorter is better. OpenAI measured 10 to 15% higher eval scores with 41 to
  66% fewer prompt tokens. A 2026 study of agent context files (arXiv
  2602.11988) found they raised cost by more than 20% and rarely improved
  success, and that repository overviews did not help. An AI Engineer speaker
  cut 10,000+ generated lines of skills to 553 lines of gotchas and measured
  one skill at 77% when loaded versus 97% without it (single source, own
  measurement).
- Include only what the agent cannot infer: commands, traps, unrecorded
  decisions, and anything corrected twice. Leave out architecture tours
  (Claude Code best practices).
- Settings beat wording: effort controls reasoning depth, structured outputs
  replace "return only JSON", and "think hard" or "keep going" lines are
  obsolete. Several 2025 techniques now return errors on current Claude
  models (thinking budgets, prefill, forced tool choice on some models).
- Make failure messages do the instructing: write lint and test failures as
  fix instructions, and surface a rule at the moment it applies instead of
  loading every rule up front (Lopopolo, OpenAI, AI Engineer 2026-04).

### 3. Context and sessions

- Current models have about 1M tokens of context and compact automatically,
  so running out of room is rare; cost still grows with everything loaded
  (Claude Code best practices; Claude context-window documentation).
- Claude Code's "what you can stop doing" list includes treating the window as
  the main constraint and using subagents to protect context. Anthropic's
  2026-03 harness post replaced context resets with a continuous session and
  automatic compaction.
- Fresh sessions still have a place: `/clear` between unrelated tasks, and
  once a specification exists, "start a fresh session to build from it, so the
  build begins with a clean context and a written definition of done"
  (Claude Code best practices). After two failed corrections, clear and
  restate the task. This is the basis for keeping one fresh session per
  chunk (owner decision, 2026-11-08).
- Keep durable state in files (progress notes, a task list, git history),
  because current models are good at discovering state from the filesystem.

### 4. Verification and evidence

- Give the agent a pass/fail check and ask for evidence (Anthropic, OpenAI).
  An agent faked test runs until the author stored a hash of the real test
  output; others attach before-and-after browser video to pull requests
  (AI Engineer, several talks). OpenAI's Govindarajan asks for a run receipt:
  trigger, state, authority used, what ran, and the evidence that survived.
- Check work in a separate context: a builder agent and an independent
  verifier with a rubric, with the loop ending only when the verifier passes
  it (several AI Engineer talks across vendors; ADR-0004 already requires it).
- Deterministic checks first: "never send an LLM to do a linter's job"
  (HumanLayer). Agents must not edit tests (Anthropic).
- A turn that ends with text and no tool call is a progress report; continue
  it automatically at most two or three times (Anthropic).
- After a timeout, check whether the call went through before retrying: blind
  retries duplicated effects 54% of the time in one benchmark, and `git revert`
  does not undo runtime or external effects (Sah and Sah, AI Engineer
  2026-11-08, own benchmark).

### 5. Evaluation

- Start with 20 to 50 tasks drawn from real failures, kept as data. Separate
  capability and regression suites, isolate trials, grade outcomes, read the
  transcripts, and calibrate model graders against human graders (Anthropic
  "Demystifying evals", 2026-01; OpenAI evaluation guidance).
- Error analysis is the core loop: read 30 to 50 traces, write open notes,
  group and count failure types, then fix with deterministic checks; use one
  pass/fail LLM judge per subjective failure type, checked against human
  labels (Husain and Shankar evals FAQ; Eugene Yan).
- Benchmark-shipped judges can mislead: one agent scored 74% under an official
  judge and about 38% under a rubric-and-screenshot verifier (AI Engineer,
  "Your LLM Judge Is a Confident Liar").
- Evaluate the deployment, not just the model: an analysis of 1,368 incidents
  linked harm most to the quality of human review and monitoring (AI Engineer,
  "1,368 AI Failures").
- Changes to `AGENTS.md`, skills, and templates are harness changes; test them
  on the golden set for success and cost (Thoughtworks Technology Radar).

### 6. Security

- Rule of Two (Meta, 2025-10) and the lethal trifecta (Simon Willison): when a
  session combines untrusted input, sensitive data, and the ability to change
  state or send data out, require a human gate or split the work.
- Classifiers are tripwires, not boundaries: adaptive attacks beat most
  published prompt-injection defenses ("The Attacker Moves Second", 2025-10).
  Plan from the trusted request before reading untrusted data, and allow-list
  tools per phase (Google DeepMind's CaMeL pattern).
- Least privilege, authorization outside the model, approvals bound to the
  exact action, schema-validated tool calls, failing closed, and caps on
  tokens, cost, retries, and depth (OWASP Top 10 for LLM Applications 2025,
  OWASP Top 10 for Agentic Applications 2025-12, OWASP AI Agent Security cheat
  sheet).
- Keep secrets and network access outside the agent: inject credentials the
  agent cannot read, restrict egress through a proxy, and keep the harness
  separate from the sandbox (AI Engineer talks by Modal, Anthropic, and others;
  vendors). Egress allow-lists alone have been bypassed (Willison, 2026).
- Coding sessions: an OS sandbox for filesystem and network, staging-only
  credentials, and agents never applying, destroying, or migrating production.
  Agent configuration in a cloned repository can execute code (CVE-2025-59536,
  patched).
- Supply chain: pin MCP servers, skills, and packages by version and hash and
  review updates; confirm a package exists before installing it, because
  models suggest invented package names (USENIX Security 2025).

### 7. Multi-agent work and review

- Multi-agent runs cost about 15 times the tokens of one agent. Use them for
  parallel work, isolating noisy output, and independent review; they do not
  make answers smarter (Anthropic).
- One agent writes; the others contribute intelligence rather than actions
  (Cognition, 2026-04). One AI Engineer team killed its one-agent-per-step
  pipeline in favour of deterministic code plus one reasoning agent.
- Review is now the bottleneck. Keep pull requests small; DX's survey of 400+
  organizations found average pull request size grew from 44 to 72 lines while
  developer confidence fell, and a median productivity gain of 7.7% (vendor
  data).

### 8. Cost and models

- Prompt caching dominates agent cost: put static content first, because one
  changed byte breaks the cache. At a 0% cache hit rate one $21 task cost over
  $200 (Artificial Analysis, AI Engineer 2026-11-03, vendor).
- A stronger model at low effort is often cheaper than a weaker model at high
  effort. The main cost drivers are input tokens, cache hit rate, and turns.
- Route by task, benchmark shortlisted models on your own tasks, and keep the
  orchestrating agent on a strong model, because weaker primary models are
  poor at knowing when to escalate (Cognition).

### 9. Protocols and standards

- MCP's 2026-07-28 specification is stateless, moves tasks into an extension,
  and deprecates Sampling, Roots, and Logging. The MCP Registry is still in
  preview.
- AGENTS.md is stewarded by the Agentic AI Foundation, which A2A (now 1.0) has
  also joined. Claude Code reads `AGENTS.md` only when no `CLAUDE.md` exists;
  Codex reads `AGENTS.md` files from the root down, the nearest wins, and the
  default cap is 32 KiB.
- The OpenTelemetry GenAI semantic conventions for agents were still at
  development status, so projects should log a minimal trace schema they own.

## Jev and Laya: where they add the most value

Both are "System One" models: they return typed, calibrated judgments (choose
one of a set, yes/no probability, a score on a rubric, and for Jev 1.14 a
bounding box) instead of generating text. Code owns the workflow; the model
supplies common-sense judgment where ordinary code cannot.

| | Jev (TypeSafe) | Laya (`convaiinnovations/laya`) |
| --- | --- | --- |
| Where it runs | Hosted API (`POST /v1/systemone`) | Local, open weights (Apache 2.0), CPU-capable |
| Current version | Jev 1.14, released 2026-10-14 | English, multilingual, and typed-decisions checkpoints |
| Zero-shot | Designed for it | Base checkpoints are near chance on typed decisions (0.36 against a 0.32 random baseline); "a fast base to specialise, not a zero-shot decision engine" (Laya README) |
| Inputs | Text and images; 64k-token request limit by default | Text; images, audio, and video through extras |
| Cost | Charged per input token; output free | Local compute only |
| Documented weak spots | Counting, arithmetic, dates, multi-hop indirection, irrelevant context, option order, adversarial content | Negation, boolean-word labels, high-cardinality choices without budget tuning |

Adam's own evidence: the Offline Local Agent project qualified the English
Laya checkpoint on 2026-10-10 for request-mode routing. It ran fully offline
(warm p95 0.372 s, about 2.8 GiB peak memory) but failed adoption: 8 of 150
held-out suggestions accepted at the frozen threshold, 119 of 150 raw
accuracy. It stays disconnected.

Where they add the most value:

1. Inside harnesses (TypeSafe lists "harness engineering" as a headline use):
   routing to a handler, tool, or model; screening inputs, outputs, and tool
   calls as a tripwire; verifying extracted fields or cited claims against
   their evidence and escalating failures to a reasoning model or a person;
   selecting retrieved context and deciding what is worth remembering; and
   classifying agent traces at scale for error analysis.
2. Inside products: ticket and message triage, moderation, scoring against a
   rubric, and "select instead of generate" extraction, where code finds
   candidate values and the model picks the intended one.
3. In CI: semantic lints of documentation, conventions, and instruction files.
4. Over large data: map-reduce classification and feature extraction where an
   LLM call per item would cost too much.

Rules that follow from the evidence:

- Neither is a coding-agent model. TypeSafe states that Jev cannot replace the
  model behind Claude Code or Codex; use it in what the coding agent builds.
- Prefer Jev for zero-shot decisions. Use Laya only when data must stay on the
  machine and labeled data exists to fine-tune it, and rely on it only after a
  held-out evaluation passes.
- Keep arithmetic, dates, counting, lookups, and policy in code.
- Confidence never grants permission. A typed answer guarantees the format,
  not the truth, and thresholds must be set on the project's own data.
- Both can be steered by adversarial content, so neither is a security
  boundary; use them as one layer of signal.
- Jev's performance figures come from the vendor; verify them on your tasks.

## Contested points

- Growing instruction files with every failure (Hashimoto) versus pruning them
  as models improve (Thoughtworks Radar, Latent Space). Middle ground: add a
  rule when a failure recurs, prune on a schedule, and measure the change.
- Building your own harness gates versus driving first-party harnesses such as
  Claude Code or Codex.
- Reading the code (Horthy, Mistele) versus only requiring that it can be
  explained (Huntley, Lopopolo).
- Plan review: reviewing the plan gives more leverage than reviewing code
  (Horthy), but approving an unread plan bakes in bad instructions (Lopopolo).
- Parallel writing agents: they fail (Cognition) versus parallel sessions are
  now normal and review is the limit (Thoughtworks).
- Unattended loops (Ralph, overnight builds) produce more than anyone can
  review; one proponent limits them to new projects.
- Graph-based context versus plain search: agents sometimes perform worse with
  graph context (Thoughtworks Radar). This bears on the workspace's
  Graphify-first rule and supports ADR-0005's "measure before keeping".

## Volatile facts

Re-verify before encoding any of these. Dates are when they were checked.

| Fact | As of 2026-11-08 | Source |
| --- | --- | --- |
| Claude models | Fable 5.1 (2026-09-01), Opus 5.5 (2026-09-22), Sonnet 5.5 (2026-09-28), Haiku 5.5 (2026-10-07); all 1M-token context | Claude models documentation |
| Claude Code default effort for 5.5 models | medium | Claude Code documentation |
| OpenAI models | GPT-6 family: Astra (2026-09-03), 6.1 Sol (2026-09-29), 6.1 Terra (2026-10-26), Luna | OpenAI models documentation |
| Google models | Gemini 4 Argon, Gemini 3.8 Flash | Gemini models documentation |
| MCP specification | 2026-07-28 (stateless; tasks as an extension) | modelcontextprotocol.io |
| Jev | 1.14 (2026-10-14); 64k request context by default | TypeSafe models documentation |
| Claude Code auto mode | default for interactive sessions since 2026-08-14 | research notes |

## What this research changed in the repository

- `templates/project/docs/playbooks/` (Chunk Forty-Three): eight build
  playbooks for coding agents.
- `AI_BOOTSTRAP.md`, `CLAUDE.md`: a "Working With Frontier Models" section and
  the fresh-session close-out (Chunk Forty-Five).
- `docs/standards/context-hygiene-standard.md` and its template: subagent and
  compaction guidance for 1M-token models.
- `docs/standards/engineering-governance-by-use-case.md` and its template:
  Harness Engineering Controls.
- `docs/policy/durable-development-engineering-policy.md` and its template:
  working with current coding agents.
- Harness README and model registry templates.
- `docs/proposals/2026-11-08 - AI Coding Practices Knowledge Base Change Proposal.md`:
  proposed changes to the knowledge base, not yet applied.

## Sources

AI Engineer talks analysed (speakers and dates as recorded in the research notes):

| Talk | Speaker or organization | Date |
| --- | --- | --- |
| [Harness Engineering: How to Build Software When Humans Steer, Agents Execute](https://www.youtube.com/watch?v=am_oeAoUhew) | Lopopolo, OpenAI | 2026-04-17 |
| [How I deleted 95% of my agent skills and got better results](https://www.youtube.com/watch?v=vy7o1g2iHY8) | Nisi, WorkOS | 2026-05-30 |
| [Your coding agent doesn't always follow your rules](https://www.youtube.com/watch?v=MpZzWMdmQCE) | Checkout.com | 2026-07-08 |
| [The Great Loops Debate](https://www.youtube.com/watch?v=c35YoMdnI78) | Huntley, Pstrucha, Livingstone, and others | 2026-07-17 |
| [Claude for Long-Horizon Tasks](https://www.youtube.com/watch?v=9QebvrrY3KY) | Anthropic (machine-translated transcript; low confidence) | 2026-07-22 |
| [Why We Killed Our Multi-Agent Pipeline](https://www.youtube.com/watch?v=u6jJcIFDLE4) | ZS | 2026-07-23 |
| [Loop Engineering from First Principles](https://www.youtube.com/watch?v=xIt_mTQp6mY) | Mistele, HumanLayer | 2026-07-25 |
| [The Model Was Right. The Harness Failed.](https://www.youtube.com/watch?v=BInpv7lGp1o) | OpenAI | 2026-07 |
| [No, That's Not a Software Factory](https://www.youtube.com/watch?v=HvboD89DyQ8) | WorkOS | 2026-09-27 |
| [The State of AI in Software Development: Data from 400+ Orgs](https://www.youtube.com/watch?v=Se8jHLliLXE) | DX | 2026-09-30 |
| [Your LLM Judge Is a Confident Liar: Building Better Verifiers](https://www.youtube.com/watch?v=xLxhT2ZI7UM) | Browserbase and Microsoft | 2026-10-05 |
| [Why We Deleted Our MCP Server and Rebuilt It](https://www.youtube.com/watch?v=jJQoVkd5yLg) | Reducto | 2026-10-08 |
| [Let Anyone at Your Company Ship Internal Apps with AI](https://www.youtube.com/watch?v=HTzgC3FoYsI) | WorkOS | 2026-10-08 |
| [The 6 Pillars of an Agentic Harness for Production](https://www.youtube.com/watch?v=eXA2tjRZIbY) | Railway | 2026-10 |
| [Sandboxes Aren't Optional: 4 Ways to Isolate Coding Agents](https://www.youtube.com/watch?v=iH_wV8BbS24) | OpenHands | 2026-10-12 |
| [Is the Agent Harness Dead?](https://www.youtube.com/watch?v=7Y4sbZgBdnc) | Jediah Katz, SpaceXAI (formerly Cursor) | 2026-10 |
| [1,368 AI Failures and What They Teach About Evals](https://www.youtube.com/watch?v=mMw3arwQsL0) | Srivastava and Sah | 2026-10 |
| [How Anthropic Merges 30,000 Code Changes a Day](https://www.youtube.com/watch?v=AnsXWH2_EBU) | Anthropic | 2026-10-28 |
| [Without Caching, Your AI Agent Costs 10x More](https://www.youtube.com/watch?v=prGP0huECPo) | Artificial Analysis | 2026-11-03 |
| [Your Old Prompts Are Making Claude Worse](https://www.youtube.com/watch?v=ys6YQ2yfBpM) | Anthropic | 2026-11-06 |
| [Your AI Agent Is Hiding Its Mistakes From You](https://www.youtube.com/watch?v=pz74r-4dGfQ) | Warp | 2026-11-06 |
| [Don't Vibe Code Your Agent Infrastructure](https://www.youtube.com/watch?v=_0SQh8a1Osk) | Modal | 2026-11-07 |
| [Your Coding Agent Can't Undo Its Own Mistakes](https://www.youtube.com/watch?v=BT1Mo-fD-g0) | Tanmay Sah and Dolly Sah | 2026-11-08 |
| [Please... Enough with the Sloppy, One-Shot SaaS Replacements](https://www.youtube.com/watch?v=oixzVKMAXG0) | (front-end polish patterns) | 2026 |

Frontier labs and protocols:

- Anthropic engineering: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents), [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps), [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [Managed agents](https://www.anthropic.com/engineering/managed-agents), [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode), [Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- Claude documentation: [Claude Code best practices](https://code.claude.com/docs/en/best-practices), [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows), [Compaction](https://platform.claude.com/docs/en/build-with-claude/compaction)
- OpenAI: [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf), [Prompt guidance](https://developers.openai.com/api/docs/guides/prompt-guidance), [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [Run long-horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices), [AGENTS.md in Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- Google: [Gemini models](https://ai.google.dev/gemini-api/docs/models)
- Protocols: [MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [MCP security best practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices), [AGENTS.md](https://agents.md/), [OpenTelemetry GenAI agent spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)

Practitioners, evaluation, and security:

- [Harness engineering, Martin Fowler's site](https://martinfowler.com/articles/harness-engineering.html); [Context engineering for coding agents](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html); [Spec-driven development tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- [Thoughtworks Technology Radar](https://www.thoughtworks.com/radar); [Mitchell Hashimoto, My AI adoption journey](https://mitchellh.com/writing/my-ai-adoption-journey); [Armin Ronacher, The final bottleneck](https://lucumr.pocoo.org/2026/2/13/the-final-bottleneck/); [Geoffrey Huntley, Ralph](https://ghuntley.com/ralph/)
- [HumanLayer, 12-factor agents](https://github.com/humanlayer/12-factor-agents); [Advanced context engineering for coding agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md); [Manus, context engineering lessons](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Simon Willison, Designing agentic loops](https://simonwillison.net/2025/Sep/30/designing-agentic-loops/); [New prompt injection papers](https://simonwillison.net/2025/Nov/2/new-prompt-injection-papers/); [Meta, practical AI agent security (Rule of Two)](https://ai.meta.com/blog/practical-ai-agent-security/)
- [Hamel Husain, Evals FAQ](https://hamel.dev/blog/posts/evals-faq/); [Eugene Yan, Product evals](https://eugeneyan.com/writing/product-evals/); [Agent context files study, arXiv 2602.11988](https://arxiv.org/abs/2602.11988)
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/); [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/); [OWASP AI Agent Security cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)

Jev and Laya:

- TypeSafe: [System One](https://docs.typesafe.ai/concepts/system-one.md), [Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents.md), [Use-case map](https://docs.typesafe.ai/concepts/use-case-map.md), [Models](https://docs.typesafe.ai/models.md), [Model jaggedness](https://docs.typesafe.ai/model-jaggedness.md)
- Laya: [README and honest limits](https://github.com/NandhaKishorM/laya), [English checkpoint](https://huggingface.co/convaiinnovations/laya)
- Owner evidence: Offline Local Agent, `docs/2026-10-10 - Local Decision Model Qualification Results.md` (a separate repository).
