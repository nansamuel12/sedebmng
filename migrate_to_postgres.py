"""
Copy your existing data (finebot_v2.db) into the new online database,
so Hanna / Konjit and all fines are kept.

Run ONCE on your PC, in the project folder:

    python migrate_to_postgres.py "postgresql://USER:PASSWORD@HOST/DBNAME" [finebot_v2.db]

The target database must be new/empty. Nothing is deleted from the .db file.
"""
import sys

from sqlalchemy import func, inspect, select, text

import models  # noqa: F401  (registers tables)
from database import Base, make_engine

TABLES = ("users", "partnerships", "entries")  # order matters (foreign keys)


def migrate(source_url: str, target_url: str, out=print) -> dict:
    src, dst = make_engine(source_url), make_engine(target_url)
    Base.metadata.create_all(dst)
    insp = inspect(src)
    counts = {}
    with src.connect() as s, dst.begin() as d:
        for name in TABLES:
            table = Base.metadata.tables[name]
            if d.execute(select(func.count()).select_from(table)).scalar():
                raise SystemExit(f"Stopped: the target table '{name}' already has data. Use an empty database.")
        for name in TABLES:
            table = Base.metadata.tables[name]
            if not insp.has_table(name):
                continue
            have = {c["name"] for c in insp.get_columns(name)}
            cols = [c for c in table.c if c.name in have]   # old files may lack newer columns
            rows = [dict(r._mapping) for r in s.execute(select(*cols))]
            if rows:
                d.execute(table.insert(), rows)
            counts[name] = len(rows)
            out(f"{name}: copied {len(rows)} rows")
        if dst.dialect.name == "postgresql":   # let new rows continue after the old ids
            for name in TABLES:
                d.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{name}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {name}), 0) + 1, false)"
                ))
    return counts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    source = sys.argv[2] if len(sys.argv) > 2 else "finebot_v2.db"
    migrate(f"sqlite:///{source}", sys.argv[1])
    print("Done. Your data is now in the online database.")
