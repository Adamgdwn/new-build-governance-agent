# Governance Level Standard

Document ID: STD-ENG-009
Version: 1.0
Status: active
Owner: Project Owner
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This standard defines the `governance_level` selector used in `project-control.yaml`: what each level means, what controls each level requires, and how the level relates to the risk tiers in [Risk Classification Standard](risk-classification-standard.md) and the agent-action tiers in [Engineering Governance By Use Case](engineering-governance-by-use-case.md).

`governance_level` is validated by automation as an integer from `0` through `4`. This document is the single definition of those five levels.

## Core Rule

`risk_tier` and `governance_level` are set independently in `project-control.yaml`, and both remain the source of truth for the project.

- `risk_tier` records how much harm the project can cause (see [Risk Classification Standard](risk-classification-standard.md)).
- `governance_level` records how much process, review, and control the owner has selected.

The crosswalk below gives the **recommended default** pairing. Bootstrap tooling applies the default automatically when only one of the two values is supplied. An owner may deviate — for example, a low-risk repo run at strict review, or a high-risk prototype temporarily held at level 2 — but the deviation must be justified in `project-control.yaml` notes or an exception record, and it should be revisited when the project is reclassified.

Agents and automation must not silently raise or lower either value. Governance mismatch findings (for example, a money-handling project at level 2) are owner-decision prompts, not automatic overrides.

## Governance Levels

### Level 0 — Full autonomy

Intent: throwaway experiments, sandboxes, and scratch work where the cost of a mistake is negligible and an agent may act without supervision.

Required controls:

- universal controls only: README or usage note, source control, secrets kept out of code
- clear prototype or experiment labeling, with no claims of production readiness
- isolation from production systems, credentials, and real sensitive data

### Level 1 — Light guardrails

Intent: low-risk projects that will persist, such as documentation repositories, small internal scripts, and isolated prototypes.

Required controls, in addition to level 0:

- core governance docs: `START_HERE.md` and `project-control.yaml`
- basic linting or validation where relevant
- backup or recovery note where project state matters

### Level 2 — Standard supervised

Intent: the default level for internal tools, non-critical automations, and public websites without sensitive regulated data. Agents work supervised: they propose material actions for review.

Required controls, in addition to level 1:

- defined test strategy
- staging or equivalent validation before production changes
- access and secret management controls
- release checklist before production changes
- governance preflight before risk-triggering changes

### Level 3 — Strict review

Intent: customer-facing applications, revenue-affecting systems, authenticated APIs, and agentic systems that can take impactful actions. This is the recommended minimum level for projects that handle money or sensitive data.

Required controls, in addition to level 2:

- stronger test coverage and integration checks
- deployment guide and operational runbook
- incident handling path and rollback procedure
- explicit approval before production release
- security review of sensitive surfaces

### Level 4 — Critical controls

Intent: money movement, sensitive personal data at scale, broad privileged access, or agents capable of autonomous external actions with material risk. Agents operate human-in-the-loop.

Required controls, in addition to level 3:

- separation of duties where feasible
- mandatory release approval by the project owner and, where those are distinct people, a separate technical lead; a solo owner records single-owner approval with the rationale rather than staging a two-hats ceremony (see the exception process in `document-control-standard.md`)
- auditable change and deployment history
- stronger access controls and mandatory security review
- disaster recovery expectations and recovery objectives

## Crosswalk: Governance Level, Risk Tier, and Agent-Action Tiers

This is the single crosswalk between the numeric governance levels, the Low/Medium/High/Critical risk tiers defined in [Risk Classification Standard](risk-classification-standard.md), and the agent-action tiers (Tier 0–5) defined in [Engineering Governance By Use Case](engineering-governance-by-use-case.md).

| Governance level | Name | Default risk tier | Default agent autonomy | Agent-action ceiling without human approval |
|---|---|---|---|---|
| 0 | Full autonomy | low | A2 | Tier 3 (external reversible actions) |
| 1 | Light guardrails | low | A2 | Tier 3 (external reversible actions) |
| 2 | Standard supervised | medium | A1 | Tier 2 (draft actions) |
| 3 | Strict review | high | A1 | Tier 2 (draft actions) |
| 4 | Critical controls | critical | A0 | Tier 0 (read-only, low sensitivity) |

Notes:

- The default risk tier column is the recommended pairing, not a derivation. When only a `risk_tier` is supplied, tooling fills in the matching level (`low` → 1, `medium` → 2, `high` → 3, `critical` → 4).
- Autonomy levels (`A0` advisory, `A1` proposes for approval, `A2` bounded actions with logging) are the scaffold defaults; agent projects may tighten them in `project-control.yaml`. The ceiling column follows the autonomy level: `A2` allows Tier 3 (external reversible actions), `A1` allows Tier 2 (preparing drafts and proposals, which is what "proposes for approval" means), and `A0` allows Tier 0 (read-only). Levels 2 and 3 share the Tier 2 ceiling by design — an A1 agent must be able to draft at both — and differ instead in their required controls (level 3 adds coverage, runbooks, rollback, and security review).
- At every governance level, Tier 4 actions (destructive or production) require explicit approval, and Tier 5 actions (irreversible or high-stakes) require a human decision. The ceiling column can lower these thresholds; it never raises them.
- Deviations from the default pairing must be justified in `project-control.yaml` notes or an exception record.

## Related Standards

- [Risk Classification Standard](risk-classification-standard.md) — sole definition of the Low/Medium/High/Critical risk tiers.
- [Engineering Governance By Use Case](engineering-governance-by-use-case.md) — use-case control guidance and the agent-action tier model.
- [Ship-Ready Engineering Standard](ship-ready-engineering-standard.md) — completion and release evidence expectations that scale with the selected level.
