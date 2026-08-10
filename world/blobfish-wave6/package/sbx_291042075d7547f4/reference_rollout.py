#!/usr/bin/env python3
"""Reference rollout — executable tool calls + VCode verification -> trajectories with
failure reports. Usage: reference_rollout.py <world.json> [max_tasks]"""
import json, os, shutil, sqlite3, sys, tempfile, uuid
from isolation import execute_generated_tool, run_generated_verifier

# Default task cap; main() overrides it from argv. Kept OUT of import-time so
# train/run_training_eval.py can import this module under its own CLI flags.
MAX_TASKS = 8

def seed_db(db_path, world):
    conn = sqlite3.connect(db_path)
    for table in world.get("tables", []):
        cols = table.get("columns", [])
        defs = []
        for c in cols:
            parts = ['"' + c["name"] + '"', c.get("type", "TEXT")]
            if c.get("pk"): parts.append("PRIMARY KEY")
            defs.append(" ".join(parts))
        if not defs: continue
        try:
            conn.execute('CREATE TABLE IF NOT EXISTS "' + table["name"] + '" (' + ", ".join(defs) + ')')
        except Exception: continue
        for row in table.get("sample_rows", []) or []:
            names = [c["name"] for c in cols if c["name"] in row]
            if not names: continue
            ph = ", ".join(["?"] * len(names))
            cn = ", ".join('"' + n + '"' for n in names)
            vals = [json.dumps(row[n]) if isinstance(row[n], (dict, list)) else row[n] for n in names]
            try:
                conn.execute('INSERT OR IGNORE INTO "' + table["name"] + '" (' + cn + ') VALUES (' + ph + ')', vals)
            except Exception: pass
    conn.execute('CREATE TABLE IF NOT EXISTS "_forge_actions" ("id" TEXT PRIMARY KEY, "operation" TEXT NOT NULL, "action" TEXT NOT NULL, "target" TEXT, "payload" TEXT, "created_at" TEXT NOT NULL)')
    conn.commit(); conn.close()

def snapshot(db_path):
    conn = sqlite3.connect(db_path); conn.row_factory = sqlite3.Row
    out = {}
    for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
        out[name] = [dict(r) for r in conn.execute('SELECT * FROM "' + name + '" ORDER BY rowid').fetchall()]
    conn.close(); return out

def execute_tool(world, db_path, tool_name, args):
    tool = next((t for t in world.get("tools", []) if t["name"] == tool_name), None)
    if not tool: return {"ok": False, "error": "tool '" + tool_name + "' not found"}
    src = tool.get("source") or ""
    if ("def " + tool_name) not in src: return {"ok": False, "error": "tool has no executable source"}
    return execute_generated_tool(src, tool_name, db_path, args)

def _row_id_for_entity(world, entity):
    # Return a real seeded id from the table whose name matches the entity
    # (e.g. "driver" -> drivers, "po" -> purchase_orders via prefix match).
    for t in world.get("tables", []):
        tn = t["name"].lower()
        if entity and (entity in tn or tn.rstrip("s") == entity or tn.startswith(entity)):
            rows = t.get("sample_rows") or []
            if rows and rows[0].get("id") is not None: return rows[0]["id"]
    return None

def _clean_val(v):
    return v.strip("'") if isinstance(v, str) else v

def infer_args(tool, discovered, world, pins=None):
    # Build args from the tool's DECLARED parameters — never pass a parameter the
    # tool doesn't accept (the old code blindly sent {"limit": 5} to every read
    # tool, causing "unexpected keyword argument 'limit'"). Thread real ids from
    # prior results (discovered) and from seeded rows, so multi-step walks chain.
    if not tool: return {}
    params = tool.get("parameters") or {}
    if not params:
        return {"limit": 5} if tool.get("type") == "read" else {}
    targets = tool.get("target_tables") or []
    tables = {t["name"]: t for t in world.get("tables", [])}
    row0 = {}
    for tn in targets:
        rows = (tables.get(tn) or {}).get("sample_rows") or []
        if rows: row0 = rows[0]; break
    # Pin: the task's expected_state_change for this tool's target table names the
    # EXACT row + target value the verifier will check. Threading it makes the
    # reference rollout reproduce the verifier's expected end state (so a valid
    # walk actually PASSES), and it advances status along the real lifecycle
    # instead of a naive guess (avoiding lifecycle_violation rejections).
    pin = None
    if tool.get("type") == "write":
        for pc in (pins or []):
            if pc.get("table") in targets and pc.get("id") is not None and pc.get("field") not in (None, "(new row)"):
                pin = pc; break
    args = {}
    # Write tools follow the convention def tool(db_path, id, **kwargs): the target
    # row's primary key is a positional id that is NOT in declared parameters.
    if tool.get("type") == "write" and "id" not in params:
        _tid = (pin or {}).get("id") if pin else None
        if _tid is None: _tid = discovered.get("id")
        if _tid is None and targets:
            _ent = targets[0][:-1] if targets[0].endswith("s") else targets[0]
            _tid = _row_id_for_entity(world, _ent)
        if _tid is None and row0.get("id") is not None: _tid = row0["id"]
        if _tid is not None: args["id"] = _tid
    for p, ptype in params.items():
        pl = p.lower()
        # Pin the target field's value (e.g. status -> the exact transition target).
        if pin and (p == pin.get("field") or (pl in ("new_status", "status") and pin.get("field") == "status")):
            pv = _clean_val(pin.get("to"))
            if pv not in (None, "", "changed"): args[p] = pv; continue
        if p == "id" or pl.endswith("_id"):
            if pin and p == "id": args[p] = pin.get("id"); continue
            if p in discovered: args[p] = discovered[p]; continue
            entity = pl[:-3] if pl.endswith("_id") else ""
            rid = _row_id_for_entity(world, entity) if entity else None
            args[p] = rid if rid is not None else (discovered.get("id") or row0.get("id") or 1)
            continue
        if pl == "limit": args[p] = 5; continue
        if pl == "new_status": args[p] = "completed"; continue
        if pl == "status": args[p] = "approved"; continue
        if p in discovered: args[p] = discovered[p]; continue
        if p in row0 and row0[p] is not None: args[p] = row0[p]; continue
        t = str(ptype).lower()
        if "int" in t: args[p] = 1
        elif "float" in t or "real" in t or "number" in t or "cents" in pl: args[p] = 1.0
        elif "bool" in t: args[p] = True
        else: args[p] = "value"
    return args

def absorb(discovered, result):
    if not isinstance(result, dict): return
    # Capture any *_id / id the tool returned so later steps can thread it.
    for k, v in result.items():
        if (k == "id" or k.endswith("_id")) and v is not None: discovered[k] = v
    rows = result.get("rows") or []
    if rows and isinstance(rows[0], dict):
        r0 = rows[0]
        if r0.get("id") is not None: discovered["id"] = r0["id"]
        for k, v in r0.items():
            if k.endswith("_id") and v is not None: discovered.setdefault(k, v)

def run_verifier(world, task_id, initial, final, trace):
    v = next((x for x in world.get("verifiers", []) if x["task_id"] == task_id), None)
    if not v or not v.get("vcode"): return {"passed": False, "reward": 0.0, "error": "verifier not found", "assertions": []}
    return run_generated_verifier(v["vcode"], task_id, initial, final, trace)

def main():
    world = json.load(open(sys.argv[1]))
    max_tasks = int(sys.argv[2]) if len(sys.argv) > 2 else MAX_TASKS
    tmp = tempfile.mkdtemp(prefix="rollout-")
    seed = os.path.join(tmp, "seed.db")
    trajectories = []
    try:
        seed_db(seed, world)
        for i, task in enumerate(world.get("tasks", [])[:max_tasks]):
            try:
                state = os.path.join(tmp, "state_" + str(i) + ".db")
                shutil.copy2(seed, state)
                initial = snapshot(state)
                steps, discovered = [], {}
                # required_tools is EMPTY for intent-only (scrubbed) tasks — the
                # ordered tool sequence lives in walk / _reference_tools. Prefer
                # those so the reference rollout actually executes tools instead
                # of doing nothing (the empty-trajectory regression). Reads first
                # so ids are sourced before writes consume them.
                seq = task.get("walk") or task.get("_reference_tools") or task.get("required_tools", [])
                _ttype = {t["name"]: t.get("type", "read") for t in world.get("tools", [])}
                seq = sorted(seq, key=lambda n: 0 if _ttype.get(n) == "read" else 1)
                # Pins from the task's expected end state — drive write tools to the
                # exact rows + target values the verifier checks. Session tasks
                # (WS4) already carry POST-correction pins, so the reference walk
                # honors the scripted correction by construction; the scripted
                # user turns are delivered into the step log at their scripted
                # positions so the trajectory records the full session.
                pins = [sc for sc in (task.get("expected_state_changes") or []) if sc.get("id")]
                session = sorted([t for t in (task.get("session") or [])
                                  if isinstance(t, dict) and t.get("user_text")],
                                 key=lambda t: t.get("turn", 0))
                si = 0
                def _deliver_session(upto):
                    nonlocal si
                    while si < len(session) and (upto is None or session[si].get("turn", 0) < upto):
                        steps.append({"step": len(steps) + 1, "tool": "_user_turn",
                                      "args": {"kind": session[si].get("kind"), "user_text": str(session[si].get("user_text"))[:300]},
                                      "ok": True, "observation": "scripted mid-episode user turn delivered"})
                        si += 1
                for j, tool_name in enumerate(seq, 1):
                    _deliver_session(j)
                    tool = next((t for t in world.get("tools", []) if t["name"] == tool_name), None)
                    args = infer_args(tool, discovered, world, pins)
                    r = execute_tool(world, state, tool_name, args)
                    absorb(discovered, r.get("result") or {})
                    steps.append({"step": len(steps) + 1, "tool": tool_name, "args": args, "ok": r.get("ok", False),
                                  "observation": (json.dumps(r.get("result")) if r.get("result") is not None else str(r.get("error")))[:300]})
                _deliver_session(None)
                final = snapshot(state)
                tool_steps = [s for s in steps if s["tool"] != "_user_turn"]
                trace = [{"tool": s["tool"], "ok": s["ok"]} for s in tool_steps]
                vr = run_verifier(world, task["task_id"], initial, final, trace)
                vr = dict(vr) if isinstance(vr, dict) else {"passed": False, "reward": 0.0, "error": "verifier returned a non-object", "assertions": []}
                vr["task_id"] = task["task_id"]
                passed = bool(vr.get("passed")); reward = vr.get("reward", 1.0 if passed else 0.0)
                failed = vr.get("failed_conditions") or vr.get("failed_assertions") or \
                    [a for a in (vr.get("assertions") or []) if isinstance(a, dict) and not a.get("passed")]
                failure_report = {"task_id": task["task_id"], "outcome": "passed" if passed else "failed",
                                  "reward": reward, "state_changed": initial != final, "steps_executed": len(tool_steps),
                                  "session_turns_delivered": si,
                                  "tools_ok": sum(1 for s in tool_steps if s["ok"]), "tools_failed": [s["tool"] for s in tool_steps if not s["ok"]],
                                  "failed_conditions": failed,
                                  "explanation": vr.get("explanation") or vr.get("error") or ("all verifier assertions passed" if passed else "verifier assertions not satisfied by the reference rollout")}
                trajectories.append({"id": "traj_" + uuid.uuid4().hex[:12], "task_id": task["task_id"], "prompt": task.get("prompt", ""),
                                     "provider": "reference", "model": "deterministic_reference_rollout", "required_tools": task.get("required_tools", []),
                                     "model_evidence": False, "run_kind": "reference", "steps": steps,
                                     "verifier": vr, "vcode_verifier": vr, "verification_basis": "vcode",
                                     "reward": reward, "passed": passed, "failure_report": failure_report})
            except Exception as e:
                trajectories.append({"id": "traj_" + uuid.uuid4().hex[:12], "task_id": task.get("task_id", "task_" + str(i)),
                                     "provider": "reference", "model": "deterministic_reference_rollout",
                                     "model_evidence": False, "run_kind": "reference", "passed": False, "reward": 0.0,
                                     "failure_report": {"task_id": task.get("task_id"), "outcome": "error", "explanation": str(e)[:200]}})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"trajectories": trajectories}))

if __name__ == "__main__":
    main()
