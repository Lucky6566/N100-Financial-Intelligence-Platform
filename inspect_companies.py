import pandas as pd

df = pd.read_excel("data/raw/companies.xlsx", header=1)

df.columns = [
    str(c).strip().lower().replace(" ", "_")
    for c in df.columns
]

print("LAST 15 COMPANIES:")
print(df[["id", "company_name"]].tail(15).to_string(index=False))
