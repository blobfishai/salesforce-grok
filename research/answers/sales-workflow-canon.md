# Sales workflow canon — the named methodologies practitioners actually run, as gradeable agent scenarios

> Answers QUESTIONS.md #3/#4 (what each stakeholder does, what "done" means), #9 (input
> documents), #11 (what state change proves completion) and #12 (answer vs state vs
> communication tasks). Researched 2026-08-10 via live web search against vendor
> documentation (Salesforce, HubSpot, Gong, Clari, DocuSign, Ironclad, LeanData,
> CaptivateIQ, Gainsight), methodology owners (Force Management, Winning by Design,
> MEDDICC.com, Huthwaite) and practitioner sources. Every claim carries a URL.
>
> Companion to `sales-agent-workflows.md`, which maps our mock world onto real stacks.
> **This file goes the other direction**: it captures the *external canon* — what the
> industry considers a named, teachable workflow — and converts each into a scenario
> with a deterministic verifier.

**Scenario format.** Every entry is phrased as
**TRIGGER → REQUIRED READS → REQUIRED WRITES → PROOF OF COMPLETION**, matching the
shape of `bench/tasks/*.json` (`required_tools` ≈ reads, `tables_affected` +
`expected_state_changes` ≈ writes, verifier assertions ≈ proof). Where a workflow maps
onto an existing table or tool in `world/blobfish-wave6/world.json`, it is named in
the **maps to** line so task authors can go straight to a seed.

**Three properties separate a gradeable scenario from a plausible-looking one**, and
they recur throughout:

1. **Conservation identities** — waterfall balance, splits summing to 100%, child-record
   counts preserved across a merge, `Won + Lost + Open == cohort size`. These are
   algebraic invariants that fail loudly under partial work, and they are worth more
   than any single field assertion.
2. **Read-the-config, don't-know-the-answer** — picklist values, country mappings,
   stage ladders, survivorship priority tables. An agent answering from world knowledge
   produces plausible-but-wrong values. Assert *set membership against live metadata*,
   not string equality to an expected literal.
3. **Negative assertions / graded restraint** — what must NOT have changed. The most
   common agent failure mode in a CRM is collateral mutation, and several of the best
   scenarios below are ones where the correct answer is to *not* write.

**21 gradeable scenarios distilled below.** Each is phrased so a deterministic verifier can score it; several are *restraint-graded*, where the correct behaviour is to refuse or to write nothing.

| # | scenario | grading shape |
|---|---|---|
| 1.1 | MEDDPICC gap remediation (Paper Process red) | state-diff |
| 1.2 | Champion vs Coach discrimination | restraint (correct answer may be *no write*) |
| 1.3 | BANT lead conversion gate | state-diff |
| 1.4 | SPICED completeness after discovery | state-diff |
| 1.5 | Value Framework completion before proposal | state-diff |
| 1.6 | SPIN call scoring and coaching trigger | state-diff |
| 2.1 | Build the mutual close plan | state-diff |
| 2.2 | Gate the stage advance | restraint (correct answer may be *no write*) |
| 2.3 | Run and record the deal review | state-diff |
| 2.4 | Weekly pipeline hygiene sweep | state-diff |
| 2.5 | Submit the weekly forecast | state-diff |
| 2.6 | Sandbagging / happy-ears audit | restraint (correct answer may be *no write*) |
| 2.7 | Multi-threading risk sweep | state-diff |
| 2.8 | Win/loss capture on close | state-diff |
| 3.1 | Inbound MQL SLA breach recovery | state-diff |
| 3.2 | MQL rejected with reason code and recycled | state-diff |
| 3.3 | Fuzzy-matched merge with source-priority survivorship | state-diff |
| 3.4 | Territory carve with ramped quota allocation | restraint (correct answer may be *no write*) |
| 3.5 | Split-credit commission statement with clawback and dispute | state-diff |
| 3.6 | Monthly contact hygiene and normalization pass | state-diff |
| 3.7 | Quarterly funnel conversion and pipeline waterfall | answer + conservation identity |

---

# 1 · Qualification &amp; discovery frameworks

The most CRM-instrumented layer of the canon. The recurring schema convention across
every vendor is a **status field + an evidence/notes field per element** — Gong's AI
Deal Reviewer pushes exactly "two fields per element to the CRM opportunity record —
one for the status, one for the note"
([help.gong.io](https://help.gong.io/docs/understanding-ai-deal-reviewer)).

## 1.1 MEDDIC / MEDDICC / MEDDPICC

**Origin.** Created inside PTC in 1996 by **Dick Dunkel** under SVP John McMahon, with
Jack Napoli operationalizing it
([meddicc.com](https://meddicc.com/resources/who-created-meddic)); canonized in Andy
Whyte's 2020 book *MEDDICC* ([meddicc.com](https://meddicc.com/meddicc-the-book)).

**Definition.** A checklist-based qualification and deal-inspection framework that
validates whether a complex enterprise opportunity is winnable.

| Letter | Canonical wording ([meddicc.com](https://meddicc.com/meddpicc-sales-methodology-and-process)) |
|---|---|
| **M** Metrics | the quantifiable measures of value your solution provides |
| **E** Economic Buyer | the person with overall authority in the buying decision |
| **D** Decision Criteria | the principles, guidelines and requirements |
| **D** Decision Process | the series of steps the buyer will follow |
| **P** Paper Process | the steps from Decision to signature |
| **I** Implicate the Pain | Identified, Indicated, *and* Implicated |
| **C** Champion | a person with power, influence, and credibility |
| **C** Competition | any person, vendor, or initiative competing for the same funds |

MEDDIC = 6 letters; MEDDICC adds Competition; MEDDPICC adds Paper Process.
**Grading trap:** MEDDICC.com says *"Implicate the Pain"* (a three-stage escalation);
HubSpot says *"Identify Pain"*
([blog.hubspot.com](https://blog.hubspot.com/sales/meddpicc-methodology)). Both
circulate; strict-canonical is *Implicate*.

**Artifacts.** Eight picklist fields on Opportunity — best practice is a *single Global
Value Set* (Red/Yellow/Green) applied across all eight rather than eight separate
picklists — plus eight paired long-text notes fields, eight `IMAGE()` formula fields
rendering traffic lights, and one summary formula concatenating all eight for list
views ([salesmethods.com](https://salesmethods.com/blog/how-to-use-meddic-in-salesforce/),
[weflow.ai](https://www.weflow.ai/blog/meddpicc)). The human elements live on
**OpportunityContactRole**, whose standard `Role` values include Decision Maker,
Economic Buyer, Evaluator, Executive Sponsor, Influencer, Technical Buyer; MEDDIC shops
add Champion and Coach. Only one `IsPrimary` per Opportunity
([salesforceben.com](https://www.salesforceben.com/introduction-to-salesforce-opportunity-contact-roles/)).
HubSpot's equivalent is a "MEDDPICC" property group with a **dual-property model per
letter — one qualitative text capture, one 0–4 numeric score**
([coffee.ai](https://www.coffee.ai/articles/implement-meddpicc-sales-methodology-crm)).

**Scoring.** Red/Yellow/Green per pillar is most common, with the operative forecast
gate: **"every deal in the commit forecast must have zero reds and no more than two
yellows"** ([weflow.ai](https://www.weflow.ai/blog/meddpicc)). One published weighted
alternative: Champion 20%, Economic Buyer 20%, Metrics 15%, Identified Pain 15%,
Decision Criteria 12%, Decision Process 12%, Competition 6%, with a stage gate blocking
Negotiation below 65
([revengine.substack.com](https://revengine.substack.com/p/how-to-build-meddicc-scoring-in-salesforce)).
MEDDIC Academy's convention: total score approaches 100% near close date, and **60%
three weeks from quarter-end is a signal not to commit**
([meddic.academy](https://meddic.academy/meddic-score-calculator-by-meddic-academy/)).

**Maps to:** `meddic_scorecard`, `meddic_extraction_scorecard`, `transcript_evidence`,
`opportunity_stage_gates`.

### Scenario 1.1 — MEDDPICC gap remediation (Paper Process red)

- **TRIGGER:** Opportunity `Amount > $250,000` AND stage = Solution Validation AND
  `Paper_Process__c = "Red"`.
- **REQUIRED READS:** the Opportunity and all 8 status + 8 notes fields; every
  `OpportunityContactRole`; the 3 most recent activities; the Account's contacts filtered
  to Legal/Procurement/Security titles.
- **REQUIRED WRITES:** set `Paper_Process__c = "Yellow"` **only if** a Legal or
  Procurement contact exists on the Account, otherwise leave Red; write
  `Paper_Process_Notes__c` with a numbered list of outstanding paper steps and the named
  owner of each, or the literal `"NO PAPER PROCESS OWNER IDENTIFIED"`; create one
  `OpportunityContactRole` with `Role = "Economic Buyer"` **iff** none exists and a
  C-level/VP contact is present; create a Task `"MEDDPICC gap: Paper Process"` due
  today+7; recompute `MEDDPICC_Score__c`.
- **PROOF:** notes field non-empty; exactly one open Task with that subject; count of
  Economic Buyer contact roles is exactly 1 (never 2 — idempotency); `MEDDPICC_Score__c`
  equals the weighted formula recomputed from the 8 picklists; **no Opportunity field
  outside the declared write-set changed**.

**Why it grades well:** the restraint branch. An agent that marks Paper Process green
with no named procurement owner has failed in exactly the way the source literature
warns about.

### Scenario 1.2 — Champion vs Coach discrimination *(restraint-graded)*

The three-way distinction agents routinely collapse:

- **Champion** — has *power, influence, and credibility*, and actively sells on your
  behalf when you're not in the room. Tested by asking them to *do* something.
- **Coach** — gives information and guidance but **lacks the power or willingness to
  advocate internally**. A coach tells you where the bodies are buried; a champion moves
  them.
- **Mobilizer** (CEB, *The Challenger Customer*) — drives internal consensus. CEB's seven
  profiles: Go-Getter, Teacher, Skeptic, Guide, Friend, Climber, Blocker. Go-Getters,
  Teachers and Skeptics are Mobilizers; the rest are **"Talkers."** CEB's explicit and
  counterintuitive advice is to **identify Mobilizers, not "Customer Champions"** —
  because champion-hunting selects for people who *like you* rather than people who can
  *drive change* ([insidesales.com](https://www.insidesales.com/b2b-sales-mobilizers/),
  [b2bsell.com](https://www.b2bsell.com/challenger-customer/)).

- **TRIGGER:** Opportunity in a mid stage with no contact role of type Champion, and one
  contact holding 60%+ of all logged email activity.
- **REQUIRED READS:** all activities grouped by contact; contact titles; existing contact
  roles; any calendar invites with multiple internal attendees.
- **REQUIRED WRITES:** assign `Role = "Champion"` **only** where there is evidence of the
  contact acting on the seller's behalf with third parties — forwarding materials
  internally, scheduling meetings with the Economic Buyer, appearing as organizer on a
  multi-stakeholder invite. Otherwise assign `Role = "Coach"` and create a Task
  `"Champion test: request an introduction to the Economic Buyer"`.
- **PROOF:** the most-emailed contact is labelled Champion **iff** a third-party-facing
  action exists in the activity record; where only bilateral email exists, the role is
  Coach and the champion-test Task exists. **An agent that writes Champion for the
  most-responsive contact fails.**

## 1.2 BANT

**Origin.** IBM, 1950s–60s (sources disagree on the exact year — cite the decade range),
built when a sale meant placing a mainframe with one IT director holding a fixed budget
([mailchimp.com](https://mailchimp.com/resources/what-is-bant/),
[zoominfo](https://pipeline.zoominfo.com/sales/bant-sales-qualification-process)).

**Definition.** A four-gate lead-qualification checklist: **B**udget, **A**uthority,
**N**eed, **T**imeline.

**Structural criticism worth encoding:** BANT is seller-centric and budget-first,
designed for a single-decision-maker world. CHAMP, GPCTBA and NOTE all exist as
re-orderings of exactly this complaint.

**Artifacts.** BANT lives at the **Lead/MQL layer**, not the Opportunity layer — this is
the key artifact distinction versus MEDDIC. Four Lead fields, Lead Status / Lead Score,
the MQL→SQL conversion gate, a disqualification-reason picklist, and the Lead Conversion
record itself (Account + Contact + Opportunity) as the success artifact.

**Scoring.** Most commonly a **boolean AND across all four** — any single "no"
disqualifies. That all-or-nothing property is what makes BANT easy to automate and easy
to criticize.

**Maps to:** `sales_leads`, `lead_scoring_policy`, `mql_definition`, `sal_gate`.

### Scenario 1.3 — BANT lead conversion gate

- **TRIGGER:** `Lead.Status = "Marketing Qualified"`, created within 14 days.
- **REQUIRED READS:** the Lead; all activity on it; the Lead's Company matched against
  existing Accounts to detect duplicates.
- **REQUIRED WRITES:** populate Budget/Authority/Need/Timeline each as one of
  {`Confirmed`, `Assumed`, `Unknown`}; write `BANT_Score__c` = count of `Confirmed`. If
  4 → set Sales Qualified and convert. If < 4 → set Nurture and write
  `Disqualification_Reason__c` naming the specific missing letter(s).
- **PROOF:** `BANT_Score__c` equals the count of fields set to `Confirmed` (arithmetic
  check); **conversion occurred iff the score is 4**; on non-conversion the reason names
  at least one non-Confirmed letter; **no Opportunity was created for a sub-4 lead**.

## 1.3 SPICED — Winning by Design

**Definition.** A five-part diagnostic used as a shared operating language across sales,
marketing, CS and RevOps for the *entire customer lifecycle*, built for recurring-revenue
businesses ([winningbydesign.com](https://winningbydesign.com/spiced-framework/)).

**S**ituation · **P**ain · **I**mpact · **C·E** Critical Event · **D**ecision.
**Grading trap: Critical Event is two letters (CE), not one.**

**Artifacts.** Winning by Design publishes no specific field names — a genuine gap versus
MEDDIC. In practice: five Opportunity fields, with **Critical Event as a Date** (its
whole purpose is a deadline) and **Impact as currency/number**. Because SPICED spans the
lifecycle, the same five fields appear on onboarding, QBR and renewal records — the
differentiating artifact versus MEDDIC
([highspot.com](https://www.highspot.com/blog/spiced-sales-methodology/)).

**Scoring.** No canonical numeric rubric. The operative gate is **Critical Event = a
defensible future date**, since a deal without one has no forcing function.

### Scenario 1.4 — SPICED completeness after discovery

- **TRIGGER:** a Discovery Call event is marked Completed on an Opportunity in Discovery.
- **REQUIRED READS:** the completed event and its transcript; the five SPICED fields; the
  Account's industry and employee count.
- **REQUIRED WRITES:** populate all five; `Impact__c` numeric in currency plus a text
  basis; `Critical_Event__c` as a **Date**; set `SPICED_Complete__c` TRUE only if all five
  non-null AND Critical Event is a future date; if Critical Event is null, write
  `Next_Step__c = "Establish critical event"`.
- **PROOF:** `Critical_Event__c` is either a valid future date or null-with-Next-Step-set
  — **never a past date, never free text**; `Impact__c` numeric and non-zero when Pain is
  non-empty; `SPICED_Complete__c` TRUE iff all five conditions hold; **`CloseDate` is not
  later than `Critical_Event__c`** (cross-field consistency).

## 1.4 CHAMP, GPCTBA/C&amp;I, Command of the Message, SPIN

**CHAMP** (InsightSquared) — **CH**allenges, **A**uthority, **M**oney,
**P**rioritization. BANT re-sequenced to lead with the buyer's problem. The whole
innovation is the ordering; *Prioritization* also differs meaningfully from *Timeline* —
Timeline asks **when**, Prioritization asks **versus what else**, which is the better
predictor of slippage ([revenue.io](https://www.revenue.io/inside-sales-glossary/what-is-champ),
[salesmate.io](https://www.salesmate.io/blog/champ-methodology/)). Distinguishing gate: a
deal can pass with weak Money if Challenges and Prioritization are strong — the inverse
of BANT.

**GPCTBA/C&amp;I** (HubSpot) — Goals, Plans, Challenges, Timeline, Budget, Authority,
Negative **C**onsequences &amp; Positive **I**mplications
([gtm.club](https://www.gtm.club/gpctba-c-i-framework/),
[clay.com](https://www.clay.com/glossary/gpctba-c-i)). **Grading trap: the slash matters
and the polarity is the most common error** — Consequences = negative (what happens if
they don't act), Implications = positive (what happens if they do). Goals must be
quantifiable, so `goal_metric_value` is numeric.

**Command of the Message / Value Framework** (Force Management) — a company-wide
value-articulation framework so the message a buyer hears doesn't depend on which rep
they got. Elements: **Before Scenario, Negative Consequences, After Scenario, Positive
Business Outcomes, Required Capabilities, Metrics**, plus Proof Points and
Differentiation. Force Management's own page confirms these are used "in sales meetings,
deal reviews, or **CRM fields**"
([forcemanagement.com](https://www.forcemanagement.com/blog/what-is-a-value-framework),
[forcemanagement.com](https://www.forcemanagement.com/blog/whats-the-meaning-of-command-of-the-message)).
The load-bearing definition: **Required Capabilities are "not product features" but the
functional requirements that map to the buyer's problems** — framed *before any product
is mentioned*. In practice CoM and MEDDPICC deploy together: CoM supplies the
Metrics/Pain content, MEDDPICC the qualification scaffolding
([AppExchange](https://appexchange.salesforce.com/appxListingDetail?listingId=a0N3A00000Ecr5RUAR)).

**SPIN Selling** (Neil Rackham / Huthwaite, 1988; 12 years of research, 35,000+ calls
across 23 countries) — **S**ituation, **P**roblem, **I**mplication, **N**eed-payoff
([huthwaiteinternational.com](https://www.huthwaiteinternational.com/spin-methodology)).
The central research finding: top performers do not pitch or close better — they ask
**Implication questions far more often**, and Implication density is the strongest single
predictor of close rate in large deals
([huthwaiteinternational.com](https://www.huthwaiteinternational.com/blog/neil-rackham-research-spin)).
SPIN is a **rep-behavior** scoring framework, not a deal-scoring one; the modern artifact
is a conversation-intelligence scorecard measuring question-type distribution.

Note that CoM's Consequences/Outcomes pair, GPCTBA's C&amp;I pair, and SPIN's
Implication/Need-payoff pair are **three vocabularies for the same two moves**.

**Maps to:** `snippets`, `tracker_keywords`, `conversation_intelligence_standards`,
`talk_ratio`, `transcript_evidence`.

### Scenario 1.5 — Value Framework completion before proposal

- **TRIGGER:** Opportunity stage → Proposal AND `Amount > $100,000`.
- **REQUIRED READS:** the six Value Framework fields; the Proof Point library filtered by
  the Account's industry.
- **REQUIRED WRITES:** ensure all six non-empty; set `Value_Framework_Complete__c`; create
  up to 3 proof-point junctions with matching industry; write
  `Quantified_Business_Impact__c` as currency derived from Metrics.
- **PROOF:** `Quantified_Business_Impact__c` is non-null currency **greater than
  `Opportunity.Amount`** — a value case must exceed its price, a strong deterministic
  check; between 1 and 3 junctions, all industry-matched; **`Required_Capabilities__c`
  contains no string from the product-name list** (enforces "capabilities, not features").

### Scenario 1.6 — SPIN call scoring and coaching trigger

- **TRIGGER:** a call transcript is associated with an early-stage Opportunity.
- **REQUIRED READS:** the full transcript; the Opportunity; the rep's last 5 scored calls.
- **REQUIRED WRITES:** one Call Score record with Situation/Problem/Implication/Need-payoff
  counts as integers plus `SPIN_Ratio__c` = Implication ÷ Situation; if Implication count
  is 0, create a coaching Task for the rep's manager.
- **PROOF:** the four counts are non-negative integers summing to ≤ total questions in the
  transcript; the ratio equals Implication ÷ Situation to 2dp with **division-by-zero
  handled as null, not error**; the coaching Task exists iff Implication count is 0;
  **exactly one Call Score per call (idempotency on re-run)**.

## 1.5 The minor frameworks, and how vendors auto-extract

**ANUM** (Ken Krogue, InsideSales) — Authority, Need, Urgency, Money. BANT with
**Authority first**. Artifact: a seniority field checked *before* any discovery field is
populated.

**FAINT** (Mike Schultz, RAIN Group) — Funds, Authority, Interest, Need, Timing. The
insight: for genuinely new categories the buyer has **no allocated budget**, so replace
Budget with **Funds** (overall purchasing power) and add **Interest** (which the seller
*creates*, not detects). Artifact: a `Funds__c` capacity estimate **on the Account**
rather than a Budget field on the Opportunity — a meaningful schema difference.

**NOTE** (Sean Burke, KiteDesk, 2016) — Need, Opportunity, Team, Effect. Explicitly
treats the buying committee as a *team*, so the artifact is a stakeholder/impact map
rather than a single Authority field.

**How the vendors auto-extract (2025–26).** Gong's **AI Data Extractor** (rolled out
Oct 2025 → early 2026) is configured as Question + Additional Instructions + target
object/data type, outputs Yes/No, free text, single-select, number, date, or **range**
(the type that makes numeric MEDDIC scoring possible), reads calls from the last six
months, and — importantly — **cannot create new CRM fields**; mapping to a pre-existing
field is mandatory for deal-target extractors. Max 20 published extractors per workspace
([help.gong.io](https://help.gong.io/docs/ai-data-extractor)). Gong's **AI Deal Reviewer**
maps playbook elements to smart trackers and syncs **two fields per element** (status +
note) bidirectionally
([help.gong.io](https://help.gong.io/docs/understanding-ai-deal-reviewer)). Clari's
4-point deal inspection tracks methodology adherence explicitly across MEDDIC, BANT,
SPIN, Challenger and Sandler
([clari.com](https://www.clari.com/blog/how-to-increase-sales-effectiveness-with-the-4-point-deal-inspection/)).
People.ai captures activity and **contacts not yet in Salesforce**, writing people to
Contact Roles, and flags gaps like **missing economic buyers**
([people.ai](https://www.people.ai/blog/automated-sales-activity-capture-for-ai)).
HubSpot Breeze's Smart Deal Progression operates on a **suggestion model requiring the
rep to approve each suggestion individually** — a meaningful architectural contrast with
Gong's direct write-back
([askelephant.ai](https://www.askelephant.ai/blog/how-does-hubspot-use-ai-breeze)).

**The universal pattern:** ingest → match activity to Account/Opportunity/Contact →
extract per-element answers → write a status field + an evidence field to a
**pre-existing** field → score → surface gaps. **None of them create fields.** For a
benchmark, that means field pre-existence is a fair precondition, and "wrote evidence
alongside status" is the realistic bar.

**Deal health scoring.** HubSpot ships the most concretely documented version: a **"Deal
Score" property on a 0–100 scale**, where "a score of 85 predicts an 85% likelihood of
winning." Inputs: amount and amount *changes*, close-date proximity, **time in current
stage**, **next-step update timing**, owner changes, rep activity (overdue tasks,
scheduled meetings), buyer engagement (opens/clicks/replies), and stalling detection. New
deals scored within ~36 hours; existing deals update within 6 hours on a ±3% change
([knowledge.hubspot.com](https://knowledge.hubspot.com/records/use-deal-scores)).

---

# 2 · Deal management &amp; forecasting

## 2.0 The field reference this whole section depends on

Verified from the [Salesforce Opportunity object reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunity.htm):

| API name | Notes |
|---|---|
| `StageName` | required; drives `IsClosed`, `IsWon`, `Probability`, `ForecastCategoryName` |
| `ForecastCategory` | **read-only**; values `BestCase, Closed, Forecast, MostLikely, Omitted, Pipeline` |
| `ForecastCategoryName` | **updatable**; values `Best Case, Closed, Commit, Most Likely, Omitted, Pipeline` |
| `LastStageChangeDate` | datetime, API v52.0+ |
| `PushCount` | int, API v53.0+ — count of close-date pushes **by one calendar month** |
| `ExpectedRevenue` | read-only, `Amount × Probability` |
| `LastActivityDate` | most recent Event or closed Task |

> **The single most important gotcha in this entire document.** `ForecastCategory` and
> `ForecastCategoryName` are **different picklists with different values**.
> `ForecastCategory = 'Forecast'` ↔ `ForecastCategoryName = 'Commit'`. A verifier that
> reads the wrong one will mark correct agent behavior as failure, and vice versa. Any
> forecasting task in this repo must filter on `ForecastCategoryName`.

Salesforce's default stage→probability→category mapping
([Salesforce Help](https://help.salesforce.com/s/articleView?id=sales.faq_forecasts_category_mapping.htm&language=en_US&type=5)):
Prospecting/Qualification 10% Pipeline · Needs Analysis 20% Pipeline · Value Proposition
50% Pipeline · Id. Decision Makers 60% Pipeline · Perception Analysis 70% Best Case ·
Proposal/Price Quote 75% Best Case · Negotiation/Review 90% Commit · Closed Won 100%
Closed · Closed Lost 0% Omitted. **Users can override `ForecastCategoryName` on
opportunities they own** — that override is exactly what sandbagging detection keys on.

## 2.1 Mutual Action Plan (MAP)

**Aliases.** Mutual Close Plan, Joint Execution Plan, Close Plan, Mutual Success Plan.

**Definition.** A shared, dated, owner-assigned task plan co-authored by seller and buyer
that **back-plans every step from go-live and signature back to today**.

**Structure** ([Dock](https://www.dock.us/library/mutual-action-plans)): Overview,
Success criteria, Stakeholders (both sides), Timeline → phases → tasks → owner → due date
→ status, Supporting resources. Buying groups are 6–10 people and 77% call the process
too complex, so **cap the plan at 8–12 milestones**; the rep does the bulk of maintenance
even though the plan is co-owned.

**Standard milestone spine.** Evaluation → stakeholder alignment → technical
validation/POC → security review → business case → commercials → legal redline →
procurement/vendor intake → PO → signature → kickoff → go-live
([GetAccept](https://www.getaccept.com/blog/mutual-action-plans),
[ORM](https://orm-tech.com/blog/mutual-action-plan-template)).

**Ownership convention.** Every row gets exactly one owner, **side-prefixed**:
`Buyer — Sarah Chen (IT Security)` / `Seller — Ana Ruiz (AE)`. That prefix is what makes
the plan *mutual* rather than a seller checklist.

**Backward planning.** Anchor on the **buyer's** go-live date (fiscal year start, contract
expiry, compliance deadline), then subtract backward. Dock: "leverage real urgency — the
buyer's own deadlines," not fake discount deadlines. **Sequencing insight worth grading:
security review and procurement intake run in parallel; legal redlines generally cannot
complete until security clears.** A rep who parallelizes independent steps compresses a
16-week path to ~10.

**Vendors.** Accord, Recapped, Dock, GetAccept; Salesforce's "Close Plan" is implemented
as the **Quip [Mutual Close Plan template](https://quip.com/templates/close-plan)**
embedded on the Opportunity, auto-generated on stage change.

**Maps to:** `opportunity_stage_gates`, `tasks`, `agent_documents`, `sow`.

### Scenario 2.1 — Build the mutual close plan

- **TRIGGER:** Opportunity → Proposal/Price Quote with `Amount >= 100000` and
  `Go_Live_Date__c` populated.
- **REQUIRED READS:** the Opportunity; all contact roles → contacts (name, title, email);
  existing open Tasks on the Opportunity (to avoid duplicates); the Account's security-
  review-required flag.
- **REQUIRED WRITES:** insert exactly **9** Tasks with canonical subjects (`MAP: Technical
  Validation`, `MAP: Security Review`, `MAP: Business Case Approval`, `MAP: Commercial
  Terms Agreed`, `MAP: Legal Redline`, `MAP: Procurement/Vendor Intake`, `MAP: PO Issued`,
  `MAP: Signature`, `MAP: Kickoff`), each back-planned from `Go_Live_Date__c` by a fixed
  offset table; each Description naming a buyer-side owner drawn from the contact roles;
  `NextStep` = the earliest-dated open MAP task; `CloseDate` = the Signature task's date.
- **PROOF:** exactly 9 MAP tasks and the subject set equals the canonical set;
  **`MAP: Security Review`.date ≤ `MAP: Legal Redline`.date** (dependency ordering);
  `max(MAP task date) ≤ Go_Live_Date__c`; `CloseDate == Signature task date`; `NextStep`
  contains the min-dated task's subject; every Description regex-matches
  `Buyer — .+ \(.+\)` and the extracted name **exists in the Opportunity's contact roles**.

## 2.2 Stage-gate exit criteria

**Definition.** The specific, externally-verifiable conditions that must all be true
before an opportunity may advance.

**The governing rule — the "verifiable outcome" test.** Exit criteria hold only when
every one is a fact you could verify from *outside* the deal. **"Buyer returned a
redlined contract" is verifiable; "prospect seems excited" is not.** Define each stage by
a *buyer action*, not a *seller activity*
([ORM](https://orm-tech.com/blog/how-to-build-a-sales-pipeline/),
[Prospeo](https://prospeo.io/s/crm-deal-stages),
[WeFlow](https://www.weflow.ai/blog/sales-process)).

Design rules: **5–7 stages max**, **2–4 verifiable exit criteria per stage**, and
probabilities aligned to *observed historical* conversion rather than a linear ramp.

**Stage skipping is not blocked natively.** A jump from Qualification straight to Closed
Won records only Qualification's duration
([Chartio](https://chartio.com/learn/marketing-analytics/stage-duration-report-salesforce/)).
Detection is an `OpportunityHistory` diff against the canonical ordered stage list.
**Stage age** = days since `LastStageChangeDate`; recommended stale thresholds are
**1.5×–2.0× the median days-in-stage** for that stage/segment
([Outreach](https://www.outreach.ai/resources/blog/sales-pipeline-ageing)).

**Maps to:** `opportunity_stage_gates`, `stale_opportunity_ladder`.

### Scenario 2.2 — Gate the stage advance *(restraint-graded, two branches)*

- **TRIGGER:** agent is asked to advance an Opportunity from Solution Validation to
  Proposal/Negotiation.
- **REQUIRED READS:** the Opportunity + its criteria fields; contact-role count; completed
  demo/POC activity; the org's stage-criteria definition table.
- **REQUIRED WRITES — pass branch:** set the stage, set `ForecastCategoryName = 'Best
  Case'`, refresh NextStep, and log a completed Task listing each criterion and its
  evidence record id. **Fail branch:** make **no** change to StageName; instead insert one
  Task per missing criterion and write the blocking criterion into NextStep.
- **PROOF:** stage advanced **iff** Economic Buyer identified AND business case delivered
  AND critical event non-null AND ≥2 contact roles AND ≥1 completed demo/POC. In the fail
  branch **StageName is byte-identical to its pre-run value** and the gap-Task count
  equals the number of unmet criteria. In the pass branch a new `OpportunityHistory` row
  exists and `ForecastCategoryName == 'Best Case'` (**the verifier must read
  `ForecastCategoryName`, not `ForecastCategory`**). `newStageIndex - oldStageIndex == 1`
  — no skipping.

## 2.3 Deal reviews / deal inspection

**Definition.** A structured inspection of a single active opportunity by manager + AE
(± SE, deal desk, exec) to assess health, surface risk, verify the next step is credible,
and decide whether the deal belongs in the forecast.

**Clari's canonical six questions**
([clari.com](https://www.clari.com/blog/6-questions-to-ask-in-every-deal-inspection/)):
(1) What's changed since the last meeting? (2) How much activity, and is it the *right
type*? (3) Is your team building healthy relationships? (4) Does this deal follow our
sales process? (5) **Is this deal tied to an urgent initiative?** — *"If a deal isn't tied
to an urgent initiative within your prospect's organization, the deal won't close.
Period."* (6) What is the *real* revenue — the rep's "commit bank account," not an
inflated estimate.

**Agenda** ([clari.com](https://www.clari.com/blog/sales-pipeline-review/)): assign
homework (reps complete the assessment *before* the meeting) → summarize deals →
create actionable next steps **documented in the CRM, not the meeting notes**. Governing
principle: "show up informed" — the meeting is for decisions, not status readout.

**Red-flag checklist.** Missing/unengaged economic buyer; single-threaded; no next meeting
on the calendar; unclear procurement path; close date moved twice; no critical event; the
rep's only large deal; last activity >14 days in a mid/late stage; amount changed >25%
without a stage change; competitor unnamed.

**Maps to:** `deal_health_score`, `risk_notes_csm_post_call`, `coaching_cadence`.

### Scenario 2.3 — Run and record the deal review

- **TRIGGER:** weekly job over Opportunities in Commit/Best Case closing this quarter.
- **REQUIRED READS:** the Opportunity; `OpportunityHistory` ordered by date (what changed);
  contact roles; last-30-day activities; open future-dated Tasks (is a next meeting
  actually scheduled?).
- **REQUIRED WRITES:** one Task `Deal Review {YYYY-MM-DD}` per opportunity, status
  Completed, Description containing a structured answer to all six Clari questions **each
  with the record id(s) that evidence it**; set `Deal_Risk_Level__c` by deterministic rule
  (**Red** if <2 contact roles OR >14 days since activity OR PushCount ≥2; **Yellow** if
  exactly one; **Green** if none); if Red AND Commit, downgrade to Best Case and log why;
  rewrite NextStep as `"{action} — {owner} — {YYYY-MM-DD}"`.
- **PROOF:** one review Task per opportunity matching `^Deal Review \d{4}-\d{2}-\d{2}$`;
  each Description contains all six headers and ≥1 valid record id per answer;
  `Deal_Risk_Level__c` equals the value **recomputed independently by the verifier** from
  the same three inputs; **no opportunity remains Commit with Red risk**; NextStep
  regex-matches the dated pattern with a date ≥ today.

## 2.4 Pipeline inspection &amp; hygiene

Five standard checks:

**(a) Stale deals.** 21+ days with no *buyer-initiated* activity, or stage-relative
thresholds at 1.5–2.0× median days-in-stage, plus a secondary trigger: any mid/late-stage
deal with no logged activity in 14 days regardless of stage age.

**(b) Past-due close date.** Open deals where `CloseDate < TODAY`. This filter returns
**15–30% of open deals** in a typical unmanaged CRM
([Tomba](https://tomba.io/blog/deals-pipeline)). A past-due close date is never a valid
state — every one must be re-dated with a buyer-grounded reason or closed lost.

**(c) Slipped/pushed deals.** Salesforce gives this natively as **`PushCount`**. Common
policy: ≥2 → mandatory manager review; ≥3 → auto-demote out of Commit. "Chronic slip is
the leading indicator of a missed quarter and it's visible six weeks early."

**(d) Pipeline coverage ratio.** Clari's rigorous formula is **Required Coverage = 1 ÷
Win Rate** (25% win rate → 4x; 20% → 5x; 50% → 2x), with enterprise teams typically
needing 4x–7x ([clari.com](https://www.clari.com/blog/pipeline-coverage-best-practices/)).
The conventional band is 3x–4x for B2B SaaS; **under 2x is critical, over 5x usually
means inflation rather than strength**
([Startups.com](https://www.startups.com/lexicon/pipeline-coverage)). **Quarter-start
coverage is the most predictive measurement point.**

**(e) Pipeline generation targets.** Coverage is the stock; PG is the flow.

**Maps to:** `stale_opportunity_ladder`, `coverage_ratio`, `slipped_pulled_in_lost`,
`25-pipeline-inspection-rules.md`.

### Scenario 2.4 — Weekly pipeline hygiene sweep

- **TRIGGER:** Monday 06:00 scheduled job for a named team.
- **REQUIRED READS:** all open opportunities for the team; per-rep quota for the quarter;
  trailing 4-quarter win rate per segment.
- **REQUIRED WRITES:** a high-priority Task for every past-due close date; a Task for every
  stale (>21 day) opportunity; demote Commit→Best Case for every `PushCount >= 2` with a
  logged reason; one hygiene-snapshot row per rep carrying open pipeline, quota,
  `Coverage_Ratio__c`, `Required_Coverage__c` (= 1 ÷ win rate), stale amount, past-due
  amount, slipped count.
- **PROOF:** the past-due Task count **exactly equals** the verifier's independent count —
  no extras, no misses; same exact-match test for the stale set **with boundary cases
  checked at exactly 21 and 22 days**; zero records remain Commit with PushCount ≥2;
  `Coverage_Ratio__c` recomputes to within ±0.01; **no `CloseDate` or `Amount` was
  mutated** — hygiene flags, it does not fabricate data.

## 2.5 Forecast categories &amp; the forecast call

**Definitions in practice.** *Commit* = "money in the bank." *Best Case* = upside.
**Entry criteria to promote Best Case → Commit:** verbal or written commitment received,
all stakeholders aligned, pricing agreed, and only legal/procurement review remaining
([ORM](https://orm-tech.com/blog/sales-forecast-categories-explained),
[Outreach](https://www.outreach.ai/resources/blog/sales-forecast-categories)). Clari
layers **rep call → manager judgment → AI projection** as separate comparable numbers, so
the delta between them is itself the coaching artifact.

**HubSpot quirk worth grading:** `forecast_category` auto-sets from stage probability, but
**manually editing `hs_deal_stage_probability` permanently detaches auto-update** until
the deal hits a 100% or 0% stage
([HubSpot](https://knowledge.hubspot.com/forecast/use-the-forecast-tool)).

**Cadence.** A common SLA chain: reps submit Tue → managers validate Wed → RevOps
reconciles Thu → Finance reviews Fri
([Forecastio](https://forecastio.ai/blog/sales-forecasting-best-practices)).
**Accuracy benchmarks:** world-class 90–95%; 85% strong; median B2B SaaS 70–80%; average
50–70%; only ~7% of companies exceed 90%
([Forecastio](https://forecastio.ai/blog/sales-forecasting-accuracy-and-analysis)).
Measure at rep/segment/deal-size tier — **company-level accuracy is useless for coaching**.

**Maps to:** `forecast_methodology`, `commit`, `best_case`, `coverage_ratio`.

### Scenario 2.5 — Submit the weekly forecast

- **TRIGGER:** Tuesday 12:00, submission window opens for a rep, current quarter.
- **REQUIRED READS:** all open opportunities owned by the rep closing this quarter;
  closed-won this quarter; the rep's quota; the Commit promotion-criteria definition.
- **REQUIRED WRITES:** set each opportunity's `ForecastCategoryName`; for every Commit,
  populate `Commit_Justification__c` naming which of the four criteria are met **with an
  evidence record id**; insert one forecast-submission record with closed-won, commit and
  best-case sums, forecast, quota, gap.
- **PROOF:** `Commit_Amount__c` equals to the cent the verifier's independent sum;
  `Forecast == Closed_Won + Commit` exactly; **zero Commit opportunities have blank
  justification**; zero Commit opportunities have a CloseDate outside the quarter; **zero
  opportunities in Prospecting/Qualification are categorized Commit** (stage/category
  coherence); and reading the read-only `ForecastCategory` on each Commit record returns
  `Forecast` — a record where that mirror disagrees with `ForecastCategoryName` is an
  automatic fail.

## 2.6 Sandbagging detection

**Definition.** Deliberately holding a deal's forecast confidence *below* its actual state
to build a buffer ([ORM](https://orm-tech.com/blog/how-to-reduce-forecast-sandbagging/),
[Quotavue](https://quotavue.com/blog/rep-sandbagging-how-to-detect-it-in-the-pipeline)).

**Cohort signals.** Commit conversion **≥95–100% consistently** → deals are being withheld
until effectively already closed (healthy is ~85–92%). Best Case converting at a high rate
while the Commit count is small — "that's sandbagging, not discipline."

**Deal-level signals.** The classic signature: **a deal submitted as Commit in the same
week it closed, while history shows it had been at an advanced stage for weeks.** Also:
`Probability >= 75%` or late stage but category = Pipeline; close date parked just past
quarter end on a deal whose MAP signature milestone is inside the quarter.

**The inverse — "happy ears."** Commit with <2 contact roles, or PushCount ≥2, or activity
>14 days stale, or no buyer-returned redline. Cohort tell: Commit conversion below ~70%.

**Root-cause caveat every source repeats:** reps sandbag because the incentive system
rewards it or the forecasting process penalizes accuracy. **Detection without incentive
change just moves the behavior.**

**Maps to:** `sandbagging_red_flags`, `slipped_pulled_in_lost`, `commit`, `best_case`.

### Scenario 2.6 — Sandbagging / happy-ears audit *(restraint-graded)*

- **TRIGGER:** end-of-quarter + 3 days, for a team.
- **REQUIRED READS:** all opportunities closed in the quarter; `OpportunityHistory` stage
  sequences; `OpportunityFieldHistory` for `ForecastCategoryName`; each rep's weekly
  forecast submissions; still-open opportunities with stage/probability/category/activity.
- **REQUIRED WRITES:** one behavior-audit record per rep with commit conversion rate, late-
  commit count (**first move to Commit ≤7 days before close AND at a late stage ≥21 days**),
  category/stage mismatch count, happy-ears count, and a `Classification__c` of
  Sandbagger / Happy Ears / Calibrated by deterministic rule; a manager Task per mismatched
  open opportunity. **Do NOT auto-change `ForecastCategoryName` on any open deal** — this
  audit flags for human judgment only.
- **PROOF:** one audit record per rep, no duplicates; classification recomputes identically
  by the verifier; late-commit count is reproducible from field history; the flag-Task count
  equals the verifier's independent count; and **the negative check: no
  `ForecastCategoryName` value changed during the run — diff before/after, any mutation is
  a fail.**

## 2.7 Multi-threading, win/loss, competitive displacement

**Multi-threading.** Gong's own page confirms **"closed-won deals include 67% more
contacts than closed-lost deals"**
([gong.io](https://www.gong.io/resources/guides/the-data-backed-guide-to-multi-threading-and-team-selling)).
Widely-circulated further figures (130% win-rate lift above $50K, 5+ stakeholders closing
at 1.7×, 17 contacts on strategic deals) appear only in aggregators citing Gong — **treat
as secondary**. Practical gate: **≥4 named contacts across ≥3 functions** before
forecasting Commit above $250K ACV.

**Win/loss review.** Interview **7–14 days after decision** (emotional distance, vivid
memory), use an **independent interviewer** because reps get sanitized answers, and use a
standardized question bank across decision process / product fit / sales experience /
competitive comparison ([Guru](https://www.getguru.com/blog/win-or-lose-implementing-a-post-deal-review-process),
[Growth Velocity](https://growthvelocity.com/how-to-conduct-a-win-loss-analysis/)). Key
warning: **default picklists ("No budget," "Bad timing") do not capture actionable
detail** — use a hierarchical reason model with competitor linking.

**Competitive displacement.** The buyer isn't picking the best option, they're evaluating
whether the **risk of change** is worth it; migration work and retraining mean a 10% price
cut moves nobody. The play centers on trigger timing (renewal windows, incumbent price
hikes, leadership change, incumbent outage), a **Value Wedge** (unique + important to the
buyer + defensible with data), explicitly de-risking migration, and **minimum three
engaged contacts across different roles**
([MarketBetter](https://www.marketbetter.ai/blog/competitive-displacement-campaign-playbook/),
[Corporate Visions](https://corporatevisions.com/blog/competitive-differentiation/)).

**Maps to:** `their_strengths_do_not_dismiss`, `their_weaknesses_attack_here`,
`winloss_talking_points`, `pricing_pressure_guidance`, `win_rate_calculation_rules`.

### Scenario 2.7 — Multi-threading risk sweep

- **TRIGGER:** nightly job over open opportunities ≥ $250K.
- **REQUIRED READS:** contact roles (id, role, isPrimary); last-30-day activities → distinct
  contact set; forecast category.
- **REQUIRED WRITES:** `Contacts_Engaged__c` = distinct contacts with activity in 30 days;
  `Distinct_Functions__c` = distinct contact-role values; `Single_Threaded__c`; and if
  Commit/Most Likely with <4 engaged or <3 functions, a high-priority manager Task.
- **PROOF:** both counts recompute exactly from their source queries; `Single_Threaded__c`
  true iff engaged ≤1; the flag-Task count equals the verifier's independent count of the
  under-threaded-in-Commit set; **exactly one contact role has `IsPrimary = true`**.

### Scenario 2.8 — Win/loss capture on close

- **TRIGGER:** an Opportunity closes with `Amount >= 50000`.
- **REQUIRED READS:** the Opportunity; the primary contact role; the competitor field; the
  loss-reason taxonomy (L1 → dependent L2).
- **REQUIRED WRITES:** require `Loss_Reason_Primary__c` and its **dependent**
  `Loss_Reason_Detail__c`; a PMM-queue Task `"Win/Loss: schedule buyer interview"` dated
  `CloseDate + 7`; a win/loss review shell record with interviewee = the primary contact
  and target date `CloseDate + 10`.
- **PROOF:** no closed-lost ≥$50K has a blank primary reason; **`Loss_Reason_Detail__c` is
  a valid dependent value of the selected primary** (set-membership against live
  metadata, not a string guess); exactly one review record; `Task.ActivityDate ==
  CloseDate + 7` exactly; interviewee equals the `IsPrimary = true` contact role.

---

# 3 · RevOps routines

## 3.1 Lead routing SLAs / speed-to-lead

**The evidence base** — two studies routinely conflated:

- **MIT / InsideSales Lead Response Management Study (2007)** — 6 companies, 15,000+
  leads, 100,000+ dials. Contacting at **5 minutes vs 30 minutes** yields **100× higher
  odds of contact** and **21× higher odds of qualifying**.
- **HBR "The Short Life of Online Sales Leads" (2011)** — 2.24M leads. Responding **within
  1 hour** made firms **~7× more likely to qualify**
  ([rework](https://resources.rework.com/libraries/lead-management/lead-response-time)).
- Corollary: **78% of buyers purchase from the first responder.**

**Routing models.** Round robin · weighted round robin (senior rep = 2× a new hire) ·
territory · account-based (lead→account match, route to account owner) · named account.

**Native Salesforce constraints worth grading against.** Only **one assignment rule set
active at a time**; rules are criteria-ordered and **stop on first match**; they are
**not availability-aware** and **fire once at creation with no rebalancing**. Native
lead-to-account matching is **email-domain only**; there is **no native SLA enforcement,
no auto-rerouting, and no built-in record of which rule fired and why** — routing
misfires are not diagnosable natively
([LeanData](https://www.leandata.com/blog/salesforce-lead-routing-automation/)).
Queue-based **Omni-Channel** routing is the native answer to capacity awareness
([Salesforce Help](https://help.salesforce.com/s/articleView?id=sf.omnichannel_routing.htm&language=en_US&type=5)).

**LeanData mechanics.** Round-robin pools support weighting, **lead caps** (time-based or
conditional), **availability/PTO/working-hours schedules with automatic skip**, and
**fallback rules**. Every routing action writes to a **full audit log** with the reason
for each decision. SLA timers are per-rule: a miss triggers rep alert, manager escalation,
or automatic reassignment ([LeanData](https://www.leandata.com/round-robin-assignments/)).

**Chili Piper.** **Form Concierge** intercepts the form submit and renders the matched
rep's live calendar for one-click booking — **collapsing speed-to-lead to zero by
scheduling before the prospect leaves the page**
([chilipiper.com](https://www.chilipiper.com/products/form-concierge)). **Handoff Router**
manages SDR→AE→CS transitions.

**Maps to:** `inbound_routing_matrix`, `routing_decision_table`, `web_form_definitions`,
`meeting_scheduling_sla`, `visitor_identification`.

### Scenario 3.1 — Inbound MQL SLA breach recovery

- **TRIGGER:** an enterprise demo-request Lead routed to rep R1 at T0; SLA is 15 minutes to
  first touch; at T0+22min no Task exists and status is still New.
- **REQUIRED READS:** the Lead; the SLA policy config for this segment+source; all
  activities on the Lead (confirm zero); the round-robin pool membership **and availability
  calendar** (to identify the next eligible rep, skipping PTO and capped reps); R1's
  manager.
- **REQUIRED WRITES:** `SLA_Breached__c = true`; `SLA_Breach_At__c = T0 + 15min` (**the due
  time, not the detection time**); reassign to the next eligible pool member; update the
  routing timestamp; one routing-log row with reason `SLA_BREACH_REASSIGN`, previous and
  new owner, rule fired, and skipped users with skip reasons; an escalation Task to R1's
  manager; advance the pool cursor by exactly 1.
- **PROOF:** new owner is in the pool **and not on PTO and not at cap**;
  `SLA_Breach_At__c == original routed-at + 15min` exactly; exactly one routing-log row
  with that reason; exactly one open Task owned by the manager; cursor advanced by exactly
  1. **Negatives: status was NOT set to Converted; no Opportunity created; no other lead's
  owner changed.**

## 3.2 MQL → SQL handoff

**Lifecycle ladder.** Subscriber → Lead → MQL → **SAL (Sales Accepted Lead)** → SQL →
Opportunity → Customer. HubSpot's default stages match this, with a behavioral constraint
worth grading: **HubSpot's default automatic updates only move the stage forward, never
backward** ([HubSpot](https://knowledge.hubspot.com/records/use-lifecycle-stages)).

**Why SAL exists.** It is the stage that **forces sales to explicitly accept or reject**,
converting a silent handoff into a measurable one. Without SAL you cannot measure how long
sales takes to accept or reject an MQL
([Pedowitz](https://www.pedowitzgroup.com/difference-between-mqls-sqls-and-sals)).

**Scoring — fit vs intent.** HubSpot formalizes the two-axis model: **fit score**
(firmographic) + **engagement score** (behavioral), producing **three properties** (total,
fit, engagement). Range −100 to 10,000, per-group caps. Thresholds map to a **letter-number
tier** (A–C fit, 1–3 engagement), so a high-fit/low-engagement record reads as **"C1"** —
exactly the grid RevOps routes on
([HubSpot](https://knowledge.hubspot.com/scoring/build-lead-scores)).

**The accept/reject/recycle contract.** Four parts: acceptance criteria; a **fixed set of
coded rejection reasons** so a returned lead carries a reason rather than silence; a
**recycle path** sending rejected-but-recoverable records to nurture rather than dropping
them; an SLA measurement point.

**The modern shift.** SiriusDecisions coined MQL inside the **Demand Waterfall** (2002,
rev. 2012) — lead-centric. Forrester shipped the **B2B Revenue Waterfall in May 2021**:
opportunity-centric, tracking **buying groups** rather than individuals, and explicitly
adding **renewal, cross-sell and upsell opportunity types** alongside net-new. Rationale:
**>80% of purchases now involve complex multi-stakeholder buying**
([Forrester](https://www.forrester.com/press-newsroom/forrester-debuts-next-generation-b2b-revenue-waterfall-to-help-firms-accelerate-revenue-growth/)).
The nuanced counter-position: MQLs aren't dead, they were **poorly defined** — reframe as
account-level interest signals and run dual-funnel tracking
([MarketingOps.com](https://marketingops.com/mql-is-dead-or-is-it/)).

**Benchmarks:** MQL→SQL typically **10–20%**; SQL→Opportunity **40–60%**.

**Maps to:** `mql_definition`, `sal_gate`, `handoff_to_ae`, `company_marketing_handoffs`,
`company_sales_handoffs`, `disposition_codes`.

### Scenario 3.2 — MQL rejected with reason code and recycled

- **TRIGGER:** a Lead crosses the MQL threshold and routes to an SDR; at T0+6h the SDR
  determines the contact is a **student on a .edu address at a non-ICP account** — not
  qualified, but the company is a target account, so recycle rather than suppress.
- **REQUIRED READS:** the Lead and its scores; **the disqualification-reason picklist
  metadata** (the agent must not invent a free-text reason); the reason→nurture-track
  mapping; the matched Account (confirm target status); existing campaign memberships.
- **REQUIRED WRITES:** status Rejected/Recycled; `Disqualification_Reason__c` set to an
  **existing picklist value**; `SAL_Date__c` stamped even on reject (SAL means *reviewed*);
  `MQL_Accepted__c = false`; elapsed minutes; recycle date and reason; one campaign
  membership on the mapped nurture track; a completed Task documenting the disposition;
  **engagement score reset to 0, fit score unchanged**.
- **PROOF:** the reason is **non-null AND a member of the active picklist value set**
  (assert set membership, not string equality); `SAL_Date__c > MQL_Date__c` and elapsed
  minutes == the computed difference; exactly one campaign membership on the mapped track
  and **zero on any other**; engagement == 0 and **fit unchanged from its pre-trigger
  value**. **Negatives: `IsConverted == false`; no Account/Contact/Opportunity created;
  owner unchanged (rejection does not reassign); record not deleted (recycle ≠ delete).**

## 3.3 Dedupe &amp; merge survivorship

**Salesforce matching methods** — Exact, **Fuzzy**, Jaro-Winkler Distance, Metaphone 3,
Edit Distance, Name Variants &amp; Acronyms. Composite fields are decomposed: "Addresses
are broken into sections... Each section has its own matching method and match score."
**Match keys** narrow candidates to the **100 most likely duplicates** before the full
equation runs
([Trailhead](https://trailhead.salesforce.com/content/learn/modules/sales_admin_duplicate_management/sales_admin_duplicate_management_unit_2)).

**Limits.** Up to **5 active duplicate rules per object**, **3 matching rules per duplicate
rule**, **5 active matching rules per object**. Actions: Allow with alert / Block /
Report. **Custom picklist fields are not supported in cross-object matching rules**
([Salesforce Ben](https://www.salesforceben.com/salesforce-duplicate-rules/)).

**Merge mechanics.** Limited to **3 records at a time**, one Master. Default survivorship:
**the master's populated value always wins**; where the master's field is **empty**, the
value carries from the **most recently updated** duplicate that has a non-empty value.
**The master's Record ID is retained.** Losing values are recoverable **only via the audit
trail** ([DataTrim](https://www.datatrim.com/merge_rules/)).

**The three canonical survivorship strategies** RevOps configures: **most recent** (highest
LastModifiedDate), **most complete** (highest populated-field count), **source priority**
(a ranked source-of-truth list, e.g. CRM-entered > enrichment vendor > form fill).

**On merge**, all children re-parent to the master — Contacts, Opportunities, Cases,
Activities, Campaign Members, Notes &amp; Attachments — and non-master records are
soft-deleted with `MasterRecordId` set.

**Maps to:** `data_quality_rules`, `dedupe_race_handling`. **Note:** merge/delete
operations are a deliberate named partial in our world — dupe *detection* works, merges do
not, precisely because merges are the classic collateral-damage trap.

### Scenario 3.3 — Fuzzy-matched merge with source-priority survivorship

- **TRIGGER:** a duplicate job produces a record set with two Contacts on one Account, with
  differing emails, titles, phones, and `Data_Source__c` values, and differing child
  records. Policy: master = oldest CreatedDate; master-wins-when-populated; **exception:
  `Title` uses source priority where CRM Manual Entry > Enrichment Vendor**.
- **REQUIRED READS:** the duplicate record set and its items; both full Contact records
  including CreatedDate, LastModifiedDate and Data_Source__c; **the survivorship policy
  config and the source-priority ranking table**; all child records on both.
- **REQUIRED WRITES:** merge with the older record as master; each surviving field per
  policy; loser soft-deleted with `MasterRecordId` set; all children re-parented; one
  merge-audit row per field where the values differed, recording the rule applied
  (`MASTER_WINS` / `FILL_BLANK_FROM_DUP` / `SOURCE_PRIORITY`).
- **PROOF:** **the surviving record's id equals the master's original id** (ID retention);
  the loser resolves with `IsDeleted = true` and the right `MasterRecordId`; field-by-field
  equality against the five expected values; **child counts sum-preserved with zero
  orphans**; and the discriminating assertion — **exactly one audit row with
  `Rule_Applied__c = 'SOURCE_PRIORITY'` on `Title`**. A naive merge produces the right
  Title *by accident* but cannot produce that audit row with the right rule label.
  **Negatives: no third contact created; account unchanged; no opportunity deleted.**

## 3.4 Territory &amp; quota planning

**Salesforce ETM objects.** Territory Model (container) · Territory Type · Territory
(hierarchical) · Object Territory Assignment Rule · UserTerritoryAssociation. **2 models in
Enterprise Edition, 4 in Unlimited, but only ONE may be Active at a time** — the others sit
in **Planning** or **Archived**, which is exactly what makes carve-up modeling safe
([Salesforce Help](https://help.salesforce.com/s/articleView?id=000212540&language=en_US&type=1)).
Territory types are **organizational only and do not appear in the model hierarchy**.

**Assignment rules** run only for territories in Planning or Active models; you can scope a
run to all accounts or a filtered subset; two org-level toggles control automatic
evaluation on save and on insert
([Salesforce Help](https://help.salesforce.com/apex/HTViewHelpDoc?id=tm2_run_assignment_rules.htm)).

**Quota methods.** Top-down (cascade the board target) · bottom-up (territory potential ×
capacity × productivity) · historical (prior attainment + growth). The consensus RevOps
position is **not to choose** — run both and reconcile the gap. Cascading top-down without
regard to territory potential or ramp produces "a plan sellers will never trust"
([Fullcast](https://www.fullcast.com/content/sales-quota-scenario-planning/)).

**Heuristics.** **Quota-to-OTE of 4–6× for AEs** (degrades at scale), pipeline coverage
3–5×, **ramp of 3–6 months to full productivity** in SaaS. Ramp is expressed as a monthly
percentage vector, and **the un-ramped delta must be absorbed somewhere in the plan
(overassignment) or aggregate quota won't cover the target**
([Fullcast](https://www.fullcast.com/content/enterprise-sales-capacity-planning/)).

**Salesforce quota storage.** `ForecastingQuota`, per user per period; supports revenue,
quantity or custom measure; **each forecast type maintains separate quota information**
([Salesforce Help](https://help.salesforce.com/s/articleView?language=en_US&id=sales.forecasts3_quotes_intro.htm&type=5)).

**Maps to:** `territory`, `account_tiering_standard`,
`account_transfer_protocol_on_rep_departure`, `29-quota-comp-plan.md`.

### Scenario 3.4 — Territory carve with ramped quota allocation *(restraint-graded)*

- **TRIGGER:** stand up a **Planning-state** model that moves accounts matching three ANDed
  criteria into a new territory, assigns a tenured rep and a mid-year starter, and allocates
  an annual territory quota across four quarters honoring the starter's ramp vector.
- **REQUIRED READS:** existing models and their states (confirm a slot is free); the
  territory hierarchy and types; all accounts matching the three criteria → the exact
  expected count; both users including start date and the ramp policy table; existing quota
  rows (avoid double-allocation); fiscal period definitions.
- **REQUIRED WRITES:** a new model **with state Planning**; the territory with a valid type
  and parent; an assignment rule with **all three criteria ANDed**; run rules; user
  associations; 8 quota rows (2 reps × 4 quarters) satisfying both the annual sum and the
  ramp ratios; one reassignment-log row per moved account.
- **PROOF:** model state is Planning and **the count of Active models is unchanged**; the
  associated-account **id set is identical** to the verifier's independent query (not merely
  the same count); **zero accounts failing any one criterion are associated** — this catches
  an agent that ANDed only two; the quota sum matches exactly in integer cents; ramp
  compliance holds per quarter to within 1 cent. **Negatives: no `Account.OwnerId` was
  mutated — a Planning-state model must not change live ownership; the pre-existing
  territory still exists in the active model; no opportunity owner changed.**

## 3.5 Comp &amp; commission statements

**Plan components.** OTE = base + target variable at 100% (typical B2B AE 50/50, SDR
60/40) · quota · **accelerators kicking in at 100–110% of quota, paying 1.5×–3× the base
rate on incremental revenue** · decelerators (may engage between 40–60% attainment) ·
SPIFs · **clawbacks** (a well-drafted one specifies exact trigger conditions, the lookback
window, and whether it applies to base commission only or accelerators too) · **draws**
(recoverable = repaid from future commissions; non-recoverable = guaranteed floor)
([Salesforce](https://www.salesforce.com/sales/incentive-compensation-management/sales-compensation-plans/),
[ORM](https://orm-tech.com/blog/sales-compensation-plan-template)).

**Crediting rules — the part that generates most disputes.** **Split credit** divides one
booking across reps summing to 100%. **Overlay credit** goes to non-quota-carrying
specialists (SE, product overlay, partner manager) **in addition to** the AE's, *not carved
out of it*. Every comp plan generates exceptions, and **"ad hoc rulings create perceived
unfairness and erode trust in the comp system."**

**The statement + dispute process.** Modern ICM makes this a first-class workflow:
rep-facing dashboards showing real-time accrual, statements viewable and **inquiries
submittable at any point during the quarter** (not just after close), so finance resolves
discrepancies **before payroll cutoff**. The explicit design goal is to eliminate **shadow
accounting** — reps maintaining private spreadsheets because they don't trust the statement
([CaptivateIQ](https://www.captivateiq.com/blog/sales-commission-disputes),
[CaptivateIQ](https://www.captivateiq.com/blog/managing-pay-inquiries-all-from-one-place)).

**ASC 606 / ASC 340-40.** Sales commissions are **incremental costs of obtaining a
contract**. If expected to be recoverable they must be **capitalized and amortized on a
systematic basis consistent with the transfer of goods/services** — for SaaS typically the
expected customer life including anticipated renewals, not just the initial term.
**Practical expedient:** expense as incurred if the amortization period would be **one year
or less**
([PwC Viewpoint](https://viewpoint.pwc.com/dt/us/en/fasb_financial_accou/trg_revenue/trg_revenue_US/capitalization_and_a_US.html),
[RevenueHub](https://www.revenuehub.org/article/incremental-costs-obtaining-contract)).

**Maps to:** `29-quota-comp-plan.md`, `journal_entries`, `finance_approval_thresholds`.

### Scenario 3.5 — Split-credit commission statement with clawback and dispute

- **TRIGGER:** period close. A rep has a split deal (70/30), a deal with an **additive
  overlay** credit, and a prior-quarter deal that churned inside the clawback window. The
  rep then files an inquiry disputing the split.
- **REQUIRED READS:** the comp plan (quota, rate, accelerator threshold and multiplier,
  draw type, clawback window and scope); all closed-won opportunities in the period where
  the rep holds credit; **the stored split percentages** (not assumed); the churned deal and
  its original commission line at the then-effective rate; the prior draw balance; any
  existing statement for the period.
- **REQUIRED WRITES:** credit rows per opportunity with correct types; the statement with
  quota, credited amount, attainment, gross commission, clawback, draw recovery and net
  payable; one open inquiry linked to the statement and the disputed line; capitalized-
  commission rows with amortization start and period.
- **PROOF:** **split percentages sum to exactly 100**; **overlay is additive** in total
  credit but **excluded from the statement's quota-relevant credited amount** — this is the
  trap: including overlay or using 100% of the split deal both inflate attainment past the
  accelerator threshold and **falsely trigger an accelerator line**; assert
  `COUNT(accelerator lines) == 0` when attainment is below threshold; net payable equals the
  arithmetic identity `gross − clawback − draw recovery`, asserted as an identity rather
  than a literal; exactly one statement for (rep, period); exactly one open inquiry; every
  capitalized row has non-null amortization start and months, with the **practical-expedient
  flag true iff months ≤ 12**. **Negatives: the inquiry did NOT mutate the published
  statement's amounts** — disputes adjust via a subsequent adjustment record, never by
  silent restatement; **other reps' statements were not altered.**

## 3.6 Data hygiene audits

**The four canonical quality dimensions:** completeness, accuracy, consistency, timeliness.

**Scorecard metrics with published targets** — the most gradeable content in the domain
([Cleanlist](https://www.cleanlist.ai/blog/2026-02-24-crm-data-quality-benchmarks),
[ZoomInfo](https://pipeline.zoominfo.com/marketing/data-hygiene-best-practices)):

| Metric | Target |
|---|---|
| Duplicate rate | **< 2%** (above 10% = failed record-creation governance) |
| Null/blank required-field rate | **< 10%** |
| Email bounce rate | **< 2%** |
| Data freshness since verification | **< 90 days** |
| Enrichment match rate | **> 85%** |
| Routing accuracy rate | **> 95%** |

**Cadence:** monthly spot checks, quarterly deep dives. **Enrichment:** "data starts
decaying the moment you clean it" — continuous automated enrichment **on trigger**, not
quarterly batch. **Governance:** assign **owner, steward, consumer** per data domain.

**Maps to:** `data_quality_rules`, `record_retention`, `activity_logging_standards`.

### Scenario 3.6 — Monthly contact hygiene and normalization pass

- **TRIGGER:** scheduled monthly audit on Contacts in a segment, with a required-field
  policy, a 90-day staleness threshold, and normalization policies for country → ISO
  alpha-2, title → a controlled seniority taxonomy, and phone → E.164.
- **REQUIRED READS:** all in-scope contacts; **the required-field policy config** (read, not
  assumed); **the country normalization mapping table and the title→seniority taxonomy** —
  the agent must map from the org's own tables, not world knowledge; email validation and
  bounce history; the prior period's scorecard; account associations (to find orphans).
- **REQUIRED WRITES:** one issue row per **(record, issue type)** pair — a contact missing
  both title and phone produces **two** rows; normalization writes **only where a mapping
  exists**; orphan and stale flags; do-not-email for contacts with ≥2 bounces; one scorecard
  row with each metric and a pass/fail against its documented threshold.
- **PROOF:** the missing-field issue set matches the verifier's recomputed **(RecordId,
  Field) set exactly**, not just the count; completeness % recomputes to 2dp; **every
  contact whose country has no mapping entry has a null country code AND an
  `'Unmappable Country'` issue row** — this is the discriminating check against an agent
  that guesses codes from world knowledge; every seniority value is a member of the
  controlled set with **zero outside it**; every phone matches the E.164 regex; stale and
  do-not-email sets are **boundary-exact** (90 vs 91 days, 1 vs 2 bounces). **Negatives: no
  contact deleted; no email overwritten — validation flags, never mutates, the email; no
  AccountId invented for an orphan (orphans are flagged for stewardship, not auto-parented).**

## 3.7 Funnel conversion analytics

**Core metrics.** Stage-to-stage conversion · velocity (days in stage) · win rate
(**median B2B 19% in 2024**; enterprise >$100K ACV 15–20%; SMB <$25K 30–40%) · ASP · cycle
length · **pipeline velocity = (# opportunities × ASP × win rate) ÷ cycle length**, "the
most diagnostic metric available," because decomposing it says exactly where the problem
lives ([Clari](https://www.clari.com/sales-pipeline/),
[rework](https://resources.rework.com/libraries/pipeline-management/conversion-rate-analysis)).

**Cohort / vintage analysis.** Group opportunities by **creation period** and track
won/lost/still-open in each subsequent month. This is the correction for the naive win-rate
bug: **computing wins ÷ closed in a close-date window flatters the number because long-cycle
losses haven't landed yet.**

**Pipeline waterfall.** Decomposes the delta between two points in time into: starting
pipeline, created, won, lost, **slipped** (pushed out), **pulled in**, value increased,
value decreased, ending pipeline.

**The Bowtie model** (Winning by Design) extends the funnel past Closed Won: Awareness →
Education → Selection → **[Closed Won]** → Onboarding → Impact → Expansion, measuring
**volume, conversion and velocity** at every stage, with the 2023 update mapping metrics
against GTM motions (No/Low/Medium/High/Dedicated Touch)
([Winning by Design](https://winningbydesign.com/resources/research/bowtie-standard/)).

**Maps to:** `funnel_conversion_rates`, `win_rate_calculation_rules`,
`revenue_metric_definitions`, `board_pack_metrics`, `aggregates`.

### Scenario 3.7 — Quarterly funnel conversion and pipeline waterfall *(answer-task)*

- **TRIGGER:** quarter close; produce the conversion and waterfall analysis for a segment,
  given a prior-quarter-end snapshot as the starting baseline.
- **REQUIRED READS:** the **union** of opportunities open at quarter start, created during,
  or closed during (not just those closed in the quarter); stage and amount and close-date
  field history within the quarter; the prior snapshot; fiscal boundaries; **the stage-order
  metadata** (conversion is directional and the ladder must be read, not assumed).
- **REQUIRED WRITES:** a quarter-end snapshot; stage-to-stage conversion rows; days-in-stage
  per opportunity; the waterfall with all eight components; an aggregate metrics record with
  **win rate stored in two separate fields** (close-date variant and cohorted variant), ASP,
  median and mean cycle days, pipeline velocity, coverage ratio; cohort rows at month
  offsets.
- **PROOF:** **the waterfall balance identity holds exactly** — `starting + created − won −
  lost − slipped + pulled_in + value_increase − value_decrease == ending`. This single
  assertion catches nearly every mis-derivation. Ending pipeline equals the verifier's
  independent sum; **the two win-rate variants are in different fields and must differ where
  the data makes them differ** (an agent that writes the same number to both fails);
  pipeline velocity recomputes from the agent's own stored components (internal
  consistency); every conversion rate is in [0,1] and **each stage's downstream outcomes sum
  to its entered count — no opportunities vanish between stages**; cohort rows satisfy
  `won + lost + open == cohort size` at **every** offset. **Negative: no opportunity record
  was modified — analytics is read-only over the transactional layer, and an agent that
  "fixes" a stage value to make the math work fails.**

