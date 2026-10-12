# Dubai Residential Property Market Analysis (2026)

An end-to-end analytics project on **105,000+ real residential property sales** registered with the **Dubai Land Department (DLD)** in 2026. It takes raw government data through Python cleaning, a SQL Server database, T-SQL analysis and an interactive Power BI dashboard.

**Tools:** Python (pandas) · SQL Server (T-SQL) · Power BI (DAX)

![Dashboard](images/dashboard.png)

---

## Business questions

1. How is Dubai's residential market moving month by month in 2026?
2. Which communities drive the most sales value?
3. Do off-plan apartments cost more than ready ones, and why?
4. What size of home do buyers actually purchase?

## Key findings (Jan–Sep 2026)

| Metric | Value |
|---|---|
| Residential sales | **103,599** |
| Total sales value | **AED 192.0 billion** |
| Off-plan share of sales | **75.7%** |
| Homes sold under AED 2M | **~69%** |

**1. Off-plan costs 21% more per sqft, but buyers pay the same total price.**
Off-plan apartments sold at AED 2,023/sqft vs AED 1,674/sqft for ready units. Yet the average ticket size is almost identical (AED 1.64M vs 1.66M), because off-plan units are **18% smaller** (811 vs 991 sqft). Developers are keeping prices affordable by shrinking units.

**2. Small units dominate.** Studios and 1-bedroom apartments make up **72% of apartment sales**, which points to an investor-driven market focused on rentable units.

**3. Sales are concentrated in new-launch areas.** Madinat Al Mataar (the Dubai South area) led with about 12,000 sales, **99% of them off-plan**. Downtown Dubai (registered by DLD as *Burj Khalifa*) had the highest average price (AED 3.5M) and was mostly ready stock.

**4. Most homes sell for under AED 2 million.** Despite Dubai's luxury image, only about 4% of sales were above AED 5M.

**5. Activity cooled in the second half.** Monthly sales fell from about 14,000 in January–February to about 9,400 in September. Off-plan apartment prices per sqft also stepped down from around AED 2,100 to around AED 1,900 from May. This is partly a **mix effect**: more launches in lower-priced communities pull the average down, even if individual homes did not get cheaper.

---

## Project workflow

```
DLD website (CSV)  →  Python: data quality check & cleaning  →  SQL Server  →  T-SQL analysis  →  Power BI dashboard
   123,311 rows          105,746 clean rows (86% kept)         reporting view     4 business queries      KPIs + trends
```

### 1. Data source
Residential sales transactions from the [Dubai Land Department open data portal](https://dubailand.gov.ae/en/open-data/real-estate-data/), 1 Jan 2026 to early Oct 2026.

### 2. Data cleaning: Python (`src/`)
- `eda.py` profiles the raw data: missing values, duplicates, categories, and value ranges.
- `clean.py` produces the analysis-ready file.

| Cleaning step | Rows |
|---|---|
| Raw file | 123,311 |
| Removed duplicate transactions | 123,288 |
| Kept only flats and villas (removed offices, shops, hotel rooms, land, whole buildings) | 108,452 |
| Removed impossible values (price < AED 100k, size < 15 m²) | 107,906 |
| Removed extreme price-per-sqft outliers (top and bottom 1%, by property type) | **105,746** |

Other cleaning steps: converted m² to sqft, standardised inconsistent area-name casing (e.g. `BUSINESS BAY` → `Business Bay`), and turned the sparse metro column into a yes/no flag.

**Validation:** the cleaned median apartment price (AED 1,714/sqft) is within 1.5% of DLD's published median for the same period, which confirms the cleaning did not distort the data.

### 3. SQL analysis: SQL Server (`sql/analysis.sql`)
- **Q1** Monthly trend: volume, value, apartment price per sqft, off-plan share
- **Q2** Top 10 communities by sales value
- **Q3** Off-plan vs ready apartment pricing (CTE)
- **Q4** Sales by bedroom type with share of total (window function)
- **`vw_sales_dashboard`**: a reporting view that groups rare categories and adds price bands. It is the single source for Power BI.

SQL techniques used: conditional aggregation (`SUM(CASE WHEN …)`), CTEs, window functions (`SUM(...) OVER ()`), `NULLIF` for safe division, and views.

### 4. Dashboard: Power BI (`powerbi/Dubai_Real_Estate.pbix`)
- Connected to SQL Server via the reporting view (Import mode)
- DAX measures: Total Sales, Sales Value, Median Price, Apartment Price per Sqft, Off-plan Share, Off-plan Premium (`CALCULATE`, `DIVIDE`, `VAR`)
- Interactive slicers for month, property type, community and registration type
- The incomplete current month is excluded from trend charts so it does not distort them

**Cross-check:** the Off-plan Premium measure in DAX (20.8%) matches the SQL result exactly.

---

## Design decisions

- **Price per sqft is area-weighted** (`total price ÷ total area`), not an average of per-unit ratios, so a few small studios cannot skew it.
- **Apartments and villas are analysed separately.** DLD's villa size may reflect plot area, so mixing the two would distort averages.
- **Official DLD area names are kept** as registered. Some differ from marketing names (e.g. *Burj Khalifa* = Downtown Dubai, *Madinat Al Mataar* = the Dubai South area).

## Limitations and next steps

- The data covers 2026 only. Adding 2025 would allow year-on-year comparisons.
- The off-plan premium partly reflects location mix. A like-for-like comparison within each community is a natural next step.
- Planned additions: rental yield using Ejari rent contracts, and a price-prediction model in Python.

## Repository structure

```
dubai_real_estate/
├── src/
│   ├── eda.py              # data quality profiling
│   └── clean.py            # cleaning pipeline
├── sql/
│   └── analysis.sql        # business queries + reporting view
├── powerbi/
│   └── Dubai_Real_Estate.pbix
├── images/
│   └── dashboard.png
└── README.md
```

The raw and cleaned CSV files are not included because of their size. Download the raw data from the DLD portal linked above and run `src/clean.py` to recreate them.

---

**Author:** Rakesh Nagesh Rao · Data Analyst / BI Developer
[LinkedIn](https://www.linkedin.com/in/your-profile) · your.email@example.com
