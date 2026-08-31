# Code Complexity Control Standard

Document ID: STD-ENG-023
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-08-31
Last Reviewed: 2026-08-31
Next Review: 2026-11-30
Document type: engineering control standard
Audience: coding agents, human coders, reviewers, and technical leads

## Purpose

This standard uses cyclomatic complexity as a practical signal for code that may be
harder to understand, test, and safely change. It provides plain-language guidance,
default review bands, and a safe path from reporting to enforcement.

## Plain-Language Meaning

Cyclomatic complexity is a rough count of the decision routes through a function or
method. A straight-line function starts at one. Conditions, loops, exception branches,
and similar choices increase the score.

The score is a smoke alarm, not a verdict. It can point to code that deserves closer
review and stronger tests, but it does not measure naming, architecture, business
difficulty, side effects, security, or overall readability.

## Core Rule

Use complexity to start a design and testing conversation. Do not treat one number as
proof that code is good or bad, and do not split coherent code into shallow wrappers
merely to lower a score.

## Default Control Bands

Projects may tune these bands for their language, tooling, codebase, and risk. Record
the chosen values in `project-control.yaml` or the repository's equivalent control
file.

| Score | Default response |
|---|---|
| 1-10 | Ordinary review and normal risk-appropriate tests. |
| 11-20 | Advisory warning. Inspect responsibilities, nesting, state changes, and branch-focused tests. |
| 21+ | Refactor into coherent responsibilities or record a justified exception with stronger test evidence. |

Generated code, parsers, protocol handlers, dispatch tables, state machines,
compatibility logic, and other inherently branch-heavy code may reasonably need an
exception.

## Required Agent Behavior

When meaningful code is added or changed, the coding agent should:

1. Use the project's existing complexity tool when one is configured and practical.
2. Discuss a finding in plain language: what decisions make the code hard to follow,
   what can fail, and what tests cover the important routes.
3. Prefer early returns, named decisions, decision tables, clear state transitions,
   and separation of pure decision logic from side effects when those changes improve
   the design.
4. Keep a complex block when it is the clearest model of the problem, then record the
   rationale, focused tests, reviewer or owner, and review point.
5. Avoid unrelated repository-wide cleanup. Existing findings form a baseline; changed
   code should not make them worse without an explicit reason.

## Testing Companion

Complexity findings should change the testing conversation, not just the shape of the
code. For important decision logic, use one or more of:

- a decision table mapping conditions to outcomes
- branch and boundary tests
- negative-path and failure-mode tests
- state-transition tests
- property-based tests where combinations are large

Cyclomatic complexity estimates independent control-flow paths. It does not prove that
those paths are feasible or that a specific number of tests is sufficient.

## Rollout And Enforcement

Adopt the control in stages:

1. **Report:** show findings without failing validation.
2. **No regression:** review new or materially worsened findings in changed code.
3. **Decision gate:** require refactoring or a recorded exception for new or changed
   code at 21 or above.
4. **Risk-scaled enforcement:** use stricter project-specific gates for authorization,
   payments, destructive actions, safety checks, and critical workflow state changes.

Do not turn an existing baseline into an immediate blocking gate. Inventory it first,
select a threshold deliberately, and retain approved exceptions.

## Tooling Guidance

Use the project's normal linter or static-analysis stack where possible. Examples:

- Python with Ruff: `python -m ruff check <paths> --select C901`
- JavaScript or TypeScript with ESLint: configure the core `complexity` rule

Counting rules and defaults differ between tools and languages. A project threshold is
therefore local configuration, not a universal quality score. Do not add a dependency
solely for this metric without explaining its maintenance cost and expected value.

## Exceptions

An exception should record:

- affected function or module
- measured score and tool
- why the branching is clearer or safer than the available refactor
- focused test evidence
- compensating review control
- owner and next review date

## Review Cadence

Review this control at least quarterly while it is being introduced, and after a
material change to the project's language, linting stack, risk, or architecture. Use
the Governance Source Alignment Standard to compare project-local controls with the
current governance source.

## References

- [McCabe, A Complexity Measure](https://doi.org/10.1109/TSE.1976.233837)
- [NIST Structured Testing](https://www.nist.gov/publications/structured-testing-testing-methodology-using-cyclomatic-complexity-metric)
- [Ruff C901](https://docs.astral.sh/ruff/rules/complex-structure/)
- [ESLint complexity rule](https://eslint.org/docs/latest/rules/complexity)
- [Shepperd, A Critique of Cyclomatic Complexity as a Software Metric](https://doi.org/10.1049/sej.1988.0003)
