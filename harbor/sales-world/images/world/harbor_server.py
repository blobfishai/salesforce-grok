#!/usr/bin/env python3
"""Harbor entrypoint for the world server.

Wraps the packaged world server rather than editing it: subclass its Handler and
add the one endpoint a Harbor verifier needs — read-only SQL against whatever
state the agent left behind.

    POST /verifier/query   {"sql": "SELECT ...", "params": [...]}
    header X-Verifier-Token: <HARBOR_VERIFIER_TOKEN>

Why this exists: Harbor verifiers run in a separate container from the world, so
a pytest assertion cannot open state.db directly. The alternative — verifying
through the same MCP tools the agent used — would let a tool bug mark a correct
trajectory as failed (and vice versa). Grading reads the database.

The endpoint is deliberately not reachable by the agent: the token is injected
only into `[verifier.env]` in task.toml, never `[environment.env]`. Statements are
restricted to SELECT/WITH and the connection is opened read-only, so a verifier
cannot mutate the state it is grading either.
"""
from __future__ import annotations

import json
import os
import sqlite3
import re
from urllib.parse import urlparse

import server  # the packaged world server; importing is safe (main() is __main__-guarded)

TOKEN = os.environ.get("HARBOR_VERIFIER_TOKEN", "").strip()
READ_ONLY = re.compile(r"^\s*(select|with)\b", re.I)
FORBIDDEN = re.compile(r"\b(attach|pragma|insert|update|delete|drop|alter|create|replace|vacuum)\b", re.I)
MAX_ROWS = 5000


class HarborHandler(server.Handler):
    def _verifier_query(self):
        if TOKEN and (self.headers.get("X-Verifier-Token") or "").strip() != TOKEN:
            self._json({"error": "forbidden"}, 403)
            return
        body = self._read_body()
        if body is None:
            return
        sql = str(body.get("sql") or "")
        params = body.get("params") if isinstance(body.get("params"), list) else []
        if not READ_ONLY.match(sql) or FORBIDDEN.search(sql):
            self._json({"error": "read_only", "detail": "only SELECT/WITH statements are allowed"}, 400)
            return
        # `db: "seed"` reads the pristine pre-trial world, which is how collateral
        # guards are expressed: "these rows must look exactly as they did before".
        which = str(body.get("db") or "state").lower()
        path = server.SEED_DB if which == "seed" else server.current_state_db()
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            rows = [dict(r) for r in conn.execute(sql, params).fetchmany(MAX_ROWS)]
            conn.close()
        except sqlite3.Error as e:
            self._json({"error": "sql_error", "detail": str(e)}, 400)
            return
        self._json({"rows": rows, "count": len(rows)})

    def _verifier_trace(self):
        """Every tool the agent actually invoked, for false-completion checks.

        R2A-Sales' sharpest finding: a customer-visible sentence such as "I sent
        the PDF" is not a tool event. State assertions alone cannot tell apart an
        agent that correctly declined from one that tried, failed, and narrated
        success — nor one that reports work it never attempted. This exposes the
        trace so a verifier can assert on what was *called*, not just what stuck.
        """
        if TOKEN and (self.headers.get("X-Verifier-Token") or "").strip() != TOKEN:
            self._json({"error": "forbidden"}, 403)
            return
        calls = []
        for t in server.current_traces():
            if t.get("type") != "mcp_tool_call":
                continue
            result = t.get("result") if isinstance(t.get("result"), dict) else {}
            calls.append({
                "tool": (t.get("tool") or "").split(".")[-1],
                "qualified": t.get("tool"),
                "ok": bool(result.get("ok", True)),
                "timestamp": t.get("timestamp"),
            })
        self._json({"calls": calls, "count": len(calls)})

    def do_POST(self):  # noqa: N802 - BaseHTTPRequestHandler naming
        path = urlparse(self.path).path.rstrip("/")
        if path == "/verifier/query":
            self._reset_request_context()
            self._verifier_query()
            return
        if path == "/verifier/trace":
            self._reset_request_context()
            self._verifier_trace()
            return
        super().do_POST()


def main():
    from http.server import HTTPServer

    port = int(os.environ.get("PORT", "8080"))
    print(f"sales-world listening on :{port} (+ POST /verifier/query)", flush=True)
    HTTPServer(("0.0.0.0", port), HarborHandler).serve_forever()


if __name__ == "__main__":
    main()
