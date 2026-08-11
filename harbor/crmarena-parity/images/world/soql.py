"""SOQL → SQLite translation for the CRMArena parity world.

CRMArena ships a SQLite mirror of its org (`local_data/*.db`) but its tool
functions talk to a live Salesforce sandbox through `simple_salesforce`. Running
its 1,170 task instances without org credentials therefore needs one thing: a
`run_query` that speaks enough SOQL to answer them against the mirror.

Deliberately a *subset*, and the governing rule is **never answer wrongly**:
anything not explicitly translated raises `SoqlUnsupported`. A shim that returns
plausible-looking garbage would silently corrupt every measurement built on it —
an earlier revision of this file did exactly that, emitting the literal string
`COUNT(Id)` as if it were a count, which is why the field parser below is
explicit rather than regex-and-hope.

Supported
  SELECT  plain fields, COUNT(), COUNT(f), SUM/AVG/MIN/MAX(f), mixed with fields
  FROM    one object
  WHERE   AND/OR/NOT, = != <> < <= > >=, LIKE, IN / NOT IN, NULL tests,
          SOQL date literals (TODAY, YESTERDAY, LAST_N_DAYS:n, ...)
  GROUP BY / ORDER BY (ASC|DESC, NULLS FIRST|LAST) / LIMIT / OFFSET

Refused (raises, never guessed)
  relationship traversal (Account.Name), subqueries, HAVING, TYPEOF, FOR UPDATE,
  any field expression that is not a bare identifier or a supported aggregate.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import date, timedelta


class SoqlUnsupported(Exception):
    """Query uses SOQL we do not translate. Raised rather than answered."""


class SoqlError(Exception):
    """Malformed query, mirroring Salesforce's MALFORMED_QUERY."""


# CRMArena pins "today" per task in its metadata; the world's clock is fixed so
# relative date literals resolve identically on every run.
TODAY = date(2024, 11, 15)

_SELECT_RE = re.compile(
    r"^\s*SELECT\s+(?P<fields>.+?)\s+FROM\s+(?P<object>[A-Za-z0-9_]+)(?P<rest>.*)$", re.I | re.S)
_LIMIT_RE = re.compile(r"\bLIMIT\s+(\d+)", re.I)
_OFFSET_RE = re.compile(r"\bOFFSET\s+(\d+)", re.I)
_ORDER_RE = re.compile(r"\bORDER\s+BY\s+(?P<cols>.+?)(?=\bLIMIT\b|\bOFFSET\b|$)", re.I | re.S)
_GROUP_RE = re.compile(r"\bGROUP\s+BY\s+(?P<cols>.+?)(?=\bORDER\s+BY\b|\bLIMIT\b|\bOFFSET\b|$)", re.I | re.S)
_WHERE_RE = re.compile(
    r"\bWHERE\s+(?P<pred>.+?)(?=\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|\bOFFSET\b|$)", re.I | re.S)
_UNSUPPORTED = re.compile(r"\bTYPEOF\b|\bFOR\s+UPDATE\b|\bHAVING\b|\(\s*SELECT\b", re.I)

_IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_AGG = re.compile(r"^(COUNT|SUM|AVG|MIN|MAX)\s*\(\s*([A-Za-z0-9_]*)\s*\)$", re.I)
_DATE_LITERAL = re.compile(
    r"\b(TODAY|YESTERDAY|TOMORROW|THIS_WEEK|LAST_WEEK|THIS_MONTH|LAST_MONTH|"
    r"LAST_N_DAYS:\d+|NEXT_N_DAYS:\d+)\b", re.I)
# `field OP DATE_LITERAL` — captured whole so the column can be date-truncated.
_DATE_CMP = re.compile(
    r"\b([A-Za-z][A-Za-z0-9_]*)\s*(=|!=|<>|<=|>=|<|>)\s*(" + _DATE_LITERAL.pattern + r")", re.I)
# Bare ISO literals are ordinary SOQL (`CreatedDate <= 2024-05-26`). Unquoted,
# SQLite evaluates them as arithmetic (2024-05-26 -> 1993) and silently returns
# nothing, so they must be recognised explicitly rather than passed through.
_ISO_CMP = re.compile(
    r"\b([A-Za-z][A-Za-z0-9_]*)\s*(=|!=|<>|<=|>=|<|>)\s*"
    r"(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?)(?![\w'\"-])")
_BARE_DATEISH = re.compile(r"(?<![\w'\"])\d{4}-\d{2}-\d{2}")


def _split_top_level(text: str) -> list[str]:
    """Split on commas that are not inside parentheses."""
    parts, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def _resolve_date_literal(tok: str) -> str:
    t = tok.strip().upper()
    if t == "TODAY":
        d = TODAY
    elif t == "YESTERDAY":
        d = TODAY - timedelta(days=1)
    elif t == "TOMORROW":
        d = TODAY + timedelta(days=1)
    elif t == "THIS_MONTH":
        d = TODAY.replace(day=1)
    elif t == "LAST_MONTH":
        first = TODAY.replace(day=1)
        d = (first - timedelta(days=1)).replace(day=1)
    elif t == "THIS_WEEK":
        d = TODAY - timedelta(days=TODAY.weekday())
    elif t == "LAST_WEEK":
        d = TODAY - timedelta(days=TODAY.weekday() + 7)
    else:
        m = re.fullmatch(r"LAST_N_DAYS:(\d+)", t)
        if m:
            d = TODAY - timedelta(days=int(m.group(1)))
        else:
            m = re.fullmatch(r"NEXT_N_DAYS:(\d+)", t)
            if not m:
                raise SoqlUnsupported(f"date literal not translated: {tok}")
            d = TODAY + timedelta(days=int(m.group(1)))
    return d.isoformat()


def _translate_fields(fields_raw: str) -> tuple[str, list[str]]:
    """Build the SQLite select list. Aggregates are aliased expr0, expr1, ...
    exactly as Salesforce names them, in order of appearance."""
    selects, agg_index = [], 0
    for f in _split_top_level(fields_raw):
        if "." in f:
            raise SoqlUnsupported(f"relationship field not translated: {f}")
        m = _AGG.match(f)
        if m:
            fn, inner = m.group(1).upper(), m.group(2)
            expr = f"{fn}(*)" if (fn == "COUNT" and not inner) else f'{fn}("{inner}")'
            if fn != "COUNT" and not inner:
                raise SoqlError(f"MALFORMED_QUERY: {fn}() requires a field")
            selects.append(f"{expr} AS expr{agg_index}")
            agg_index += 1
            continue
        if not _IDENT.match(f):
            # The defect this file exists to prevent: anything not clearly a
            # field or an aggregate must raise, never be quoted and returned.
            raise SoqlUnsupported(f"field expression not translated: {f}")
        selects.append(f'"{f}"')
    if not selects:
        raise SoqlError("MALFORMED_QUERY: no fields selected")
    return ", ".join(selects), []


def _translate_predicate(pred: str) -> str:
    """SOQL WHERE → SQLite WHERE.

    Date comparisons are rewritten to compare the *date prefix* of the stored
    value, because the mirror stores full ISO timestamps
    ('2024-05-26T06:58:00.000+0000'). Comparing those against a bare 'YYYY-MM-DD'
    silently drops same-day rows on <= and <.
    """
    def date_cmp(m):
        col, op, lit = m.group(1), m.group(2), m.group(3)
        op = "!=" if op == "<>" else op
        return f"substr(\"{col}\", 1, 10) {op} '{_resolve_date_literal(lit)}'"

    def iso_cmp(m):
        col, op, lit = m.group(1), m.group(2), m.group(3)
        op = "!=" if op == "<>" else op
        return f"substr(\"{col}\", 1, 10) {op} '{lit[:10]}'"

    out = _DATE_CMP.sub(date_cmp, pred)
    out = _ISO_CMP.sub(iso_cmp, out)
    if _DATE_LITERAL.search(out):
        raise SoqlUnsupported("date literal used in a position we do not translate")
    if _BARE_DATEISH.search(out):
        raise SoqlUnsupported("bare date literal in a position we do not translate")
    out = re.sub(r"\bTRUE\b", "1", out, flags=re.I)
    out = re.sub(r"\bFALSE\b", "0", out, flags=re.I)
    return out


def soql_to_sql(soql: str) -> str:
    q = " ".join(soql.strip().rstrip(";").split())
    if _UNSUPPORTED.search(q):
        raise SoqlUnsupported(f"unsupported SOQL construct: {q[:120]}")
    m = _SELECT_RE.match(q)
    if not m:
        raise SoqlError("MALFORMED_QUERY: expected SELECT ... FROM ...")

    select, _ = _translate_fields(m.group("fields").strip())
    obj, rest = m.group("object"), m.group("rest") or ""
    sql = [f'SELECT {select} FROM "{obj}"']

    wm = _WHERE_RE.search(rest)
    if wm:
        sql.append("WHERE " + _translate_predicate(wm.group("pred").strip()))
    gm = _GROUP_RE.search(rest)
    if gm:
        cols = []
        for c in _split_top_level(gm.group("cols")):
            if not _IDENT.match(c):
                raise SoqlUnsupported(f"GROUP BY expression not translated: {c}")
            cols.append(f'"{c}"')
        sql.append("GROUP BY " + ", ".join(cols))
    om = _ORDER_RE.search(rest)
    if om:
        parts = []
        for c in _split_top_level(om.group("cols")):
            mm = re.match(r"^([A-Za-z][A-Za-z0-9_]*)\s*(ASC|DESC)?\s*(?:NULLS\s+(FIRST|LAST))?$", c, re.I)
            if not mm:
                raise SoqlUnsupported(f"ORDER BY clause not translated: {c}")
            col, direction, nulls = mm.groups()
            frag = f'"{col}" {(direction or "ASC").upper()}'
            if nulls:
                frag += f" NULLS {nulls.upper()}"
            parts.append(frag)
        sql.append("ORDER BY " + ", ".join(parts))
    lm = _LIMIT_RE.search(rest)
    sql.append(f"LIMIT {int(lm.group(1))}" if lm else "LIMIT 2000")
    om2 = _OFFSET_RE.search(rest)
    if om2:
        sql.append(f"OFFSET {int(om2.group(1))}")
    return " ".join(sql)


def run_soql(db_path: str, soql: str) -> dict:
    """Execute SOQL against the mirror, returning a Salesforce-shaped result."""
    try:
        sql = soql_to_sql(soql)
    except (SoqlUnsupported, SoqlError) as e:
        return {"error": type(e).__name__, "message": str(e)}
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in conn.execute(sql).fetchall()]
    except sqlite3.Error as e:
        return {"error": "INVALID_FIELD", "message": str(e)}
    finally:
        conn.close()
    return {"totalSize": len(rows), "done": True, "records": rows}
