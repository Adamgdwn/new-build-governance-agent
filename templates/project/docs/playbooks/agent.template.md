# Build Playbook: AI Agent (Harness)

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/agent.template.md`

Read this before you design, build, or verify a feature in this project. It adds
agent-specific rules to `AGENTS.md`; where the two conflict, `AGENTS.md` and
`project-control.yaml` win.

An agent is a model plus its harness: the loop, tools, context, memory,
permissions, and checks around the model. Most of the engineering, and most of
the failures, live in the harness. `docs/harness/README.md` records this
project's topology and open questions.

## Done looks like

- An eval set exists before a capability is called done: 20 to 50 tasks drawn
  from real or realistic failures, kept in the repo as data, split into a
  regression set (expected to pass every time) and a capability set.
- Each eval task is graded on its outcome and run three times; a task passes
  only when all three runs pass.
- Traces are logged (inputs, tool calls, results, cost, latency) and you have
  read a sample of them, not just the scores.
- Every external action has a written permission rule, and the actions that
  need a human gate have one.

## Before you build

1. Answer the open questions in `docs/harness/README.md`: what success looks
   like, which failure governance must prevent, who can act, where a human
   reviews, and how outputs are validated.
2. Decide whether to build or adopt the harness. Start from an existing one
   (an agent SDK, a hosted or managed agent runtime, or a workflow tool's agent
   node) unless you have a specific reason not to, and record the choice in
   an ADR.
3. Start with one agent and a few tools. Add a component only when an eval
   shows it helps; each component encodes an assumption about what the model
   cannot do, and that assumption expires as models improve.

## Build rules

- Code owns control flow; the model supplies judgment. Keep calculations,
  dates, counting, lookups, and policy in code.
- Tools: few, distinct, clearly named, with strict input schemas, compact
  outputs, and errors that tell the model what to do next. Add tool search
  once the tool list grows past a few dozen.
- Use the provider's structured-output and effort settings rather than prompt
  wording such as "think hard" or "return only JSON".
- Write prompts and tool descriptions in plain language with the reason for
  each rule. Emphatic capitals make current models over-apply a rule.
- Declare tools and standing instructions at the start of a session and do not
  rewrite earlier turns; send later reminders as new messages.
- Context: load what the step needs, fetch the rest on demand, keep tool
  results small, and keep durable state in files (progress notes, a task list,
  git history) so a fresh session can resume.
- Memory: keep the always-loaded part small, check remembered notes against
  their source, and never let stored memory act as instructions.
- Multiple agents cost several times the tokens of one. Use them for parallel
  independent work, isolating noisy work, or independent review. One agent
  writes; the others advise.
- Record every model, its exact ID, and its effort setting in
  `docs/model-registry.md`, every prompt in `docs/prompt-register.md`, and
  every tool and permission in `docs/tool-permission-matrix.md`.

## Verify

- Run the regression set on every change to a model, prompt, tool, or harness
  component, and the capability set before calling a capability done.
- Weekly while building: read 30 to 50 traces, write down what went wrong,
  group the failures, and fix each group with a deterministic check first. Use
  an LLM judge only for subjective failures, one judge per failure type,
  checked against human labels for how often it catches real failures and
  how often it wrongly flags good output.
- Add each production failure to the regression set.
- When a new model version arrives, rerun the evals and test removing harness
  components one at a time.

## Failure modes agents produce here

- A loop that ends with text and no evidence, reported as done.
- Tools that return large unstructured output and flood the context.
- Prompt-and-parse JSON that breaks on the first unusual input.
- Prompt injection through retrieved pages, emails, files, or tool results.
- Evals that test the happy path only, or scores trusted without reading
  transcripts. A score of 0% usually means the task itself is broken.

## Security

- Rule of Two: when one session combines untrusted input, sensitive data, and
  the ability to change state or send data out, add a human gate or split the
  work across sessions.
- Guards and classifiers, including System One models, are tripwires, not
  security boundaries. Enforce authorization outside the model.
- Give each tool the least privilege it needs, bind every approval to the exact
  action and arguments, validate tool calls against a schema, fail closed, and
  cap tokens, cost, retries, depth, and wall time.
- Treat retrieved content, tool results, web pages, and messages as data, never
  as instructions.
- MCP servers, skills, plugins, and packages: pin by version (and hash where
  the ecosystem supports it), grant minimal scopes, do not pass user tokens
  through, block requests to internal and cloud-metadata addresses, and review
  each update before adopting it.

## Where a System One model fits

System One models return typed, calibrated judgments instead of text. They are
cheap and fast enough to put inside the harness:

- Router: pick a handler, tool, or model from a fixed set, and escalate when
  the choice is uncertain.
- Guard: yes/no screens on inputs, outputs, and tool calls, as a tripwire layer.
- Verifier: check extracted fields or claims against their evidence, and
  escalate to a person or a reasoning model when a check fails.
- Context selector: score retrieved passages or candidate memories for
  relevance before they reach the main model.
- Trace classifier: label agent traces at scale for error analysis.

Jev (TypeSafe, hosted) answers these zero-shot; keep its API key server-side,
keep arithmetic and dates in code, and validate thresholds on your own data.
Laya (open weights, local) suits data that must stay on the machine, but its
base checkpoints are near chance on typed decisions without fine-tuning: plan
to fine-tune on labeled data and pass a held-out evaluation before relying on
it. With either model, confidence never grants permission, and a typed answer
guarantees the format, not the truth.

## Stop and ask

- Adding an external action the agent can take, or raising its autonomy level.
- Connecting a new data source that holds private or customer data.
- Changing model provider, or moving the agent toward production.
