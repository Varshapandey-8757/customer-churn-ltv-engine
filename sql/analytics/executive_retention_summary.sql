-- =============================================================================
-- Business Analytics: executive_retention_summary.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Executive KPI dashboard summary providing a single-pane snapshot of
--   customer base scale, global churn %, MRR at risk, and segment health.
-- =============================================================================

WITH features AS (
    SELECT * FROM fct_churn_ltv_features
)

SELECT
    -- Customer Base Volume
    COUNT(customer_id) AS total_customer_base,
    SUM(CASE WHEN is_churned = 0 THEN 1 ELSE 0 END) AS active_customers,
    SUM(is_churned) AS churned_customers,
    ROUND(CAST(SUM(is_churned) AS FLOAT) * 100.0 / COUNT(customer_id), 2) AS overall_churn_rate_pct,

    -- Financial Totals (MRR & ARR equivalent)
    ROUND(SUM(monthly_charges), 2) AS total_mrr,
    ROUND(SUM(monthly_charges) * 12.0, 2) AS estimated_arr,
    ROUND(AVG(monthly_charges), 2) AS global_arpu,

    -- Cumulative Realized Revenue (Historical LTV)
    ROUND(SUM(total_charges), 2) AS total_realized_revenue,
    ROUND(AVG(total_charges), 2) AS avg_historical_ltv,

    -- Churn Financial Impact
    ROUND(SUM(CASE WHEN is_churned = 1 THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_mrr,
    ROUND(SUM(CASE WHEN is_churned = 1 THEN total_charges ELSE 0 END), 2) AS lost_historical_revenue,

    -- Active Exposure: MRR at Risk from High Risk Segment
    ROUND(
        SUM(CASE WHEN is_churned = 0 AND risk_profile = 'High Risk' THEN monthly_charges ELSE 0 END), 2
    ) AS active_mrr_at_risk,

    -- Target for Immediate Retention (High Value & High Risk)
    SUM(CASE WHEN is_churned = 0 AND customer_strategic_segment = 'High Value - Urgent Retention' THEN 1 ELSE 0 END) AS urgent_retention_target_accounts,
    ROUND(
        SUM(CASE WHEN is_churned = 0 AND customer_strategic_segment = 'High Value - Urgent Retention' THEN monthly_charges ELSE 0 END), 2
    ) AS urgent_retention_mrr

FROM features;
