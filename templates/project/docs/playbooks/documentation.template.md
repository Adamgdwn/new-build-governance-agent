# Build Playbook: Documentation

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/documentation.template.md`

Read this before you write or revise documentation in this project. It adds
documentation rules to `AGENTS.md`; where the two conflict, `AGENTS.md` and
`project-control.yaml` win.

## Done looks like

- Every command and code sample in the changed pages was run as written and
  works.
- Every link resolves.
- The reader the page is for can complete its task. Check by giving the page
  to an agent with a fresh context and asking it to follow the steps.

## Before you write

1. Name the reader and the task the page helps them complete.
2. Decide what kind of page it is (tutorial, how-to guide, reference, or
   explanation), and keep those kinds in separate pages.
3. Search for an existing page to update before creating a new one.

## Writing rules

- Point to code by file and line instead of copying it, so the page cannot
  drift from the code.
- Record why a decision was made, not only what it was; ADRs hold the reasons.
- Update the documentation in the same change as the behavior it describes.
- Follow the repository's naming rule for working documents (date-prefixed
  `YYYY-MM-DD - Title.md`) and its metadata header rules.
- Keep agent instruction files short and limited to what an agent cannot work
  out from the repository: commands, traps, and decisions. Do not write a tour
  of the repository into them; studies of agent context files found that tours
  add cost without improving results.

## Verify

- Run every command shown, check every link, and do the fresh-context reader
  test above.

## Failure modes agents produce here

- Plausible commands and options that do not exist.
- New documents that duplicate existing ones and then drift apart.
- Long generated instruction files and repository tours.
- Decisions recorded without their reasons.

## Where a System One model fits

A typed-judgment model can lint documentation in CI against your own rules:
whether a page still contains a placeholder, whether a step contradicts a
named standard, or whether a cited source supports the claim. Jev (TypeSafe,
hosted) works zero-shot; Laya (open weights, local) needs fine-tuning and a
held-out evaluation first. Treat each result as a review flag, not a verdict.

## Stop and ask

- Publishing externally, and legal, policy, or pricing text.
