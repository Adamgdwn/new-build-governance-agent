# New Build Governance Agent Consolidation Plan

Document ID: PRC-ENG-004
Version: 1.0.0
Status: retired
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Note: Decision executed — retained for traceability.

## Decision

`New Build Governance Agent` should remain the primary product and operator entrypoint.

`New Project Setup Agent` should not continue as a separate end-user product.
Its strongest ideas should be folded into `New Build Governance Agent` and the shared governance automation in this repository.

## Why

`New Build Governance Agent` already owns the user-facing workflow:

- desktop launcher
- GUI intake
- project classification
- root selection under `~/code/agents` and `~/code/Applications`
- governed scaffolding through `automation/bootstrap_project.sh`
- initial scope capture

`New Project Setup Agent` overlaps with that purpose, but adds backend-oriented capabilities that are valuable:

- structured change requests
- approval and apply workflow
- managed project inventory
- project audit logic
- workspace-boundary enforcement

The overlap is significant enough that keeping both as parallel products would create confusion and drift.

## Product Direction

The combined system should look like this:

- `New Build Governance Agent` remains the desktop and GUI intake layer.
- `bootstrap_project.sh` remains the core scaffolding engine.
- governance checks remain repo-local shell tooling for portability.
- structured controller features are added behind the launcher, not as a second product identity.

In practice, the product becomes:

1. intake and classification
2. governed scaffold generation
3. project registration and inventory
4. audit and drift detection
5. approval-driven structural upgrades
6. roadmap/manual/document refresh support
7. staged external promotion planning

## What To Keep

Keep these `New Build Governance Agent` strengths as the stable base:

- `automation/new_build_gui.py`
- `automation/new_build.sh`
- `automation/bootstrap_project.sh`
- `automation/governance_check.sh`
- `templates/project/`
- the existing desktop launcher and icon

Keep these `New Project Setup Agent` concepts and port them in:

- controlled workspace boundary checks
- structured change manifests instead of prose-only notes
- change states such as `pending`, `approved`, `applied`, `rejected`
- managed project inventory
- repo audit summaries
- generated manuals and roadmap artifacts as first-class outputs

## What To Retire

Retire the idea of `New Project Setup Agent` as a separate launcher-facing product.

Do not keep:

- a second launcher for the same job
- a second independent scaffolding identity
- a separate product name for the same domain

The repo can remain temporarily as a prototype/reference while work is ported over, but it should be archived or absorbed after the merge.

## Target Architecture

Recommended architecture inside `New Build Governance Agent`:

```text
automation/
  new_build_gui.py
  new_build.sh
  bootstrap_project.sh
  governance_check.sh
  project_registry.py
  change_control.py
  audit_projects.py
  promotion_plan.py
  install_new_build_agent_launcher.sh

templates/
  project/
    README.template.md
    AGENTS.template.md
    AI_BOOTSTRAP.template.md
    project-control.template.yaml
    docs/
      architecture.template.md
      manual.template.md
      roadmap.template.md
      runbook.template.md
      CHANGELOG.template.md
      risk-register.template.md
      agent-inventory.template.md
      model-registry.template.md
      prompt-register.template.md
      tool-permission-matrix.template.md
    scripts/
      governance-preflight.template.sh

data/
  new-build-governance-agent/
    registry.sqlite3
    exports/
```

## Capability Merge Map

### Phase 1: Strengthen the current scaffold

Add to the existing template set:

- `docs/manual.md`
- `docs/roadmap.md`
- optional `docs/human-oversight-rules.md`

Expand `bootstrap_project.sh` so these are created by default.

Result:

- every new project starts with the same fuller governance baseline
- no product rename is required
- minimal disruption to the existing GUI

### Phase 2: Add project registry and audit backend

Add a local SQLite registry for:

- projects created by `New Build Governance Agent`
- path, type, governance level, risk tier, builder, created date
- audit status
- latest governance check result

Add a Python or shell-backed audit command that can:

- scan `~/code/agents` and `~/code/Applications`
- identify governed projects
- report missing required files
- export summary reports

Result:

- the launcher becomes aware of past builds
- you gain a real inventory of managed projects

### Phase 3: Add controlled upgrade workflow

Introduce structured change manifests for project-wide upgrades such as:

- add missing docs
- standardize preflight scripts
- refresh template-generated files
- inject new governance sections

Recommended flow:

1. detect drift
2. generate upgrade manifest
3. preview affected files
4. approve
5. apply
6. record result

Result:

- `New Build Governance Agent` becomes a true project controller, not only a bootstrapper

### Phase 4: Unify GUI and controller features

Extend the GUI with additional tabs or panels:

- `Create`
- `Inventory`
- `Audit`
- `Upgrades`
- `Reports`

Do not replace the current simple create flow first.
Add these features incrementally so the current launcher remains reliable.

## Implementation Order

1. Expand templates to include `manual` and `roadmap`.
2. Update `bootstrap_project.sh` to create the new baseline files.
3. Update `new_build_gui.py` to show the fuller scaffold summary.
4. Add `project_registry.py` with SQLite-backed project records.
5. Record each successful scaffold into the registry.
6. Add `audit_projects.py` to scan and summarize governed projects.
7. Add a GUI inventory/audit view.
8. Add structured change manifests for upgrades.
9. Port only the useful backend logic from `New Project Setup Agent`.
10. Archive or absorb the sidecar repo after parity is reached.

## Risks

### Risk: two sources of truth

If both products keep evolving, templates and behavior will drift.

Mitigation:

- treat this repository as the canonical product
- port features in one direction only

### Risk: overcomplicating the launcher too early

If approval, registry, and audit features all land at once, the GUI may become brittle.

Mitigation:

- keep the create flow stable
- add inventory and audit as read-oriented features first

### Risk: shell and Python logic drift apart

Current behavior is split across shell and Tkinter code.

Mitigation:

- move shared logic into small reusable helpers
- keep shell scripts thin where possible

## Recommended Immediate Next Step

Start with Phase 1 and Phase 2 only.

That gives you:

- a better governed scaffold immediately
- one canonical product
- no user-facing ambiguity
- a clear backend foundation for future upgrade control

Do not begin by porting the whole API app.
Port the concepts, not the second product.
