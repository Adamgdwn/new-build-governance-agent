# Code Complexity Control Standard

Document type: engineering control standard
Status: active
Owner: Project owner or human technical lead
Audience: coding agents, human coders, reviewers, and technical leads

## Purpose

This standard uses cyclomatic complexity as a practical signal for code that may be
harder to understand, test, and safely change.

## Plain-Language Meaning

Cyclomatic complexity is a rough count of the decision routes through a function or
method. A straight-line function starts at one. Conditions, loops, exception branches,
and similar choices increase the score.

The score is a smoke alarm, not a verdict. It can point to code that deserves closer
review and stronger tests, but it does not measure naming, architecture, business
difficulty, side effects, security, or overall readability.

## Default Control Bands

| Score | Default response |
|---|---|
| 1-10 | Ordinary review and normal risk-appropriate tests. |
| 11-20 | Advisory warning. Inspect responsibilities, nesting, state changes, and branch-focused tests. |
| 21+ | Refactor into coherent responsibilities or record a justified exception with stronger test evidence. |

Projects may tune these bands for their language, tooling, codebase, and risk. Record
the selected values in `project-control.yaml` or the repository's equivalent control
file. Generated code, parsers, protocol handlers, dispatch tables, state machines, and
compatibility logic may reasonably need an exception.

## Agent Rules

- Use the project's existing complexity tool when one is configured and practical.
- Explain findings in plain language: the important decisions, failure paths, and test
  coverage.
- Prefer coherent responsibilities, named decisions, decision tables, clear state
  transitions, and separation of pure decisions from side effects.
- Do not create shallow wrappers merely to lower a score.
- Keep an inherently complex block when it is the clearest model, then record the
  rationale, focused tests, reviewer or owner, and review point.
- Treat existing findings as a baseline and avoid unrelated repository-wide cleanup.

## Testing Companion

For important decision logic, use branch and boundary tests, negative-path tests,
decision tables, state-transition tests, or property-based tests as appropriate.
Cyclomatic complexity does not prove that every route is feasible or that a particular
number of tests is sufficient.

## Rollout

1. Report findings without failing validation.
2. Review new or materially worsened findings in changed code.
3. Require refactoring or a recorded exception for new or changed code at 21 or above.
4. Use stricter project-specific gates for high-risk decision logic when justified.

Do not turn an existing baseline into an immediate blocking gate. Counting rules and
defaults differ between tools and languages, so project thresholds remain local
configuration.

## Exception Record

Record the affected block, score and tool, rationale, test evidence, compensating
review, owner, and next review date.

## Review Cadence

Review this control when the language, linting stack, risk, or architecture changes,
and during the periodic governance-source alignment review.
