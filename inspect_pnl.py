import pandas as pd

df = pd.read_excel("data/raw/profitandloss.xlsx", header=1)

df.columns = [
    str(c).strip().lower().replace(" ", "_")
    for c in df.columns
]

print("LAST 20 P&L COMPANIES:")
print(
    df[["company_id", "year"]]
    .tail(20)
    .to_string(index=False)
)
