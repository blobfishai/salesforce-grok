# Practitioner workflow census — what sales people actually automate

> Answers QUESTIONS.md **C2** (and feeds **B2**, **D1**). Evidence: 185 skill
> definitions harvested from 7 cloned repos →
> `research/answers/_data/workflow-skills.tsv`. Compiled 2026-08-11.

Skill counts by repo: YALC GTM-OS 61 · hubspot-admin-skills 37 · markster-os 35 ·
LeanScale marketplace 18 · gtm-eng-skills 15 · gtm-pipeline-skills 10 ·
b2b-sdr-agent-template 9.

These are not eval tasks — they are things practitioners bothered to write down
and ship, which makes them a better prior for *what work exists* than any
benchmark.

---

## Family 1 — CRM hygiene & RevOps administration (the biggest evidence pile)

Source: `workflow/TomGranot__hubspot-admin-skills` (37 skills), corroborated by
`landbase.com` CRM-audit and `default.com` hygiene guides.

| Task | Observable done-state |
|---|---|
| `merge-duplicate-companies` — find dupes by domain+name, export audit CSV, guided merge | duplicate pair count ↓, survivor keeps associations |
| `fix-lifecycle-stages` / `lifecycle-progression-workflow` | every contact/company has a stage; Lead→MQL→SQL→Customer transitions automated |
| `cleanup-lead-owners`, `reassign-deactivated-owners`, `assign-unowned-contacts` | zero records owned by inactive users; zero unowned marketable contacts |
| `cleanup-properties` / `-lists` / `-workflows` / `-forms` / `-dashboards` / `-deals` | unused objects archived; test deals removed; deals with missing amount/close date fixed |
| `suppress-hard-bounced`, `suppress-global-unsubscribes`, `suppress-ghost-contacts`, `review-bounced-contacts`, `bounce-monitoring-workflow` | suppression lists correct; **legal compliance** and sender reputation preserved |
| `backfill-geo-data`, `standardize-geo-values`, `enrich-industry`, `enrich-company-name`, `waterfall-enrich-contacts` | required fields populated; country/state values normalized to one vocabulary |
| `build-lead-scoring` (separate Fit + Engagement scores), `create-icp-tiers`, `build-smart-lists`, `create-segment-lists` | scoring model live; accounts tiered by firmographics |
| `hubspot-audit` → `hubspot-implementation-plan`, `quarterly-database-cleanup`, `weekly-cleanup-routine` | audit report → **prioritized sequenced plan**; recurring cadence |
| `audit-api-usage`, `workflows-as-code` (export workflows to versioned JSON, diff), `sandbox-self-test` | integration inventory; config under version control |

**Why this matters for the world:** these are exactly the tasks that require
*bulk* operations with a *pinned* target subset and hard collateral guards — the
failure mode our wave-1/wave-5 scans already found grok-4.5 breaking on. The
evidence says this family is real work, not a synthetic difficulty knob.

## Family 2 — Outbound / GTM engineering pipeline

Source: `workflow/keinsaasforever__gtm-pipeline-skills` (explicit staged
pipeline), `workflow/getaero-io__gtm-eng-skills`,
`workflow/Othmane-Khadri__YALC-the-GTM-operating-system`,
`workflow/kaymen99__sales-outreach-automation-langgraph`.

Canonical stage order, stated identically across three independent repos:

```
ICP definition → company search → contact/people search → contact filter
  → people enrichment (email/phone/LinkedIn) → signal search (intent scoring)
  → personalization → sequence build → send → track → reply handling
```

Concrete named steps worth mirroring as tools/tasks: `build-tam`,
`find-qualified-titles`, `linkedin-url-lookup` (*"strict identity validation to
avoid false matches"*), `niche-signal-discovery` (*"signals that differentiate
Closed Won vs Closed Lost"*), `enrich-with-signals` (jobs, news, funding, tech,
leadership changes), `find-lookalikes`, `scrape-post-engagers`,
`qualify-leads` (**a 7-gate qualification pipeline**), `personalize-message`,
`launch-linkedin-campaign` (connect → DM1 → DM2), `send-cold-email`,
`track-campaigns` (poll provider, advance sequence steps), `reply-handler`,
`outbound-analyst` (benchmark campaign performance against 244K campaigns),
`lost-deal-revival-agent` (*"revival messages for closed-lost deals when a public
signal contradicts the original loss reason"*).

Copywriting is **segmented by buyer seniority** — YALC ships separate
`copywriting-ic-sequence`, `-manager-sequence`, `-vp-sequence`. That is a
personalization axis no eval models.

## Family 3 — Deal execution & post-meeting operations

Source: `workflow/markster-public__markster-os` (35 skills),
`workflow/iPythoning__b2b-sdr-agent-template`.

- `debrief` — *"takes meeting notes and creates CRM records"* → the
  artifact→state task shape (unstructured in, structured writes out).
- `follow-up` — *"stage-aware follow-up generator … based on deal stage"*.
- `prospect-brief`, `event-prep` (pre-event ICP-matching brief), `case-study-builder`.
- `quotation-generator` — proforma invoice PDF with letterhead, multi-language.
- `funnel-review` — *grades* a funnel against benchmarks and emits a scored fix list.

## Family 4 — Inbox ↔ CRM synchronization

Source: `workflow/jacob-dietle__Autonomous-Sales-Inbox-and-CRM-Assistant`.
Triage inbound mail, auto-draft replies, sync to CRM. This is the surface where
the *same fact* (a customer's stated timeline, a price they were quoted) exists
in an email body and in a CRM field, and the two disagree — direct feed to E1/E2.

## Family 5 — Spreadsheet-as-CRM

Source: `workflow/BraaMohammed__bricks` (local open Clay alternative: a sheet
with enrichment/agent columns). Corroborates the shadow-spreadsheet finding in
`pedowitzgroup.com` (*"shadow spreadsheets are proof that users no longer trust
the CRM source of truth"*). The sheet is not a fallback surface — it is a
first-class system of record in real orgs, and must be one in the world.

---

## Cross-cutting observations that should shape the world

1. **Enrichment is a waterfall with a budget.** Repeated in `waterfall-enrich-contacts`,
   `gtm-pipeline:people-enrichment`, and YALC's provider/adapter model: try
   provider A, fall back to B, stop when found, track credits. Any faithful
   enrichment tool needs *cost and partial success*, not a lookup that always works.
2. **Providers disagree, and the agent must pick.** YALC ships `list-adapters` and
   `provider-builder` precisely because one capability has many backing vendors.
   The world should expose ≥2 providers for the same fact and let them conflict.
3. **Identity resolution is an explicit, named risk.** `linkedin-url-lookup`
   exists only to avoid false matches; `merge-duplicate-companies` exports an
   audit CSV *for human review before merging*. Both say: the correct behavior on
   an ambiguous match is to stop and surface, not to guess — a restraint task.
4. **Everything recurs on a cadence.** weekly cleanup, quarterly audit, campaign
   polling. The world needs a clock, and tasks whose correct answer depends on
   "as of when" (feeds A4/E-time semantics).
5. **The audit → plan → execute arc.** `hubspot-audit` → `hubspot-implementation-plan`
   → individual fix skills. A genuinely long-horizon task family where the
   intermediate artifact is a *plan*, gradeable at checkpoints.
