/*CREATE DATABASE DubaiRealEstate;
GO
USE DubaiRealEstate;
GO
*/


USE DubaiRealEstate;

SELECT COUNT(*) AS total_rows FROM dbo.sales;

SELECT TOP 5 * FROM dbo.sales;


-- Q1. Monthly market trend: volume, value, apartment price per sqft, off-plan share

SELECT
    month,
    COUNT(*)                                        AS sales,
    ROUND(SUM(price_aed) / 1e9, 2)                  AS value_aed_bn,
    ROUND(SUM(CASE WHEN property_type = 'Apartment' THEN price_aed END)
        / SUM(CASE WHEN property_type = 'Apartment' THEN size_sqft END), 0) AS apt_price_per_sqft,
    CAST(100.0 * SUM(CASE WHEN registration = 'Off-plan' THEN 1 ELSE 0 END)
     / COUNT(*) AS DECIMAL(5,1))                    AS offplan_pct
FROM dbo.sales
GROUP BY month
ORDER BY month;


-- Q2. Top 10 communities by total sales value

SELECT TOP 10
    community,
    COUNT(*)                                        AS sales,
    ROUND(SUM(price_aed) / 1e9, 2)                  AS value_aed_bn,
    ROUND(AVG(price_aed), -3)                       AS avg_price_aed,
    ROUND(SUM(CASE WHEN property_type = 'Apartment' THEN price_aed END)
        / NULLIF(SUM(CASE WHEN property_type = 'Apartment' THEN size_sqft END), 0), 0) AS apt_price_per_sqft,
    CAST(100.0 * SUM(CASE WHEN registration = 'Off-plan' THEN 1 ELSE 0 END)
     / COUNT(*) AS DECIMAL(5,1))                    AS offplan_pct
FROM dbo.sales
GROUP BY community
ORDER BY SUM(price_aed) DESC;


-- Q3. Off-plan vs ready apartments: price comparison
WITH apt AS (
    SELECT
        registration,
        COUNT(*)                            AS sales,
        SUM(price_aed) / SUM(size_sqft)     AS price_per_sqft,
        AVG(price_aed)                      AS avg_price,
        AVG(size_sqft)                      AS avg_size_sqft
    FROM dbo.sales
    WHERE property_type = 'Apartment'
    GROUP BY registration
)
SELECT
    registration,
    sales,
    CAST(price_per_sqft AS DECIMAL(10,0))   AS price_per_sqft,
    CAST(avg_price AS DECIMAL(12,0))        AS avg_price_aed,
    CAST(avg_size_sqft AS DECIMAL(8,0))     AS avg_size_sqft,
    CAST(100.0 * (price_per_sqft / (SELECT price_per_sqft FROM apt WHERE registration = 'Ready') - 1)
         AS DECIMAL(5,1))                   AS premium_vs_ready_pct
FROM apt;


-- Q4. Apartment sales by bedroom type, with share of total
SELECT
    bedrooms,
    COUNT(*)                                            AS sales,
    CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(5,1)) AS share_pct,
    CAST(AVG(price_aed) AS DECIMAL(12,0))               AS avg_price_aed,
    CAST(SUM(price_aed) / SUM(size_sqft) AS DECIMAL(10,0)) AS price_per_sqft
FROM dbo.sales
WHERE property_type = 'Apartment'
  AND bedrooms <> 'Unknown'
GROUP BY bedrooms
ORDER BY sales DESC;

GO
-- View used by the Power BI dashboard
CREATE OR ALTER VIEW dbo.vw_sales_dashboard AS
SELECT
    TRANSACTION_NUMBER,
    CAST(sale_date AS DATE)                         AS sale_date,
    month,
    community,
    project,
    property_type,
    CASE WHEN bedrooms IN ('5 B/R', '6 B/R', 'PENTHOUSE') THEN '5+ B/R / Penthouse'
         ELSE bedrooms END                          AS bedrooms,
    registration,
    near_metro,
    size_sqft,
    price_aed,
    price_per_sqft,
    CASE WHEN price_aed < 1000000 THEN 'Under 1M'
         WHEN price_aed < 2000000 THEN '1M - 2M'
         WHEN price_aed < 5000000 THEN '2M - 5M'
         ELSE '5M+' END                             AS price_band
FROM dbo.sales
WHERE bedrooms <> 'Office';
GO

SELECT price_band, COUNT(*) AS sales
FROM dbo.vw_sales_dashboard
GROUP BY price_band
ORDER BY MIN(price_aed);