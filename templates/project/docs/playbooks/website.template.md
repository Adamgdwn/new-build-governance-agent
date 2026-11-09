# Build Playbook: Website

Document type: build playbook
Status: active
Owner: Technical Lead
Last Updated: 2026-11-08
Source: New Build Governance Agent, `templates/project/docs/playbooks/website.template.md`

Read this before you design, build, or verify a page or feature in this
project. It adds website-specific rules to `AGENTS.md`; where the two conflict,
`AGENTS.md` and `project-control.yaml` win.

## Done looks like

- The page renders in a real browser at phone width (375 px) and desktop width,
  with screenshots kept as evidence. Code that looks right is not evidence
  that the rendered page is right.
- The browser console shows no errors on the changed pages.
- An automated accessibility check (axe, Lighthouse, or the project's tool)
  passes, and the page works with a keyboard alone.
- Every link and form on the changed pages works.

## Before you build

1. Name the audience and the one action each page should lead to.
2. Find the existing components, styles, and content structure, and reuse them.

## Build rules

- Use semantic HTML first: headings in order, labelled form fields, alt text
  that describes the image's purpose, and buttons for actions.
- Meet colour-contrast and focus-visibility basics; do not remove focus
  outlines without a replacement.
- Keep a performance budget: right-sized and lazy-loaded images, no unused
  scripts, and fonts that do not block rendering.
- Set titles, descriptions, canonical URLs, and social preview tags for each
  public page.
- Validate forms on the server and protect them from spam. Client-side
  validation is for the user's convenience only.
- Treat CMS and user-supplied content as untrusted and escape it before
  rendering.
- Review every third-party script for what data it collects.

## Verify

- Run the build, serve it locally, and check the changed pages in a browser at
  both widths.
- Run the accessibility and link checks, and Lighthouse or an equivalent for
  performance on the main pages.

## Failure modes agents produce here

- Pages that fail basic accessibility checks.
- Cross-site scripting through unescaped content.
- A backend-as-a-service key or database exposed to the browser without
  row-level security.
- Layouts that break at phone width.
- Packages that do not exist, or that are not the package you meant.
  Confirm a package before adding it, and commit the lockfile.

## Security

- No secrets in client code or public environment variables.
- Set a content security policy and other security headers when the host
  allows it.

## Where a System One model fits

A typed-judgment model suits narrow decisions behind the site, such as sorting
contact-form messages by intent or flagging spam. Call it from a server
function, never from browser code. Jev (TypeSafe, hosted) works zero-shot;
Laya (open weights, local) needs fine-tuning and a held-out evaluation first.

## Stop and ask

- Domain or DNS changes, analytics or tracking that collects personal data,
  and publishing to production.
