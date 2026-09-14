-- =============================================================================
-- Business Analytics: churn_by_cohort_segment.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Calculates customer counts, churn counts, churn rates, and lost monthly revenue
--   sliced by tenure cohorts, contract types, and payment methods.
-- =============================================================================

WITH features AS (
    SELECT * FROM fct_churn_ltv_features
)

SELECT
    tenure_cohort,
    contract_type,
    payment_method,
    COUNT(customer_id) AS total_customers,
    SUM(is_churned) AS churned_customers,
    ROUND(CAST(SUM(is_churned) AS FLOAT) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS total_mrr,
    ROUND(SUM(CASE WHEN is_churned = 1 THEN monthly_charges ELSE 0 END), 2) AS lost_mrr,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge,
    ROUND(AVG(total_charges), 2) AS avg_total_charges

FROM features
GROUP BY 
    tenure_cohort, 
    contract_type, 
    payment_method
ORDER BY 
    churn_rate_pct DESC,
    lost_mrr DESC;
