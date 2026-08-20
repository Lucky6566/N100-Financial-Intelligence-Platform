import pandas as pd

MASTER = "data/raw/companies.xlsx"

TITLE_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}

master = pd.read_excel(MASTER, header=None)
master.columns = master.iloc[1]
master = master.iloc[2:]

master_ids = set(
    master["id"].dropna().astype(str).str.strip()
)

files = [
    "sectors.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
    "financial_ratios.xlsx",
    "peer_groups.xlsx",
    "stock_prices.xlsx",
    "market_cap.xlsx",
]

print("=" * 70)
print("N100 COMPANY-ID VALIDATION")
print("=" * 70)
print("Master companies:", len(master_ids))
print()

for filename in files:

    path = "data/raw/" + filename

    if filename in TITLE_FILES:
        raw = pd.read_excel(path, header=None)
        raw.columns = raw.iloc[1]
        df = raw.iloc[2:].copy()
    else:
        df = pd.read_excel(path)

    df = df.dropna(how="all")

    if "company_id" not in df.columns:
        print(f"{filename:25} company_id NOT FOUND")
        continue

    company_ids = (
        df["company_id"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    invalid_ids = sorted(
        set(company_ids) - master_ids
    )

    invalid_rows = (
        ~company_ids.isin(master_ids)
    ).sum()

    print(
        f"{filename:25} "
        f"total={len(df):5} "
        f"invalid_ids={len(invalid_ids):2} "
        f"invalid_rows={invalid_rows:5}"
    )

    if invalid_ids:
        print("   Invalid:", invalid_ids)

print()
print("=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)
