import pandas as pd

df = pd.read_csv(r"data\transactions-2026-10-07.csv")  

# 1. Size and missing values
print("Rows, columns:", df.shape)
print("\nMissing values per column:")
print(df.isna().sum())

# 2. Duplicates
print("\nDuplicate transaction numbers:", df["TRANSACTION_NUMBER"].duplicated().sum())

# 3. What categories exist?
for col in ["GROUP_EN", "IS_OFFPLAN_EN", "USAGE_EN", "PROP_TYPE_EN", "PROP_SB_TYPE_EN", "ROOMS_EN"]:
    print(f"\n{col}:")
    print(df[col].value_counts(dropna=False).head(10))

# 4. Price and size ranges (looking for impossible values)
print("\nPrice (AED) and size (sq m) summary:")
print(df[["TRANS_VALUE", "PROCEDURE_AREA"]].describe().round(0))

# 5. How many communities?
print("\nNumber of communities:", df["AREA_EN"].nunique())
print(df["AREA_EN"].value_counts().head(15))
