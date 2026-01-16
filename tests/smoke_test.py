from __future__ import annotations

import sys

from app import db


CORE_TABLES = {
    "meta",
    "users",
    "tools",
    "program_files",
    "print_files",
}


def main() -> int:
    try:
        db.init_db()
        with db.connect() as conn:
            for table in CORE_TABLES:
                row = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (table,),
                ).fetchone()
                if not row:
                    raise RuntimeError(f"Missing expected table: {table}")

            conn.execute("INSERT INTO meta(key, value) VALUES(?, ?)", ("smoke_test", "ok"))
            row = conn.execute("SELECT value FROM meta WHERE key=?", ("smoke_test",)).fetchone()
            if not row or row["value"] != "ok":
                raise RuntimeError("Smoke test insert/select failed")
            conn.execute("DELETE FROM meta WHERE key=?", ("smoke_test",))
        return 0
    except Exception as exc:
        print(f"Smoke test failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
