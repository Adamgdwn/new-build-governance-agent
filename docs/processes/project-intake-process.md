# Project Intake Process

Document ID: PRC-ENG-001
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: 2026-07-10
Last Reviewed: 2026-07-10
Next Review: 2026-10-10

## Purpose

This process defines how a new project enters governance under this framework.

## Intake Steps

1. Create the repository or identify the monorepo subproject boundary.
2. Assign project owner and technical lead.
3. Classify project type and initial governance level.
4. Create the required documents from templates.
5. Define environments, testing approach, and release path.
6. Document sensitive data, money flow, or privileged access if applicable.
7. Record any startup exceptions.
8. Enable baseline machine enforcement.

## Required Intake Outputs

- `project-control.yaml`
- `README.md`
- architecture overview
- risk register
- deployment guide if deployable
- runbook if operable
- agent controls if agentic

## Baseline Machine Enforcement

At minimum, enable or plan:

- required-file checks
- lint or validation
- test execution where applicable
- secret scanning
- changelog or release record validation
