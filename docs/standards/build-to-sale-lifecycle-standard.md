# Build-To-Sale Lifecycle Standard

Document ID: STD-ENG-025
Version: 1.0.0
Status: active
Owner: Project Owner
Approver: Project Owner
Effective Date: 2026-09-30
Last Reviewed: 2026-09-30
Next Review: 2026-12-30
Document type: product lifecycle standard
Audience: project owners, coding agents, technical leads, and release reviewers

## Purpose

This standard carries a product from problem to repeatable sale, not only from plan to
shipped code. The engineering standards in this repository define what good code and a
ship-ready change look like. They do not say whether anyone wants the product, what a
customer will commit to, or what commercial, trust and support material must exist
before a sale. This standard fills that gap.

Part A holds the adoption rules for governed builds. Part B is the source framework,
the Build-to-Sale Operating System, which supplies the phase detail, checklists and
templates.

## Adoption Record

- Source: `build-to-sale-operating-system.md`, supplied by the project owner on
  2026-09-30.
- Decision: Adam Goodwin, 2026-09-30, approved cross-project use, and asked that the
  lifecycle include a search for grants, loans, hosting credits and partners.
- First application: the Span OS full lifecycle plan
  (`docs/planning/FULL-LIFECYCLE-PLAN.md` in that repository), which also keeps its own
  unchanged copy of the source.

## Scope

Apply this standard to any project intended for external customers or sale: paid
applications, SaaS services, sold tools, and agent products offered to others.

Internal tools, personal automations, infrastructure, documentation projects and this
governance source may use parts of it but are not required to. When a project's
audience changes from internal to external, this standard starts to apply at that
point, alongside the risk reclassification the change requires.

## Relationship To Other Standards

| Standard | Relationship |
|---|---|
| [Ship-Ready Engineering Standard](ship-ready-engineering-standard.md) | Governs how each engineering change is framed, built, tested and released. Its twelve-step *change* lifecycle is separate from the twelve *business* phases here. It supplies the Engineering and much of the Operational definition of done. |
| [Risk Classification Standard](risk-classification-standard.md) | Reclassify when the audience changes: synthetic demonstration → design partner → paying customer → public release. Do not wait for launch. |
| [Engineering Governance By Use Case](engineering-governance-by-use-case.md) | Use-case controls still apply within each phase. |
| [Governance Source Alignment Standard](governance-source-alignment-standard.md) | Existing projects adopt this standard through an alignment review, not a silent overwrite. |

Project-local gates, milestones and decisions remain authoritative. Map them onto the
phases; do not replace them.

## Core Rules

1. **Record the lifecycle position.** Each project in scope keeps a phase table in its
   active plan or a lifecycle document. Record the status for each phase as Not started,
   Hypothesis, Partial, Evidenced or Not yet due. Update it at material planning work.
2. **Exits need evidence, not code.** Do not begin substantial Phase 05 engineering
   spending until Phase 02 has exited and Phase 03 has produced a commitment: a design
   partner, paid discovery, a letter of intent or a pre-sale. The owner may record an
   exception, such as funded research or a personal tool, with the reason and a review
   point.
3. **Treat early builds as instruments.** Anything built before the Phase 02 exit is a
   validation instrument. It uses synthetic data, is time-boxed and may use a disposable
   toolchain. Decide the production toolchain and supported devices at the Phase 04
   exit, from customer evidence.
4. **Classify features P0–P3 at Phase 04.** Nothing is P0 until evidence confirms the
   outcome it serves.
5. **Use four definitions of done:** Engineering, Product, Commercial and Operational.
   Do not describe a product as complete when only Engineering is done.
6. **Change prices only on evidence.** Record the customer evidence and the reason with
   each price change.
7. **Choose and test a channel before general release.** A release with no channel is
   not a launch.
8. **Schedule productization against demand.** Build billing, licensing and commerce
   when a pilot or customer needs them. Do not build them before a demand signal, and do
   not leave them missing when one arrives.
9. **Log founder intervention** from the first pilot day. Hidden founder work is not a
   repeatable product.
10. **Record plan-versus-action drift when it happens.** When work departs from the
    planned phase order, say so and record the reason.
11. **Keep customer contact visible.** Before the Phase 02 exit, when planning,
    documentation or engineering effort far outweighs recorded customer contact, the
    agent says so at the start of material planning work.

## Funding, Credits And Partners Track

This track runs alongside the customer phases. It can lower cash need and speed the
build, but it never replaces customer evidence.

- **Phase 01 — inventory what is already held.** Cloud and hosting credits, developer
  tool programs, AI model credits, existing accounts and partner memberships. For each,
  record: provider, amount, owning entity (personal or company), expiry, usage
  restrictions, and whether a one-time startup eligibility has already been used.
- **Phases 01–03 — search what is available** for the project's jurisdiction, sector
  and stage. Cover grants, research and development tax credits, loans, wage subsidies,
  startup credit programs, accelerators, and partner or channel programs relevant to
  the systems the product works with. Record the source link, the date checked, the
  eligibility prerequisites (for example incorporation, ownership, location, revenue or
  an affiliation) and the stage at which each becomes usable.
- **Timing rules:**
  - Credits usually expire. Activate them when the matching build or pilot work starts,
    not during discovery.
  - Credits are one input to the production provider decision at the Phase 04 exit.
    They do not decide it early.
  - Some grants exclude costs incurred before approval. Engage the program before
    spending on the work it would fund.
  - Research tax credits typically need records made at the time of the work. Start
    them with the first engineering work.
  - Financial models keep possible funding separate from committed funding. Downside
    cases exclude possible funding.
- **Refresh** the search at each phase exit and at least every 90 days while the
  project is active. Programs open, close and change terms.
- **Authority:** agents research and prepare. Applications, account creation,
  acceptance of terms, sign-ups and contact with programs are owner actions.

## Agent Boundaries

- Do not contact prospects, investors, programs or partners, publish, spend, sign up
  or process real customer data without the owner's authorization.
- Never invent customer evidence, commitments, sign-off or program eligibility. Record
  a commitment only as the owner reports it, with its source and date.
- Prepare the instruments: trackers, interview guides, offers, demonstrations using
  synthetic data, and funding searches.

## Document Locations

The source framework places lifecycle documents in root `/product`, `/engineering` and
`/commercial` folders. Projects may put them elsewhere, for example `docs/lifecycle/`,
when those folders are reserved or would clash with source code. Record the choice in
the project's plan. Create each document when its phase is reached, not all at once.

## Lessons Behind The Adaptations

The core rules above add to the source framework. They come from a 2026 consumer
product build in this workspace:

- Market validation was planned more than once, then displaced by infrastructure work.
- Pricing changed three times in a week without customer input.
- Commerce was built before any demand signal, against its own plan.
- Risk was reclassified weeks after the audience became external.
- A paid launch went live with no channel chosen.

## Distribution

The single canonical copy is this file. A short summary lives in the workspace-level
`CLAUDE.md`. This standard is not a mandatory startup read, and no per-project copy is
generated yet. Scaffold templates, the upgrade manifest and a `project-control.yaml`
lifecycle field are deferred; see `CARRY_FORWARD.md`.

## Review Cadence

Review this standard quarterly during its initial rollout, and at least annually after
it is stable.

---

# Part B — Source Framework

The owner supplied the text below on 2026-09-30. Headings are shifted down one level so
that they sit under this part. The text is otherwise unchanged.

## Build-to-Sale Operating System for Coding Agents

### Purpose

This framework governs software projects from idea through repeatable commercial operation.

The core principle is:

> **Do not wait until the product is complete to discover whether the market wants it.**

Software should move through market validation, customer discovery, demonstrations, pilot commitments, and where appropriate paid pre-sales before engineering is complete.

The objective is to build toward a verified customer, verified problem, and verified buying pathway rather than finishing a technically strong product and only then attempting to find a market for it.

A project is not successful because it works on the developer's machine.

A successful project must ultimately allow a target customer to:

> **Discover it → understand it → trust it → commit to it → access it → get value → get help → renew or expand**

---

## 1. Core Operating Principles

All coding agents, planning agents, product agents, and review agents must follow these principles.

### 1.1 Validate before fully building

Do not assume that technical usefulness equals commercial demand.

Before committing substantial engineering effort, establish:

- who the target customer is
- what problem is being solved
- how the customer currently solves it
- why the problem matters enough to change behaviour
- whether there is budget or willingness to pay
- what minimum feature set is required for purchase or pilot
- what objections or trust barriers exist
- what outcome the buyer expects

### 1.2 Sell the outcome, not the architecture

Technical sophistication is supporting evidence, not the primary commercial message.

Commercial messaging should describe:

- the problem
- the outcome
- the user
- the use case
- the measurable benefit
- the buying pathway

Do not lead with model architecture, orchestration, frameworks, infrastructure, databases, agent design, or implementation details unless the customer specifically needs them.

### 1.3 Do not overbuild before evidence

Once a product is sufficiently functional to demonstrate the intended value, engineering should slow down and market learning should increase.

Agents must not create speculative features merely because they appear useful.

Every significant feature should be traceable to at least one of:

- validated customer need
- contractual requirement
- pilot requirement
- security requirement
- operational requirement
- regulatory requirement
- measurable product usage evidence
- explicit strategic requirement from the product owner

### 1.4 Commercial readiness is part of product quality

A technically complete application is not a complete product.

Commercial readiness includes:

- production deployment
- account creation
- authorization
- onboarding
- pricing
- billing or contracting
- trust and security information
- customer support
- monitoring
- analytics
- administration
- renewal or expansion pathways

### 1.5 Founder intervention must be visible

If the founder must manually configure, explain, repair, provision, or operate part of the customer experience, that dependency must be documented.

Founder-led onboarding is acceptable during validation and early sales.

Undocumented founder dependency is not acceptable.

---

## 2. Product Lifecycle

Use the following lifecycle for all software builds.

```text
01 PROBLEM DEFINITION
        ↓
02 MARKET VALIDATION
        ↓
03 OFFER AND PRE-SALE
        ↓
04 PRODUCT DESIGN
        ↓
05 ENGINEERING
        ↓
06 PILOT / DESIGN PARTNER VALIDATION
        ↓
07 ENGINEERING COMPLETE
        ↓
08 PRODUCTIZATION
        ↓
09 COMMERCIAL READY
        ↓
10 GENERAL RELEASE
        ↓
11 REPEATABLE SALES
        ↓
12 SCALE
```

A project should not automatically move forward because code exists.

Each phase has an exit gate.

---

## 3. Phase 01: Problem Definition

### Objective

Define a real problem for a specific customer before designing the full solution.

### Required outputs

Create or update:

```text
/product/PROBLEM.md
/product/ICP.md
/product/USE-CASES.md
```

### Required questions

The project must answer:

- Who specifically experiences the problem?
- How often does it occur?
- What does it cost in time, money, risk, delay, labour, or lost opportunity?
- How is it solved today?
- What is frustrating about the current solution?
- Who owns the problem?
- Who has authority to purchase a solution?
- Who will actually use the product?
- What measurable outcome would make the product valuable?

### Exit gate

Do not proceed to full product design until there is a credible problem hypothesis and identifiable target customer.

---

## 4. Phase 02: Market Validation

### Objective

Test whether the problem and proposed outcome matter to real prospective customers before substantial engineering investment.

### Validation activities

Use combinations of:

- customer interviews
- workflow observation
- problem interviews
- prototype demonstrations
- mockups
- clickable interfaces
- manual concierge versions
- landing pages
- waitlists
- pricing discussions
- letters of intent
- pilot agreements
- paid discovery
- pre-sales
- design partner commitments

### Important rule

Validation is not:

> "Would you use this?"

Prefer evidence based on commitment.

Stronger signals include:

1. Customer provides meaningful operational information.
2. Customer agrees to another meeting.
3. Customer introduces additional stakeholders.
4. Customer agrees to test a prototype.
5. Customer agrees to a pilot.
6. Customer signs a letter of intent.
7. Customer provides procurement requirements.
8. Customer pays for discovery, implementation, pilot, or product access.

### Required output

Create:

```text
/product/MARKET-VALIDATION.md
```

It should track:

| Customer / Segment | Problem Confirmed | Current Solution | Must-Have Features | Buying Authority | Price Signal | Commitment | Notes |
|---|---|---|---|---|---|---|---|

### Exit gate

Before major engineering begins, there should be enough evidence to answer:

- who the initial customer is
- what problem is being solved
- what outcome they will pay for
- what the minimum valuable feature set is

---

## 5. Phase 03: Offer and Pre-Sale

### Objective

Turn the validated problem into something that can be purchased before the complete product exists.

The preferred sequence is:

```text
Problem
   ↓
Outcome
   ↓
Offer
   ↓
Price
   ↓
Commitment
   ↓
Build
```

Not:

```text
Idea
   ↓
Build everything
   ↓
Launch
   ↓
Hope
```

### Define the offer

Create:

```text
/product/OFFER.md
/product/PRICING.md
```

The offer must define:

- target customer
- problem being solved
- promised outcome
- initial scope
- exclusions
- implementation requirements
- pilot structure
- commercial model
- price or pricing hypothesis
- support model
- expected time to first value

### Pre-sale models

Depending on the product, use one or more:

#### Design Partner

Customer receives early influence and preferential access in exchange for structured feedback.

#### Paid Pilot

Customer pays for a bounded implementation or trial.

#### Founding Customer

Customer commits before general release in exchange for preferential commercial terms or enhanced participation.

#### Paid Discovery

Customer pays for process analysis, integration mapping, data assessment, workflow design, or implementation planning before the full product exists.

#### Letter of Intent

Useful where procurement timing prevents immediate payment but purchase intent can be documented.

### Ethical requirement

Never represent incomplete software as complete.

Clearly distinguish:

- available now
- prototype
- beta
- pilot
- planned
- under development

### Exit gate

Before substantial feature expansion, the project should have at least one credible commercial pathway such as:

- committed design partner
- paid pilot
- paid discovery
- signed LOI
- documented procurement pathway
- credible buyer actively progressing toward purchase

---

## 6. Phase 04: Product Design

### Objective

Design only enough product to deliver the validated customer outcome.

### Required outputs

```text
/product/PRODUCT.md
/product/REQUIREMENTS.md
/product/USER-JOURNEYS.md
/product/ONBOARDING.md
```

### Feature classification

Every planned feature must be classified:

#### P0: Required to deliver the purchased or validated outcome

Must be built.

#### P1: Required for safe and reliable operation

Examples:

- authentication
- permissions
- logging
- backup
- security controls
- auditability

Must be built before appropriate release.

#### P2: Improves usability or customer value

Build when validated.

#### P3: Speculative enhancement

Do not build without supporting evidence.

---

## 7. Phase 05: Engineering

### Objective

Build the smallest reliable product capable of delivering the validated outcome.

### Engineering path

```text
Requirements
    ↓
Architecture
    ↓
Implementation
    ↓
Testing
    ↓
Security
    ↓
Deployment
    ↓
Observation
```

### Engineering rules

Agents must:

- preserve traceability from requirement to implementation
- maintain a production-capable architecture
- avoid unnecessary platform complexity
- create automated tests appropriate to risk
- document environment variables
- manage database migrations
- provide rollback capability
- implement logging and observability
- document external dependencies
- identify security-sensitive functionality
- keep customer data boundaries explicit
- prevent hidden manual dependencies

### Required engineering documentation

```text
/engineering/ARCHITECTURE.md
/engineering/STANDARDS.md
/engineering/TESTING.md
/engineering/SECURITY.md
/engineering/DEPLOYMENT.md
/engineering/RELEASE.md
```

---

## 8. Phase 06: Pilot / Design Partner Validation

### Objective

Put the incomplete but usable product in front of real customers before declaring engineering complete.

The purpose is to discover:

- missing requirements
- unnecessary features
- onboarding friction
- confusing workflows
- integration problems
- trust barriers
- performance issues
- actual customer value
- willingness to continue paying

### Pilot success measures

Track:

- activation rate
- time to first value
- feature usage
- task completion
- customer-reported value
- support requests
- defects
- implementation effort
- founder intervention
- willingness to continue
- willingness to expand
- willingness to provide referral or reference

### Required output

```text
/product/PILOT-RESULTS.md
```

### Build rule

A pilot request does not automatically become a permanent product feature.

Classify feedback as:

- customer-specific configuration
- repeatable market requirement
- usability issue
- integration requirement
- defect
- optional feature
- strategic opportunity

---

## 9. Phase 07: Engineering Complete

### Objective

Establish that the validated core product is technically complete.

This is not the same as commercial completion.

### Exit checklist

- core functionality complete
- validated must-have features complete
- critical defects resolved
- automated tests passing
- security review complete
- production build succeeds
- database migrations tested
- environment configuration documented
- backups established
- rollback tested
- monitoring active
- logs available
- production deployment verified
- documentation current

At this point, the product status becomes:

> **ENGINEERING COMPLETE**

Do not label the project "DONE."

---

## 10. Phase 08: Productization

### Objective

Make the software usable by customers without undocumented developer intervention.

### Customer infrastructure

Confirm:

- production URL
- authentication
- password or identity recovery
- account creation
- tenant isolation where applicable
- roles and permissions
- account suspension
- account deletion
- usage limits
- customer configuration
- admin console

### Commercial infrastructure

Confirm:

- pricing plans
- product entitlements
- subscription or contract logic
- trial rules
- billing integration where applicable
- invoice or receipt handling
- upgrade
- downgrade
- cancellation
- failed payment handling

### Operational infrastructure

Confirm:

- uptime monitoring
- error monitoring
- usage analytics
- audit logs
- backup verification
- recovery process
- support intake
- incident escalation
- customer communication process

### Trust infrastructure

Confirm:

- privacy policy
- terms of service
- data handling statement
- security information
- customer contact information
- subprocessors where relevant
- AI-use disclosure where relevant
- retention policy
- deletion policy

---

## 11. AI Product Requirements

For AI-enabled products, explicitly document:

```text
/product/AI-GOVERNANCE.md
```

Include:

- approved model providers
- model routing rules
- data classification
- customer-data boundaries
- inference jurisdiction
- retention rules
- connector permissions
- audit logging
- human approval boundaries
- autonomous action limits
- credential handling
- persistent memory rules
- high-risk action restrictions
- fallback behaviour
- model failure behaviour

Route models by:

> **Capability + Cost + Provenance + Jurisdiction + Risk**

Low-cost or higher-risk models should only be used for bounded, sanitized, reversible workloads where appropriate.

They must not automatically receive:

- credentials
- sensitive customer information
- privileged connectors
- persistent memory
- autonomous authority

---

## 12. Phase 09: Commercial Ready

### Objective

Ensure that a prospective customer can understand, evaluate, trust, and purchase the product.

### Commercial Pack

Every product should have:

1. One-sentence problem
2. One-sentence outcome
3. Ideal customer profile
4. Three primary use cases
5. Three measurable benefits
6. Pricing
7. Demo
8. Proof or pilot evidence
9. Security and trust information
10. Clear call to action

### Commercial messaging test

A non-technical prospect should be able to answer:

- What is this?
- Is it for me?
- What problem does it solve?
- What does it change?
- Why should I trust it?
- What does it cost?
- What happens next?

If these questions cannot be answered quickly, the product is not commercially ready.

---

## 13. Phase 10: General Release

### Objective

Move from controlled early customer use to broader availability.

Before release, confirm:

- production stability
- support process
- onboarding process
- commercial terms
- pricing
- legal requirements
- monitoring
- analytics
- entitlement management
- customer communications
- incident response
- cancellation process
- data deletion process

---

## 14. Phase 11: Repeatable Sales

### Objective

Establish whether customer acquisition can be repeated.

Track the funnel:

```text
Traffic
   ↓
Lead
   ↓
Qualified Lead
   ↓
Demo
   ↓
Pilot / Trial
   ↓
Proposal
   ↓
Closed Won
   ↓
Activated
   ↓
Retained
   ↓
Expanded / Referred
```

### Initial metrics

Track:

| Metric | Purpose |
|---|---|
| Visitors → Leads | Positioning effectiveness |
| Leads → Demos | Offer relevance |
| Demos → Pilots | Product credibility |
| Pilots → Paid | Delivered value |
| Time to First Value | Onboarding quality |
| 30 / 90 Day Retention | Ongoing usefulness |
| Customer Acquisition Cost | Sales efficiency |
| Revenue per Customer | Unit economics |
| Support Time per Customer | Hidden scaling cost |
| Expansion Revenue | Depth of value |
| Referral Rate | Customer advocacy |

Do not optimize vanity metrics before validating customer value.

---

## 15. Phase 12: Scale

### Objective

Scale only after evidence of repeatable value and repeatable purchasing behaviour.

Scale decisions may include:

- additional engineering capacity
- sales hiring
- partner channels
- automation
- customer success roles
- infrastructure scaling
- new pricing tiers
- broader integrations
- geographic expansion
- new market segments

Do not scale unresolved product-market problems.

Automation multiplies both good and bad processes.

---

## 16. Onboarding Levels

Every product must intentionally select an onboarding model.

### Level 1: Self-Service

```text
Signup → Connect → Configure → First Result
```

Target time to first value should generally be very short.

### Level 2: Assisted

Customer receives a structured onboarding session.

Useful for higher-value B2B products.

### Level 3: Implementation

Customer receives a defined implementation project involving configuration, integration, governance, migration, training, or process redesign.

This may be the correct model for complex enterprise software.

The same software can support different onboarding models, but each must be priced and documented intentionally.

---

## 17. Definition of Done

A software project is not commercially complete when the application functions correctly.

It is commercially complete when a target customer can:

- discover the product
- understand its value
- establish trust
- purchase or contract for it
- gain authorized access
- complete onboarding
- achieve the intended outcome
- obtain support
- continue using the product
- renew, expand, or exit cleanly

without requiring undocumented founder intervention.

Use four separate completion states:

```text
ENGINEERING DoD
PRODUCT DoD
COMMERCIAL DoD
OPERATIONAL DoD
```

---

## 18. Repository Structure

Recommended minimum structure:

```text
/product
    PROBLEM.md
    ICP.md
    MARKET-VALIDATION.md
    OFFER.md
    PRICING.md
    PRODUCT.md
    REQUIREMENTS.md
    USE-CASES.md
    USER-JOURNEYS.md
    ONBOARDING.md
    PILOT-RESULTS.md
    AI-GOVERNANCE.md
    GTM.md
    SUPPORT.md

/engineering
    ARCHITECTURE.md
    STANDARDS.md
    TESTING.md
    SECURITY.md
    DEPLOYMENT.md
    RELEASE.md

/commercial
    SALES-DEMO.md
    FAQ.md
    TRUST.md
    PROCUREMENT.md
    COMMERCIAL-READINESS.md
    LAUNCH-PLAN.md
```

Not every file must exist on day one.

Create them when the lifecycle reaches the relevant phase.

---

## 19. Commercial Readiness Audit

Coding or review agents should periodically evaluate the project across these dimensions:

```text
PROBLEM VALIDATION
MARKET VALIDATION
PRE-SALE
PRODUCT
ENGINEERING
SECURITY
PRODUCTION
PRODUCTIZATION
COMMERCIAL
OPERATIONS
```

Example:

```text
Problem Validation     PASS
Market Validation      80%
Pre-Sale               60%
Product                75%
Engineering            72%
Security               65%
Production             40%
Productization         25%
Commercial             35%
Operations             20%

STATUS:
VALIDATED BUILD IN PROGRESS

NEXT CRITICAL ACTION:
Complete the workflow required by the first paid pilot.
```

Percentages should be supported by explicit checklist evidence.

Do not create arbitrary confidence scores.

---

## 20. Agent Decision Rules

When an agent is asked to continue development, it should first determine:

1. What lifecycle phase is the project currently in?
2. What customer evidence supports the requested work?
3. Is this work required for an existing pilot, customer, validated use case, security requirement, or operational requirement?
4. Is there a more direct way to test the assumption without fully building it?
5. Will the requested work move the project toward revenue, customer value, safety, reliability, or repeatability?

If not, flag the work as potentially speculative.

Do not block explicit owner instructions, but clearly identify speculative work.

---

## 21. Feature Decision Framework

Before implementing a significant new feature, classify it.

```text
Does a customer or validated use case require it?
        │
       YES
        ↓
Is it required for the core outcome?
        │
   YES ─┴─ NO
    ↓       ↓
   P0      P2

If not customer-driven:

Is it required for security, reliability,
compliance, or operation?
        │
       YES
        ↓
       P1

Otherwise:
        ↓
       P3
SPECULATIVE
```

P3 features should normally remain in backlog until evidence changes their priority.

---

## 22. Preferred Commercial Development Loop

The default operating loop should be:

```text
Customer Conversation
        ↓
Problem Evidence
        ↓
Offer
        ↓
Commitment
        ↓
Build Smallest Required Capability
        ↓
Deploy
        ↓
Observe Real Usage
        ↓
Collect Feedback
        ↓
Improve
        ↓
Renew / Expand / Sell Again
```

This loop should repeat continuously.

The goal is not to perfectly predict the final product.

The goal is to learn from real commercial behaviour while maintaining strong engineering discipline.

---

## 23. Primary Rule for Coding Agents

> **Do not optimize for finishing the software. Optimize for delivering a validated customer outcome through reliable software.**

The project should move toward commercial evidence as early as practical.

A strong technical product with no customer pathway is incomplete.

A pre-sold product with weak engineering is also incomplete.

The target is both:

> **Validated demand + strong engineering.**
