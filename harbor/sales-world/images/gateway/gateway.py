#!/usr/bin/env python3
"""Vendor MCP gateway — presents one namespace of the world as its own MCP server.

The world server exposes every tool under a dotted namespace
(`salesforce.lead_merge`, `stripe.invoice_create`, ...). Real agents do not meet
a company that way: they connect to Salesforce, to Stripe, to Slack, each its own
server with its own bare tool names. This gateway is the adapter — one container
per vendor, filtering `tools/list` to a single namespace and re-qualifying names
on `tools/call`.

Environment:
  UPSTREAM   MCP endpoint of the world server (default http://world:8080/mcp)
  NAMESPACE  vendor prefix to expose, e.g. "salesforce"
  VENDOR     display name for serverInfo (default: NAMESPACE)
  PORT       listen port (default 8000)

Speaks the streamable-HTTP MCP dialect Harbor's clients use: JSON-RPC over
POST /mcp, JSON responses, session id echoed through the Mcp-Session-Id header.
Stdlib only, so the image stays a bare python:3.12-slim.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = os.environ.get("UPSTREAM", "http://world:8080/mcp")
NAMESPACE = os.environ.get("NAMESPACE", "").strip()
VENDOR = os.environ.get("VENDOR", NAMESPACE or "world")
PORT = int(os.environ.get("PORT", "8000"))
MAX_BODY = 4_000_000
PROTOCOL_VERSION = "2025-03-26"

if not NAMESPACE:
    print("NAMESPACE is required (e.g. NAMESPACE=salesforce)", file=sys.stderr)
    raise SystemExit(2)

PREFIX = NAMESPACE + "."


def upstream_rpc(payload: dict, session_id: str | None) -> dict:
    """Forward one JSON-RPC call to the world server."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(UPSTREAM, data=data, method="POST")
    req.add_header("content-type", "application/json")
    if session_id:
        req.add_header("Mcp-Session-Id", session_id)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:                      # keep the world's own error text
        raw = e.read() or json.dumps({"error": str(e)}).encode()
    except Exception as e:                                   # noqa: BLE001 - surfaced to the agent
        return {"jsonrpc": "2.0", "id": payload.get("id"),
                "error": {"code": -32001, "message": f"upstream unreachable: {e}"}}
    try:
        return json.loads(raw or b"{}")
    except json.JSONDecodeError:
        return {"jsonrpc": "2.0", "id": payload.get("id"),
                "error": {"code": -32002, "message": "upstream returned non-JSON"}}


def visible_tools(session_id: str | None) -> list[dict]:
    """The world's tools for this namespace, with the prefix stripped off."""
    res = upstream_rpc({"jsonrpc": "2.0", "id": "list", "method": "tools/list"}, session_id)
    tools = (res.get("result") or {}).get("tools") or []
    out = []
    for t in tools:
        name = t.get("name", "")
        if not name.startswith(PREFIX):
            continue
        local = dict(t)
        local["name"] = name[len(PREFIX):]
        out.append(local)
    return out


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *a):  # quiet: Harbor captures container logs already
        pass

    def _send(self, obj, code=200, session_id=None):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        if session_id:
            self.send_header("Mcp-Session-Id", session_id)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") in ("/health", ""):
            tools = visible_tools(None)
            self._send({"status": "healthy", "vendor": VENDOR,
                        "namespace": NAMESPACE, "tools": len(tools)})
            return
        self._send({"error": "not_found"}, 404)

    def do_DELETE(self):
        # Streamable-HTTP clients may DELETE to end a session; nothing to tear down.
        self._send({}, 200)

    def do_POST(self):
        if self.path.rstrip("/") not in ("/mcp", ""):
            self._send({"error": "not_found"}, 404)
            return
        length = int(self.headers.get("content-length") or 0)
        if length > MAX_BODY:
            self._send({"error": "payload_too_large"}, 413)
            return
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send({"jsonrpc": "2.0", "id": None,
                        "error": {"code": -32700, "message": "parse error"}}, 400)
            return

        session_id = (self.headers.get("Mcp-Session-Id") or "").strip() or None
        rpc_id = body.get("id")
        method = body.get("method")
        params = body.get("params") if isinstance(body.get("params"), dict) else {}

        if method == "initialize":
            self._send({"jsonrpc": "2.0", "id": rpc_id, "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": VENDOR, "version": "1.0.0"},
                "instructions": f"{VENDOR} tools for this company. Call tools/list to see the surface.",
            }}, session_id=session_id)
            return

        if method in ("notifications/initialized", "notifications/cancelled"):
            self._send({}, 202)
            return

        if method == "ping":
            self._send({"jsonrpc": "2.0", "id": rpc_id, "result": {}})
            return

        if method == "tools/list":
            self._send({"jsonrpc": "2.0", "id": rpc_id,
                        "result": {"tools": visible_tools(session_id)}})
            return

        if method == "tools/call":
            requested = str(params.get("name") or "")
            # Accept both bare and already-qualified names; agents copy either.
            qualified = requested if requested.startswith(PREFIX) else PREFIX + requested
            forwarded = {"jsonrpc": "2.0", "id": rpc_id, "method": "tools/call",
                         "params": {"name": qualified,
                                    "arguments": params.get("arguments") or {}}}
            self._send(upstream_rpc(forwarded, session_id), session_id=session_id)
            return

        self._send({"jsonrpc": "2.0", "id": rpc_id,
                    "error": {"code": -32601, "message": f"method not found: {method}"}}, 400)


if __name__ == "__main__":
    print(f"{VENDOR} gateway: namespace={NAMESPACE} upstream={UPSTREAM} port={PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
