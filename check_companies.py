import pandas as pd

df = pd.read_excel("data/raw/companies.xlsx", header=1)

df.columns = [
    str(c).strip().lower().replace(" ", "_")
    for c in df.columns
]

wanted = [
    "ULTRACEMCO",
    "UNIONBANK",
    "UNITDSPR",
    "VBL",
    "VEDL",
    "WIPRO",
    "ZOMATO",
    "ZYDUSLIFE",
]

print(df[df["id"].astype(str).str.upper().isin(wanted)][
    ["id", "company_name"]
].to_string(index=False))