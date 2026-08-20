import sqlite3
import pandas as pd

db_path = "db/nifty100.db"
pnl_path = "data/raw/profitandloss.xlsx"

# Read the Excel file using the actual header row.
pnl = pd.read_excel(pnl_path, header=1)

# Clean column names.
pnl.columns = [
    str(col).strip().lower().replace(" ", "_")
    for col in pnl.columns
]

print("P&L columns:")
print(pnl.columns.tolist())

print("\nP&L rows:", len(pnl))

con = sqlite3.connect(db_path)

companies = pd.read_sql_query(
    "SELECT id FROM companies",
    con
)

db_ids = set(
    companies["id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

pnl_ids = set(
    pnl["company_id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

missing = sorted(pnl_ids - db_ids)

print("P&L companies:", len(pnl_ids))
print("DB companies:", len(db_ids))
print("Missing company IDs:", len(missing))

if missing:
    print("\nMISSING IDs:")
    for x in missing:
        print(x)
else:
    print("\nALL P&L COMPANY IDs EXIST IN COMPANIES.")

con.close()