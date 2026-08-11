#!/usr/bin/env python3
"""CRMArena parity world — serves CRMArena's own org mirror over MCP.

Tools mirror what CRMArena hands its agent:
  issue_soql_query(query)         SOQL over the shipped SQLite mirror (soql.py)
  issue_sosl_query(search)        FIND {term} across the text-bearing objects
  search_knowledge_articles(q)    Knowledge__kav lookup
  get_schema(object)              field list, so the agent can orient
  respond(answer)                 CRMArena's answer channel; recorded, then graded

Verifier-only endpoints (token-gated, unreachable from the agent):
  POST /verifier/answer   -> {"answer": ..., "responded": bool, "calls": [...]}
  POST /verifier/query    -> read-only SQL, for state assertions

Grading reads the recorded answer, not the transcript: CRMArena scores a single
final answer with exact/fuzzy match, and reproducing its metric is the whole
point of running its tasks here.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from soql import run_soql, SoqlUnsupported

DB = os.environ.get("CRMARENA_DB", "/world/crmarena_data.db")
TOKEN = os.environ.get("HARBOR_VERIFIER_TOKEN", "").strip()
PORT = int(os.environ.get("PORT", "8080"))
PROTOCOL_VERSION = "2025-03-26"

_STATE: dict = {"answer": None, "responded": False, "calls": []}

TOOLS = [
    {"name": "issue_soql_query",
     "description": "Run a SOQL query against the CRM. Returns matching records. "
                    "Relationship traversal (Account.Name) and subqueries are not supported.",
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string", "description": "A SOQL statement, e.g. SELECT Id, Subject FROM Case LIMIT 10"}},
         "required": ["query"]}},
    {"name": "issue_sosl_query",
     "description": "Full-text search across text fields of an object, in the style of SOSL FIND.",
     "inputSchema": {"type": "object", "properties": {
         "search_term": {"type": "string", "description": "Text to search for."},
         "object": {"type": "string", "description": "Object to search, e.g. Case, Product2, Knowledge__kav."},
         "limit": {"type": "integer", "description": "Max records (default 20)."}},
         "required": ["search_term"]}},
    {"name": "search_knowledge_articles",
     "description": "Search the knowledge base for articles matching a query.",
     "inputSchema": {"type": "object", "properties": {
         "search_term": {"type": "string"}, "limit": {"type": "integer"}},
         "required": ["search_term"]}},
    {"name": "get_schema",
     "description": "List the fields available on an object, and the objects available if omitted.",
     "inputSchema": {"type": "object", "properties": {
         "object": {"type": "string", "description": "Object API name; omit to list all objects."}}}},
    {"name": "respond",
     "description": "Submit your final answer. Give the answer only — an Id, a value, or 'None' if the "
                    "question cannot be answered from the data. Call this exactly once, at the end.",
     "inputSchema": {"type": "object", "properties": {
         "answer": {"type": "string", "description": "The final answer."}},
         "required": ["answer"]}},
]

# Searchable columns are derived from the table, not hardcoded: an allowlist
# missed Knowledge__kav's FAQ_Answer__c and Summary — exactly where the substance
# lives — and silently returned zero hits for a question the data can answer.
_NON_TEXT = re.compile(r"(^Id$|Id$|Date$|__History$|^Created|^Closed|Time|Count|Number$)", re.I)


def _searchable(cols: list[str]) -> list[str]:
    return [c for c in cols if not _NON_TEXT.search(c)] or [c for c in cols if c.lower() != "id"]


def _objects() -> list[str]:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        return [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    finally:
        conn.close()


def _columns(obj: str) -> list[str]:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        return [r[1] for r in conn.execute(f'PRAGMA table_info("{obj}")')]
    finally:
        conn.close()


def call_tool(name: str, args: dict) -> dict:
    _STATE["calls"].append({"tool": name, "args": args})

    if name == "issue_soql_query":
        return run_soql(DB, str(args.get("query") or ""))

    if name in ("issue_sosl_query", "search_knowledge_articles"):
        term = str(args.get("search_term") or "").strip()
        obj = "Knowledge__kav" if name == "search_knowledge_articles" else str(args.get("object") or "Case")
        limit = max(1, min(100, int(args.get("limit") or 20)))
        if obj not in _objects():
            return {"error": "INVALID_TYPE", "message": f"unknown object: {obj}"}
        cols = _columns(obj)
        texty = _searchable(cols)
        if not term or not texty:
            return {"totalSize": 0, "records": []}
        # SOSL-ish: every token must appear somewhere in the record. A single
        # literal LIKE '%golf shoes%' misses articles that say "golf" and "shoes"
        # in different sentences, which is most of them.
        tokens = [t for t in re.split(r"\s+", term) if len(t) > 1] or [term]
        clauses, params = [], []
        for tok in tokens:
            clauses.append("(" + " OR ".join(f'"{c}" LIKE ?' for c in texty) + ")")
            params.extend([f"%{tok}%"] * len(texty))
        where = " AND ".join(clauses)
        conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            rows = [dict(r) for r in conn.execute(
                f'SELECT * FROM "{obj}" WHERE {where} LIMIT {limit}', params)]
            if not rows and len(tokens) > 1:
                # Fall back to any-token so a narrow phrase does not look like "no data".
                where_any = " OR ".join(clauses)
                rows = [dict(r) for r in conn.execute(
                    f'SELECT * FROM "{obj}" WHERE {where_any} LIMIT {limit}', params)]
        except sqlite3.Error as e:
            return {"error": "SEARCH_ERROR", "message": str(e)}
        finally:
            conn.close()
        return {"totalSize": len(rows), "records": rows}

    if name == "get_schema":
        obj = args.get("object")
        if not obj:
            return {"objects": _objects()}
        if obj not in _objects():
            return {"error": "INVALID_TYPE", "message": f"unknown object: {obj}"}
        return {"object": obj, "fields": _columns(obj)}

    if name == "respond":
        _STATE["answer"] = str(args.get("answer", ""))
        _STATE["responded"] = True
        return {"accepted": True, "answer": _STATE["answer"]}

    return {"error": "UNKNOWN_TOOL", "message": name}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # container logs already capture what matters
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authed(self) -> bool:
        return not TOKEN or (self.headers.get("X-Verifier-Token") or "").strip() == TOKEN

    def do_GET(self):
        if self.path.rstrip("/") in ("/health", ""):
            self._send({"status": "healthy", "objects": len(_objects()), "db": DB})
            return
        self._send({"error": "not_found"}, 404)

    def do_POST(self):
        path = self.path.rstrip("/")
        length = int(self.headers.get("content-length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send({"error": "parse_error"}, 400)
            return

        if path == "/verifier/answer":
            if not self._authed():
                self._send({"error": "forbidden"}, 403)
                return
            self._send({"answer": _STATE["answer"], "responded": _STATE["responded"],
                        "calls": _STATE["calls"]})
            return

        if path == "/verifier/query":
            if not self._authed():
                self._send({"error": "forbidden"}, 403)
                return
            sql = str(body.get("sql") or "")
            if not re.match(r"^\s*(select|with)\b", sql, re.I):
                self._send({"error": "read_only"}, 400)
                return
            conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            try:
                rows = [dict(r) for r in conn.execute(sql, body.get("params") or [])]
            except sqlite3.Error as e:
                self._send({"error": "sql_error", "detail": str(e)}, 400)
                return
            finally:
                conn.close()
            self._send({"rows": rows, "count": len(rows)})
            return

        if path != "/mcp":
            self._send({"error": "not_found"}, 404)
            return

        rpc_id, method = body.get("id"), body.get("method")
        params = body.get("params") if isinstance(body.get("params"), dict) else {}
        if method == "initialize":
            self._send({"jsonrpc": "2.0", "id": rpc_id, "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "crmarena-parity", "version": "1.0.0"},
                "instructions": "CRM org. Query with issue_soql_query, then submit exactly one respond().",
            }})
        elif method in ("notifications/initialized", "notifications/cancelled"):
            self._send({}, 202)
        elif method == "ping":
            self._send({"jsonrpc": "2.0", "id": rpc_id, "result": {}})
        elif method == "tools/list":
            self._send({"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            name = str(params.get("name") or "")
            out = call_tool(name, params.get("arguments") or {})
            self._send({"jsonrpc": "2.0", "id": rpc_id, "result": {
                "content": [{"type": "text", "text": json.dumps(out, default=str)}],
                "structuredContent": out,
                "isError": bool(isinstance(out, dict) and out.get("error")),
            }})
        else:
            self._send({"jsonrpc": "2.0", "id": rpc_id,
                        "error": {"code": -32601, "message": f"method not found: {method}"}}, 400)


if __name__ == "__main__":
    print(f"crmarena-parity on :{PORT} db={DB} objects={len(_objects())}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
