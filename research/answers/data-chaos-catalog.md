# Data chaos catalog — why the same question has several defensible answers

> Answers QUESTIONS.md **E1–E5**. Sources: dated web articles listed in
> `research/SOURCES.md` §5 plus cloned-repo evidence. Compiled 2026-08-11.
> This is the design brief for the multi-system layer of the world.

## 0. The governing fact

A real revenue org does not have one system of record. It has a CRM, a billing
system, an ERP/GL, an engagement tool, an enrichment cache, and — crucially —
**spreadsheets that people trust more than the CRM**. Shadow spreadsheets are
described in the field as *"proof that users no longer trust the CRM source of
truth"* (pedowitzgroup.com, 2026). The chaos is not noise added for difficulty;
it is the normal operating condition, and it is the thing agents are actually
hired to navigate.

## 1. Where the same fact lives twice (E1)

| Fact | Copy A | Copy B | Copy C | Authoritative for… |
|---|---|---|---|---|
| Deal value | CRM `Opportunity.Amount` | Order form PDF / quote | Billing subscription MRR×term | A: pipeline & forecast · B: what was signed · C: what will be invoiced |
| Revenue "this month" | CRM closed-won sum | Invoices issued | GL recognized revenue | each answers a *different* question (bookings vs billings vs revenue) |
| Account owner | CRM `Owner` | Territory sheet | Comp plan roster | CRM for routing; comp roster for payout |
| Contact email/title | CRM field | Enrichment provider cache | Last email signature | freshest wins, but freshness is unknown without a timestamp |
| Renewal date | CRM renewal opp | Subscription `current_period_end` | MSA clause | contract (C) is legally authoritative; A/B drift from it |
| Stage / lifecycle | CRM stage | Sequence tool status | CSM health board | none — this is the classic three-way disagreement |

**Design rule:** for each seeded fact, record *which copy is authoritative for
which question*, and make at least one task whose difficulty is choosing the
right copy rather than reading it.

## 2. Drift mechanisms, with sources (E2)

1. **Bookings ≠ billings ≠ recognized revenue.** *"HubSpot logs the full deal
   value at close while accounting systems spread that value over time"*; the CRM
   deal amount *"rarely matches recognized revenue"* (durity.com, 2026).
2. **Cloned renewal deals double-count.** *"Renewal opportunities typically get
   cloned or created manually, and without automated linking [the CRM] counts
   them as new deals instead of extensions of existing revenue"* (scalexp.com).
3. **Multi-rep expansion overlap.** Overlapping deals inflate CRM totals while
   finance records one contract value (durity.com).
4. **Close-before-invoice timing.** A deal marked closed before the invoice
   issues shows revenue the billing system has not recognized yet.
5. **Duplicates at scale.** *"Most CRMs have 15–25% duplicate rates before
   cleanup, and 76% of CRM entries are less than half complete"* (default.com).
6. **Enrichment lag.** *"A 14-day enrichment lag … means territory assignments and
   routing decisions are made on data that is two weeks stale"* (pedowitzgroup.com).
7. **Partial migration.** *"54% of organizations experience significant CRM
   migration delays, 67% discover major data quality issues mid-migration, 43%
   report problems extending beyond six months post-launch"* (syncmatters.com) —
   i.e. two CRMs live simultaneously with a partial, lossy mapping.
8. **Picklist / option-slug drift.** The documented values are not the values in
   the workspace: the Attio benchmark's compound-filter query failed twice because
   documented employee-count options (`501-1000`) did not exist; the real slugs
   were `5K-10K`, `10K-50K`, `50K-100K`, `100K+`
   (`eval/ArcadeAI__attio-mcp-benchmark/README.md`).
9. **Suppression/consent state split across systems.** Bounce and unsubscribe
   state lives in the marketing tool while the CRM keeps mailing
   (`workflow/TomGranot__hubspot-admin-skills`: 5 distinct suppression skills).
10. **Ownership decay.** Deactivated users still own records
    (`reassign-deactivated-owners`, `cleanup-lead-owners`).
11. **Currency & FX.** Multi-currency pipeline summed at deal-date vs
    period-close rate gives two different totals.
12. **Fiscal calendar & timezone.** "This week" is Mon–Sun locally, Sun–Sat in
    the CRM report, and 4-4-5 in finance; a deal closed 2026-08-11 23:40 PT is
    next week in UTC.

## 3. The canonical question: "what's the total sales number this week?" (E3)

There are **at least six defensible answers**, and the difference between a good
agent and a bad one is not arithmetic — it is disclosure.

| # | Reading | Where it comes from | Typical divergence |
|---|---|---|---|
| 1 | New **bookings** (opps moved to Closed Won this week) | CRM | the number sales leadership means |
| 2 | **Net new ARR** (bookings minus churn/downgrade) | CRM + billing | lower; the number the board means |
| 3 | **Billings** (invoices issued this week) | billing/ERP | lags bookings by the invoice cycle |
| 4 | **Recognized revenue** for the week | GL | far lower for annual contracts |
| 5 | **Cash collected** | payments | lags billings by DSO |
| 6 | Whatever the **ops spreadsheet** says | sheet | usually #1 with manual adjustments nobody re-applied |

A correct agent response: pick a defensible default (bookings, because the asker
is a sales manager), **state the definition and the window boundary used**, name
the systems queried, and flag the largest known discrepancy (e.g. "two renewal
opps look like clones of the same contract — $180K may be double-counted").

**Grading policy this implies:** the answer alone cannot be the assertion. Full
credit requires (a) a number within tolerance of the graded definition, (b) an
explicit statement of the definition + window, and (c) disclosure of any
detectable conflict. This is the checkpoint-style scoring SCUBA uses, applied to
an analytics answer.

## 4. Detectable vs invisible chaos (E4)

Only chaos an agent could *notice from inside the world* may be graded as a miss:

**Detectable** — two records with the same domain/name (dupes); a deal amount
that disagrees with its linked subscription; a renewal opp with no link to a
prior contract; a record owned by an inactive user; an enrichment field whose
`updated_at` is older than policy; a picklist value present in data but absent
from the documented list; a currency mismatch; a stage that violates the
documented gate.

**Invisible** — which of two equally-plausible copies the *asker* meant;
unrecorded verbal agreements; whether a manual spreadsheet adjustment was
intentional. These may exist in the world as flavor, but must never be the
difference between pass and fail unless the task prompt or a readable document
supplies the disambiguator.

## 5. The healthy-record baseline (E5)

Needed so "dirty" is measurable rather than vibes. Grounded in the hygiene
skills' own acceptance criteria (`workflow/TomGranot__hubspot-admin-skills`):

- every marketable contact has an **owner** and a **lifecycle stage**;
- every company has a normalized **country/state** value from a fixed vocabulary;
- every open deal has an **amount** and a **close date**;
- no record is owned by a deactivated user;
- hard-bounced / globally-unsubscribed contacts are suppressed;
- duplicate rate below the audit threshold (field baseline: pre-cleanup CRMs run
  15–25%);
- required-field completeness above threshold (field baseline: 76% of entries are
  <50% complete).

Seed the world **deliberately off-baseline** at a measured rate, and record the
ground-truth dirty-record set so hygiene tasks have an exact target subset and an
exact collateral set.
