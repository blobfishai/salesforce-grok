"""Isolated generated-tool and VCode execution for a downloaded Blobfish world."""
from __future__ import annotations

import base64
import json
import marshal
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid


_CHILD_GUARD = r'''
import ast, builtins

_ALLOWED_IMPORTS = {
    "__future__", "collections", "datetime", "decimal", "fractions",
    "functools", "hashlib", "itertools", "json", "math", "random", "re",
    "sqlite3", "statistics", "typing", "uuid",
}
# CPython's datetime.strftime() performs a lazy 'import time' from the
# generated function's builtins. The source validator still rejects an
# explicit 'import time' in untrusted tool/VCode source; this second set is
# only for dependency imports performed by an already-allowed stdlib module.
_RUNTIME_IMPORTS = {"time"}
_BLOCKED_CALLS = {
    "__import__", "breakpoint", "compile", "copyright", "credits", "delattr",
    "dir", "eval", "exec", "exit", "getattr", "globals", "help", "input",
    "license", "locals", "open", "print", "quit", "setattr", "vars",
}
_BLOCKED_NAMES = {
    "__builtins__", "__cached__", "__file__", "__loader__", "__package__",
    "__spec__", "os", "SystemExit",
}
_BLOCKED_ATTRS = {
    "abort", "backup", "blobopen", "chdir", "chmod", "chown", "deserialize",
    "enable_load_extension", "environ", "execl", "execle", "execlp",
    "execlpe", "execv", "execve", "execvp", "execvpe", "fdopen", "fork",
    "forkpty", "getenv", "kill", "killpg", "link", "listdir",
    "load_extension", "makedirs", "mkdir", "os", "popen", "posix_spawn",
    "posix_spawnp", "putenv", "read", "remove", "removedirs", "rename",
    "replace", "rmdir", "scandir", "set_authorizer", "spawnl", "spawnle",
    "spawnlp", "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe",
    "system", "symlink", "truncate", "unlink", "walk", "write",
}
_SAFE_METHOD_COLLISIONS = {"remove", "replace"}

def _root(node):
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None

def _validate(tree):
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in _ALLOWED_IMPORTS:
                    raise RuntimeError("import not allowed: %s" % alias.name)
                aliases[alias.asname or root] = root
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if node.level or root not in _ALLOWED_IMPORTS:
                raise RuntimeError("import not allowed: %s" % node.module)
            if any(alias.name.startswith("_") or alias.name == "os" for alias in node.names):
                raise RuntimeError("private import not allowed")
            for alias in node.names:
                aliases[alias.asname or alias.name] = root
        elif isinstance(node, ast.Name) and (
            node.id.startswith("__")
            or node.id in _BLOCKED_NAMES
            or node.id in _BLOCKED_CALLS
        ):
            raise RuntimeError("name not allowed: %s" % node.id)
        elif isinstance(node, ast.Call):
            root = aliases.get(_root(node.func), _root(node.func))
            leaf = node.func.attr if isinstance(node.func, ast.Attribute) else None
            if root == "os" or (
                leaf in _BLOCKED_ATTRS and leaf not in _SAFE_METHOD_COLLISIONS
            ):
                raise RuntimeError("call not allowed: %s" % (leaf or root))
        elif isinstance(node, ast.Attribute):
            root = aliases.get(_root(node), _root(node))
            if node.attr.startswith("_") or root == "os" or node.attr == "os":
                raise RuntimeError("attribute not allowed: %s" % node.attr)
            if (
                node.attr in _BLOCKED_ATTRS
                and node.attr not in _SAFE_METHOD_COLLISIONS
            ):
                raise RuntimeError("attribute not allowed: %s" % node.attr)

def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level or name.split(".", 1)[0] not in (_ALLOWED_IMPORTS | _RUNTIME_IMPORTS):
        raise RuntimeError("import not allowed: %s" % name)
    return builtins.__import__(name, globals, locals, fromlist, level)

def _safe_builtins():
    safe = dict(vars(builtins))
    for name in _BLOCKED_CALLS:
        safe.pop(name, None)
    safe["__import__"] = _safe_import
    return safe
'''

_TOOL_CHILD = _CHILD_GUARD + r'''
import base64, inspect, json, marshal, os, sqlite3, sys

payload = json.loads(sys.stdin.read())
source = payload["source"]
tree = ast.parse(source, filename="generated_tool.py")
_validate(tree)
database_path = os.path.realpath(payload["db_path"])
result_marker = payload["result_marker"]
original_connect = sqlite3.connect
original_connection = sqlite3.Connection
original_type = type
sqlite_attach = sqlite3.SQLITE_ATTACH
sqlite_detach = sqlite3.SQLITE_DETACH
sqlite_deny = sqlite3.SQLITE_DENY
sqlite_ok = sqlite3.SQLITE_OK

def _authorize(action, arg1, arg2, db_name, trigger_name):
    del arg1, arg2, db_name, trigger_name
    return sqlite_deny if action in (sqlite_attach, sqlite_detach) else sqlite_ok

class ScopedConnectionMeta(original_type):
    def __call__(cls, database=database_path, *args, **kwargs):
        return scoped_connect(database, *args, **kwargs)

    def __instancecheck__(cls, instance):
        return isinstance(instance, original_connection)

class ScopedConnection(metaclass=ScopedConnectionMeta):
    pass

def scoped_connect(database=database_path, *args, **kwargs):
    requested = os.fspath(database)
    if kwargs.get("factory") is ScopedConnection:
        kwargs["factory"] = original_connection
    if requested == ":memory:":
        connection = original_connect(requested, *args, **kwargs)
    else:
        requested_path = os.path.realpath(requested)
        # Friction wrappers persist only their deterministic attempt counter in
        # this exact reset-scoped sidecar. No other generated SQLite path is
        # allowed, and ATTACH/DETACH remain denied by the authorizer.
        friction_path = database_path + ".bf-friction"
        if requested_path not in (database_path, friction_path):
            raise sqlite3.OperationalError(
                "generated tools may only open the episode database or its friction counter"
            )
        kwargs.pop("uri", None)
        connection = original_connect(requested_path, *args, **kwargs)
    connection.set_authorizer(_authorize)
    return connection

def scoped_type(value, *args, **kwargs):
    if not args and isinstance(value, original_connection):
        return ScopedConnection
    return original_type(value, *args, **kwargs)

shared = {"conn": None}

def _connect():
    if shared["conn"] is None:
        connection = scoped_connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        shared["conn"] = connection
    return shared["conn"]

def _audit(db, actor, action, entity, entity_id, details=None):
    count = db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
    audit_id = "aud_" + str(7000 + count + 1)
    db.execute(
        "INSERT INTO audit_logs "
        "(id, actor, action, entity, entity_id, details, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (
            audit_id, actor, action, entity, entity_id,
            json.dumps(details or {}, sort_keys=True, default=str), "2026-05-01",
        ),
    )
    return audit_id

sqlite3.connect = scoped_connect
sqlite3.dbapi2.connect = scoped_connect
sqlite3.Connection = ScopedConnection
sqlite3.dbapi2.Connection = ScopedConnection
safe_builtins = _safe_builtins()
safe_builtins["type"] = scoped_type
scope = {
    "__builtins__": safe_builtins,
    "_connect": _connect,
    "_audit": _audit,
    "json": json,
    "sqlite3": sqlite3,
}
exec(compile(tree, "generated_tool.py", "exec"), scope, scope)
function = scope.get(payload["tool"])
if not callable(function):
    raise RuntimeError("tool source does not define the requested callable")

signature_target = getattr(function, "blobfish_original", function)
signature = inspect.signature(signature_target)
parameters = signature.parameters
has_var_kwargs = any(
    parameter.kind == inspect.Parameter.VAR_KEYWORD
    for parameter in parameters.values()
)
call_args = {}
for key, value in payload["args"].items():
    if key == "db_path" or (not has_var_kwargs and key not in parameters):
        continue
    parameter = parameters.get(key)
    if parameter is not None and isinstance(value, str):
        annotation = parameter.annotation
        default = parameter.default
        wants_int = annotation is int or (
            annotation is inspect.Parameter.empty
            and isinstance(default, int)
            and not isinstance(default, bool)
        )
        wants_float = annotation is float or (
            annotation is inspect.Parameter.empty and isinstance(default, float)
        )
        if wants_int:
            try:
                value = int(value)
            except (TypeError, ValueError):
                pass
        elif wants_float:
            try:
                value = float(value)
            except (TypeError, ValueError):
                pass
    call_args[key] = value
if "db_path" in parameters:
    call_args["db_path"] = database_path

result = function(**call_args)
if shared["conn"] is not None:
    shared["conn"].commit()
    shared["conn"].close()
if isinstance(result, list):
    result = {"rows": result, "count": len(result)}
elif not isinstance(result, dict):
    result = {"result": result}
try:
    encoded_result = marshal.dumps(result)
except (TypeError, ValueError):
    encoded_result = marshal.dumps({
        "success": False,
        "error": "tool result is not serializable",
    })
if len(encoded_result) > 1_000_000:
    encoded_result = marshal.dumps({
        "success": False,
        "error": "tool result exceeds 1 MB",
    })
print(result_marker + base64.b64encode(encoded_result).decode("ascii"))
'''

_VERIFIER_CHILD = _CHILD_GUARD + r'''
import base64, json, marshal, sqlite3, sys

payload = json.loads(sys.stdin.read())
tree = ast.parse(payload["vcode"], filename="generated_vcode.py")
_validate(tree)
verdict_marker = payload["verdict_marker"]

def _deny_database(*args, **kwargs):
    del args, kwargs
    raise sqlite3.OperationalError("state-trace VCode has no database capability")

sqlite3.connect = _deny_database
sqlite3.dbapi2.connect = _deny_database
sqlite3.Connection = _deny_database
sqlite3.dbapi2.Connection = _deny_database
scope = {
    "__builtins__": _safe_builtins(),
    "json": json,
    "sqlite3": sqlite3,
}
exec(compile(tree, "generated_vcode.py", "exec"), scope, scope)
verify = scope.get("verify")
if not callable(verify):
    result = {"error": "vcode defines no verify() callable"}
else:
    result = verify(payload["initial"], payload["final"], payload["trace"])
try:
    encoded_result = marshal.dumps(result)
except (TypeError, ValueError):
    encoded_result = marshal.dumps({"error": "verifier result is not serializable"})
if len(encoded_result) > 1_000_000:
    encoded_result = marshal.dumps({"error": "verifier result exceeds 1 MB"})
print(verdict_marker + base64.b64encode(encoded_result).decode("ascii"))
'''

_MISSING = object()
_SQLITE_SIDECARS = ("-journal", "-shm", "-wal")
_MAX_SOURCE_BYTES = 1_000_000
_MAX_TOOL_INPUT_BYTES = 1_000_000
_MAX_VERIFIER_INPUT_BYTES = 5_000_000
_DEFAULT_CHILD_FILE_BYTES = 1 * 1024 * 1024
_MIN_TOOL_FILE_BYTES = 16 * 1024 * 1024
_MAX_TOOL_FILE_BYTES = 256 * 1024 * 1024


def _decode(stdout, marker):
    for line in reversed(stdout.splitlines()):
        if marker not in line:
            continue
        encoded = line.rsplit(marker, 1)[1].strip()
        try:
            return marshal.loads(base64.b64decode(encoded, validate=True))
        except (EOFError, TypeError, ValueError):
            continue
    return _MISSING


def _limit_resources(file_bytes):
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        if hasattr(resource, "RLIMIT_AS"):
            memory = 256 * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))
        resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    except (ImportError, OSError, ValueError):
        pass


def _run_child(
    source,
    payload,
    marker,
    timeout_s,
    file_bytes=_DEFAULT_CHILD_FILE_BYTES,
):
    file_bytes = max(
        _DEFAULT_CHILD_FILE_BYTES,
        min(_MAX_TOOL_FILE_BYTES, int(file_bytes)),
    )
    with tempfile.TemporaryFile() as stderr_file:
        try:
            process = subprocess.run(
                [sys.executable, "-I", "-c", source],
                input=json.dumps(payload),
                text=True,
                stdout=subprocess.PIPE,
                stderr=stderr_file,
                timeout=timeout_s,
                env={"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"},
                start_new_session=True,
                preexec_fn=(
                    (lambda: _limit_resources(file_bytes))
                    if os.name == "posix"
                    else None
                ),
            )
        except subprocess.TimeoutExpired:
            return _MISSING, "generated code timed out"
        stderr_file.seek(0, os.SEEK_END)
        size = stderr_file.tell()
        stderr_file.seek(max(0, size - 500))
        stderr = stderr_file.read().decode("utf-8", errors="replace").strip()
    if process.returncode != 0:
        return _MISSING, stderr or "generated code failed"
    result = _decode(process.stdout, marker)
    if result is _MISSING:
        return _MISSING, "generated code returned malformed output"
    return result, None


def _snapshot_database(database, snapshot_path):
    source = sqlite3.connect(database)
    target = sqlite3.connect(snapshot_path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def _restore_database(snapshot_path, database):
    restore_path = database + "." + uuid.uuid4().hex + ".restore"
    for suffix in _SQLITE_SIDECARS:
        try:
            os.remove(database + suffix)
        except FileNotFoundError:
            pass
    try:
        shutil.copy2(snapshot_path, restore_path)
        os.replace(restore_path, database)
    finally:
        try:
            os.remove(restore_path)
        except FileNotFoundError:
            pass
    for suffix in _SQLITE_SIDECARS:
        try:
            os.remove(database + suffix)
        except FileNotFoundError:
            pass


def _structured_error(output):
    if not isinstance(output, dict):
        return None
    explicit = output.get("ok") is False or output.get("success") is False
    raw_error = output.get("error")
    unqualified = (
        raw_error not in (None, "", False)
        and output.get("ok") is not True
        and output.get("success") is not True
    )
    if not explicit and not unqualified:
        return None
    return (
        str(raw_error)
        if raw_error not in (None, "", False)
        else "tool returned a structured failure"
    )


def _failure(error):
    normalized_error = str(error)[:500]
    return {
        "ok": False,
        "error": normalized_error,
        "result": {"error": normalized_error},
    }


def execute_generated_tool(source, tool_name, db_path, args):
    if len(source.encode("utf-8")) > _MAX_SOURCE_BYTES:
        return _failure("tool source exceeds 1 MB")
    if not isinstance(args, dict):
        return _failure("tool arguments must be an object")
    try:
        encoded_args = json.dumps(args)
    except (TypeError, ValueError) as exc:
        return _failure("tool arguments are not serializable: " + str(exc)[:300])
    if len(encoded_args.encode("utf-8")) > _MAX_TOOL_INPUT_BYTES:
        return _failure("tool arguments exceed 1 MB")
    try:
        database_bytes = os.path.getsize(db_path)
    except OSError as exc:
        return _failure("tool database is unavailable: " + str(exc)[:400])
    tool_file_bytes = min(
        _MAX_TOOL_FILE_BYTES,
        max(_MIN_TOOL_FILE_BYTES, database_bytes * 4),
    )
    backup_path = db_path + "." + uuid.uuid4().hex + ".snapshot"
    try:
        _snapshot_database(db_path, backup_path)
    except Exception as exc:
        try:
            os.remove(backup_path)
        except OSError:
            pass
        return _failure("failed to snapshot tool state: " + str(exc)[:400])

    cleanup_backup = False

    def rollback(error, result=_MISSING):
        nonlocal cleanup_backup
        try:
            _restore_database(backup_path, db_path)
            cleanup_backup = True
        except Exception as exc:
            cleanup_backup = False
            error = (
                error + "; rollback failed: " + str(exc)[:200]
                + "; recovery snapshot: " + backup_path
            )
        normalized_error = str(error)[:500]
        response = {"ok": False, "error": normalized_error}
        response["result"] = (
            result if result is not _MISSING else {"error": normalized_error}
        )
        return response

    try:
        marker = "__BF_TOOL_RESULT_" + uuid.uuid4().hex + "__"
        result, child_error = _run_child(
            _TOOL_CHILD,
            {
                "source": source,
                "tool": tool_name,
                "db_path": db_path,
                "args": args,
                "result_marker": marker,
            },
            marker,
            20,
            tool_file_bytes,
        )
        if child_error:
            return rollback(child_error)
        application_error = _structured_error(result)
        if application_error:
            return rollback(application_error, result)
        cleanup_backup = True
        return {"ok": True, "result": result, "error": None}
    except Exception as exc:
        return rollback(str(exc))
    finally:
        if cleanup_backup:
            try:
                os.remove(backup_path)
            except OSError:
                pass


def _verifier_error(task_id, message):
    return {
        "task_id": task_id,
        "passed": False,
        "reward": 0.0,
        "explanation": message,
        "assertions": [],
        "failed_conditions": ["verifier_execution"],
        "error": message,
    }


def _vcode_state(state):
    if not isinstance(state, dict):
        return {}
    return {
        table: list(rows.values())
        if isinstance(rows, dict)
        else rows
        if isinstance(rows, list)
        else []
        for table, rows in state.items()
    }


def run_generated_verifier(vcode, task_id, initial, final, trace):
    if len(vcode.encode("utf-8")) > _MAX_SOURCE_BYTES:
        return _verifier_error(task_id, "verifier source exceeds 1 MB")
    marker = "__BF_VERDICT_" + uuid.uuid4().hex + "__"
    payload = {
        "vcode": vcode,
        "initial": _vcode_state(initial),
        "final": _vcode_state(final),
        "trace": trace,
        "verdict_marker": marker,
    }
    try:
        encoded = json.dumps(payload)
    except (TypeError, ValueError) as exc:
        return _verifier_error(task_id, "verifier input is not serializable: " + str(exc))
    if len(encoded.encode("utf-8")) > _MAX_VERIFIER_INPUT_BYTES:
        return _verifier_error(task_id, "verifier input exceeds 5 MB")
    result, child_error = _run_child(_VERIFIER_CHILD, payload, marker, 10)
    if child_error:
        return _verifier_error(task_id, child_error)
    if not isinstance(result, dict):
        return _verifier_error(task_id, "verifier returned a non-object result")
    if result.get("error"):
        return _verifier_error(task_id, "verifier reported an error: " + str(result["error"])[:300])
    if result.get("task_id") not in (None, task_id):
        return _verifier_error(task_id, "verifier task_id mismatch")
    if not isinstance(result.get("passed"), bool):
        return _verifier_error(task_id, "verifier passed must be boolean")
    reward = result.get("reward", 1.0 if result["passed"] else 0.0)
    if isinstance(reward, bool):
        return _verifier_error(task_id, "verifier reward must be numeric")
    try:
        reward = float(reward)
    except (TypeError, ValueError):
        return _verifier_error(task_id, "verifier reward must be numeric")
    if reward < 0 or reward > 1:
        return _verifier_error(task_id, "verifier reward must be within [0, 1]")
    assertions = result.get("assertions", [])
    failed = result.get("failed_conditions", [])
    advisory = result.get("advisory_conditions", [])
    explanation = result.get("explanation", "")
    if not isinstance(assertions, list):
        return _verifier_error(task_id, "verifier assertions are malformed")
    if not isinstance(failed, list) or any(not isinstance(item, str) for item in failed):
        return _verifier_error(task_id, "verifier failed_conditions are malformed")
    if not isinstance(advisory, list) or any(not isinstance(item, str) for item in advisory):
        return _verifier_error(task_id, "verifier advisory_conditions are malformed")
    if not isinstance(explanation, str):
        return _verifier_error(task_id, "verifier explanation must be a string")
    return {
        "task_id": task_id,
        "passed": result["passed"],
        "reward": reward,
        "explanation": explanation,
        "assertions": assertions,
        "failed_conditions": failed,
        "advisory_conditions": advisory,
    }
