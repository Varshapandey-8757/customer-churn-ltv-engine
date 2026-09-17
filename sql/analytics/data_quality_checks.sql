-- Customer Churn LTV Engine
-- PostgreSQL Data Quality Checks
-- Owner: Harshitha - Data Engineering & PostgreSQL


-- =========================================================
-- 1. Total number of customers
-- =========================================================

SELECT
    COUNT(*) AS total_customers
FROM analytics.customer_churn;


-- =========================================================
-- 2. Check duplicate customer IDs
-- =========================================================

SELECT
    COUNT(*) AS total_customers,
    COUNT(DISTINCT customer_id) AS unique_customer_ids
FROM analytics.customer_churn;


-- =========================================================
-- 3. Check missing values
-- =========================================================

SELECT
    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE customer_id IS NULL
    ) AS missing_customer_id,

    COUNT(*) FILTER (
        WHERE gender IS NULL
    ) AS missing_gender,

    COUNT(*) FILTER (
        WHERE tenure IS NULL
    ) AS missing_tenure,

    COUNT(*) FILTER (
        WHERE monthly_charges IS NULL
    ) AS missing_monthly_charges,

    COUNT(*) FILTER (
        WHERE total_charges IS NULL
    ) AS missing_total_charges,

    COUNT(*) FILTER (
        WHERE churn IS NULL
    ) AS missing_churn

FROM analytics.customer_churn;


-- =========================================================
-- 4. Validate numeric ranges
-- =========================================================

SELECT
    MIN(tenure) AS minimum_tenure,
    MAX(tenure) AS maximum_tenure,
    MIN(monthly_charges) AS minimum_monthly_charges,
    MAX(monthly_charges) AS maximum_monthly_charges,
    MIN(total_charges) AS minimum_total_charges,
    MAX(total_charges) AS maximum_total_charges
FROM analytics.customer_churn;


-- =========================================================
-- 5. Validate churn distribution
-- =========================================================

SELECT
    churn,
    COUNT(*) AS customer_count,
    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM analytics.customer_churn
GROUP BY churn
ORDER BY churn;


-- =========================================================
-- 6. Check tenure = 0 customers
--    These records can have NULL TotalCharges
-- =========================================================

SELECT
    COUNT(*) AS zero_tenure_customers,
    COUNT(*) FILTER (
        WHERE total_charges IS NULL
    ) AS zero_tenure_missing_total_charges
FROM analytics.customer_churn
WHERE tenure = 0;


-- =========================================================
-- 7. Check for invalid churn values
-- =========================================================

SELECT DISTINCT churn
FROM analytics.customer_churn
ORDER BY churn;


-- =========================================================
-- 8. Check customer ID NULL values
-- =========================================================

SELECT *
FROM analytics.customer_churn
WHERE customer_id IS NULL;