-- =============================================================================
-- Business Analytics: service_penetration_churn_impact.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Evaluates service penetration / attach rates and quantifies their direct 
--   impact on customer churn rate and LTV retention.
-- =============================================================================

WITH features AS (
    SELECT * FROM fct_churn_ltv_features
)

SELECT 
    'Tech Support' AS service_name,
    CASE WHEN has_tech_support = 1 THEN 'Enrolled' ELSE 'Not Enrolled' END AS enrollment_status,
    COUNT(customer_id) AS total_customers,
    ROUND(CAST(SUM(is_churned) AS FLOAT) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS arpu,
    ROUND(AVG(total_charges), 2) AS avg_ltv
FROM features
GROUP BY has_tech_support

UNION ALL

SELECT 
    'Online Security' AS service_name,
    CASE WHEN has_online_security = 1 THEN 'Enrolled' ELSE 'Not Enrolled' END AS enrollment_status,
    COUNT(customer_id) AS total_customers,
    ROUND(CAST(SUM(is_churned) AS FLOAT) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS arpu,
    ROUND(AVG(total_charges), 2) AS avg_ltv
FROM features
GROUP BY has_online_security

UNION ALL

SELECT 
    'Fiber Optic w/o TechSupport Risk' AS service_name,
    CASE WHEN has_fiber_no_techsupport_risk = 1 THEN 'High Risk Exposure' ELSE 'Normal / Safe' END AS enrollment_status,
    COUNT(customer_id) AS total_customers,
    ROUND(CAST(SUM(is_churned) AS FLOAT) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS arpu,
    ROUND(AVG(total_charges), 2) AS avg_ltv
FROM features
GROUP BY has_fiber_no_techsupport_risk

UNION ALL

SELECT 
    'Streaming Bundle (TV + Movies)' AS service_name,
    CASE WHEN has_streaming_bundle = 1 THEN 'Both Subscribed' ELSE 'Partial / None' END AS enrollment_status,
    COUNT(customer_id) AS total_customers,
    ROUND(CAST(SUM(is_churned) AS FLOAT) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS arpu,
    ROUND(AVG(total_charges), 2) AS avg_ltv
FROM features
GROUP BY has_streaming_bundle

ORDER BY 
    service_name, 
    enrollment_status;
