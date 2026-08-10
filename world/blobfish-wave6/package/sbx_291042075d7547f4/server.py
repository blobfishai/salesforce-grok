#!/usr/bin/env python3
"""Harbor runtime server — exposes one prebuilt company world as REST + MCP.

Endpoints:
  GET    /health                — Health check
  GET    /world                 — World identity, thesis, and resource-count summary
  GET    /tools                 — List tool definitions and input schemas
  GET    /tasks                 — List packaged tasks
  GET    /traces                — List traces recorded in the current runtime state
  GET    /tables                — List tables with row counts
  GET    /tables/{name}         — Sample rows from one table
  POST   /sessions              — Create an isolated copy-on-write world session
  DELETE /sessions/{session_id} — Close an isolated session and remove its mutable state
  POST   /mcp                   — MCP JSON-RPC initialize, tools/list, and tools/call
  POST   /tool-call             — Execute one tool with {tool, args}
  POST   /task/{task_id}/run    — Replay a packaged task trajectory and run VCode
  POST   /chat                  — Run the bundled stateful heuristic agent with {message}
  POST   /reset                 — Reset runtime state from the immutable seed
  POST   /verify/{task_id}      — Run the verifier for one task
"""
import contextvars, hashlib, hmac, json, os, re, shutil, sqlite3, sys, time, uuid
from isolation import execute_generated_tool, run_generated_verifier
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
WORLD_PATH = os.path.join(BASE, "world.json")
STATE_DB = os.path.join(BASE, "state.db")
SEED_DB = os.path.join(BASE, "seed.db")
TRACES_DIR = os.path.join(BASE, "traces")
RUNTIME_TRACES_DIR = os.path.join(TRACES_DIR, "runtime")
SESSIONS_DIR = os.path.join(BASE, ".sessions")
MAX_REQUEST_BYTES = 1_000_000
SQLITE_RESET_SIDECARS = ("-journal", "-shm", "-wal", ".bf-friction")
os.makedirs(TRACES_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, mode=0o700, exist_ok=True)
try:
    os.chmod(SESSIONS_DIR, 0o700)
except OSError:
    pass
TRACES: list[dict] = []
ROOT_TRACES_LOADED = False
SESSION_TRACES: dict[str, list[dict]] = {}
REQUEST_STATE_DB = contextvars.ContextVar("blobfish_request_state_db", default=None)
REQUEST_SESSION_ID = contextvars.ContextVar("blobfish_request_session_id", default=None)
SESSION_ID_RE = re.compile(r"^bfs_[0-9a-f]{32}$")
WORLD_API_KEY = os.environ.get("BLOBFISH_API_KEY", "").strip()
try:
    MAX_SESSIONS = max(1, min(10_000, int(os.environ.get("BLOBFISH_MAX_SESSIONS", "256"))))
except ValueError:
    MAX_SESSIONS = 256
try:
    SESSION_TTL_SECONDS = max(1, min(2_592_000, int(os.environ.get("BLOBFISH_SESSION_TTL_SECONDS", "86400"))))
except ValueError:
    SESSION_TTL_SECONDS = 86_400

def current_state_db() -> str:
    return REQUEST_STATE_DB.get() or STATE_DB

def trace_directory(session_id: str | None = None) -> str:
    return os.path.join(TRACES_DIR, "sessions", session_id) if session_id else RUNTIME_TRACES_DIR

def load_trace_directory(session_id: str | None = None) -> list[dict]:
    directory = trace_directory(session_id)
    if not os.path.isdir(directory):
        return []
    loaded = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(directory, name), encoding="utf-8") as handle:
                entry = json.load(handle)
            if isinstance(entry, dict):
                loaded.append(entry)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
    def sort_key(entry: dict) -> tuple[float, str]:
        try:
            timestamp = float(entry.get("timestamp", 0) or 0)
        except (TypeError, ValueError):
            timestamp = 0.0
        return timestamp, str(entry.get("id", ""))
    loaded.sort(key=sort_key)
    return loaded

def current_traces() -> list[dict]:
    global ROOT_TRACES_LOADED
    session_id = REQUEST_SESSION_ID.get()
    if not session_id:
        if not ROOT_TRACES_LOADED:
            TRACES.extend(load_trace_directory())
            ROOT_TRACES_LOADED = True
        return TRACES
    if session_id not in SESSION_TRACES:
        SESSION_TRACES[session_id] = load_trace_directory(session_id)
    return SESSION_TRACES[session_id]

def clear_current_traces() -> None:
    session_id = REQUEST_SESSION_ID.get()
    current_traces().clear()
    directory = trace_directory(session_id)
    if not os.path.isdir(directory):
        return
    for name in os.listdir(directory):
        if not name.endswith(".json"):
            continue
        try:
            os.remove(os.path.join(directory, name))
        except FileNotFoundError:
            pass

def session_state_db(session_id: str) -> str | None:
    if not SESSION_ID_RE.fullmatch(session_id):
        return None
    return os.path.join(SESSIONS_DIR, session_id + ".db")

class SessionCapacityError(RuntimeError):
    pass

def cleanup_expired_sessions(now: float | None = None) -> int:
    cutoff = (time.time() if now is None else now) - SESSION_TTL_SECONDS
    removed = 0
    for name in os.listdir(SESSIONS_DIR):
        if not name.endswith(".db"):
            continue
        session_id = name[:-3]
        target = session_state_db(session_id)
        if target is None:
            continue
        try:
            expired = os.path.getmtime(target) <= cutoff
        except FileNotFoundError:
            continue
        if expired and close_state_session(session_id):
            removed += 1
    return removed

def create_state_session() -> tuple[str, str]:
    if not os.path.exists(SEED_DB):
        raise FileNotFoundError("seed.db not found")
    cleanup_expired_sessions()
    existing = sum(1 for name in os.listdir(SESSIONS_DIR) if name.endswith(".db"))
    if existing >= MAX_SESSIONS:
        raise SessionCapacityError(f"session capacity reached ({MAX_SESSIONS})")
    session_id = "bfs_" + uuid.uuid4().hex
    target = session_state_db(session_id)
    if target is None:
        raise RuntimeError("could not allocate session path")
    temporary = target + "." + uuid.uuid4().hex + ".create"
    try:
        shutil.copy2(SEED_DB, temporary)
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    finally:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
    SESSION_TRACES[session_id] = []
    return session_id, target

def close_state_session(session_id: str) -> bool:
    target = session_state_db(session_id)
    if target is None or not os.path.isfile(target):
        return False
    for suffix in ("", *SQLITE_RESET_SIDECARS):
        try:
            os.remove(target + suffix)
        except FileNotFoundError:
            pass
    SESSION_TRACES.pop(session_id, None)
    shutil.rmtree(trace_directory(session_id), ignore_errors=True)
    return True

def clear_state_sidecars() -> None:
    state_db = current_state_db()
    for suffix in SQLITE_RESET_SIDECARS:
        try:
            os.remove(state_db + suffix)
        except FileNotFoundError:
            pass

def reset_state_database() -> None:
    """Atomically restore the immutable seed and discard SQLite sidecars."""
    state_db = current_state_db()
    reset_path = state_db + "." + uuid.uuid4().hex + ".reset"
    clear_state_sidecars()
    try:
        shutil.copy2(SEED_DB, reset_path)
        os.replace(reset_path, state_db)
    finally:
        try:
            os.remove(reset_path)
        except FileNotFoundError:
            pass
        clear_state_sidecars()

def record_trace(entry: dict) -> None:
    """Keep the trace in memory AND export it to traces/<id>.json."""
    current_traces().append(entry)
    temporary = None
    try:
        session_id = REQUEST_SESSION_ID.get()
        trace_dir = trace_directory(session_id)
        os.makedirs(trace_dir, exist_ok=True)
        target = os.path.join(trace_dir, f"{entry.get('id', 'trace')}.json")
        temporary = target + "." + uuid.uuid4().hex + ".write"
        with open(temporary, "w", encoding="utf-8") as f:
            json.dump(entry, f, default=str, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, target)
    except Exception:
        pass
    finally:
        if temporary:
            try:
                os.remove(temporary)
            except FileNotFoundError:
                pass

def load_world() -> dict:
    with open(WORLD_PATH) as f:
        return json.load(f)

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(current_state_db())
    conn.row_factory = sqlite3.Row
    return conn

def public_table_names() -> list[str]:
    """Expose only customer-world tables declared by the sealed manifest.

    Generated tools use the private _forge_actions ledger for execution and
    verifier evidence. It is deliberately retained in SQLite snapshots, but it
    is not a company-data table and must not leak into the public state panel.
    """
    return [
        str(table.get("name")) for table in load_world().get("tables", [])
        if isinstance(table, dict) and table.get("name")
    ]

def table_info(conn: sqlite3.Connection) -> list[dict]:
    tables = []
    for name in public_table_names():
        count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        tables.append({"name": name, "row_count": count})
    return tables

def sample_rows(conn: sqlite3.Connection, table_name: str, limit: int = 20) -> list[dict]:
    if table_name not in set(public_table_names()):
        return [{"error": "table not found"}]
    try:
        rows = conn.execute(f'SELECT * FROM "{table_name}" LIMIT ?', (limit,)).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]

def snapshot(db_path: str) -> dict:
    """Dump every table's rows keyed by rowid — the before/after state the verifier compares."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    out = {}
    try:
        for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
            rows = {}
            for row in conn.execute(f'SELECT rowid AS _bf_rowid_, * FROM "{name}"'):
                d = dict(row)
                rid = d.pop("_bf_rowid_")
                rows[rid] = d
            out[name] = rows
    finally:
        conn.close()
    return out

def compute_diff(before: dict, after: dict) -> list[dict]:
    """Row-level diff between two snapshots produced by snapshot()."""
    diff = []
    for table in sorted(set(before) | set(after)):
        b = before.get(table, {})
        a = after.get(table, {})
        for rid in sorted(set(b) | set(a)):
            rb = b.get(rid)
            ra = a.get(rid)
            if rb == ra:
                continue
            op = "insert" if rb is None else ("delete" if ra is None else "update")
            row_id = (ra or rb or {}).get("id", rid)
            diff.append({"table": table, "row_id": str(row_id), "operation": op, "before": rb, "after": ra})
            if len(diff) >= 200:
                return diff
    return diff

REPLAY_VOLATILE_INSERT_COLUMNS = {"created_at", "updated_at", "modified_at"}

def _quoted_sql_identifier(value: str) -> str:
    return '"' + str(value).replace('"', '""') + '"'

def stabilize_measured_insert_clock(expected_step: dict | None, execution: dict) -> None:
    """Reproduce captured database-clock values for measured task replay only.

    Generated insert capabilities legitimately use SQLite's live clock. A later
    portable replay must nevertheless reproduce the original row patch and any
    downstream read of that row. Reconcile ONLY volatile timestamp columns on
    a newly inserted row after proving that table, row id, operation, and every
    nonvolatile column match the real execution. Direct MCP calls never enter
    this path, and any substantive mismatch remains visible to replay parity.
    """
    if not isinstance(expected_step, dict) or not execution.get("ok"):
        return
    expected_diffs = expected_step.get("state_diffs")
    actual_diffs = execution.get("db_diff")
    if not isinstance(expected_diffs, list) or not isinstance(actual_diffs, list):
        return

    updates = []
    for expected in expected_diffs:
        if not isinstance(expected, dict) or expected.get("field") != "_inserted":
            continue
        expected_after = expected.get("after")
        if not isinstance(expected_after, dict) or "id" not in expected_after:
            continue
        table = str(expected.get("table") or "")
        row_id = str(expected.get("row_id") or expected_after.get("id") or "")
        actual = next((candidate for candidate in actual_diffs
                       if isinstance(candidate, dict)
                       and candidate.get("operation") == "insert"
                       and str(candidate.get("table") or "") == table
                       and str(candidate.get("row_id") or "") == row_id), None)
        actual_after = actual.get("after") if isinstance(actual, dict) else None
        if not isinstance(actual_after, dict) or actual_after.get("id") != expected_after.get("id"):
            continue
        volatile = {
            column: expected_after[column]
            for column in REPLAY_VOLATILE_INSERT_COLUMNS
            if column in expected_after
            and column in actual_after
            and actual_after[column] != expected_after[column]
        }
        if not volatile:
            continue
        expected_stable = {
            key: value for key, value in expected_after.items()
            if key not in REPLAY_VOLATILE_INSERT_COLUMNS
        }
        actual_stable = {
            key: value for key, value in actual_after.items()
            if key not in REPLAY_VOLATILE_INSERT_COLUMNS
        }
        if actual_stable != expected_stable:
            continue
        updates.append((table, expected_after["id"], volatile))

    if not updates:
        return
    allowed_tables = set(public_table_names())
    connection = sqlite3.connect(current_state_db())
    try:
        for table, row_id, volatile in updates:
            if table not in allowed_tables:
                continue
            table_sql = _quoted_sql_identifier(table)
            columns = {
                str(row[1]) for row in connection.execute(
                    f"PRAGMA table_info({table_sql})"
                ).fetchall()
            }
            if "id" not in columns or any(column not in columns for column in volatile):
                continue
            assignments = ", ".join(
                f"{_quoted_sql_identifier(column)} = ?" for column in sorted(volatile)
            )
            values = [volatile[column] for column in sorted(volatile)]
            values.append(row_id)
            connection.execute(
                f"UPDATE {table_sql} SET {assignments} WHERE {_quoted_sql_identifier('id')} = ?",
                values,
            )
        connection.commit()
    finally:
        connection.close()

def execute_tool(world: dict, tool_name: str, args: dict) -> dict:
    """Run the tool's REAL generated Python source against state.db, mirroring
    the product runtime's canonical generated-Python isolation boundary exactly:
      - Compatibility shims for _connect()/_audit() style sources
      - inspect.signature: drop unexpected kwargs unless **kwargs present
      - Coerce string → int/float for declared numeric parameters
      - Inject db_path when the function signature requests it
      - Row-level DB diff from before/after snapshots
    """
    tool = next((t for t in world.get("tools", [])
                 if tool_name in (t.get("name"), t.get("mcp_name"))), None)
    if not tool:
        return {"ok": False, "tool": tool_name, "error": f"tool '{tool_name}' not found"}
    executable_name = tool["name"]
    argument_error = validate_tool_args(tool, args)
    if argument_error:
        return {
            "ok": False,
            "tool": executable_name,
            "requested_tool": tool_name,
            "result": argument_error,
            "mutated": False,
            "db_diff": [],
            "error": argument_error["code"],
        }
    src = tool.get("source") or ""
    if f"def {executable_name}" not in src:
        return {"ok": False, "tool": tool_name, "error": "tool has no executable source"}

    state_db = current_state_db()
    before = snapshot(state_db)
    execution = execute_generated_tool(src, executable_name, state_db, args)
    if not execution.get("ok"):
        return {
            "ok": False,
            "tool": executable_name,
            "requested_tool": tool_name,
            "result": execution.get("result"),
            "mutated": False,
            "db_diff": [],
            "error": execution.get("error"),
        }
    after = snapshot(state_db)
    diff = compute_diff(before, after)
    return {
        "ok": True,
        "tool": executable_name,
        "requested_tool": tool_name,
        "result": execution.get("result"),
        "mutated": len(diff) > 0,
        "db_diff": diff,
        "error": None,
    }

def harvest_context(ctx: dict, tool_name: str, result: dict) -> None:
    """Thread ids and quantities discovered by one tool into args for the next step.
    Mirrors harvestContext() in sandboxAgent.ts."""
    if not isinstance(result, dict):
        return
    # Direct scalar ids returned by write tools (e.g. pack_package → package_id)
    for k in ("package_id", "shipment_id", "po_id", "invoice_id", "driver_id", "inventory_id"):
        if k in result and result[k] is not None:
            ctx[k] = result[k]
    # First-row ids from read results (rows / orders / drivers / invoices / items)
    rows = None
    for key in ("orders", "rows", "drivers", "invoices", "items"):
        v = result.get(key)
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            rows = v
            break
    if rows:
        first = rows[0]
        if first.get("id") is not None:
            ctx["last_read_id"] = first["id"]
        if tool_name == "find_purchase_orders" or "purchase_order" in tool_name:
            ctx["po_id"] = first.get("id", ctx.get("po_id"))
            ctx["po_number"] = first.get("po_number")
        elif "driver" in tool_name:
            ctx["driver_id"] = first.get("id", ctx.get("driver_id"))
        elif "inventory" in tool_name or "stock" in tool_name:
            ctx["inventory_id"] = first.get("id", ctx.get("inventory_id"))
            qty = first.get("quantity_available") or first.get("quantity_on_hand") or 1
            ctx["reserve_qty"] = max(1, min(3, int(qty)))
    if tool_name == "create_shipment" and result.get("shipment_id") is not None:
        ctx["shipment_id"] = result["shipment_id"]
    if tool_name == "pack_package" and result.get("package_id") is not None:
        ctx["package_id"] = result["package_id"]

def delegation_request_for_tool(tool: dict, prompt_lower: str) -> str:
    """Translate an end-user request into the declared delegation grammar.

    Records agents are read-only, so forwarding an update sentence to them is
    both semantically wrong and rejected by their parser. Workflow agents need
    the original mutation intent. Resolve the shared entity handle once, then
    give each sub-agent the operation it can actually perform.
    """
    target_tables = sorted(
        [str(name) for name in (tool.get("target_tables") or []) if name],
        key=len,
        reverse=True,
    )
    table_name = next((name for name in target_tables if name.lower() in prompt_lower), None)
    handle = re.search(r'\bfind\s+([a-z][a-z0-9_]*)\s+"([^"]+)"', prompt_lower)
    if not table_name or not handle:
        return prompt_lower

    field, value = handle.group(1), handle.group(2)
    prefix = f'in table {table_name}, find {field} "{value}"'
    if tool.get("type") == "read" or tool.get("name", "").endswith("_records_agent"):
        return prefix + " and return the complete record."
    if any(phrase in prompt_lower for phrase in (
        "next declared lifecycle", "next lifecycle", "advance", "progress to the next",
    )):
        return prefix + " and set status to the next declared lifecycle stage."
    return prompt_lower if prompt_lower.startswith("in table ") else "in table " + prompt_lower[3:] if prompt_lower.startswith("in ") else prompt_lower

OPAQUE_ENTITY_ID_RE = re.compile(r"\b[a-z][a-z0-9_-]*[_-]\d+\b")

def prompt_entity_id(prompt_lower: str) -> str | None:
    match = OPAQUE_ENTITY_ID_RE.search(prompt_lower or "")
    return match.group(0) if match else None

def build_args_for_tool(tool: dict, ctx: dict, prompt_lower: str) -> dict:
    """Build best-effort call args for a tool using the planner context.
    Mirrors the buildArgs lambdas in planToolChain() / planGeneric() in sandboxAgent.ts."""
    name = tool.get("name", "")
    tp = tool.get("type", "read")
    raw_parameters = tool.get("parameters") if isinstance(tool.get("parameters"), dict) else {}
    shallow_parameters = raw_parameters.get("properties", {}) if raw_parameters.get("type") == "object" else raw_parameters
    schema_candidate = tool.get("input_schema") or tool.get("inputSchema")
    input_schema = schema_candidate if isinstance(schema_candidate, dict) else {}
    schema_parameters = input_schema.get("properties") if isinstance(input_schema.get("properties"), dict) else {}
    required_parameters = {
        str(key) for key in (input_schema.get("required") or []) if isinstance(key, str)
    }
    has_canonical_schema = bool(schema_parameters)
    # Compatibility maps intentionally collapse schemas to {name: type}. The
    # exported agent must prefer the canonical JSON Schema so enum constraints
    # and numeric types survive argument synthesis.
    parameters = dict(shallow_parameters)
    parameters.update(schema_parameters)

    def include_parameter(key: str, spec) -> bool:
        if not has_canonical_schema or key in required_parameters:
            return True
        lowered = key.lower()
        detail = spec if isinstance(spec, dict) else {"type": spec}
        enum = detail.get("enum") if isinstance(detail.get("enum"), list) else []
        if lowered in ("limit", "page_size", "pagesize", "per_page"):
            return tp == "read"
        if lowered == "request" or "query" in lowered or lowered in ("q", "search"):
            return True
        if lowered == "id" or lowered.endswith("_id") or lowered.endswith("id"):
            return key in ctx or "last_read_id" in ctx or prompt_entity_id(prompt_lower) is not None
        if enum:
            value_requested = any(str(value).lower() in prompt_lower for value in enum)
            field_requested = lowered == "status" or lowered.replace("_", " ") in prompt_lower
            return value_requested and field_requested
        return lowered.replace("_", " ") in prompt_lower

    def inferred_value(key: str, spec):
        lowered = key.lower()
        detail = spec if isinstance(spec, dict) else {"type": spec}
        enum = detail.get("enum") if isinstance(detail.get("enum"), list) else []
        if lowered == "request":
            return delegation_request_for_tool(tool, prompt_lower)
        if lowered in ("limit", "page_size", "pagesize", "per_page"):
            return 5
        if lowered == "id" or lowered.endswith("_id") or lowered.endswith("id"):
            return ctx.get(key, ctx.get("last_read_id", prompt_entity_id(prompt_lower) or 1))
        if lowered == "status":
            for value in enum:
                if str(value).lower() in prompt_lower:
                    return value
            match = re.search(r"\b(?:to|as)\s+([a-z][a-z0-9_-]*)", prompt_lower)
            if match:
                return match.group(1)
            return enum[0] if enum else "active"
        if enum:
            return enum[0]
        kind = str(detail.get("type", "string")).lower()
        if kind in ("integer", "number"):
            return 1
        if kind == "boolean":
            return False
        if "query" in lowered or lowered in ("q", "search"):
            return prompt_lower[:120]
        if "token" in lowered or "cursor" in lowered:
            return "1"
        if lowered in ("owner", "repo", "account", "user"):
            return "blobfish"
        return ctx.get(key, "default")

    if tp == "read":
        args = {}
        for key, spec in parameters.items():
            if include_parameter(key, spec):
                args[key] = inferred_value(key, spec)
        return args
    # Write tools — dependency-ordered args
    did = ctx.get("last_read_id", ctx.get("po_id", 1))
    if "pack" in name:
        return {"po_id": ctx.get("po_id", did), "contents": "Order items", "weight_kg": 5.0, "size": "medium"}
    if "assign_driver" in name:
        return {"driver_id": ctx.get("driver_id", 1), "shipment_id": ctx.get("shipment_id", did)}
    if "create_shipment" in name:
        return {"package_id": ctx.get("package_id", did), "destination": "100 Main St, Chicago IL", "carrier_type": "ground"}
    if "update_po" in name or ("update" in name and "po" in name):
        new_status = "shipped" if "ship" in prompt_lower else "packed"
        return {"po_id": ctx.get("po_id", did), "new_status": new_status}
    if "reserve" in name:
        return {"inventory_id": ctx.get("inventory_id", did), "quantity": ctx.get("reserve_qty", 1)}
    if "reconcile" in name:
        return {"invoice_id": ctx.get("invoice_id", ctx.get("last_read_id", did)), "amount_cents": 50000, "method": "wire"}
    if "estimate" in name:
        return {"shipment_id": ctx.get("shipment_id", did)}
    # Generic fallback: satisfy the declared contract instead of guessing a
    # universal id argument. Generated tools commonly use claim_id,
    # access_review_id, status, cursor, and other required names.
    args: dict = {}
    for key, spec in parameters.items():
        if include_parameter(key, spec):
            args[key] = inferred_value(key, spec)
    return args

TOOL_STOP_WORDS = {
    "a", "an", "and", "answer", "available", "before", "data", "for", "from",
    "get", "inspect", "into", "list", "of", "one", "record", "records", "state",
    "style", "summarize", "the", "this", "tool", "tools", "use", "with", "world",
}

READ_ONLY_PHRASES = (
    "do not change", "don't change", "without changing", "no changes",
    "do not modify", "don't modify", "do not update", "don't update",
    "read only", "read-only",
)

# Generated composite worlds intentionally expose a primary business resource
# beside its audit, evidence, review, remediation, and history projections.
# Those projections repeat the resource noun in both their tool name and table
# name, which otherwise lets a generic request such as "list litigation cases"
# outrank the primary cases list. They remain first-class when the user asks for
# the projection explicitly.
AUXILIARY_PROJECTION_TOKENS = {
    "audit", "event", "evidence", "history", "remediation", "review",
}

def prompt_is_read_only(prompt_lower: str) -> bool:
    return any(phrase in prompt_lower for phrase in READ_ONLY_PHRASES)

def prompt_requests_mutation(prompt_lower: str) -> bool:
    if prompt_is_read_only(prompt_lower):
        return False
    return bool(lexical_tokens(prompt_lower) & {
        "advance", "approve", "assign", "bind", "cancel", "change", "close",
        "create", "delete", "file", "mark", "modify", "move", "mutate",
        "open", "progress", "promote", "reject", "send", "set", "settle",
        "submit", "transition", "update",
    })

def lexical_tokens(value: str) -> set[str]:
    result = set()
    for token in re.findall(r"[a-z0-9]+", (value or "").lower()):
        if len(token) < 3 or token in TOOL_STOP_WORDS:
            continue
        result.add(token)
        if token.endswith("ies") and len(token) > 4:
            result.add(token[:-3] + "y")
        elif token.endswith("s") and not token.endswith("ss") and len(token) > 3:
            result.add(token[:-1])
    return result

def tool_relevance(tool: dict, prompt_tokens: set[str]) -> int:
    name_tokens = lexical_tokens(tool.get("name", ""))
    table_tokens = lexical_tokens(" ".join(tool.get("target_tables") or []))
    description_tokens = lexical_tokens(tool.get("description", ""))
    unrequested_projection_tokens = (
        (name_tokens | table_tokens) & AUXILIARY_PROJECTION_TOKENS
    ) - prompt_tokens
    return (
        8 * len(prompt_tokens & table_tokens)
        + 5 * len(prompt_tokens & name_tokens)
        + len(prompt_tokens & description_tokens)
        - 12 * len(unrequested_projection_tokens)
    )

def plan_tool_chain(world: dict, prompt_lower: str) -> list[dict]:
    """Build a dependency-ordered read→write tool sequence from the world's tools
    and the user's intent. Mirrors planToolChain() / planGeneric() in sandboxAgent.ts."""
    tools = world.get("tools", [])
    by_name = {t["name"]: t for t in tools}
    is_logistics = "find_purchase_orders" in by_name or "pack_package" in by_name

    if not is_logistics:
        # Generic: rank exact business nouns in table/name ahead of prose.
        # Common words such as "state", "world", and "available" previously
        # made unrelated Google/Calendar tools tie with an insurance claim tool.
        reads = [t for t in tools if t.get("type") == "read"]
        writes = [t for t in tools if t.get("type") == "write"]
        relevance_text = prompt_lower
        for phrase in READ_ONLY_PHRASES:
            relevance_text = relevance_text.replace(phrase, " ")
        prompt_tokens = lexical_tokens(relevance_text)
        def ranked(candidates):
            scored = [(tool_relevance(tool, prompt_tokens), tool) for tool in candidates]
            return [(score, tool) for score, tool in sorted(scored, key=lambda item: (-item[0], item[1]["name"])) if score >= 5]
        read_scores = ranked(reads)
        write_scores = ranked(writes)
        if read_scores:
            read_floor = max(5, read_scores[0][0] - 3)
            rel_reads = [tool for score, tool in read_scores if score >= read_floor][:3]
        else:
            rel_reads = []
        # An explicit entity id calls for one precise get/retrieve operation,
        # not a broad list plus several loosely related reads.
        if prompt_entity_id(prompt_lower):
            exact_reads = [tool for tool in rel_reads if tool.get("name", "").endswith("_get") or "retrieve" in tool.get("description", "").lower()]
            if exact_reads:
                rel_reads = exact_reads[:1]
        elif re.search(r"\b(?:all|find|list|search|show|which)\b", prompt_lower):
            collection_reads = [
                tool for tool in rel_reads
                if tool.get("name", "").endswith("_list")
                or tool.get("name", "").startswith(("find_", "list_", "search_"))
            ]
            if collection_reads:
                rel_reads = collection_reads[:3]
        if write_scores:
            write_floor = max(5, write_scores[0][0] - 3)
            rel_writes = [tool for score, tool in write_scores if score >= write_floor][:2]
        else:
            rel_writes = []
        write_intent = prompt_requests_mutation(prompt_lower)
        chosen = rel_reads + (rel_writes if write_intent else [])
        return chosen[:8]

    # Logistics world — intent-aware tool selection
    wantPack = any(w in prompt_lower for w in ["pack", "packing"])
    wantShipment = any(w in prompt_lower for w in ["shipment", "dispatch", "ship"])
    wantDriver = any(w in prompt_lower for w in ["driver", "assign", "courier"])
    wantInventory = any(w in prompt_lower for w in ["invent", "stock", "reserve"])
    wantInvoice = any(w in prompt_lower for w in ["invoice", "reconcile", "payment"])
    wantMarkShipped = any(w in prompt_lower for w in ["mark", "update", "set"]) and "ship" in prompt_lower

    plan = []
    def push(name):
        t = by_name.get(name)
        if t: plan.append(t)

    push("find_purchase_orders")
    if wantPack or wantInventory or wantShipment: push("check_inventory")
    if wantDriver or wantShipment: push("find_available_drivers")
    if wantPack: push("pack_package")
    if wantMarkShipped: push("update_po_status")
    if wantShipment: push("create_shipment")
    if wantDriver: push("assign_driver")
    if wantMarkShipped: push("update_po_status")
    if wantInventory: push("reserve_inventory")
    if wantInvoice:
        push("lookup_invoice")
        push("reconcile_payment")
    # Always do at least one write if only find_purchase_orders was selected
    if len(plan) <= 1 and "pack_package" in by_name:
        push("pack_package")
    return plan[:12]

def run_heuristic_agent(world: dict, message: str) -> dict:
    """Deterministic tool-calling agent — mirrors runHeuristicAgentSqlite() in
    sandboxAgent.ts. No LLM required; produces a genuine read→write trajectory
    that mutates state.db and returns live state-diffs.

    Returns a trajectory dict identical in shape to the LLM path:
      {id, provider, model, prompt, steps, final_answer, passed, reward,
       initial_state, final_state, state_changes, verifier}
    """
    prompt_lower = message.lower()
    plan = plan_tool_chain(world, prompt_lower)
    ctx: dict = {}
    steps = []
    initial = snapshot(current_state_db())
    MAX_STEPS = 12

    def explicitly_retryable(result: dict) -> bool:
        receipt = result.get("result")
        if isinstance(receipt, dict) and receipt.get("retryable") is True:
            return True
        error = result.get("error")
        return isinstance(error, dict) and error.get("retryable") is True

    for tool in plan:
        if len(steps) >= MAX_STEPS:
            break
        args = build_args_for_tool(tool, ctx, prompt_lower)
        attempts = [execute_tool(world, tool["name"], args)]
        if (not attempts[0].get("ok") and explicitly_retryable(attempts[0])
                and len(steps) + 1 < MAX_STEPS):
            # Retry exactly once with byte-equivalent arguments. Semantic
            # validation errors are never retried; only an explicit
            # environment receipt can open this recovery route.
            attempts.append(execute_tool(world, tool["name"], args))
        verb = "inspect" if tool.get("type") == "read" else "modify"
        tables = ", ".join(tool.get("target_tables") or ["data"])
        for attempt_index, res in enumerate(attempts):
            if res.get("ok"):
                harvest_context(ctx, tool["name"], res.get("result") or {})
            retry_prefix = "Retry" if attempt_index else "Execute"
            retry_reason = " after an explicit retryable environment failure" if attempt_index else ""
            steps.append({
                "step": len(steps) + 1,
                "thought": f"{retry_prefix} {tool['name']} to {verb} {tables}{retry_reason}.",
                "tool": tool["name"],
                "arguments": args,
                "observation": json.dumps(res.get("result", {}), default=str)[:800],
                "ok": res.get("ok", False),
                "error": res.get("error"),
                "db_diff": res.get("db_diff", []),
            })

    final = snapshot(current_state_db())
    diff = compute_diff(initial, final)

    # Collect all field-level state changes for the caller
    state_changes = []
    for d in diff:
        if d["operation"] == "update" and d["before"] and d["after"]:
            for k in d["after"]:
                if str(d["before"].get(k)) != str(d["after"].get(k)):
                    state_changes.append({"table": d["table"], "row_id": d["row_id"],
                                          "field": k, "before": d["before"].get(k), "after": d["after"].get(k)})
        elif d["operation"] == "insert":
            state_changes.append({"table": d["table"], "row_id": d["row_id"],
                                  "field": "_inserted", "before": None, "after": d["after"]})

    # Inline verifier — same assertions as sandboxAgent.ts runVerifier()
    tool_type_map = {t["name"]: t.get("type") for t in world.get("tools", [])}
    # A failed read is not inspection evidence. Behavioral ordering uses only
    # successful calls; the full step list still feeds all_tools_succeeded.
    successful_steps = [s for s in steps if s.get("ok")]
    tool_names = [s["tool"] for s in successful_steps]
    called_reads = [n for n in tool_names if tool_type_map.get(n) == "read"]
    called_writes = [n for n in tool_names if tool_type_map.get(n) == "write"]
    mutated_count = len([s for s in steps if s.get("db_diff")])
    company = world.get("thesis", {}).get("company", "this world")

    def observation_summary(step: dict) -> str:
        try:
            payload = json.loads(step.get("observation") or "{}")
        except Exception:
            payload = {}
        rows = None
        if isinstance(payload, dict):
            for key in ("rows", "items", "orders", "results"):
                if isinstance(payload.get(key), list):
                    rows = payload[key]
                    break
        if rows and isinstance(rows[0], dict):
            values = [f"{key}={value}" for key, value in rows[0].items()
                      if isinstance(value, (str, int, float, bool))][:8]
            return f"{step['tool']} returned " + ", ".join(values)
        if isinstance(payload, dict):
            values = [f"{key}={value}" for key, value in payload.items()
                      if isinstance(value, (str, int, float, bool))][:8]
            if values:
                return f"{step['tool']} returned " + ", ".join(values)
        return f"{step['tool']} completed successfully"

    if state_changes:
        final_answer = (
            f"{company}: completed {len(state_changes)} verified state change"
            f"{'s' if len(state_changes) != 1 else ''} using {', '.join(tool_names)}."
        )
    elif successful_steps:
        summaries = [observation_summary(step) for step in successful_steps[:3]]
        final_answer = f"{company}: {'; '.join(summaries)}. No database state was changed."
    elif steps:
        errors = [f"{step['tool']}: {step.get('error') or 'failed'}" for step in steps]
        final_answer = f"No tool call succeeded: {'; '.join(errors[:3])}."
    else:
        final_answer = "No sufficiently relevant executable tool was found for this request."

    assertions = []

    def chk(name, passed, details):
        assertions.append({"name": name, "passed": passed, "details": details})

    state_changed = bool(diff)
    requires_state_change = prompt_requests_mutation(prompt_lower)
    if requires_state_change:
        chk("state_changed", state_changed,
            "world state changed" if state_changed else "NO state change — requested mutation was not completed")
    else:
        chk("read_only_state_preserved", not state_changed,
            "read-only request preserved world state" if not state_changed else "READ-ONLY request unexpectedly changed world state")

    reads_first = bool(called_reads) and (
        not called_writes or tool_names.index(called_reads[0]) < tool_names.index(called_writes[0])
    )
    chk("reads_before_writes", reads_first,
        f"{len(called_reads)} reads, {len(called_writes)} writes, read_first={reads_first}")

    shortcut = bool(called_writes) and not called_reads
    chk("no_shortcut", not shortcut,
        "SHORTCUT: wrote without reading" if shortcut else "inspected data before modifying")

    ok_n = sum(1 for s in steps if s.get("ok"))
    chk("all_tools_succeeded", len(steps) > 0 and ok_n * 5 >= len(steps) * 4,
        f"{ok_n}/{len(steps)} succeeded")

    failed = [a["name"] for a in assertions if not a["passed"]]
    # Reward semantics must match the hosted verifier: behavioral checks
    # grant NO credit, and anti-hack behaviors (shortcut writes, skipped
    # reads) VETO the reward to 0. Global tool-call success stays diagnostic:
    # optional/exploratory failures do not erase a correct task outcome.
    _BEHAVIORAL = {"state_changed", "read_only_state_preserved", "reads_before_writes", "no_shortcut", "all_tools_succeeded"}
    _ANTI_HACK = {"reads_before_writes", "no_shortcut"}
    _ADVISORY = {"all_tools_succeeded"}
    core = [a for a in assertions if a["name"] not in _BEHAVIORAL]
    core_failed = [a for a in core if not a["passed"]]
    anti_hack_failed = [a for a in assertions if a["name"] in _ANTI_HACK and not a["passed"]]
    advisory_failed = [a for a in assertions if a["name"] in _ADVISORY and not a["passed"]]
    structural_failed = [name for name in failed if name not in _ADVISORY]
    if anti_hack_failed:
        reward = 0.0
    elif core:
        reward = (len(core) - len(core_failed)) / len(core)
    else:
        reward = 0.0 if structural_failed else 1.0

    verifier = {
        "passed": len(structural_failed) == 0,
        "reward": round(reward, 4),
        "assertions": assertions,
        "failed_conditions": structural_failed,
        "advisory_conditions": [a["name"] for a in advisory_failed],
        "explanation": ("All task checks passed" + (f"; advisory: {', '.join(a['name'] for a in advisory_failed)}" if advisory_failed else "")) if not structural_failed else f"Failed: {', '.join(structural_failed)}",
    }

    return {
        "id": f"traj_{uuid.uuid4().hex[:12]}",
        "provider": "heuristic",
        "model": "heuristic-planner",
        "prompt": message,
        "steps": steps,
        "final_answer": final_answer,
        "passed": verifier["passed"],
        "reward": verifier["reward"],
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "initial_state": {t: list(rows.values()) for t, rows in initial.items()},
        "final_state": {t: list(rows.values()) for t, rows in final.items()},
        "state_changes": state_changes,
        "verifier": verifier,
    }

def compact_public_trajectory(trajectory: dict) -> dict:
    """Keep causal chat evidence without returning two full database copies."""
    public = dict(trajectory)
    initial = public.pop("initial_state", None)
    final = public.pop("final_state", None)
    if initial is not None:
        public["initial_state_digest"] = hashlib.sha256(
            json.dumps(initial, sort_keys=True, separators=(",", ":"), default=str).encode()
        ).hexdigest()
    if final is not None:
        public["final_state_digest"] = hashlib.sha256(
            json.dumps(final, sort_keys=True, separators=(",", ":"), default=str).encode()
        ).hexdigest()
    return public

def infer_args(tool: dict, discovered: dict) -> dict:
    """Best-effort arguments for the /task/{id}/run reference rollout."""
    if tool.get("type") == "read":
        return {"limit": 5}
    n = tool["name"]
    did = discovered.get("id", 1)
    if "pack" in n: return {"po_id": discovered.get("po_id", did), "contents": "items", "weight_kg": 5.0, "size": "medium"}
    if "assign_driver" in n: return {"driver_id": discovered.get("driver_id", 1), "shipment_id": discovered.get("shipment_id", did)}
    if "create_shipment" in n: return {"package_id": discovered.get("package_id", did), "destination": "1 Main St", "carrier_type": "ground"}
    if "update_po" in n: return {"po_id": discovered.get("po_id", did), "new_status": "picking"}
    if "reserve" in n: return {"inventory_id": discovered.get("inventory_id", did), "quantity": 1}
    if "reconcile" in n: return {"invoice_id": discovered.get("invoice_id", did), "amount_cents": 1, "method": "wire"}
    if "estimate" in n: return {"shipment_id": discovered.get("shipment_id", did)}
    return {"id": did}

def absorb_ids(discovered: dict, tool: dict, result: dict) -> None:
    """Thread ids produced/read by one tool into args for the next (reference rollout)."""
    if not isinstance(result, dict):
        return
    for k in ("package_id", "shipment_id", "po_id", "invoice_id", "driver_id", "inventory_id"):
        if k in result:
            discovered[k] = result[k]
    rows = result.get("rows") or result.get("orders") or result.get("drivers") or result.get("invoices") or []
    if rows and isinstance(rows[0], dict) and rows[0].get("id") is not None:
        rid = rows[0]["id"]
        discovered["id"] = rid
        keymap = {"purchase_orders": "po_id", "drivers": "driver_id", "inventory": "inventory_id",
                  "invoices": "invoice_id", "packages": "package_id", "shipments": "shipment_id"}
        for tbl in tool.get("target_tables", []):
            discovered[keymap.get(tbl, "id")] = rid

def task_reference_plan(world: dict, task: dict) -> tuple[list[dict], dict | None]:
    """Prefer the exact, measured provider trajectory packaged with the world.

    Generated task metadata does not guarantee that required_tools is in execution
    order, while the accepted trajectory contains the actual tool/argument sequence.
    Replaying that sequence makes the portable runtime reproduce the measured gym
    behavior instead of inventing placeholder arguments.
    """
    task_id = task.get("task_id")
    measured = next((trajectory for trajectory in world.get("trajectories", [])
                     if trajectory.get("task_id") == task_id
                     and isinstance(trajectory.get("steps"), list)), None)
    if measured is not None:
        plan = []
        for step in measured.get("steps", []):
            tool_name = step.get("tool") or step.get("tool_name")
            if not tool_name:
                continue
            args = step.get("arguments") if isinstance(step.get("arguments"), dict) else step.get("args")
            plan.append({
                "tool": tool_name,
                "args": args if isinstance(args, dict) else {},
                "captured_step": step,
            })
        # A model response that emitted no tool call is still an authoritative
        # measured trajectory. Preserve its empty plan and final answer so a
        # failed zero-tool episode cannot silently become a reference rollout.
        return plan, measured

    plan = []
    for tool_name in task.get("required_tools", []):
        plan.append({"tool": tool_name})
    return plan, None

def verifier_trace_from_steps(steps: list, final_answer=None) -> list:
    """Rebuild the lossless public verifier trace from stored task steps.

    /task and a later /verify call must grade the same evidence. Preserve the
    exact arguments, observation, requested tool alias, and structured error;
    future VCode is allowed to inspect any of those fields.
    """
    trace = []
    for step in steps:
        args = step.get("args") if isinstance(step.get("args"), dict) else step.get("arguments")
        observation = step.get("result") if "result" in step else step.get("observation")
        trace.append({
            "tool": step.get("tool"),
            "requested_tool": step.get("requested_tool"),
            "arguments": args if isinstance(args, dict) else {},
            "observation": observation,
            "ok": step.get("ok", False),
            "error": step.get("error"),
        })
    if final_answer is not None:
        trace.append({
            "tool": "_final_answer",
            "arguments": {"answer": final_answer},
            "observation": None,
            "ok": True,
        })
    return trace

def run_task(world: dict, task_id: str) -> dict:
    task = next((candidate for candidate in world.get("tasks", [])
                 if candidate.get("task_id") == task_id), None)
    if not task:
        return {"error": "task not found", "task_id": task_id}

    initial = snapshot(current_state_db())
    steps = []
    discovered: dict = {}
    plan, measured = task_reference_plan(world, task)
    for i, planned in enumerate(plan, 1):
        tool_name = planned["tool"]
        tool = resolve_mcp_tool(world, tool_name)
        args = (planned.get("args") if isinstance(planned.get("args"), dict)
                else (infer_args(tool, discovered) if tool else {}))
        result = execute_tool(world, tool_name, args)
        stabilize_measured_insert_clock(planned.get("captured_step"), result)
        absorb_ids(discovered, tool or {}, result.get("result") or {})
        steps.append({
            "step": i,
            "tool": (tool or {}).get("name") or tool_name,
            "requested_tool": tool_name,
            "args": args,
            "ok": result.get("ok", False),
            "mutated": result.get("mutated", False),
            "result": result.get("result"),
            "error": result.get("error"),
        })

    final = snapshot(current_state_db())
    # The measured final answer is part of the replayed artifact: answer-graded
    # verifiers read it from the "_final_answer" trace entry, so a replay that
    # executes every tool but drops the answer flips those tasks to failed.
    replayed_answer = measured.get("final_answer") if measured else None
    trace = verifier_trace_from_steps(steps, replayed_answer)
    verifier_result = run_verifier(world, task_id, initial, final, trace)
    trace_id = f"trace_{uuid.uuid4().hex[:12]}"
    trajectory = {
        "id": trace_id,
        "task_id": task_id,
        "prompt": task.get("prompt", ""),
        "steps": steps,
        "final_answer": replayed_answer,
        "verifier": verifier_result,
        "reward": verifier_result.get("reward", 0),
        "passed": verifier_result.get("passed", False),
        "replay": {
            "source": "measured_provider_trajectory" if measured else "required_tools_fallback",
            "provider": measured.get("provider") if measured else None,
            "model": measured.get("model") if measured else None,
            "original_trace_id": measured.get("id") if measured else None,
            "original_passed": measured.get("passed") if measured else None,
        },
    }
    record_trace({"id": trace_id, "type": "task_run", "task_id": task_id,
                  "trajectory": trajectory, "timestamp": time.time()})
    return trajectory

def run_verifier(world: dict, task_id: str, initial_state: dict, final_state: dict, trace: list) -> dict:
    """Run the task's REAL generated VCode verifier against real before/after
    snapshots — not a rubber stamp."""
    verifier = next((v for v in world.get("verifiers", []) if v["task_id"] == task_id), None)
    if not verifier or not verifier.get("vcode"):
        return {"task_id": task_id, "passed": False, "reward": 0.0, "error": "verifier not found", "assertions": []}
    return run_generated_verifier(
        verifier["vcode"], task_id, initial_state, final_state, trace
    )


def mcp_input_schema(tool: dict) -> dict:
    declared_schema = tool.get("input_schema")
    if isinstance(declared_schema, dict) and declared_schema.get("type") == "object":
        # Preserve the compiler's complete contract: lifecycle enums, required
        # fields, descriptions, and additionalProperties all matter to agents.
        return json.loads(json.dumps(declared_schema))
    type_map = {
        "int": "integer", "integer": "integer", "float": "number",
        "number": "number", "bool": "boolean", "boolean": "boolean",
        "list": "array", "array": "array", "object": "object",
    }
    raw_parameters = tool.get("parameters") or {}
    if isinstance(raw_parameters, dict) and raw_parameters.get("type") == "object":
        return json.loads(json.dumps(raw_parameters))
    properties = {}
    for name, declared in raw_parameters.items():
        normalized = str(declared).lower().replace("optional", "").strip(" []")
        properties[name] = {"type": type_map.get(normalized, "string")}
    return {"type": "object", "properties": properties, "additionalProperties": False}


def validate_tool_args(tool: dict, args) -> dict | None:
    if not isinstance(args, dict):
        return {
            "code": "validation_error",
            "message": "tool arguments must be a JSON object",
        }
    schema = mcp_input_schema(tool)
    required = schema.get("required") if isinstance(schema.get("required"), list) else []
    missing = [name for name in required if name not in args or args.get(name) is None]
    if missing:
        return {
            "code": "validation_error",
            "message": "missing required arguments: " + ", ".join(str(name) for name in missing),
            "missing": missing,
        }
    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    if schema.get("additionalProperties") is False:
        unexpected = sorted(str(name) for name in args if name not in properties)
        if unexpected:
            return {
                "code": "validation_error",
                "message": "unexpected arguments: " + ", ".join(unexpected),
                "unexpected": unexpected,
            }
    for name, value in args.items():
        detail = properties.get(name)
        if not isinstance(detail, dict) or not isinstance(detail.get("enum"), list):
            continue
        accepted = detail["enum"]
        if value not in accepted:
            return {
                "code": "invalid_enum_value",
                "message": f"invalid value for {name}: {value!r}; accepted values: {accepted!r}",
                "parameter": name,
                "accepted": accepted,
            }
    return None


def mcp_tool(tool: dict) -> dict:
    return {
        "name": tool.get("mcp_name") or tool["name"],
        "description": tool.get("description") or "",
        "inputSchema": mcp_input_schema(tool),
        "annotations": {
            "readOnlyHint": tool.get("type") == "read",
            "destructiveHint": False,
            "idempotentHint": tool.get("type") == "read",
            "openWorldHint": False,
            "blobfishAsset": tool.get("asset_namespace") or "core",
            "blobfishStateful": True,
        },
    }


def resolve_mcp_tool(world: dict, requested: str):
    return next((tool for tool in world.get("tools", [])
                 if requested in (tool.get("mcp_name"), tool.get("name"))), None)


class Handler(BaseHTTPRequestHandler):
    def _json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Key, Mcp-Session-Id, X-Blobfish-Session")
        session_id = REQUEST_SESSION_ID.get()
        if session_id:
            self.send_header("Mcp-Session-Id", session_id)
            self.send_header("X-Blobfish-Session", session_id)
        self.end_headers()
        self.wfile.write(body)

    def _reset_request_context(self) -> None:
        REQUEST_STATE_DB.set(None)
        REQUEST_SESSION_ID.set(None)

    def _authorized(self) -> bool:
        if not WORLD_API_KEY:
            return True
        supplied = self.headers.get("x-api-key", "").strip()
        return bool(supplied) and hmac.compare_digest(supplied, WORLD_API_KEY)

    def _select_session(self, require_session: bool = False) -> bool:
        if not self._authorized():
            self._json({"error": "unauthorized"}, 401)
            return False
        mcp_session = self.headers.get("mcp-session-id", "").strip()
        blobfish_session = self.headers.get("x-blobfish-session", "").strip()
        if mcp_session and blobfish_session and mcp_session != blobfish_session:
            self._json({"error": "conflicting_session_headers"}, 400)
            return False
        session_id = mcp_session or blobfish_session
        if not session_id:
            if require_session and WORLD_API_KEY:
                self._json({"error": "session_required", "create": "POST /sessions"}, 428)
                return False
            return True
        state_db = session_state_db(session_id)
        if state_db is None or not os.path.isfile(state_db):
            self._json({"error": "unknown_session", "session_id": session_id}, 404)
            return False
        try:
            os.utime(state_db, None)
        except FileNotFoundError:
            self._json({"error": "unknown_session", "session_id": session_id}, 404)
            return False
        REQUEST_STATE_DB.set(state_db)
        REQUEST_SESSION_ID.set(session_id)
        return True

    def _read_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            self._json({"error": "invalid Content-Length"}, 400)
            return None
        if length < 0:
            self._json({"error": "invalid Content-Length"}, 400)
            return None
        if length > MAX_REQUEST_BYTES:
            self._json({"error": "request body exceeds 1 MB"}, 413)
            return None
        if length == 0:
            return {}
        try:
            body = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json({"error": "request body must be valid JSON"}, 400)
            return None
        if not isinstance(body, dict):
            self._json({"error": "request body must be a JSON object"}, 400)
            return None
        return body

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Key, Mcp-Session-Id, X-Blobfish-Session")
        self.end_headers()

    def do_GET(self) -> None:
        self._reset_request_context()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        stateful = path in ("/tables", "/traces") or path.startswith("/tables/")
        if path != "/health" and not self._select_session(require_session=stateful):
            return

        if path == "/health":
            world = load_world()
            state_db = current_state_db()
            ok = os.path.exists(state_db) and os.path.exists(WORLD_PATH)
            self._json({"status": "healthy" if ok else "unhealthy", "world_id": world.get("world_id", ""), "job_id": world.get("job_id", ""), "world_hash": world.get("harbor", {}).get("world_hash", ""), "db_exists": os.path.exists(state_db), "session_id": REQUEST_SESSION_ID.get()}, 200 if ok else 503)
        elif path == "/world":
            world = load_world()
            self._json({
                "world_id": world.get("world_id", ""),
                "prompt": world.get("prompt", ""),
                "thesis": world.get("thesis", {}),
                "table_count": len(world.get("tables", [])),
                "tool_count": len(world.get("tools", [])),
                "task_count": len(world.get("tasks", [])),
                "verifier_count": len(world.get("verifiers", [])),
            })
        elif path == "/tables":
            conn = get_db()
            self._json({"tables": table_info(conn)})
            conn.close()
        elif path.startswith("/tables/"):
            table_name = path[len("/tables/"):]
            conn = get_db()
            self._json({"table": table_name, "rows": sample_rows(conn, table_name)})
            conn.close()
        elif path == "/traces":
            self._json({"traces": current_traces()})
        elif path == "/tools":
            world = load_world()
            self._json({"tools": [{"name": t["name"], "type": t["type"], "description": t["description"], "target_tables": t.get("target_tables", []), "parameters": t.get("parameters", {})} for t in world.get("tools", [])]})
        elif path == "/tasks":
            world = load_world()
            self._json({"tasks": world.get("tasks", [])})
        else:
            self._json({"error": "not_found"}, 404)

    def do_POST(self) -> None:
        self._reset_request_context()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/sessions":
            if not self._authorized():
                self._json({"error": "unauthorized"}, 401)
                return
            body = self._read_body()
            if body is None:
                return
            try:
                session_id, state_db = create_state_session()
            except SessionCapacityError as exc:
                self._json({"error": "session_capacity_reached", "detail": str(exc)}, 429)
                return
            except Exception as exc:
                self._json({"error": "session_creation_failed", "detail": str(exc)[:300]}, 500)
                return
            REQUEST_STATE_DB.set(state_db)
            REQUEST_SESSION_ID.set(session_id)
            self._json({"session_id": session_id, "world_id": load_world().get("world_id")}, 201)
            return

        if not self._select_session(require_session=True):
            return

        if path == "/mcp":
            body = self._read_body()
            if body is None:
                return
            rpc_id = body.get("id")
            method = body.get("method")
            params = body.get("params") if isinstance(body.get("params"), dict) else {}
            world = load_world()
            if method == "initialize":
                self._json({"jsonrpc": "2.0", "id": rpc_id, "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "blobfish-company-gym", "version": "1.0.0"},
                    "instructions": "Prebuilt copy-on-write company gym; create POST /sessions for isolated state, then call tools/list and tools/call with the returned session header. Reset with POST /reset.",
                }})
            elif method == "notifications/initialized":
                self._json({}, 202)
            elif method == "tools/list":
                self._json({"jsonrpc": "2.0", "id": rpc_id, "result": {
                    "tools": [mcp_tool(tool) for tool in world.get("tools", [])]
                }})
            elif method == "tools/call":
                requested = str(params.get("name") or "")
                tool = resolve_mcp_tool(world, requested)
                if not tool:
                    self._json({"jsonrpc": "2.0", "id": rpc_id, "error": {
                        "code": -32602, "message": "unknown tool: " + requested,
                    }}, 400)
                    return
                arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
                execution = execute_tool(world, tool["name"], arguments)
                trace_id = f"trace_{uuid.uuid4().hex[:12]}"
                record_trace({"id": trace_id, "type": "mcp_tool_call", "tool": requested,
                              "args": arguments, "result": execution, "timestamp": time.time()})
                raw_payload = execution.get("result")
                if execution.get("ok"):
                    payload = raw_payload
                elif isinstance(raw_payload, dict):
                    # Keep machine-actionable validation receipts (code,
                    # accepted enum values, missing/unexpected fields) intact
                    # across MCP rather than collapsing them to one string.
                    payload = {"error": execution.get("error"), **raw_payload}
                else:
                    payload = {"error": execution.get("error")}
                self._json({"jsonrpc": "2.0", "id": rpc_id, "result": {
                    "content": [{"type": "text", "text": json.dumps(payload, default=str)}],
                    "structuredContent": payload,
                    "isError": not bool(execution.get("ok")),
                    "_meta": {"trace_id": trace_id, "asset": tool.get("asset_namespace") or "core"},
                }})
            else:
                self._json({"jsonrpc": "2.0", "id": rpc_id, "error": {
                    "code": -32601, "message": "method not found: " + str(method),
                }}, 400)

        elif path == "/tool-call":
            body = self._read_body()
            if body is None:
                return
            tool_name = body.get("tool", "")
            args = body.get("args", {})
            world = load_world()
            result = execute_tool(world, tool_name, args)
            trace_id = f"trace_{uuid.uuid4().hex[:12]}"
            record_trace({"id": trace_id, "type": "tool_call", "tool": tool_name, "args": args, "result": result, "timestamp": time.time()})
            self._json({"trace_id": trace_id, **result})

        elif path.startswith("/task/") and path.endswith("/run"):
            task_id = path[len("/task/"):-len("/run")]
            world = load_world()
            trajectory = run_task(world, task_id)
            if trajectory.get("error") == "task not found":
                self._json({"error": "task not found"}, 404)
                return
            self._json(trajectory)

        elif path == "/chat":
            body = self._read_body()
            if body is None:
                return
            message = body.get("message", "")
            world = load_world()
            # Run a REAL deterministic tool-calling agent — reads state.db, executes
            # tools in dependency order, and returns a turn-by-turn trajectory with
            # live state-diffs. No canned response; behaviour is consistent with the
            # in-app heuristic planner (runHeuristicAgentSqlite in sandboxAgent.ts).
            trajectory = run_heuristic_agent(world, message)
            trace_id = trajectory["id"]
            public_trajectory = compact_public_trajectory(trajectory)
            record_trace({"id": trace_id, "type": "chat", "message": message, "trajectory": public_trajectory, "timestamp": time.time()})
            self._json({
                "reply": trajectory["final_answer"],
                "trajectory": public_trajectory,
                "trace_id": trace_id,
            })

        elif path == "/reset":
            if os.path.exists(SEED_DB):
                reset_state_database()
                conn = get_db()
                tables = table_info(conn)
                total_rows = sum(t["row_count"] for t in tables)
                conn.close()
                clear_current_traces()
                self._json({"status": "reset", "tables": len(tables), "total_rows": total_rows})
            else:
                self._json({"error": "seed.db not found"}, 500)

        elif path.startswith("/verify/"):
            task_id = path[len("/verify/"):]
            world = load_world()
            body = self._read_body()
            if body is None:
                return
            initial = snapshot(SEED_DB) if os.path.exists(SEED_DB) else {}
            # BF_TASK_SEED_PATCH_V2: harness may supply per-table post-task-seed
            # baselines ("initial_state": {table: {rowid -> row}} — only the
            # tables the seed touched, keeping the body small). Each supplied
            # table REPLACES that table's SEED_DB view, so fixtures are initial
            # state, not agent writes. JSON string keys coerce back to int.
            _override = body.get("initial_state") if isinstance(body, dict) else None
            if isinstance(_override, dict) and _override:
                for _t, _rows in _override.items():
                    if isinstance(_rows, dict):
                        initial[_t] = {int(_k): _v for _k, _v in _rows.items()}
            final = snapshot(current_state_db())
            trace = body.get("trace", []) if isinstance(body, dict) else []
            if not trace:
                recent = next((entry for entry in reversed(current_traces())
                               if entry.get("type") == "task_run"
                               and entry.get("task_id") == task_id), None)
                if recent:
                    recent_trajectory = recent.get("trajectory", {})
                    trace = verifier_trace_from_steps(
                        recent_trajectory.get("steps", []),
                        recent_trajectory.get("final_answer"),
                    )
            result = run_verifier(world, task_id, initial, final, trace)
            trace_id = f"trace_{uuid.uuid4().hex[:12]}"
            record_trace({"id": trace_id, "type": "verify", "task_id": task_id, "result": result, "timestamp": time.time()})
            self._json(result)

        else:
            self._json({"error": "not_found"}, 404)

    def do_DELETE(self) -> None:
        self._reset_request_context()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not self._authorized():
            self._json({"error": "unauthorized"}, 401)
            return
        prefix = "/sessions/"
        if not path.startswith(prefix):
            self._json({"error": "not_found"}, 404)
            return
        session_id = path[len(prefix):]
        mcp_session = self.headers.get("mcp-session-id", "").strip()
        blobfish_session = self.headers.get("x-blobfish-session", "").strip()
        if mcp_session and blobfish_session and mcp_session != blobfish_session:
            self._json({"error": "conflicting_session_headers"}, 400)
            return
        supplied = mcp_session or blobfish_session
        if supplied and supplied != session_id:
            self._json({"error": "session_header_mismatch"}, 409)
            return
        if not close_state_session(session_id):
            self._json({"error": "unknown_session", "session_id": session_id}, 404)
            return
        self._json({"status": "closed", "session_id": session_id})

    def log_message(self, format: str, *args) -> None:
        sys.stderr.write(f"[harbor] {args[0]} {args[1]} {args[2]}\n")


def main():
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Harbor runtime listening on :{port}")
    print("  GET  /health")
    print("  GET  /world")
    print("  GET  /tools")
    print("  GET  /tasks")
    print("  GET  /traces")
    print("  GET  /tables")
    print("  GET  /tables/{name}")
    print("  POST /sessions")
    print("  DELETE /sessions/{session_id}")
    print("  POST /mcp")
    print("  POST /tool-call")
    print("  POST /task/{task_id}/run")
    print("  POST /chat")
    print("  POST /reset")
    print("  POST /verify/{task_id}")
    server.serve_forever()

if __name__ == "__main__":
    main()
