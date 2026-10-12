from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "transactions-2026-10-07.csv"
OUTPUT = ROOT / "data" / "sales_cleaned.csv"
SQM_TO_SQFT = 10.7639

df = pd.read_csv(INPUT)
log = {"1. Rows in raw file": len(df)}

# --- 1. Remove duplicate sales
df = df.drop_duplicates(subset="TRANSACTION_NUMBER")
log["2. After removing duplicates"] = len(df)

# --- 2. Keep only homes: flats and villas
df = df[df["PROP_SB_TYPE_EN"].isin(["Flat", "Villa"])]
log["3. After keeping only flats & villas"] = len(df)

# --- 3. Fix data types
df["sale_date"] = pd.to_datetime(df["INSTANCE_DATE"], format="%d-%m-%Y %H:%M", errors="coerce")
df["price_aed"] = pd.to_numeric(df["TRANS_VALUE"], errors="coerce")
df["size_sqm"] = pd.to_numeric(df["PROCEDURE_AREA"], errors="coerce")

# --- 4. Remove impossible values (no date, price under AED 100k, size under 15 m2)
df = df[df["sale_date"].notna() & (df["price_aed"] >= 100_000) & (df["size_sqm"] >= 15)]
log["4. After removing impossible prices/sizes"] = len(df)

# --- 5. Price per sqft, the standard Dubai measure
df["size_sqft"] = df["size_sqm"] * SQM_TO_SQFT
df["price_per_sqft"] = df["price_aed"] / df["size_sqft"]

# --- 6. Remove extreme outliers: bottom 1% and top 1% of price per sqft,
#        separately for flats and villas (they have different price levels)
low  = df.groupby("PROP_SB_TYPE_EN")["price_per_sqft"].transform(lambda s: s.quantile(0.01))
high = df.groupby("PROP_SB_TYPE_EN")["price_per_sqft"].transform(lambda s: s.quantile(0.99))
df = df[(df["price_per_sqft"] >= low) & (df["price_per_sqft"] <= high)]
log["5. After removing price outliers"] = len(df)

# --- 7. Tidy columns for analysis
df["community"] = df["AREA_EN"].str.strip().str.title()          # "BUSINESS BAY" -> "Business Bay"
df["property_type"] = df["PROP_SB_TYPE_EN"].map({"Flat": "Apartment", "Villa": "Villa"})
df["registration"] = df["IS_OFFPLAN_EN"].map({"Off-Plan": "Off-plan", "Ready": "Ready"})
df["bedrooms"] = df["ROOMS_EN"].fillna("Unknown")
df["near_metro"] = df["NEAREST_METRO_EN"].notna().map({True: "Yes", False: "No"})
df["project"] = df["PROJECT_EN"].fillna("Unknown")
df["month"] = df["sale_date"].dt.to_period("M").astype(str)       # e.g. 2026-03

clean = df[["TRANSACTION_NUMBER", "sale_date", "month", "community", "project",
            "property_type", "bedrooms", "registration", "near_metro",
            "size_sqft", "price_aed", "price_per_sqft"]].round(2)

OUTPUT.parent.mkdir(exist_ok=True)
clean.to_csv(OUTPUT, index=False)

# --- Cleaning report
print("CLEANING LOG")
for step, rows in log.items():
    print(f"  {step:45s} {rows:>8,}")
print(f"\nRows kept: {len(clean):,} ({len(clean) / log['1. Rows in raw file']:.0%} of raw)")
print("\nMedian price per sqft (AED):")
print(clean.groupby("property_type")["price_per_sqft"].median().round(0))
print(f"\nSaved to: {OUTPUT}")