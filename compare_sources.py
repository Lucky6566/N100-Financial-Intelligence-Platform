import pandas as pd

companies = pd.read_excel("data/raw/companies.xlsx", header=1)
pnl = pd.read_excel("data/raw/profitandloss.xlsx", header=1)

companies.columns = [
    str(c).strip().lower().replace(" ", "_")
    for c in companies.columns
]

pnl.columns = [
    str(c).strip().lower().replace(" ", "_")
    for c in pnl.columns
]

company_ids = set(
    companies["id"].astype(str).str.strip().str.upper()
)

pnl_ids = set(
    pnl["company_id"].astype(str).str.strip().str.upper()
)

print("Companies.xlsx:", len(company_ids))
print("P&L:", len(pnl_ids))

print("\nIn P&L but NOT companies.xlsx:")
print(sorted(pnl_ids - company_ids))

print("\nIn companies.xlsx but NOT P&L:")
print(sorted(company_ids - pnl_ids))
