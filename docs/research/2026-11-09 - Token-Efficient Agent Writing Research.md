# Token-Efficient Agent Writing Research

Document type: research record
Status: active
Owner: Technical Lead
Last Updated: 2026-11-09
Audience: Adam Goodwin and coding agents changing this repository's handover and writing guidance

## Question

On 2026-11-09 Adam asked whether Markdown that only coding agents read could
use a very token-efficient shorthand. The guidance must work for any coding
agent, so nothing in it can be proprietary. This record holds the measurements
and sources behind Chunk Fifty. It is not a startup read.

## Answer

- Invented shorthand does not pay. On a real handover it cut 30% of the
  tokens, but terse plain English without backticks cut 25% on its own. The
  symbols and invented abbreviations added only 6 to 9% beyond that, and they
  cost readability, review and reliability across models.
- Compact plain English does pay: 12% fewer tokens than this repository's
  already lean style, and 25% when backticks are dropped too.
- The large savings are elsewhere. A written next-chunk handover cut start-up
  reading by at least 81%, and instruction files loaded into every session can
  cost more than any handover.
- Compression pays only for text that is loaded repeatedly. A handover read
  once costs more to compress than it saves, so write it compactly instead.

## Method And Limits

- Tokenizers:
  - OpenAI's `o200k_base` is used by the GPT-4o, GPT-4.1 and GPT-5 models,
    including GPT-5-Codex; the open-weight gpt-oss uses the same base
    vocabulary.
    `cl100k_base` is used by GPT-4 and GPT-3.5. Both were run through the
    open-source `tiktoken`.
  - Qwen3 and LFM2 are two open-weight model families. They were run through
    Hugging Face `tokenizers`, without special tokens.
  - Claude's tokenizer is not published. Anthropic's token-counting API could
    measure it; it was not used here.
- Sample: Chunk Forty-Nine's objective, read list, facts and stop condition
  (`docs/current-build-pathway.md` lines 63-76 and 91 at commit `b7e7612`),
  rewritten seven ways with the same facts. That section was written under the
  token-efficient handover practice, so the baseline is already compact; a
  looser handover would gain more.
- Token counts are exact for these tokenizers. Comprehension was not measured
  here; the published work below covers it.

## Results

### One handover, eight ways

| Form | Bytes | o200k | cl100k | Qwen3 | LFM2 | o200k change |
|---|---:|---:|---:|---:|---:|---:|
| As written | 1,812 | 481 | 482 | 522 | 531 | baseline |
| Terse plain English | 1,529 | 423 | 424 | 465 | 473 | -12% |
| Terse, common abbreviations (`cov`, `stmts`, `vars`) | 1,496 | 425 | 425 | 466 | 474 | -12% |
| Terse, no backticks | 1,453 | 360 | 360 | 401 | 405 | -25% |
| Heavy shorthand: symbols, abbreviations, a legend | 1,132 | 337 | 329 | 370 | 369 | -30% |
| Terse, with emoji and arrows | 1,719 | 501 | 518 | 551 | 579 | +4% |
| JSON | 1,549 | 395 | 394 | 435 | 447 | -18% |
| YAML | 1,501 | 389 | 388 | 429 | 432 | -19% |

- Abbreviations cut 33 bytes but added 1 or 2 tokens.
- Backticks: the 38 backticked names cost 63 to 68 tokens, about 1.7 per name.
  JSON and YAML have no backticks, which is why they beat the Markdown forms.
  Plain text without backticks beat both.
- Heavy shorthand: this was its strongest honest form, with a two-entry legend
  (16 tokens), logic symbols, no articles and no backticks. It saved 23 to 36
  tokens (6 to 9%) beyond the no-backtick form.
- Emoji added 78 to 106 tokens (18 to 22%) to the same terse text.

### Words, abbreviations and symbols

Tokens for each form, written mid-sentence, in the order o200k / cl100k / Qwen3 / LFM2:

| Word | Short form | Symbol |
|---|---|---|
| configuration 1/1/1/1 | config 1/1/1/1, cfg 1/1/1/2 | |
| statements 1/1/1/1 | stmts 2/2/2/3 | |
| because 1/1/1/1 | b/c 2/2/2/2 | ∵ 2/2/2/2 |
| without 1/1/1/1 | w/o 2/2/2/2 | |
| therefore 1/1/1/1 | | ∴ 2/2/2/2 |
| then 1/1/1/1 | | → 1/1/1/1, ➡️ 3/3/3/4 |
| not 1/1/1/1 | | ¬ 2/1/1/2 |
| passes 1/1/1/1 | | ✓ 1/1/1/2, ✅ 1/2/2/2 |
| at least 2/2/2/2 | | ≥ 1/1/1/1 |

Common English words are already one token each, so a short form can at best
tie. A symbol saves a token only when it replaces several words, such as `≥`
for "at least".

### Where the tokens go

| Start of a chunk (o200k) | Bytes | Tokens |
|---|---:|---:|
| Rebuilt from the audit backlog, `START_HERE.md`, both validate scripts and the pathway head (Chunk Forty-Seven) | 38,021 | 9,579 |
| Read `CARRY_FORWARD.md` and the ready section (Chunk Forty-Nine) | 7,033 | 1,811 |

- Chunk Forty-Seven spent about 12 minutes reading before its first edit
  (pathway, Chunk Forty-Seven findings). The table counts only the files it
  read in full, as they are today, so 81% fewer tokens is a lower bound. The
  session itself saw about 90,000 characters of reads, which puts the saving
  near 92%.
- Instruction files loaded from outside the repository, at user and workspace
  level, can arrive in every session. One workspace measured during this research
  loaded about 12,700 tokens of them. One of those files held 9,800 tokens,
  about half of them dated status notes.
- For comparison, heavy shorthand would save 144 tokens on this handover.

## Published Evidence

- Formatting alone changes results. Across plausible prompt formats, accuracy
  differed by up to 76 points for LLaMA-2-13B. For GPT-3.5 the spread reached
  56 points, with a median of 6.4, across 320 formats and 53 tasks. How well a
  format worked on one model only weakly predicted how it worked on another
  (Sclar et al., ICLR 2024). A shorthand tuned to one agent can misfire on
  another, and "any coding agent" includes small local models.
- Machine compression works on long, repetitive text. LLMLingua-2 drops tokens
  that a small classifier judges unneeded, reaching 2 to 5 times compression
  with small reported losses. Its output is meant for a model to read, not for
  a person to write or review. Handovers and rules are already dense: once the
  filler and markup are gone, little remains to compress.

## Criteria Beyond Token Counts

- Review. The owner approves plans, reviews finished chunks and reads
  carry-forward flags, so the pathway and `CARRY_FORWARD.md` are not agent-only.
  Text a person cannot read cannot be checked for drift, mistakes or injected
  instructions. Truly agent-only text is narrow: handover facts, work packets
  and agent memory notes.
- Any agent. Shared files stay plain Markdown, and `AGENTS.md` stays the
  canonical instruction file: it is an open format stewarded by the Agentic AI
  Foundation (see the 2026-11-08 research record). Vendor-specific syntax, such
  as Claude Code's `@` imports and its memory-file conventions, belongs only in
  that vendor's own files.
- Exactness. Names, paths, numbers, line ranges and negations must survive
  intact. A shorthand that drops "not" reverses a rule.

## Where Compression Pays

Loading a compression procedure costs tokens too. The Semantic Compression
skill (see Sources) is 3,397 tokens (o200k). Against that cost:

| Document type | Examples | Does compressing pay? |
|---|---|---|
| Loaded every session | Instruction files, skill bodies, tool descriptions | Yes. One pass over a 3,643-token rules block costs about 10,700 tokens and is repaid in 12 to 24 sessions. |
| Loaded when relevant | Standards, reference documents | Slowly. Loading only the relevant section pays off sooner. |
| Read once or twice | Handovers, status notes, decision records | No. Repaying one skill load takes 28 to 59 reads, so write these compactly from the start. |

Stale content in an always-loaded file should be moved out, not compressed.
Backticks cost about 1.7 tokens per name, but they keep names and commands
exact and make them render correctly, so they stay.

## External Notes Compared

On 2026-11-09 Adam shared another agent's notes, "Portable Agent Document
Compression: Build Notes". They proposed a portable compression skill, a
cross-agent evaluation set and an optional Jev or Laya checking layer. The
notes contain no measurements; this record contains no comprehension test.

- Verified:
  - The Semantic Compression skill is MIT licensed, and its rules match these
    measurements: symbols do not save tokens, structure does, and a document
    that is already dense (under about 10% gain) should be left alone.
  - SkillReducer reports skill descriptions 48% shorter and skill bodies 39%
    shorter, with task results 2.8% better. The gains came from removing
    non-actionable text and loading detail only when needed, and they held
    across five models.
  - Laya's repository and the `app2610/laya` model card are both Apache 2.0.
- Agreed:
  - concise ordinary English, with no invented vocabulary and no decoder;
  - measuring tokens, not characters;
  - LLMLingua only as a point of comparison;
  - TOON only for uniform records;
  - a short core document, with detail loaded only when a stated condition
    applies.
- Adopted into the context hygiene standard:
  - the full list of what must survive compression;
  - keeping facts, assumptions, proposals, open questions and verified results
    apart;
  - one authoritative statement per rule, with explicit cross-references;
  - the stop rule;
  - compressing only text that is loaded repeatedly.
- Deferred:
  - A compression tool, until a test shows agents still meet each requirement,
    and then only for always-loaded text.
  - The Jev or Laya checking layer. Exact-match checks are a cheap first
    filter, but they cannot judge a changed exception or scope.
  - Separate compressed copies of documents, because a second copy is a second
    source of truth.
- Open: the notes cite the Laya checkpoint `app2610/laya`, the 2026-11-08
  record cites `convaiinnovations/laya`, and the owner's local copy came from a
  2026-10-10 qualification. Settle which checkpoint to use before any test.

## Guidance

The guidance now lives in one place: `docs/standards/context-hygiene-standard.md`,
in the sections Hand Over Through The Next Ready Chunk and Write Compactly For
Agents (Chunk Fifty, 2026-11-09). This record keeps the evidence behind it.

## Sources

- Sclar, Choi, Tsvetkov and Suhr, "Quantifying Language Models' Sensitivity to
  Spurious Features in Prompt Design or: How I learned to start worrying about
  prompt formatting", ICLR 2024: <https://arxiv.org/abs/2310.11324>
- "LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic
  Prompt Compression", 2024: <https://arxiv.org/abs/2403.12968>
- Tokenizers: `tiktoken` <https://github.com/openai/tiktoken>, Qwen3
  <https://huggingface.co/Qwen/Qwen3-0.6B>, LFM2
  <https://huggingface.co/LiquidAI/LFM2-1.2B>
- `docs/research/2026-11-08 - Frontier AI Engineering Practice Research.md`
  for the AGENTS.md and instruction-file findings
- Semantic Compression skill, oh-my-pi (MIT):
  <https://github.com/can1357/oh-my-pi/blob/main/.omp/skills/semantic-compression/SKILL.md>
- "SkillReducer: Optimizing LLM Agent Skills for Token Efficiency", 2026:
  <https://arxiv.org/abs/2603.29919>
- Laya: <https://github.com/NandhaKishorM/laya>, model card
  <https://huggingface.co/app2610/laya>
