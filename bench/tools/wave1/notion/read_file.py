"""Read a seeded document fixture (CSV/TSV) by filename"""
import sqlite3

def read_file(db_path, filename=None, **kwargs):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if not filename:
        names = [r["filename"] for r in conn.execute("SELECT filename FROM agent_files ORDER BY id").fetchall()]
        conn.close()
        return {"error": "validation_error", "message": "filename is required; available files: %r" % names}
    row = conn.execute("SELECT * FROM agent_files WHERE filename = ?", (filename,)).fetchone()
    if row is None:
        names = [r["filename"] for r in conn.execute("SELECT filename FROM agent_files ORDER BY id").fetchall()]
        conn.close()
        return {"error": "not_found", "message": "no file named %r; available files: %r" % (filename, names)}
    conn.close()
    return {"filename": row["filename"], "content_type": row["content_type"], "content": row["content"], "rows": [dict(row)]}