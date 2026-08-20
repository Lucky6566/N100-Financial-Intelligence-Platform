import sqlite3

db = "db/nifty100.db"

con = sqlite3.connect(db)

tables = con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

print("TABLES:")
for table in tables:
    print(" ", table[0])

try:
    count = con.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    print("\nCOMPANIES:", count)
except Exception as e:
    print("\nCOMPANIES ERROR:", e)

con.close()
