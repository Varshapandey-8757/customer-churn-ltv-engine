-- Customer Churn LTV Engine
-- Churn Analysis Queries

-- 1. Overall churn rate
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        COUNT(*) FILTER (WHERE churn = 'Yes') * 100.0 / COUNT(*),
        2
    ) AS churn_rate_percent
FROM analytics.customer_churn;


-- 2. Churn by contract type
SELECT
    contract,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        COUNT(*) FILTER (WHERE churn = 'Yes') * 100.0 / COUNT(*),
        2
    ) AS churn_rate_percent
FROM analytics.customer_churn
GROUP BY contract
ORDER BY churn_rate_percent DESC;


-- 3. Churn by internet service
SELECT
    internet_service,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        COUNT(*) FILTER (WHERE churn = 'Yes') * 100.0 / COUNT(*),
        2
    ) AS churn_rate_percent
FROM analytics.customer_churn
GROUP BY internet_service
ORDER BY churn_rate_percent DESC;


-- 4. Cumulative charges associated with churned customers
SELECT
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        SUM(total_charges) FILTER (WHERE churn = 'Yes'),
        2
    ) AS churned_customer_total_charges
FROM analytics.customer_churn;


-- 5. Average charges and tenure by churn status
SELECT
    churn,
    COUNT(*) AS customers,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(AVG(total_charges), 2) AS avg_total_charges,
    ROUND(AVG(tenure), 2) AS avg_tenure_months
FROM analytics.customer_churn
GROUP BY churn
ORDER BY churn;
-- 6. Churn by tenure group
SELECT
    CASE
        WHEN tenure <= 6 THEN '0-6 months'
        WHEN tenure <= 12 THEN '7-12 months'
        WHEN tenure <= 24 THEN '13-24 months'
        WHEN tenure <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END AS tenure_group,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS churned_customers,
    ROUND(
        COUNT(*) FILTER (WHERE churn = 'Yes') * 100.0 / COUNT(*),
        2
    ) AS churn_rate_percent
FROM analytics.customer_churn
GROUP BY
    CASE
        WHEN tenure <= 6 THEN '0-6 months'
        WHEN tenure <= 12 THEN '7-12 months'
        WHEN tenure <= 24 THEN '13-24 months'
        WHEN tenure <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END
ORDER BY MIN(tenure);