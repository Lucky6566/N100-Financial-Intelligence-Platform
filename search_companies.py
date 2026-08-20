import pandas as pd

df = pd.read_excel(
    "data/raw/companies.xlsx",
    header=None
)

targets = [
    "ULTRACEMCO",
    "UNIONBANK",
    "UNITDSPR",
    "VBL",
    "VEDL",
    "WIPRO",
    "ZOMATO",
    "ZYDUSLIFE",
]

for target in targets:
    print(f"\n===== {target} =====")

    matches = df[
        df.astype(str)
        .apply(
            lambda row: row.str.upper()
            .str.contains(target, regex=False)
            .any(),
            axis=1
        )
    ]

    if len(matches):
        print(matches.to_string(index=False, header=False))
    else:
        print("NOT FOUND")