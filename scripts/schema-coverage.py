#!/usr/bin/env python3
"""Measure the world's data model against the data models real CRMs actually ship.

    python3 scripts/schema-coverage.py [--world <world.json>] [--out docs/SCHEMA-COVERAGE.md]

`tool-coverage.py` answers "can the world do what vendor tools do". This answers the
other half: "does the world *store* what shipping CRMs store". The denominator is not
a benchmark's opinion of the domain — it is 3,000+ tables extracted by the `schema`
ingest adapter from production CRM/ERP codebases (EspoCRM, SuiteCRM, Dolibarr,
YetiForce, Frappe, Twenty, Krayin, Monica, WukongCRM, ever-gauzy and more).

Two honesty rules, both learned the hard way in this repo:

1. RANK BY INDEPENDENT IMPLEMENTATIONS. An entity modelled by six unrelated CRMs is a
   domain concept; one modelled by a single repo is that vendor's idiosyncrasy. The
   headline coverage number is computed over entities that at least MIN_REPOS distinct
   codebases model, so a long tail of bespoke tables cannot quietly deflate the score.

2. NEVER TRUNCATE THE BACKLOG. tool-coverage.py used to print its top 40 gaps while
   reporting 63, which made the artifact that exists to prove coverage understate the
   work. Every uncovered entity is listed here.

Framework plumbing (migrations, sessions, cache, job queues, permission tables) is
excluded: it is present in every PHP/Laravel/Django app and says nothing about CRM
domain coverage. The exclusion list is explicit and printed in the report so the
filtering can be argued with rather than taken on trust.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WCP = ROOT / "research" / "parity" / "wcp"

# An entity has to appear in at least this many independent codebases to count as a
# domain concept rather than one product's private table.
MIN_REPOS = 3

# Vendor table prefixes: Dolibarr ships llx_, YetiForce vtiger_/u_yf_, Sugar-family
# fields_, WordPress-ish wp_. Stripping them is what lets llx_societe and
# vtiger_account be recognised as the same idea.
#
# aos/aor/aow/aod/aop/aok/am/jjwg/fp are SuiteCRM MODULE prefixes, not domain words:
# aos_invoice is an invoice, aos_quote is a quote, aos_product is a product. Left
# unstripped they appeared as 20+ separate "core entities" purely because SuiteCRM and
# its fork ictcrm both ship them — one product's internals wearing the costume of a
# domain concept.
#
# sales/service/marketing/outreach/support are stripped because THIS world uses them:
# sales_leads, sales_quotes, service_cases, crm_activities. Without stripping, the
# world scored 0 on `lead` while holding 504 lead rows — a false negative that made
# the metric worse than useless.
PREFIXES = re.compile(r"^(llx|vtiger|u_yf|wp|tbl|tb|crm|sf|hs|pd|erp|app|core|sys|base|"
                      r"fields|glpi|civicrm|suitecrm|espo|frappe|tab|"
                      r"aos|aor|aow|aod|aop|aok|am|jjwg|fp|sugar|"
                      r"sales|service|marketing|outreach|support|rep)[_]+", re.I)
CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")

# Plumbing that every framework has and no CRM claim rests on.
INFRA = {
    "migration", "migrations", "session", "sessions", "cache", "cache_lock", "job", "jobs",
    "failed_job", "failed_jobs", "job_batch", "job_batches", "password_reset", "password_resets",
    "password_reset_token", "personal_access_token", "personal_access_tokens", "permission",
    "permissions", "role", "roles", "role_has_permission", "model_has_role", "model_has_permission",
    "migration_version", "schema_migration", "schema_migrations", "django_migration",
    "django_content_type", "django_admin_log", "django_session", "auth_permission", "auth_group",
    "content_type", "admin_log", "log", "logs", "audit_log", "audit", "setting", "settings",
    "config", "configuration", "option", "options", "meta", "metadata", "translation",
    "translations", "language", "languages", "locale", "cron", "cronjob", "queue", "queues",
    "notification", "notifications", "token", "tokens", "oauth_access_token", "oauth_client",
    "oauth_refresh_token", "api_key", "api_keys", "upload", "uploads", "attachment_version",
    "revision", "revisions", "version", "versions", "backup", "backups", "temp", "tmp",
    "import", "imports", "export", "exports", "queue_job", "webhook_log", "email_log",
    "activity_log", "system_log", "error_log", "access_log", "menu", "menus", "widget",
    "widgets", "dashboard_widget", "theme", "themes", "template_version", "sequence",
    "counter", "counters", "numbering", "entity_relation", "relation_map",
}

# Cross-CRM synonyms: HubSpot's deal, Salesforce's opportunity and Dolibarr's propal are
# one concept; societe/company/organization/account likewise.
SYNONYMS = {
    "societe": "account", "company": "account", "companies": "account", "organization": "account",
    "organisation": "account", "org": "account", "customer": "account", "client": "account",
    "accounts": "account", "account": "account", "business": "account", "firm": "account",
    "socpeople": "contact", "person": "contact", "people": "contact", "contact": "contact",
    "contacts": "contact", "individual": "contact",
    "deal": "opportunity", "propal": "opportunity", "proposal": "opportunity",
    "opportunity": "opportunity", "opportunities": "opportunity", "pipeline_deal": "opportunity",
    "lead": "lead", "leads": "lead", "prospect": "lead", "prospects": "lead", "inquiry": "lead",
    "ticket": "case", "case": "case", "cases": "case", "issue": "case", "incident": "case",
    "support_ticket": "case", "helpdesk_ticket": "case",
    "quote": "quote", "quotes": "quote", "estimate": "quote", "devis": "quote",
    "invoice": "invoice", "facture": "invoice", "bill": "invoice", "invoices": "invoice",
    "commande": "order", "order": "order", "orders": "order", "salesorder": "order",
    "sales_order": "order", "purchase_order": "purchase_order",
    "product": "product", "products": "product", "item": "product", "article": "product",
    "service": "product", "sku": "product",
    "task": "task", "tasks": "task", "todo": "task", "activity": "activity", "activities": "activity",
    "event": "event", "events": "event", "meeting": "meeting", "meetings": "meeting",
    "appointment": "meeting", "call": "call", "calls": "call", "phonecall": "call",
    "note": "note", "notes": "note", "comment": "note", "comments": "note",
    "email": "email", "emails": "email", "mail": "email", "message": "message",
    "email_message": "email", "email_messages": "email", "email_thread": "email",
    "email_threads": "email", "emailman": "email", "email_address": "email",
    "quote_line": "line_item", "quote_lines": "line_item", "line_item": "line_item",
    "products_quote": "line_item", "invoice_line": "line_item", "order_line": "line_item",
    "detail": "line_item", "details": "line_item",
    "enrollment": "enrollment", "enrollments": "enrollment", "prospect_list": "segment",
    "knowledge_base_article": "knowledge_article", "knowledgebase": "knowledge_article",
    "article": "knowledge_article", "faq": "knowledge_article",
    "campaign": "campaign", "campaigns": "campaign", "marketing_campaign": "campaign",
    "user": "user", "users": "user", "employee": "employee", "employees": "employee",
    "staff": "employee", "agent": "employee", "team": "team", "teams": "team",
    "group": "team", "groups": "team",
    "document": "document", "documents": "document", "file": "file", "files": "file",
    "attachment": "file", "attachments": "file",
    "address": "address", "addresses": "address", "country": "country", "currency": "currency",
    "tax": "tax", "taxes": "tax", "payment": "payment", "payments": "payment",
    "subscription": "subscription", "subscriptions": "subscription", "contract": "contract",
    "contracts": "contract", "project": "project", "projects": "project",
    "stage": "stage", "stages": "stage", "status": "status", "priority": "priority",
    "category": "category", "categories": "category", "tag": "tag", "tags": "tag",
    "segment": "segment", "segments": "segment", "list": "list", "lists": "list",
    "forecast": "forecast", "quota": "quota", "territory": "territory",
    "discount": "discount", "price": "price", "prices": "price", "pricebook": "price",
    "warehouse": "warehouse", "inventory": "inventory", "stock": "inventory",
    "shipment": "shipment", "delivery": "shipment", "expedition": "shipment",
    "vendor": "vendor", "supplier": "vendor", "fournisseur": "vendor",
}

SUFFIX_NOISE = re.compile(r"_(?:cstm|custom|audit|cache|tmp|bak|old|new|copy|history|log|"
                          r"index|seq|map|link|rel|ref|meta|data|extra|field_values)$", re.I)


def canon(name: str) -> str | None:
    """Normalise a physical table name to a domain entity, or None if it is plumbing."""
    n = str(name or "").strip()
    if not n:
        return None
    n = CAMEL.sub("_", n).lower()
    n = re.sub(r"[^a-z0-9_]+", "_", n).strip("_")
    prev = None
    while prev != n:                       # llx_c_ / vtiger_crm_ style stacked prefixes
        prev = n
        n = PREFIXES.sub("", n)
    n = SUFFIX_NOISE.sub("", n).strip("_")
    if not n or n.isdigit():
        return None
    if n in INFRA:
        return None
    if n in SYNONYMS:
        return SYNONYMS[n]
    # naive depluralisation, then one more synonym pass
    for singular in (re.sub(r"ies$", "y", n), re.sub(r"(ses|shes|ches|xes)$", "", n),
                     re.sub(r"s$", "", n)):
        if singular != n and singular in SYNONYMS:
            return SYNONYMS[singular]
    if n.endswith("ies"):
        n = n[:-3] + "y"
    elif n.endswith("sses") or n.endswith("shes") or n.endswith("ches"):
        n = n[:-2]
    elif n.endswith("s") and not n.endswith("ss"):
        n = n[:-1]
    return n if n and n not in INFRA else None


FORK_JACCARD = 0.8


def collapse_forks(sets: dict[str, set[str]]) -> list[list[str]]:
    """Group codebases that are forks of one product into a single source family.

    "Modelled by 3 independent codebases" is only meaningful if the codebases are
    independent. SuiteCRM and ictinnovations/ictcrm have a Jaccard similarity of
    1.00 — identical entity sets, because ictcrm is a SuiteCRM fork. Counting both
    doubled every Sugar-internal table (sugarfeed, eapm, vcal, acl_action), and a
    third Sugar-derived repo pushed them to exactly the inclusion threshold, so one
    product's plumbing was being reported as core domain vocabulary.
    """
    names = sorted(sets)
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, a in enumerate(names):
        for b in names[i + 1:]:
            A, B = sets[a], sets[b]
            if not A or not B:
                continue
            if len(A & B) / len(A | B) >= FORK_JACCARD:
                parent[find(a)] = find(b)
    families: dict[str, list[str]] = defaultdict(list)
    for n in names:
        families[find(n)].append(n)
    return [sorted(v) for v in families.values()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default=str(ROOT / "world/blobfish-wave6/package/sbx_291042075d7547f4/world.json"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "SCHEMA-COVERAGE.md"))
    ap.add_argument("--min-repos", type=int, default=MIN_REPOS)
    args = ap.parse_args()

    # ---- demand side: what production CRMs model
    repo_entities: dict[str, set[str]] = {}
    raw_tables = 0
    for f in sorted(WCP.glob("schema.*.json")):
        pkg = json.loads(f.read_text())
        repo = pkg["source"]["repo"]
        seen = set()
        for tb in pkg.get("tables", []):
            raw_tables += 1
            if (c := canon(tb.get("name"))):
                seen.add(c)
        if seen:
            repo_entities[repo] = seen
    if not repo_entities:
        print("no schema WCPs found — run: python3 scripts/ingest/ingest.py --adapter schema")
        return 1

    families = collapse_forks(repo_entities)
    merged_families = [f for f in families if len(f) > 1]
    # One vote per product family, not per clone.
    entity_sources: dict[str, set[str]] = defaultdict(set)
    for fam in families:
        label = fam[0]
        for repo in fam:
            for e in repo_entities[repo]:
                entity_sources[e].add(label)
    per_repo = {r: len(s) for r, s in repo_entities.items()}

    # ---- supply side: what the world models
    world = json.loads(Path(args.world).read_text())
    world_entities = {c for t in world.get("tables", []) if (c := canon(t.get("name")))}

    counts = Counter({e: len(s) for e, s in entity_sources.items()})
    core = {e for e, n in counts.items() if n >= args.min_repos}
    covered = core & world_entities
    missing = core - world_entities

    pct = 100 * len(covered) / max(1, len(core))
    out = [
        "# Schema coverage — the world vs the data models real CRMs ship",
        "",
        "Generated by `scripts/schema-coverage.py`. `TOOL-COVERAGE.md` asks whether the world can",
        "*do* what vendor tools do; this asks whether it *stores* what shipping CRMs store.",
        "",
        f"The denominator is **{raw_tables:,} tables** extracted by the `schema` ingest adapter from",
        f"**{len(per_repo)} production CRM/ERP codebases** — EspoCRM, SuiteCRM, Dolibarr, YetiForce,",
        "Frappe, Twenty, Krayin, Monica, WukongCRM, ever-gauzy and others — normalised onto domain",
        "entities so Dolibarr's `llx_societe`, YetiForce's `vtiger_account` and a HubSpot `company`",
        "all count once.",
        "",
        f"- distinct domain entities in the corpus: **{len(entity_sources):,}**",
        f"- independent product families (after collapsing forks): **{len(families)}** "
        f"from {len(per_repo)} codebases",
        f"- core entities (modelled by >= {args.min_repos} independent families): **{len(core)}**",
        f"- covered by the world: **{len(covered)}** ({pct:.0f}%)",
        f"- not yet covered: **{len(missing)}**",
        f"- world tables: **{len(world.get('tables', []))}** -> **{len(world_entities)}** distinct entities",
        "",
        "The headline is computed over core entities on purpose: an entity six unrelated CRMs model",
        "is a domain concept, while one that appears in a single codebase is that product's",
        "idiosyncrasy, and counting the long tail would deflate the score with other people's",
        "private tables. Framework plumbing (migrations, sessions, job queues, permission tables)",
        "is excluded — see `INFRA` in the script for the exact list.",
        "",
        "## Per-codebase contribution",
        "",
        "| codebase | distinct domain entities |",
        "|---|---:|",
    ]
    for repo, n in sorted(per_repo.items(), key=lambda kv: -kv[1]):
        out.append(f"| `{repo}` | {n} |")

    if merged_families:
        out += [
            "",
            "### Fork families collapsed to one vote",
            "",
            f"Counted once each, because \"modelled by N independent codebases\" only means",
            "something if the codebases are independent. Detected by entity-set Jaccard "
            f">= {FORK_JACCARD}.",
            "",
        ]
        for fam in merged_families:
            j_note = " + ".join(f"`{r}`" for r in fam)
            out.append(f"- {j_note}")

    out += [
        "",
        f"## Uncovered core entities ({len(missing)}), ranked by independent implementations",
        "",
        "The whole list, never a top-N: this is the backlog, and a truncated backlog reads as",
        "coverage the world does not have.",
        "",
    ]
    if missing:
        out += ["| entity | codebases modelling it |", "|---|---:|"]
        for e in sorted(missing, key=lambda x: (-counts[x], x)):
            out.append(f"| `{e}` | {counts[e]} |")
    else:
        out.append("None — every core entity is present in the world.")

    out += ["", f"## Covered core entities ({len(covered)})", "", "```",
            *sorted(covered), "```", ""]

    Path(args.out).write_text("\n".join(out))
    print(f"corpus tables {raw_tables} | entities {len(entity_sources)} | "
          f"core(>={args.min_repos} repos) {len(core)} | covered {len(covered)} ({pct:.0f}%) | "
          f"missing {len(missing)}")
    print(f"wrote {Path(args.out).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
