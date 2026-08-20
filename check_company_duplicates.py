import pandas as pd

df = pd.read_excel("data/raw/companies.xlsx", header=1)

df.columns = [
    str(c).strip().lower().replace(" ", "_")
    for c in df.columns
]

print("Rows:", len(df))
print("Unique IDs:", df["id"].nunique())
print("\nDuplicate IDs:")

dupes = df[df["id"].duplicated(keep=False)].sort_values("id")

if dupes.empty:
    print("NONE")
else:
    print(dupes[["id", "company_name"]].to_string(index=False))
