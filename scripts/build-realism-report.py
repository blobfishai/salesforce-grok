#!/usr/bin/env python3
"""Render the realism evidence page from captured artifacts.

Reads only real files — data/evidence/realism-evidence.json (live MCP calls),
data/flake/crma-clone-flash.json + crma-refix.json (measured task results), and
world.json (inventory) — so the page cannot drift from what actually ran.

Run: python3 scripts/build-realism-report.py  ->  data/evidence/realism-report.html
"""
import html
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "world", "blobfish-wave6", "package", "sbx_291042075d7547f4")
OUT = os.path.join(ROOT, "data", "evidence", "realism-report.html")

ev = json.load(open(os.path.join(ROOT, "data", "evidence", "realism-evidence.json")))
world = json.load(open(os.path.join(PKG, "world.json")))
sweep = json.load(open(os.path.join(ROOT, "data", "flake", "crma-clone-flash.json")))
refix = json.load(open(os.path.join(ROOT, "data", "flake", "crma-refix.json")))

# ---- merge the re-run of the two fixed tasks over the first sweep ------------
results = {t["taskId"]: t for t in sweep["tasks"]}
for t in refix["tasks"]:
    results[t["taskId"]] = t
crma_tasks = {t["task_id"]: t for t in world["tasks"] if t["task_id"].startswith("crma_")}

ns_vendor = {"salesforce": "salesforce-crm", "core": "revops-core", "stripe": "stripe-billing",
             "email": "sendgrid-email", "slack": "slack", "calendar": "google-calendar",
             "erp": "netsuite-erp", "notion": "notion-docs", "github": "github", "jira": "jira",
             "pagerduty": "pagerduty-support"}
vendor_counts = Counter(ns_vendor[t["asset_namespace"]] for t in world["tools"])
table_rows = {t["name"]: t.get("row_count", len(t.get("sample_rows", []))) for t in world["tables"]}

E = html.escape


def j(obj, limit=1400):
    s = json.dumps(obj, indent=1, ensure_ascii=False)
    return E(s if len(s) <= limit else s[:limit] + "\n… truncated")


def chip(kind, label):
    return f'<span class="chip {kind}">{E(label)}</span>'


# ------------------------------------------------------------------ sections
task_rows = []
for tid in sorted(crma_tasks):
    t = crma_tasks[tid]
    r = results.get(tid, {})
    prov = t["provenance"]
    passed = r.get("passRate", 0) == 1
    verdict = chip("ok", "pass") if passed else chip("bad", "fail")
    calls = r.get("avgToolCalls", "—")
    gold = t.get("gold_answer") or (t.get("expected_state_changes") or [{}])[0].get("to") or "refusal required"
    task_rows.append(
        f'<tr><td class="mono">{E(tid)}</td>'
        f'<td>{E(prov["crmarena_task_type"])}</td>'
        f'<td>{chip("neutral", prov["grading"])}</td>'
        f'<td class="mono gold">{E(str(gold)[:38])}</td>'
        f'<td class="num">{E(str(calls))}</td>'
        f'<td>{verdict}</td></tr>')

vendor_blocks = []
for vendor, calls in ev["vendors"].items():
    items = []
    for c in calls:
        resp = c["response"]
        flavour = "bad" if (isinstance(resp, dict) and any(
            k in json.dumps(resp)[:120] for k in ["not found", "not_found", "NOT_FOUND", "resource_missing"])) else "ok"
        items.append(
            f'<div class="call">'
            f'<div class="call-head"><span class="mono tool">{E(c["tool"])}</span>'
            f'{chip(flavour, "error shape" if flavour == "bad" else "200")}</div>'
            f'<div class="io"><div><span class="io-label">request</span><pre>{j(c["arguments"], 400)}</pre></div>'
            f'<div><span class="io-label">response</span><pre>{j(resp, 900)}</pre></div></div></div>')
    vendor_blocks.append(f'<section class="vendor"><h3>{E(vendor)}</h3>{"".join(items)}</section>')

doc_cards = []
for d in ev["documents"]:
    doc_cards.append(
        f'<article class="doc"><header><h4>{E(d["title"] or d["query"])}</h4>'
        f'<span class="mono muted">{d["chars"]} chars</span></header>'
        f'<pre class="excerpt">{E(d["excerpt"][:420])}…</pre></article>')

flow_steps = []
for i, st in enumerate(ev["workflow"], 1):
    fr = ""
    if st.get("retried_after_friction"):
        fr = (f'<div class="friction"><span class="io-label">injected friction, then retried</span>'
              f'<pre>{j(st["friction"], 300)}</pre></div>')
    flow_steps.append(
        f'<li><div class="step-head"><span class="step-n mono">{i}</span>'
        f'<span class="step-why">{E(st["why"])}</span>'
        f'<span class="mono tool">{E(st["tool"])}</span></div>'
        f'{fr}<pre>{j(st["response"], 700)}</pre></li>')

n_pass = sum(1 for tid in crma_tasks if results.get(tid, {}).get("passRate", 0) == 1)
n_calls = sum(len(v) for v in ev["vendors"].values()) + len(ev["workflow"]) + len(ev["documents"])
total_cost = round(sweep.get("costUsd", 0) + refix.get("costUsd", 0), 2)

HTML = f"""<title>CRMArena clone — working evidence</title>
<style>
:root {{
  --ground:#EEF1F5; --surface:#FFFFFF; --sunken:#F6F8FB;
  --ink:#0F1E33; --muted:#5C6E88; --rule:#D2DAE5;
  --accent:#1D4F8C; --ok:#1B6B4C; --bad:#A5342A; --neutral:#5C6E88;
  --shadow:0 1px 2px rgba(15,30,51,.06), 0 8px 24px -16px rgba(15,30,51,.28);
  --display: "Iowan Old Style", "Charter", Georgia, "Times New Roman", serif;
  --body: system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#0C1320; --surface:#121B2A; --sunken:#0F1826;
    --ink:#E6ECF4; --muted:#94A5BC; --rule:#22304A;
    --accent:#7FB2E8; --ok:#55C08D; --bad:#E8796A; --neutral:#94A5BC;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 28px -18px rgba(0,0,0,.9);
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0C1320; --surface:#121B2A; --sunken:#0F1826;
  --ink:#E6ECF4; --muted:#94A5BC; --rule:#22304A;
  --accent:#7FB2E8; --ok:#55C08D; --bad:#E8796A; --neutral:#94A5BC;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 28px -18px rgba(0,0,0,.9);
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink); font-family:var(--body);
  line-height:1.6; font-size:16px; }}
.wrap {{ max-width:1080px; margin:0 auto; padding:clamp(1.5rem,4vw,3rem) clamp(1rem,3vw,2rem) 5rem; }}
h1,h2,h3,h4 {{ font-family:var(--display); font-weight:600; text-wrap:balance; margin:0; }}
h1 {{ font-size:clamp(1.9rem,4vw,2.6rem); letter-spacing:-.01em; line-height:1.15; }}
h2 {{ font-size:1.5rem; margin-bottom:.25rem; }}
h3 {{ font-size:1.1rem; }}
h4 {{ font-size:1rem; }}
p {{ margin:0; max-width:68ch; }}
.mono {{ font-family:var(--mono); font-size:.82em; font-variant-numeric:tabular-nums; }}
.muted {{ color:var(--muted); }}
.eyebrow {{ font-family:var(--mono); font-size:.72rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--accent); }}
header.masthead {{ display:flex; flex-direction:column; gap:.75rem; padding-bottom:1.5rem;
  border-bottom:2px solid var(--ink); margin-bottom:2rem; }}
.masthead .sub {{ color:var(--muted); max-width:70ch; }}
.figures {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); border-radius:3px; overflow:hidden; margin:2rem 0; }}
.fig {{ background:var(--surface); padding:1rem 1.1rem; }}
.fig .n {{ font-family:var(--display); font-size:1.9rem; line-height:1; font-variant-numeric:tabular-nums; }}
.fig .l {{ font-family:var(--mono); font-size:.7rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); margin-top:.4rem; display:block; }}
section.block {{ margin:3rem 0 0; }}
section.block > p {{ color:var(--muted); margin-top:.4rem; }}
.tablewrap {{ overflow-x:auto; margin-top:1.25rem; border:1px solid var(--rule); border-radius:3px;
  background:var(--surface); }}
table {{ border-collapse:collapse; width:100%; font-size:.9rem; }}
th, td {{ text-align:left; padding:.6rem .8rem; border-bottom:1px solid var(--rule); vertical-align:top; }}
th {{ font-family:var(--mono); font-size:.7rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); background:var(--sunken); position:sticky; top:0; }}
tr:last-child td {{ border-bottom:none; }}
td.num {{ text-align:right; font-family:var(--mono); font-variant-numeric:tabular-nums; }}
td.gold {{ color:var(--muted); }}
.chip {{ display:inline-block; font-family:var(--mono); font-size:.7rem; letter-spacing:.06em;
  padding:.12rem .45rem; border-radius:2px; border:1px solid currentColor; white-space:nowrap; }}
.chip.ok {{ color:var(--ok); }} .chip.bad {{ color:var(--bad); }} .chip.neutral {{ color:var(--neutral); }}
.vendor {{ margin-top:1.5rem; }}
.vendor h3 {{ padding-bottom:.35rem; border-bottom:1px solid var(--rule); margin-bottom:.75rem; }}
.call {{ background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:.75rem .9rem;
  margin-bottom:.6rem; box-shadow:var(--shadow); }}
.call-head {{ display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:.5rem; }}
.tool {{ color:var(--accent); font-weight:600; }}
.io {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.4fr); gap:.75rem; }}
@media (max-width:720px) {{ .io {{ grid-template-columns:1fr; }} }}
.io-label {{ font-family:var(--mono); font-size:.66rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--muted); display:block; margin-bottom:.2rem; }}
pre {{ font-family:var(--mono); font-size:.76rem; line-height:1.45; background:var(--sunken); color:var(--ink);
  border:1px solid var(--rule); border-radius:2px; padding:.55rem .65rem; margin:0; overflow-x:auto;
  white-space:pre; }}
.docs {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:.75rem; margin-top:1.25rem; }}
.doc {{ background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:.8rem .9rem;
  box-shadow:var(--shadow); }}
.doc header {{ display:flex; justify-content:space-between; align-items:baseline; gap:.5rem; margin-bottom:.5rem; }}
.excerpt {{ white-space:pre-wrap; max-height:11rem; overflow:auto; }}
ol.flow {{ list-style:none; counter-reset:s; padding:0; margin:1.25rem 0 0; display:flex;
  flex-direction:column; gap:.6rem; }}
ol.flow li {{ background:var(--surface); border:1px solid var(--rule); border-left:3px solid var(--accent);
  border-radius:3px; padding:.7rem .9rem; box-shadow:var(--shadow); }}
.step-head {{ display:flex; align-items:baseline; gap:.6rem; flex-wrap:wrap; margin-bottom:.5rem; }}
.step-n {{ color:var(--accent); font-weight:700; }}
.step-why {{ font-weight:600; }}
.friction {{ margin-bottom:.5rem; }}
.friction .io-label {{ color:var(--bad); }}
.notes {{ background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:1rem 1.2rem;
  margin-top:1.25rem; }}
.notes li {{ margin-bottom:.55rem; }}
.notes li:last-child {{ margin-bottom:0; }}
footer {{ margin-top:3rem; padding-top:1rem; border-top:1px solid var(--rule); color:var(--muted);
  font-size:.85rem; }}
a {{ color:var(--accent); }}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
</style>

<div class="wrap">
<header class="masthead">
  <span class="eyebrow">Working evidence · captured live, not illustrated</span>
  <h1>CRMArena, cloned into a state-verified world</h1>
  <p class="sub">Every call, response, document excerpt and verdict below was executed against the running
  world server (<span class="mono">{E(ev['world_base'])}</span>, session
  <span class="mono">{E(ev['session'][:18])}…</span>) and recorded verbatim. The task pack clones the
  CRMArena (arXiv:2411.02305) and CRMArena-Pro (arXiv:2505.18878) evaluation surface, graded by
  deterministic verifiers — no LLM judge anywhere.</p>
</header>

<div class="figures">
  <div class="fig"><span class="n">{len(crma_tasks)}</span><span class="l">cloned task types</span></div>
  <div class="fig"><span class="n">{n_pass}/{len(crma_tasks)}</span><span class="l">passing, flash</span></div>
  <div class="fig"><span class="n">{len(world['tools'])}</span><span class="l">live tools</span></div>
  <div class="fig"><span class="n">{len(world['tables'])}</span><span class="l">backing tables</span></div>
  <div class="fig"><span class="n">{n_calls}</span><span class="l">calls captured</span></div>
  <div class="fig"><span class="n">${total_cost}</span><span class="l">measured cost</span></div>
</div>

<section class="block">
  <h2>The task pack</h2>
  <p>Every gold answer is computed from the database at build time, never hand-written, so a verifier
  cannot disagree with the world. Grading is one of three deterministic families: <strong>answer</strong>
  (exact match on the agent's final reply plus a read-only guard), <strong>state</strong> (target row
  correct, with collateral-damage guards), <strong>refusal</strong> (the seeded secret must be withheld).</p>
  <div class="tablewrap"><table>
    <thead><tr><th>task</th><th>CRMArena type</th><th>grading</th><th>gold</th><th>calls</th><th>verdict</th></tr></thead>
    <tbody>{''.join(task_rows)}</tbody>
  </table></div>
</section>

<section class="block">
  <h2>Tools, exercised for real</h2>
  <p>One read, one write and one deliberate error per vendor surface — each returning that vendor's own
  response and error shape.</p>
  {''.join(vendor_blocks)}
</section>

<section class="block">
  <h2>Seeded documents, readable in-world</h2>
  <p>The policy corpus is queryable by agents at run time; these excerpts came back from
  <span class="mono">notion.query_documents</span>. Task golds are extracted from this same text, so
  what an agent reads is by construction what the verifier expects.</p>
  <div class="docs">{''.join(doc_cards)}</div>
</section>

<section class="block">
  <h2>One workflow, end to end</h2>
  <p>Read the governing policy, find the over-authority quote, inspect its lines, reject it per policy,
  announce it in the deal room, confirm the state change — across three vendor servers in one session.</p>
  <ol class="flow">{''.join(flow_steps)}</ol>
</section>

<section class="block">
  <h2>What this does not yet show</h2>
  <div class="notes"><ul>
    <li><strong>Two aggregate tasks exhaust the turn budget.</strong> Summing 500 opportunities or grouping
    180 cases by month means paging 30 rows at a time; CRMArena hands agents SOQL aggregates, this world
    does not. Measured, not hidden — <span class="mono">crma_003</span> and <span class="mono">crma_011</span>
    ran out of turns before answering.</li>
    <li><strong>Two confidentiality tasks fail, correctly.</strong> The model disclosed an internal credit
    note to a self-declared competitor and a department budget to a journalist. That is the eval working.</li>
    <li><strong>Sales-cycle timing is not cloned.</strong> The seeded lead and opportunity dates have no
    temporal coherence (differences run −174 to +166 days), so a mean-cycle gold would grade noise.</li>
    <li><strong>Results are one trial per task on a cheap model.</strong> Flakiness needs repeat trials;
    the frontier model cannot run this surface at all until the 350-tool xAI cap is addressed.</li>
  </ul></div>
</section>

<footer>Generated by <span class="mono">scripts/build-realism-report.py</span> from
<span class="mono">data/evidence/realism-evidence.json</span> and
<span class="mono">data/flake/crma-clone-flash.json</span>. All data synthetic —
"Morgan Stanley (SIMULATED)" scenario, no real entities.</footer>
</div>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(HTML)
print(f"wrote {os.path.relpath(OUT, ROOT)} ({len(HTML)//1024} KB)")
print(f"  tasks {n_pass}/{len(crma_tasks)} passing · {n_calls} captured calls · {len(world['tools'])} tools")
