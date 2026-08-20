import sqlite3

DB = "db/nifty100.db"

connection = sqlite3.connect(DB)

print("=" * 60)
print("N100 DATABASE VALIDATION")
print("=" * 60)

violations = connection.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print()
print("FOREIGN KEY VIOLATIONS:", len(violations))

print()
print("TABLE ROW COUNTS:")

tables = connection.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name
    """
).fetchall()

for (table,) in tables:
    count = connection.execute(
        f"SELECT COUNT(*) FROM [{table}]"
    ).fetchone()[0]

    print(f"{table:20} {count}")

connection.close()

print()
print("=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
