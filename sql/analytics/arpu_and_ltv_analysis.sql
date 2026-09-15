-- =============================================================================
-- Business Analytics: arpu_and_ltv_analysis.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Computes Average Revenue Per User (ARPU), Total Realized Revenue,
--   Projected Lifetime Value, and Retention metrics sliced by value tiers
--   and strategic customer segments.
-- =============================================================================

WITH features AS (
    SELECT * FROM fct_churn_ltv_features
)

SELECT
    value_tier,
    risk_profile,
    customer_strategic_segment,
    COUNT(customer_id) AS customer_count,
    ROUND(CAST(SUM(is_churned) AS FLOAT) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    
    -- ARPU Metrics
    ROUND(AVG(monthly_charges), 2) AS arpu,
    ROUND(SUM(monthly_charges), 2) AS monthly_recurring_revenue,
    
    -- LTV Metrics
    ROUND(AVG(historical_ltv), 2) AS avg_historical_ltv,
    ROUND(AVG(estimated_total_ltv), 2) AS avg_projected_ltv,
    ROUND(SUM(historical_ltv), 2) AS total_historical_revenue,
    ROUND(SUM(estimated_total_ltv), 2) AS total_projected_ltv_pipeline,
    
    -- Revenue At Risk
    ROUND(SUM(CASE WHEN risk_profile = 'High Risk' AND is_churned = 0 THEN monthly_charges ELSE 0 END), 2) AS active_mrr_at_risk

FROM features
GROUP BY 
    value_tier,
    risk_profile,
    customer_strategic_segment
ORDER BY 
    monthly_recurring_revenue DESC;
